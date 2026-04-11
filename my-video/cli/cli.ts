#!/usr/bin/env node

import yargs from "yargs";
import { hideBin } from "yargs/helpers";
import prompts from "prompts";
import ora from "ora";
import chalk from "chalk";
import * as dotenv from "dotenv";
import { execSync } from "child_process";
import {
  generateAiImage,
  generateVoice,
  getGenerateImageDescriptionPrompt,
  getGenerateStoryPrompt,
  geminiStructuredCompletion,
  setApiKey,
  setFalApiKey,
} from "./service";
import {
  ContentItemWithDetails,
  StoryMetadataWithDetails,
  StoryScript,
  StoryWithImages,
  Timeline,
} from "../src/lib/types";
import { v4 as uuidv4 } from "uuid";
import * as fs from "fs";
import * as path from "path";
import { createTimeLineFromStoryWithDetails } from "./timeline";

dotenv.config({ quiet: true });

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Keys {
  geminiApiKey: string;
  elevenlabsApiKey: string;
  falApiKey: string;
}

interface GenerateOptions {
  apiKey?: string;
  elevenlabsApiKey?: string;
  falApiKey?: string;
  title?: string;
  topic?: string;
}

// ---------------------------------------------------------------------------
// Filesystem helpers
// ---------------------------------------------------------------------------

class ContentFS {
  title: string;
  slug: string;

  constructor(title: string) {
    this.title = title;
    this.slug = this.getSlug();
  }

  saveDescriptor(descriptor: StoryMetadataWithDetails) {
    const filePath = path.join(this.getDir(), "descriptor.json");
    fs.writeFileSync(filePath, JSON.stringify(descriptor, null, 2));
  }

  saveTimeline(timeline: Timeline) {
    const filePath = path.join(this.getDir(), "timeline.json");
    fs.writeFileSync(filePath, JSON.stringify(timeline, null, 2));
  }

  getDir(dir?: string): string {
    const segments = ["public", "content", this.slug];
    if (dir) segments.push(dir);
    const p = path.join(process.cwd(), ...segments);
    fs.mkdirSync(p, { recursive: true });
    return p;
  }

  getImagePath(uid: string): string {
    return path.join(this.getDir("images"), `${uid}.png`);
  }

  getAudioPath(uid: string): string {
    return path.join(this.getDir("audio"), `${uid}.mp3`);
  }

  getSlug(): string {
    return this.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }
}

// ---------------------------------------------------------------------------
// Resolve API keys (prompt once if missing from env)
// ---------------------------------------------------------------------------

async function resolveKeys(options: Partial<GenerateOptions>): Promise<Keys> {
  let geminiApiKey = options.apiKey || process.env.GEMINI_API_KEY;
  let elevenlabsApiKey = options.elevenlabsApiKey || process.env.ELEVENLABS_API_KEY;
  let falApiKey = options.falApiKey || process.env.FAL_KEY;

  if (!geminiApiKey) {
    const res = await prompts({
      type: "password",
      name: "v",
      message: "Enter your Gemini API key:",
      validate: (v) => v.length > 0 || "Required",
    });
    if (!res.v) { console.log(chalk.red("Gemini API key is required.")); process.exit(1); }
    geminiApiKey = res.v;
  }

  if (!elevenlabsApiKey) {
    const res = await prompts({
      type: "password",
      name: "v",
      message: "Enter your ElevenLabs API key:",
      validate: (v) => v.length > 0 || "Required",
    });
    if (!res.v) { console.log(chalk.red("ElevenLabs API key is required.")); process.exit(1); }
    elevenlabsApiKey = res.v;
  }

  if (!falApiKey) {
    const res = await prompts({
      type: "password",
      name: "v",
      message: "Enter your Fal.ai API key:",
      validate: (v) => v.length > 0 || "Required",
    });
    if (!res.v) { console.log(chalk.red("Fal.ai API key is required.")); process.exit(1); }
    falApiKey = res.v;
  }

  return { geminiApiKey: geminiApiKey!, elevenlabsApiKey: elevenlabsApiKey!, falApiKey: falApiKey! };
}

// ---------------------------------------------------------------------------
// Core asset generation — throws on failure (no process.exit)
// ---------------------------------------------------------------------------

async function generateStoryAssets(title: string, topic: string, keys: Keys): Promise<string> {
  setApiKey(keys.geminiApiKey);
  setFalApiKey(keys.falApiKey);

  console.log(chalk.blue(`\n📖 Creating story: "${title}"`));
  console.log(chalk.blue(`📝 Topic: ${topic}\n`));

  const storyWithDetails: StoryMetadataWithDetails = { shortTitle: title, content: [] };

  const storySpinner = ora("Generating story...").start();
  const storyRes = await geminiStructuredCompletion(
    getGenerateStoryPrompt(title, topic),
    StoryScript,
  );
  storySpinner.succeed(chalk.green("Story generated!"));

  const descSpinner = ora("Generating image descriptions...").start();
  const storyWithImagesRes = await geminiStructuredCompletion(
    getGenerateImageDescriptionPrompt(storyRes.text),
    StoryWithImages,
  );
  descSpinner.succeed(chalk.green("Image descriptions generated!"));

  for (const item of storyWithImagesRes.result) {
    const contentItem: ContentItemWithDetails = {
      text: item.text,
      imageDescription: item.imageDescription,
      uid: uuidv4(),
      audioTimestamps: {
        characters: [],
        characterStartTimesSeconds: [],
        characterEndTimesSeconds: [],
      },
    };
    storyWithDetails.content.push(contentItem);
  }

  const contentFs = new ContentFS(title);
  contentFs.saveDescriptor(storyWithDetails);

  const assetsSpinner = ora("Generating images and voice...").start();
  for (let i = 0; i < storyWithDetails.content.length; i++) {
    const item = storyWithDetails.content[i];
    const total = storyWithDetails.content.length * 2;

    assetsSpinner.text = `[${i * 2 + 1}/${total}] Image: ${item.text}`;
    await generateAiImage({
      prompt: item.imageDescription,
      path: contentFs.getImagePath(item.uid),
      onRetry: (attempt) => {
        assetsSpinner.text = `[${i * 2 + 1}/${total}] Image retry ${attempt}: ${item.text}`;
      },
    });

    assetsSpinner.text = `[${i * 2 + 2}/${total}] Voice: ${item.text}`;
    item.audioTimestamps = await generateVoice(
      item.text,
      keys.elevenlabsApiKey,
      contentFs.getAudioPath(item.uid),
    );
  }

  contentFs.saveDescriptor(storyWithDetails);
  assetsSpinner.succeed(chalk.green("Images and voice generated!"));

  const timelineSpinner = ora("Building timeline...").start();
  const timeline = createTimeLineFromStoryWithDetails(storyWithDetails);
  contentFs.saveTimeline(timeline);
  timelineSpinner.succeed(chalk.green("Timeline saved!"));

  return contentFs.slug;
}

// ---------------------------------------------------------------------------
// Remotion render
// ---------------------------------------------------------------------------

function renderStory(slug: string): void {
  const outDir = path.join(process.cwd(), "out");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  console.log(chalk.blue(`\n🎬 Rendering "${slug}"...`));
  execSync(`npx remotion render src/index.ts ${slug} out/${slug}.mp4`, {
    stdio: "inherit",
    cwd: process.cwd(),
  });
  console.log(chalk.green(`✅ Saved: out/${slug}.mp4\n`));
}

// ---------------------------------------------------------------------------
// Single-story command
// ---------------------------------------------------------------------------

async function generateStory(options: GenerateOptions): Promise<void> {
  try {
    const keys = await resolveKeys(options);
    let { title, topic } = options;

    if (!title || !topic) {
      const res = await prompts([
        {
          type: "text",
          name: "title",
          message: "Title of the story:",
          initial: title,
          validate: (v) => v.length > 0 || "Required",
        },
        {
          type: "text",
          name: "topic",
          message: "Topic of the story:",
          initial: topic,
          validate: (v) => v.length > 0 || "Required",
        },
      ]);

      if (!res.title || !res.topic) {
        console.log(chalk.red("Title and topic are required."));
        process.exit(1);
      }

      title = res.title;
      topic = res.topic;
    }

    await generateStoryAssets(title!, topic!, keys);
    console.log(chalk.green.bold("\n✨ Story generation complete!\n"));
    console.log("Run " + chalk.blue("npm run dev") + " to preview the story");
  } catch (error) {
    console.error(chalk.red("\n❌ Error:"), error);
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Batch command
// ---------------------------------------------------------------------------

async function batchGenerate(options: { render: boolean }): Promise<void> {
  const topicsFile = path.join(process.cwd(), "topics.txt");

  if (!fs.existsSync(topicsFile)) {
    console.error(chalk.red("topics.txt not found. Create it with lines in \"Title|Topic\" format."));
    process.exit(1);
  }

  const lines = fs
    .readFileSync(topicsFile, "utf-8")
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"));

  if (lines.length === 0) {
    console.error(chalk.red("topics.txt has no valid entries."));
    process.exit(1);
  }

  console.log(chalk.bold(`\n🚀 Batch mode: ${lines.length} videos queued\n`));

  const keys = await resolveKeys({});

  const results: Array<{ title: string; status: "success" | "failed"; error?: string }> = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const pipeIndex = line.indexOf("|");

    if (pipeIndex === -1) {
      console.warn(chalk.yellow(`[${i + 1}/${lines.length}] Skipping invalid line: "${line}"`));
      results.push({ title: line, status: "failed", error: "Missing | separator" });
      continue;
    }

    const title = line.slice(0, pipeIndex).trim();
    const topic = line.slice(pipeIndex + 1).trim();

    if (!title || !topic) {
      console.warn(chalk.yellow(`[${i + 1}/${lines.length}] Skipping empty title or topic in: "${line}"`));
      results.push({ title: line, status: "failed", error: "Empty title or topic" });
      continue;
    }

    console.log(chalk.bold.white(`\n━━━ [${i + 1}/${lines.length}] ${title} ━━━`));

    try {
      const slug = await generateStoryAssets(title, topic, keys);

      if (options.render) {
        renderStory(slug);
      }

      results.push({ title, status: "success" });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(chalk.red(`\n❌ Failed "${title}": ${message}\n`));
      results.push({ title, status: "failed", error: message });
    }
  }

  // Summary
  const succeeded = results.filter((r) => r.status === "success").length;
  const failed = results.filter((r) => r.status === "failed").length;

  console.log(chalk.bold(`\n${"━".repeat(50)}`));
  console.log(chalk.bold(`📊 Batch complete: ${succeeded} succeeded, ${failed} failed\n`));
  for (const r of results) {
    if (r.status === "success") {
      console.log(chalk.green(`  ✅ ${r.title}`));
    } else {
      console.log(chalk.red(`  ❌ ${r.title} — ${r.error}`));
    }
  }
  console.log();
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

yargs(hideBin(process.argv))
  .command(
    "batch",
    "Generate all videos from topics.txt and optionally render them",
    (y) =>
      y.option("render", {
        alias: "r",
        type: "boolean",
        default: true,
        description: "Render each video with Remotion after generating assets (use --no-render to skip)",
      }),
    async (argv) => {
      await batchGenerate({ render: argv.render });
    },
  )
  .command(
    "generate",
    "Generate a single story",
    (y) =>
      y
        .option("api-key", { alias: "k", type: "string", description: "Gemini API key" })
        .option("title", { alias: "t", type: "string", description: "Title of the story" })
        .option("topic", { alias: "p", type: "string", description: "Topic of the story" }),
    async (argv) => {
      await generateStory({ apiKey: argv["api-key"], title: argv.title, topic: argv.topic });
    },
  )
  .command(
    "$0",
    "Generate a single story (default)",
    (y) =>
      y
        .option("api-key", { alias: "k", type: "string", description: "Gemini API key" })
        .option("title", { alias: "t", type: "string", description: "Title of the story" })
        .option("topic", { alias: "p", type: "string", description: "Topic of the story" }),
    async (argv) => {
      await generateStory({ apiKey: argv["api-key"], title: argv.title, topic: argv.topic });
    },
  )
  .demandCommand(0, 1)
  .help()
  .alias("help", "h")
  .version()
  .alias("version", "v")
  .strict()
  .parse();

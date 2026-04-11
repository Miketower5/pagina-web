import { GoogleGenAI, HarmCategory, HarmBlockThreshold } from "@google/genai";
import { fal } from "@fal-ai/client";
import z from "zod";
import * as fs from "fs";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { CharacterAlignmentResponseModel } from "@elevenlabs/elevenlabs-js/api";

let apiKey: string | null = null;

export const setApiKey = (key: string) => {
  apiKey = key;
};

export const setFalApiKey = (key: string) => {
  fal.config({ credentials: key });
};

const SAFETY_SETTINGS = [
  { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, threshold: HarmBlockThreshold.BLOCK_NONE },
];

// Recursively convert a JSON Schema object to Google AI's Schema format.
// Google's SDK requires type names to be uppercase ("OBJECT", "STRING", etc.).
function toGoogleSchema(schema: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  if (typeof schema.type === "string") {
    result.type = schema.type.toUpperCase();
  }

  if (schema.properties && typeof schema.properties === "object") {
    result.properties = Object.fromEntries(
      Object.entries(schema.properties as Record<string, unknown>).map(([k, v]) => [
        k,
        toGoogleSchema(v as Record<string, unknown>),
      ]),
    );
  }

  if (schema.items && typeof schema.items === "object") {
    result.items = toGoogleSchema(schema.items as Record<string, unknown>);
  }

  if (Array.isArray(schema.required)) {
    result.required = schema.required;
  }

  return result;
}

export const geminiStructuredCompletion = async <T>(
  prompt: string,
  schema: z.ZodType<T>,
): Promise<T> => {
  const ai = new GoogleGenAI({ apiKey: apiKey! });
  const jsonSchema = z.toJSONSchema(schema);
  const googleSchema = toGoogleSchema(jsonSchema as Record<string, unknown>);

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: googleSchema,
      safetySettings: SAFETY_SETTINGS,
    },
  });

  const text = response.text;
  if (!text) throw new Error("No content in Gemini response");

  const parsed = JSON.parse(text);
  return schema.parse(parsed);
};

function saveUint8ArrayToPng(uint8Array: Uint8Array, filePath: string) {
  const buffer = Buffer.from(uint8Array);
  fs.writeFileSync(filePath, buffer as Uint8Array);
}

interface FalFluxOutput {
  images: Array<{ url: string; width: number; height: number; content_type: string }>;
}

export const generateAiImage = async ({
  prompt,
  path,
  onRetry,
}: {
  prompt: string;
  path: string;
  onRetry: (attempt: number) => void;
}) => {
  const maxRetries = 3;
  let attempt = 0;
  let lastError: Error | null = null;

  while (attempt < maxRetries) {
    try {
      const result = await fal.run("fal-ai/flux/schnell", {
        input: {
          prompt,
          image_size: { width: 1024, height: 1792 },
          num_images: 1,
          output_format: "png",
          enable_safety_checker: false,
        },
      }) as unknown as FalFluxOutput;

      const imageUrl = result.images?.[0]?.url;
      if (!imageUrl) throw new Error("Fal.ai returned no image URL");

      const res = await fetch(imageUrl);
      if (!res.ok) throw new Error(`Failed to download image from Fal.ai: ${res.status}`);

      const arrayBuffer = await res.arrayBuffer();
      saveUint8ArrayToPng(new Uint8Array(arrayBuffer), path);
      return;
    } catch (e) {
      lastError = e instanceof Error ? e : new Error(String(e));
      attempt++;
      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        onRetry(attempt);
      }
    }
  }

  throw lastError!;
};

export const getGenerateStoryPrompt = (title: string, topic: string) => {
  const prompt = `Write a short story with title [${title}] (its topic is [${topic}]).
   You must follow best practices for great storytelling.
   The script must be 8-10 sentences long.
   Story events can be from anywhere in the world, but text must be translated into English language.
   Result result without any formatting and title, as one continuous text.
   Skip new lines.`;

  return prompt;
};

export const getGenerateImageDescriptionPrompt = (storyText: string) => {
  const prompt = `You are given story text.
  Generate (in English) 5-8 very detailed image descriptions  for this story.
  Return their description as json array with story sentences matched to images.
  Story sentences must be in the same order as in the story and their content must be preserved.
  Each image must match 1-2 sentence from the story.
  Images must show story content in a way that is visually appealing and engaging, not just characters.
  Give output in json format:

  [
    {
      "text": "....",
      "imageDescription": "..."
    }
  ]

  <story>
  ${storyText}
  </story>`;

  return prompt;
};

const saveBase64ToMp3 = (data: string, path: string) => {
  const buffer = Buffer.from(data, "base64");
  fs.writeFileSync(path, buffer as Uint8Array);
};

export const generateVoice = async (
  text: string,
  apiKey: string,
  path: string,
): Promise<CharacterAlignmentResponseModel> => {
  const client = new ElevenLabsClient({
    environment: "https://api.elevenlabs.io",
    apiKey,
  });

  const voiceId = "21m00Tcm4TlvDq8ikWAM";

  const data = await client.textToSpeech.convertWithTimestamps(voiceId, {
    text,
  });

  if (!data.alignment || !data.alignment.characterEndTimesSeconds.length) {
    throw new Error("ElevenLabs response missing timestamps");
  }

  saveBase64ToMp3(data.audioBase64, path);
  return data.alignment;
};

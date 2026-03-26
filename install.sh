#!/usr/bin/env sh
set -e

# install.sh — Setup script for pagina-web
# Usage: curl -fsSL https://raw.githubusercontent.com/miketower5/pagina-web/main/install.sh | sh

REPO_URL="https://github.com/miketower5/pagina-web.git"
INSTALL_DIR="${PAGINA_WEB_DIR:-pagina-web}"

log() {
  printf '[pagina-web] %s\n' "$1"
}

die() {
  printf '[pagina-web] ERROR: %s\n' "$1" >&2
  exit 1
}

# Check required tools
command -v git >/dev/null 2>&1 || die "git is required but not installed."
command -v node >/dev/null 2>&1 || die "Node.js is required but not installed. Visit https://nodejs.org"
command -v npm >/dev/null 2>&1 || die "npm is required but not installed."

NODE_VERSION=$(node --version | sed 's/v//')
MAJOR=$(printf '%s' "$NODE_VERSION" | cut -d. -f1)
if [ "$MAJOR" -lt 18 ]; then
  die "Node.js 18 or higher is required (found v$NODE_VERSION)."
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
  log "Repository already exists at '$INSTALL_DIR'. Pulling latest changes..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  log "Cloning repository into '$INSTALL_DIR'..."
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Install dependencies
if [ -f "package.json" ]; then
  log "Installing dependencies..."
  npm install
else
  log "No package.json found — skipping dependency installation."
fi

# Copy example env if .env does not exist
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  cp .env.example .env
  log "Created .env from .env.example — update it with your values before starting."
fi

log "Setup complete."
log ""
log "  cd $INSTALL_DIR"
log "  npm run dev"

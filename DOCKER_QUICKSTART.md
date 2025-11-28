# Docker Quick Start Guide

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose (usually included with Docker Desktop)
- Discord Bot Token (see below)

## Step-by-Step Setup

### 1. Get Your Discord Bot Token

**⚠️ IMPORTANT: If you shared your token publicly, reset it first!**

1. Go to: https://discord.com/developers/applications
2. Select your application (or create a new one)
3. Go to "Bot" section
4. Click "Reset Token" (if you shared it) or copy existing token
5. Copy the token

### 2. Create .env File

In the project root, create a file named `.env`:

```bash
cd /home/wars09/Cursor/discord-bot
nano .env
```

Add this content (replace with YOUR token):
```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_PREFIX=!
```

**Example:**
```env
DISCORD_TOKEN=MTQ0MzkyODM4NzgxODM2MDgzNA.GHWpM_.zW10p-vEeGFgBEx7lXYyqVH1Gm13-_ZteVD138
DISCORD_PREFIX=!
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### 3. Build and Run the Container

```bash
# Build the Docker image and start the container
docker-compose up -d
```

The `-d` flag runs it in detached mode (in the background).

### 4. Check if Bot is Running

```bash
# View logs
docker-compose logs -f
```

You should see:
```
discord-music-bot  | BotName has connected to Discord!
discord-music-bot  | Bot is in X guild(s)
discord-music-bot  | Synced 10 slash command(s)
```

Press `Ctrl+C` to exit logs (bot keeps running).

### 5. Verify in Discord

- Bot should appear online in your server
- Try: `/help` or `!help` in a text channel

## Common Docker Commands

### Start the bot
```bash
docker-compose up -d
```

### View logs (live)
```bash
docker-compose logs -f
```

### View last 100 lines of logs
```bash
docker-compose logs --tail=100
```

### Stop the bot
```bash
docker-compose down
```

### Restart the bot
```bash
docker-compose restart
```

### Rebuild after code changes
```bash
docker-compose build
docker-compose up -d
```

### Check container status
```bash
docker ps
```

### Execute command in container
```bash
docker-compose exec discord-bot <command>
```

## Troubleshooting

### Container won't start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
- Missing `.env` file → Create it with your token
- Invalid token → Reset token in Developer Portal
- Port conflicts → Usually not an issue (no ports exposed)

### "Invalid token" error

1. Verify token in `.env` file (no extra spaces)
2. Make sure you reset the token if you shared it
3. Check token format (should be ~59 characters)

### Bot not connecting

**Check container is running:**
```bash
docker ps
```

**Check logs:**
```bash
docker-compose logs -f
```

**Restart container:**
```bash
docker-compose restart
```

### Update the bot code

After making changes to `bot.py`:
```bash
docker-compose build
docker-compose up -d
```

### View container resource usage
```bash
docker stats discord-music-bot
```

## Docker Compose File Explained

The `docker-compose.yml` file:
- **Builds** the Docker image from `Dockerfile`
- **Runs** the bot in a container
- **Auto-restarts** if it crashes (`restart: unless-stopped`)
- **Loads** environment variables from `.env` file
- **Names** the container `discord-music-bot`

## What's Included in the Container

- Python 3.11
- FFmpeg (for audio processing)
- All Python dependencies (discord.py, yt-dlp, etc.)
- Your bot code
- Runs as non-root user for security

## Production Tips

### Run on server startup

The `restart: unless-stopped` policy means:
- Container starts automatically when Docker starts
- Container restarts if it crashes
- Container stays stopped if you manually stop it

### Monitor the bot

```bash
# Watch logs continuously
docker-compose logs -f

# Check resource usage
docker stats discord-music-bot
```

### Backup your .env file

Keep your `.env` file backed up (but never commit it to Git):
```bash
cp .env .env.backup
```

## Summary

```bash
# 1. Create .env with your token
nano .env

# 2. Start the bot
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# 4. Stop when needed
docker-compose down
```

That's it! Your bot is now running in a Docker container. 🐳


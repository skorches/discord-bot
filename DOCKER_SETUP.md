# Docker Setup Guide for Discord Music Bot

This guide explains how to run the Discord bot using Docker and how to get your bot token.

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose (usually included with Docker Desktop)
- Discord Bot Token (see below for how to get it)

## Getting Your Discord Bot Token

### Step 1: Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** in the top right
3. Give it a name (e.g., "Music Bot")
4. Click **"Create"**

### Step 2: Create a Bot

1. In your application, go to the **"Bot"** section (left sidebar)
2. Click **"Add Bot"** or **"Reset Token"** if you already have one
3. Click **"Yes, do it!"** to confirm
4. **IMPORTANT**: Copy the token immediately (you'll only see it once!)
   - Click **"Reset Token"** if you lose it (creates a new one)
5. Under **"Privileged Gateway Intents"**, enable:
   - ✅ **Message Content Intent** (required for prefix commands)
   - ✅ **Server Members Intent** (optional, for member info)

### Step 3: Get Your Bot's Client ID

1. Go to **"General Information"** section
2. Copy the **"Application ID"** (this is your Client ID)
3. You'll need this for the invite URL

### Step 4: Invite Bot to Your Server

1. Go to **"OAuth2"** → **"URL Generator"**
2. Under **"Scopes"**, select:
   - ✅ `bot`
   - ✅ `applications.commands` (for slash commands)
3. Under **"Bot Permissions"**, select:
   - ✅ `Connect` (join voice channels)
   - ✅ `Speak` (transmit audio)
   - ✅ `Use Voice Activity` (optional, for voice activity)
   - ✅ `Read Message History` (for prefix commands)
   - ✅ `Send Messages` (to respond)
4. Copy the generated URL at the bottom
5. Open the URL in your browser
6. Select your server and click **"Authorize"**
7. Complete any CAPTCHA if prompted

### Step 5: Save Your Token

**Your bot token looks like this:**
```
MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.ABCdef.GHIjkl-MNOPqrsTUVwxyz1234567890
```

**⚠️ SECURITY WARNING:**
- **NEVER** share your bot token publicly
- **NEVER** commit it to Git
- **NEVER** post it online
- If exposed, immediately reset it in the Developer Portal

## Docker Setup

### Option 1: Using Docker Compose (Recommended)

1. **Create a `.env` file** in the project root:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_PREFIX=!
   ```

2. **Build and run:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the bot:**
   ```bash
   docker-compose down
   ```

5. **Restart the bot:**
   ```bash
   docker-compose restart
   ```

### Option 2: Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t discord-music-bot .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name discord-music-bot \
     --restart unless-stopped \
     -e DISCORD_TOKEN=your_bot_token_here \
     -e DISCORD_PREFIX=! \
     discord-music-bot
   ```

3. **View logs:**
   ```bash
   docker logs -f discord-music-bot
   ```

4. **Stop the bot:**
   ```bash
   docker stop discord-music-bot
   ```

5. **Remove the container:**
   ```bash
   docker rm discord-music-bot
   ```

## Environment Variables

You can set these via `.env` file or `-e` flags:

- `DISCORD_TOKEN` - **Required**: Your bot token from Developer Portal
- `DISCORD_PREFIX` - Optional: Command prefix (default: `!`)

## Verifying the Bot is Running

1. **Check container status:**
   ```bash
   docker ps
   ```
   You should see `discord-music-bot` in the list

2. **Check logs:**
   ```bash
   docker-compose logs discord-bot
   ```
   You should see:
   ```
   BotName has connected to Discord!
   Bot is in X guild(s)
   Synced 10 slash command(s)
   ```

3. **Check Discord:**
   - Bot should appear online in your server
   - Try typing `/help` or `!help` in a text channel

## Troubleshooting

### Bot doesn't connect

**Check token:**
```bash
docker-compose logs discord-bot | grep -i "token\|error"
```

**Common issues:**
- Invalid token → Reset token in Developer Portal
- Token not set → Check `.env` file or environment variables
- Token has spaces → Remove any spaces around the token

### Container keeps restarting

**Check logs:**
```bash
docker-compose logs discord-bot
```

**Common causes:**
- Missing DISCORD_TOKEN environment variable
- Invalid token format
- Network issues

### FFmpeg not found

The Dockerfile includes FFmpeg, but if you see errors:
```bash
docker-compose exec discord-bot ffmpeg -version
```

Should show FFmpeg version. If not, rebuild:
```bash
docker-compose build --no-cache
```

### Commands not working

1. **Slash commands:**
   - Wait up to 1 hour for global commands (instant for your server)
   - Check logs for "Synced X slash command(s)"
   - Verify `applications.commands` scope was selected when inviting

2. **Prefix commands:**
   - Check bot has "Read Messages" permission
   - Verify prefix in `.env` matches what you're typing

## Production Deployment

### Using Docker Compose with restart policy:

The `docker-compose.yml` includes `restart: unless-stopped`, so the bot will:
- Start automatically when Docker starts
- Restart if it crashes
- Stay stopped if you manually stop it

### Using systemd (Linux):

Create `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Music Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/discord-bot
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use Docker secrets** for production (Docker Swarm)
3. **Limit bot permissions** - Only give what's needed
4. **Monitor logs** - Watch for suspicious activity
5. **Keep Docker updated** - Regular security updates

## Updating the Bot

1. **Pull latest code:**
   ```bash
   git pull
   ```

2. **Rebuild and restart:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Summary

**Token Location:**
- Discord Developer Portal → Your Application → Bot → Token

**Docker Commands:**
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

Your bot token is the **only credential** you need - everything else is handled automatically!






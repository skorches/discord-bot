# Discord Bot Token - Quick Guide

## What Token Do You Need?

You need a **Discord Bot Token** - this is a unique secret key that identifies your bot to Discord.

## Where to Get It

### Step-by-Step:

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create a New Application**
   - Click **"New Application"** (top right)
   - Name it (e.g., "Music Bot")
   - Click **"Create"**

3. **Create a Bot**
   - Click **"Bot"** in the left sidebar
   - Click **"Add Bot"** or **"Reset Token"**
   - Click **"Yes, do it!"** to confirm

4. **Copy Your Token**
   - Click **"Reset Token"** or **"Copy"** button
   - **⚠️ IMPORTANT**: Copy it immediately - you can only see it once!
   - If you lose it, click "Reset Token" to generate a new one

5. **Enable Required Intents**
   - Scroll down to **"Privileged Gateway Intents"**
   - Enable: ✅ **Message Content Intent** (required)
   - Optional: ✅ **Server Members Intent**

## Token Format

Your token looks like this:
```
MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.ABCdef.GHIjkl-MNOPqrsTUVwxyz1234567890
```

It's a long string of letters, numbers, dots, and dashes.

## How to Use the Token

### With Docker:

1. Create a `.env` file:
   ```env
   DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.ABCdef.GHIjkl-MNOPqrsTUVwxyz1234567890
   DISCORD_PREFIX=!
   ```

2. Run:
   ```bash
   docker-compose up -d
   ```

### Without Docker:

1. Create a `.env` file:
   ```env
   DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.ABCdef.GHIjkl-MNOPqrsTUVwxyz1234567890
   DISCORD_PREFIX=!
   ```

2. Run:
   ```bash
   python bot.py
   ```

## Security Warnings

⚠️ **NEVER:**
- Share your token publicly
- Commit it to Git (it's in `.gitignore`)
- Post it online or in screenshots
- Give it to anyone you don't trust

✅ **If your token is exposed:**
1. Go to Developer Portal immediately
2. Click "Reset Token"
3. This invalidates the old token
4. Update your `.env` file with the new token

## Troubleshooting

### "Invalid token" error:
- Check for extra spaces before/after the token
- Make sure you copied the entire token
- Try resetting the token and using the new one

### "Token not found" error:
- Make sure `.env` file exists in the project root
- Check the file is named exactly `.env` (not `.env.txt`)
- Verify `DISCORD_TOKEN=` is on its own line
- Make sure there are no quotes around the token

### Token format check:
- Should be ~59 characters long
- Contains letters, numbers, dots (.), and dashes (-)
- No spaces

## What the Token Does

The token:
- Authenticates your bot with Discord
- Allows the bot to connect to Discord servers
- Identifies which bot account to use
- Is unique to your bot application

**You only need ONE token** - this is all you need to connect the bot!

## Next Steps After Getting Token

1. ✅ Save token in `.env` file
2. ✅ Invite bot to your server (see DOCKER_SETUP.md)
3. ✅ Start the bot
4. ✅ Test with `/help` or `!help`

That's it! The token is the only credential you need.


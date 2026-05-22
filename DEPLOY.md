# 🚀 Make a Number — Telegram Mini App Deployment Guide

## What you're building
A Telegram bot that launches a web-based math game as a **Telegram Mini App**
(the game runs inside Telegram — no external browser needed).

---

## Step 1 — Get your Bot Token from Telegram

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. `Make a Number`)
4. Choose a username ending in `bot` (e.g. `makeanum_bot`)
5. BotFather gives you a token like: `7312456789:AAFxxx...`
6. **Save this token** — you'll need it in Step 4

---

## Step 2 — Push code to GitHub

1. Create a new repo on GitHub (can be private)
2. In your project folder, run:

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/make-a-number-bot.git
git push -u origin main
```

---

## Step 3 — Deploy to Railway

1. Go to **railway.app** and sign up (free tier works)
2. Click **New Project → Deploy from GitHub repo**
3. Select your repo
4. Railway will auto-detect Python and deploy

Once deployed, Railway gives you a public URL like:
`https://make-a-number-bot-production.up.railway.app`

**Copy this URL** — you need it next.

---

## Step 4 — Set Environment Variables on Railway

In your Railway project → **Variables** tab, add:

| Variable   | Value                                      |
|------------|--------------------------------------------|
| `BOT_TOKEN` | Your token from BotFather (Step 1)        |
| `GAME_URL`  | Your Railway URL from Step 3              |

Example:
```
BOT_TOKEN = 7312456789:AAFxxxYourTokenHere
GAME_URL  = https://make-a-number-bot-production.up.railway.app
```

Railway will redeploy automatically after you save.

---

## Step 5 — Register the webhook

Once deployed, visit this URL in your browser **once**:

```
https://YOUR-RAILWAY-URL.up.railway.app/setup
```

This tells Telegram where to send updates. You should see:
```json
Webhook set: {"ok": true, ...}
```

---

## Step 6 — Enable Mini Apps via BotFather

Go back to **@BotFather** in Telegram:

1. Send `/mybots` → select your bot
2. Choose **Bot Settings → Menu Button**
3. Set the URL to your Railway app URL
4. This adds a menu button that launches the game directly

---

## Step 7 — Play!

Open your bot in Telegram, send `/start`, and tap **🎮 Play Now**.
The game opens as a Mini App inside Telegram. 🎉

---

## File structure

```
make_a_number_twa/
├── server.py          ← Flask server (bot webhook + static file serving)
├── static/
│   └── index.html     ← The full game (Telegram Mini App)
├── requirements.txt
├── Procfile
├── railway.toml
└── .gitignore
```

---

## Troubleshooting

**Game doesn't open?**
- Make sure `GAME_URL` has no trailing slash
- Revisit `/setup` to re-register the webhook

**Bot not responding?**
- Double-check `BOT_TOKEN` in Railway variables
- Check Railway logs (Deployments → View Logs)

**Score not sent back to chat?**
- This uses `tg.sendData()` — only works inside a real Telegram Mini App,
  not in a browser. That's expected behavior.

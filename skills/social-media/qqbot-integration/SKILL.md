---
name: qqbot-integration
description: Configure and manage QQ Bot (Tencent QQ) integration with Hermes Agent using the official QQ Bot API v2.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
prerequisites:
  env_vars: [QQ_APP_ID, QQ_CLIENT_SECRET]
  commands: [hermes]
metadata:
  hermes:
    tags: [qq, qqbot, messaging, chinese-messaging]
    homepage: https://bot.q.qq.com/wiki/
---

# QQ Bot Integration

Configure and manage Tencent QQ Bot integration with Hermes Agent using the official QQ Bot API v2.

## Overview

QQ Bot is a popular Chinese messaging platform. This integration supports:
- Private (C2C) messages
- Group @-mentions
- Guild messages
- Voice message transcription (ASR)
- Image and file attachments

## Prerequisites

1. **QQ Bot Application** - Register at https://q.qq.com:
   - Create a new application
   - Note your **App ID** and **App Secret**
   - Enable required intents: C2C messages, Group @-messages, Guild messages
   - Configure in sandbox mode for testing, or publish for production

2. **Dependencies** - The adapter requires `aiohttp` and `httpx` (usually pre-installed in Hermes venv)

## Configuration Steps

### Step 1: Add Environment Variables

Add the following to `/opt/data/.env` (or `~/.hermes/.env`):

```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

Example (use your actual credentials):
```bash
QQ_APP_ID=1903847029
QQ_CLIENT_SECRET=kQt9ByW4TjpoleP6
```

⚠️ **Security Note**: Never commit `.env` files to version control. Use environment variable substitution in production.

### Step 2: Update Gateway Configuration

Edit `/opt/data/gateway.json` to enable QQ Bot platform:

```json
{
  "allow_all_users": true,
  "platforms": {
    "feishu": {
      "enabled": true,
      "app_id": "cli_a92b8a954d78dcc9",
      "app_secret": "IVnew39vUbmEApffhVr0jff2fYmnGdFm"
    },
    "qqbot": {
      "enabled": true,
      "app_id": "1903847029",
      "client_secret": "kQt9ByW4TjpoleP6"
    }
  },
  "reset_by_platform": {
    "feishu": {"mode": "idle", "idle_minutes": 1440},
    "qqbot": {"mode": "idle", "idle_minutes": 1440}
  }
}
```

### Step 3: Restart Gateway

Restart the Hermes gateway to load the new configuration:

```bash
# Stop the current gateway process
kill -9 8

# Start a new gateway instance
nohup /opt/hermes/.venv/bin/hermes gateway run > /tmp/gateway.log 2>&1 &

# Wait a few seconds and check logs
sleep 5
tail -30 /tmp/gateway.log
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `QQ_APP_ID` | QQ Bot App ID (required) | — |
| `QQ_CLIENT_SECRET` | QQ Bot App Secret (required) | — |
| `QQ_HOME_CHANNEL` | OpenID for cron/notification delivery | — |
| `QQ_HOME_CHANNEL_NAME` | Display name for home channel | `Home` |
| `QQ_ALLOWED_USERS` | Comma-separated user OpenIDs for DM access | `open` (all users) |
| `QQ_GROUP_ALLOWED_USERS` | Comma-separated group OpenIDs for group access | `open` (all groups) |
| `QQ_MARKDOWN_SUPPORT` | Enable QQ markdown (msg_type 2) | `true` |
| `QQ_STT_API_KEY` | API key for voice-to-text provider | — |
| `QQ_STT_BASE_URL` | Base URL for STT provider | `https://open.bigmodel.cn/api/coding/paas/v4` |
| `QQ_STT_MODEL` | STT model name | `glm-asr` |

## Advanced Configuration

For fine-grained control, add platform settings to `/opt/data/gateway.json`:

```json
{
  "platforms": {
    "qqbot": {
      "enabled": true,
      "app_id": "your-app-id",
      "client_secret": "your-secret",
      "home_channel": {
        "chat_id": "user_openid_123",
        "name": "Home"
      },
      "extra": {
        "allow_from": ["user_openid_1", "user_openid_2"],
        "group_allow_from": ["group_openid_1"],
        "markdown_support": true,
        "stt": {
          "provider": "zai",
          "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
          "apiKey": "your-stt-key",
          "model": "glm-asr"
        }
      }
    }
  }
}
```

## Voice Messages (STT)

Voice transcription works in two stages:

1. **QQ built-in ASR** (free, always tried first) — QQ provides `asr_refer_text` in voice message attachments
2. **Configured STT provider** (fallback) — If QQ's ASR doesn't return text, the adapter calls an OpenAI-compatible STT API:
   - **Zhipu/GLM (zai)**: Default provider, uses `glm-asr` model
   - **OpenAI Whisper**: Set `QQ_STT_BASE_URL` and `QQ_STT_MODEL`
   - Any OpenAI-compatible STT endpoint

## Troubleshooting

### Bot disconnects immediately (quick disconnect)

This usually means:
- **Invalid App ID / Secret** — Double-check your credentials at q.qq.com
- **Missing permissions** — Ensure the bot has the required intents enabled
- **Sandbox-only bot** — If the bot is in sandbox mode, it can only receive messages from QQ's sandbox test channel

### Voice messages not transcribed

1. Check if QQ's built-in `asr_refer_text` is present in the attachment data
2. If using a custom STT provider, verify `QQ_STT_API_KEY` is set correctly
3. Check gateway logs for STT error messages

### Messages not delivered

- Verify the bot's **intents** are enabled at q.qq.com
- Check `QQ_ALLOWED_USERS` if DM access is restricted
- For group messages, ensure the bot is **@mentioned** (group policy may require allowlisting)
- Check `QQ_HOME_CHANNEL` for cron/notification delivery

### Connection errors

- Ensure `aiohttp` and `httpx` are installed: `pip install aiohttp httpx`
- Check network connectivity to `api.sgroup.qq.com` and the WebSocket gateway
- Review gateway logs for detailed error messages and reconnect behavior

## Common Issues

### DNS Resolution Failures

If you see errors like:
```
HTTPSConnectionPool(host='api.sgroup.qq.com', port=443): Max retries exceeded
```

This indicates network/DNS issues. Check:
```bash
ping api.sgroup.qq.com
nslookup api.sgroup.qq.com
```

### Keepalive Ping Timeouts

If connections keep dropping with:
```
sent 1011 (internal error) keepalive ping timeout
```

This is often a network stability issue. Consider:
- Checking firewall rules
- Using a more stable network connection
- Adjusting gateway timeout settings if available

## References

- **QQ Bot Official Documentation**: https://bot.q.qq.com/wiki/
- **Hermes QQ Bot Source**: `/opt/hermes/gateway/platforms/qqbot.py`
- **Hermes QQ Bot Guide**: `/opt/hermes/website/docs/user-guide/messaging/qqbot.md`

## Pitfalls

- **Sandbox mode**: Sandbox bots can only interact with sandbox test channels
- **Intent permissions**: All required intents must be enabled in the QQ Bot console
- **Network stability**: QQ Bot uses persistent WebSocket connections which can be fragile on unstable networks
- **Credential rotation**: If you rotate credentials, update both `.env` and `gateway.json`
- **Channel discovery**: After enabling QQ Bot, it may take a few minutes to sync channel list
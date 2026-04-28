---
name: qqbot-troubleshooting
description: Diagnose and fix QQ Bot connection issues in Hermes Agent
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [qq, qqbot, troubleshooting, messaging]
---

# QQ Bot Troubleshooting Guide

When QQ Bot connection fails, follow this systematic approach to diagnose and fix issues.

## Common Issues and Solutions

### Issue 1: "No home channel set" Error

**Error message**: `No home channel set for qqbot to determine where to send the message`

**Solution**: Set the `home_channel` in `/opt/data/gateway.json`

**Critical**: The `home_channel` object MUST include the `platform` field:

```json
{
  "platforms": {
    "qqbot": {
      "enabled": true,
      "app_id": "your-app-id",
      "client_secret": "your-secret",
      "home_channel": {
        "platform": "qqbot",  // ← Required!
        "chat_id": "user_openid",
        "name": "Home"
      }
    }
  }
}
```

**Alternative**: Set environment variable `QQ_HOME_CHANNEL` and restart gateway.

### Issue 2: "Failed to load gateway config: 'platform'" Error

**Cause**: Missing `platform` field in `home_channel` object

**Solution**: Add `"platform": "qqbot"` to the `home_channel` object as shown above.

### Issue 3: 401 Authentication Error (Error Code 11201)

**Error message**: `QQBot send failed: 401 {"message":"鉴权失败","code":11201,...}`

**Possible causes**:

1. **Invalid credentials**:
   - Verify App ID and Client Secret in QQ Bot console
   - Check `/opt/data/gateway.json` and `.env` files
   - Ensure `QQ_APP_ID` and `QQ_CLIENT_SECRET` environment variables are set

2. **Sandbox mode limitation**:
   - Sandbox bots can only receive messages from QQ's sandbox test channel
   - Publish the bot for production use if testing with regular users

3. **Missing intents**:
   - Log in to [QQ Bot Console](https://bot.q.qq.com/wiki/)
   - Ensure required intents are enabled:
     - C2C messages
     - Group @-messages
     - Guild messages (if applicable)

4. **Channel ID incorrect**:
   - Verify the OpenID/chat_id is correct
   - The chat_id should be the user's or group's OpenID, not the App ID

## Configuration Checklist

### Environment Variables
```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-secret
QQ_HOME_CHANNEL=user_openid  # Optional, can also use gateway.json
```

### Gateway Configuration (`/opt/data/gateway.json`)
```json
{
  "platforms": {
    "qqbot": {
      "enabled": true,
      "app_id": "1903847029",
      "client_secret": "kQt9ByW4TjpoleP6",
      "home_channel": {
        "platform": "qqbot",
        "chat_id": "6DEAF2F03CBA3FFDB36ADA1F90610BBA",
        "name": "Home"
      }
    }
  }
}
```

## Restart Gateway After Configuration Changes

```bash
# Find and kill gateway process
ps aux | grep gateway
kill -9 <pid>

# Wait for restart or start manually
sleep 2
/opt/hermes/.venv/bin/hermes gateway run > /tmp/gateway.log 2>&1 &
```

## Verification Steps

1. Check gateway logs: `tail -f /tmp/gateway.log`
2. Test with a message: `send_message target=qqbot message="test"`
3. Verify connection status in QQ Bot console

## Pitfalls

- **Missing `platform` field**: The most common configuration error
- **Sandbox mode**: Only works with sandbox test channels
- **Gateway restart required**: Environment variable changes need gateway restart
- **Credential rotation**: Update both `.env` and `gateway.json` if rotating credentials
- **Channel discovery**: After enabling QQ Bot, it may take minutes to sync channel list

## Advanced Troubleshooting

### Issue 4: Truncated TOKEN_URL in qqbot.py

**Symptoms**:
- Gateway logs show no QQbot initialization
- 401 errors even with correct credentials
- `TOKEN_URL="https:...oken"` appears in `/opt/hermes/gateway/platforms/qqbot.py`

**Diagnosis**:
```bash
# Check for truncated URL
grep "TOKEN_URL" /opt/hermes/gateway/platforms/qqbot.py

# Should show: TOKEN_URL="https://bot.q.qq.com/oauth2/v2/access_token"
# Corrupted shows: TOKEN_URL="https:...oken"
```

**Fix**:
```bash
# Method 1: Use sed to replace the line
sed -i 's/TOKEN_URL="https:\/\/...oken"/TOKEN_URL="https:\/\/bot.q.qq.com\/oauth2\/v2\/access_token"/' /opt/hermes/gateway/platforms/qqbot.py

# Method 2: Use Python for precise line replacement
python3 << 'EOF'
with open('/opt/hermes/gateway/platforms/qqbot.py', 'r') as f:
    lines = f.readlines()

# Line 90 (0-indexed: 89)
lines[89] = 'TOKEN_URL="https://bot.q.qq.com/oauth2/v2/access_token"\n'

with open('/opt/hermes/gateway/platforms/qqbot.py', 'w') as f:
    f.writelines(lines)
EOF
```

**After repair**:
1. Verify the fix: `grep "TOKEN_URL" /opt/hermes/gateway/platforms/qqbot.py`
2. **Restart gateway** for changes to take effect
3. Check logs: `tail -f /tmp/gateway.log`

### File Corruption Detection

If standard search/replace fails:
```bash
# Check exact bytes
python3 -c "
with open('/opt/hermes/gateway/platforms/qqbot.py', 'rb') as f:
    content = f.read()
    idx = content.find(b'TOKEN_URL=')
    print(repr(content[idx:idx+50]))
"
```

**Note**: The truncation may appear as literal `...` characters or display artifacts. Always verify with Python byte inspection if sed fails.

## References

- **QQ Bot Official Docs**: https://bot.q.qq.com/wiki/
- **Hermes QQ Bot Source**: `/opt/hermes/gateway/platforms/qqbot.py`
- **Gateway Config**: `/opt/hermes/gateway/config.py` (HomeChannel class definition)
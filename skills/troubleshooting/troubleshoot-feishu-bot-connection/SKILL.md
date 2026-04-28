---
name: troubleshoot-feishu-bot-connection
category: troubleshooting
description: Diagnose and resolve Feishu/Lark bot connection instability issues in Hermes Agent
---

# Troubleshoot Feishu (Lark) Bot Connection Issues

## Purpose
Diagnose and resolve connection instability issues with Feishu/Lark webhook bots in Hermes Agent.

## Symptoms
- WebSocket connections frequently disconnect with "keepalive ping timeout" errors
- DNS resolution failures for `open.feishu.cn`
- Repeated reconnection attempts in logs
- Bot appears connected but messages aren't received

## Diagnostic Steps

### 1. Check Configuration Files
```bash
# Main config
cat ~/config.yaml

# Gateway config
cat ~/gateway.json

# Environment variables
env | grep -i FEISHU
env | grep -i LARK
```

### 2. Verify Environment Variables
Look for:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_ACCESS_TOKEN` (if using access token mode)

### 3. Check Gateway Status
```bash
# Process status
ps aux | grep -i gateway | grep -v grep

# Gateway state (may not exist in all setups)
cat ~/gateway_state.json 2>/dev/null || echo "No gateway state file"

# Logs
cat /tmp/gateway.log | tail -50
```

### 4. Check Channel Directory
```bash
cat ~/channel_directory.json 2>/dev/null || echo "No channel directory file"
```

### 5. Filter Feishu/Lark Logs
```bash
# Get all Feishu-related log entries
cat /tmp/gateway.log | grep -i "feishu\|lark"

# Count total Feishu log entries
cat /tmp/gateway.log | grep -i "feishu\|lark" | wc -l

# Get recent Feishu activity (last 30 entries)
cat /tmp/gateway.log | grep -i "feishu\|lark" | tail -30
```

**Note**: In some Hermes setups, gateway state and channel directory files may not be persisted to `~/`. Always check `/tmp/gateway.log` as the primary source of truth for connection status.

## Common Issues & Solutions

### DNS Resolution Failures
**Error**: `Failed to resolve 'open.feishu.cn'`

**Solutions**:
- Check DNS configuration: `cat /etc/resolv.conf`
- Test connectivity: `ping open.feishu.cn`
- Try alternative DNS: `nameserver 8.8.8.8`
- Check firewall rules blocking outbound HTTPS

### Keepalive Ping Timeout
**Error**: `sent 1011 (internal error) keepalive ping timeout`

**Solutions**:
- Network instability - check connection quality
- Firewall/proxy interfering with WebSocket
- Increase idle timeout in gateway.json:
  ```json
  "reset_by_platform": {
    "feishu": {"mode": "idle", "idle_minutes": 1440}
  }
  ```
- Restart gateway: `hermes gateway run`

### Connection Loop
**Symptom**: Continuous connect/disconnect cycles

**Solutions**:
- Verify App ID and App Secret are correct
- Check if bot permissions were revoked
- Regenerate access token from Feishu developer console
- Check Feishu webhook URL format

## Verification Steps

1. **Check connection state**:
   ```bash
   cat ~/gateway_state.json | grep -A5 '"feishu"'
   ```

2. **Monitor logs in real-time**:
   ```bash
   tail -f /tmp/gateway.log | grep -i lark
   ```

3. **Test message delivery**:
   - Send a test message to the bot
   - Check if it appears in `feishu_seen_message_ids.json`

## Configuration Files Reference

### gateway.json
```json
{
  "platforms": {
    "feishu": {
      "enabled": true,
      "app_id": "your_app_id",
      "app_secret": "your_app_secret"
    }
  }
}
```

### channel_directory.json
Shows available channels/chats:
```json
{
  "platforms": {
    "feishu": [
      {
        "id": "channel_id",
        "name": "channel_name",
        "type": "dm" | "group"
      }
    ]
  }
}
```

## Prevention

1. **Monitor logs regularly**: Set up log rotation and alerting
2. **Use stable network**: Avoid public Wi-Fi for bot hosting
3. **Keep credentials secure**: Rotate secrets periodically
4. **Document configuration**: Keep config files in version control

## Related Skills
- `webhook-subscriptions`: Manage webhook events
- `troubleshooting-hermes-installation`: General Hermes issues
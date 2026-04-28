---
name: docker-hermes-path-config
category: devops
version: 1.0
date: 2026-04-16
purpose: Configure PATH and PYTHONPATH environment variables for Hermes Agent running in Docker container
description: Guide for configuring environment variables when running Hermes Agent in Docker container
---

# Docker Container Hermes Agent Path Configuration

## Problem Context

When running Hermes Agent in a Docker container, the `hermes` command may fail with:
- `hermes: command not found` - PATH not configured
- `ModuleNotFoundError: No module named 'yaml'` - Python virtual environment not activated

## Root Cause

The Hermes Agent is installed in a virtual environment at `/opt/hermes/.venv/`, but the container's PATH does not include:
- `/opt/hermes/.venv/bin` (for executables)
- `/opt/hermes` (for Python modules)

## Solution

### 1. Identify Correct Paths

```bash
# Find hermes executable
docker exec hermes find /opt -name 'hermes' -type f

# Expected output:
# /opt/hermes/hermes
# /opt/hermes/.venv/bin/hermes
```

### 2. Required Environment Variables

```bash
export PATH="/opt/hermes/.venv/bin:/opt/hermes:$PATH"
export PYTHONPATH="/opt/hermes:$PYTHONPATH"
```

### 3. Usage Methods

#### Method A: Full Path (Most Reliable)
```bash
docker exec hermes /opt/hermes/.venv/bin/hermes gateway run
```

#### Method B: Set Environment Variables
```bash
docker exec -e PATH=/opt/hermes/.venv/bin:/opt/hermes:$PATH \
             -e PYTHONPATH=/opt/hermes:$PYTHONPATH \
             hermes /opt/hermes/.venv/bin/hermes gateway run
```

#### Method C: Use Wrapper Script
```bash
docker exec hermes /opt/hermes/hermes gateway run
```

#### Method D: Activate Virtual Environment Inside Container
```bash
docker exec -it hermes bash
source /opt/hermes/.venv/bin/activate
hermes gateway run
exit
```

## Verification Commands

```bash
# Check version
docker exec hermes /opt/hermes/.venv/bin/hermes --version

# Check Python environment
docker exec hermes /opt/hermes/.venv/bin/python --version

# Check module imports
docker exec hermes /opt/hermes/.venv/bin/python -c "import yaml; print('OK')"

# Test gateway help
docker exec hermes /opt/hermes/.venv/bin/hermes gateway run --help
```

## Common Issues & Solutions

### Issue 1: "hermes: command not found"
**Cause**: PATH not configured  
**Solution**: Use full path `/opt/hermes/.venv/bin/hermes` or set PATH

### Issue 2: "ModuleNotFoundError: No module named 'yaml'"
**Cause**: Using system Python instead of virtual environment  
**Solution**: Use `/opt/hermes/.venv/bin/python` or activate venv

### Issue 3: "Permission denied"
**Cause**: File permissions  
**Solution**: Ensure `/opt/hermes/hermes` and `/opt/hermes/.venv/bin/hermes` are executable

## Configuration Files

- **Environment template**: `/opt/hermes/.env.example`
- **Actual config**: `/opt/hermes/.env` (create from template)

## Post-Reboot Configuration

After container restart, the container should be running with the correct configuration. To verify:

```bash
# 1. Check container status
docker ps | grep hermes

# 2. Test hermes command (works immediately, no source needed!)
docker exec hermes hermes --version

# 3. Enter interactive shell
docker exec -it hermes bash

# 4. Verify environment
echo $PATH
echo $PYTHONPATH
which python

# 5. Exit
exit
```

**Note**: With the `--entrypoint /bin/bash` configuration, the `hermes` command is available immediately after entering the container shell without needing to `source /opt/hermes/.venv/bin/activate`.

## Recreating Container with Environment Variables

When you need to recreate the container with updated environment variables:

```bash
# 1. Stop and remove existing container
docker stop hermes
docker rm hermes

# 2. Recreate with environment variables
docker run -d \
  --name hermes \
  -e PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e PYTHONPATH=/opt/hermes \
  -e HERMES_HOME=/opt/data \
  -v hermes-data:/opt/data \
  nousresearch/hermes-agent:latest

# 3. Verify
docker exec hermes bash -c 'which hermes && hermes --version'
```

**Important**: If you get a mount conflict error:
```
Error response from daemon: Mounts denied: 
The path /opt/data is not shared from the host or is not a valid mount point
```
Make sure the named volume `hermes-data` exists first, or remove the old container completely before recreating.

## Entry Point Behavior - Critical Discovery ⚠️

**Problem**: The container's default entrypoint script (`/entrypoint.sh`) automatically tries to run `hermes <command>` and **overrides any command you specify**. This causes:
- `hermes: error: argument command: invalid choice: 'bash'` 
- `hermes: error: argument command: invalid choice: '/bin/bash'`
- Container exits immediately

**Root Cause**: The entrypoint script parses arguments and always prepends `hermes`, so even if you specify `tail -f /dev/null`, it becomes `hermes tail -f /dev/null`.

**Key Insight**: You cannot simply override the command with `docker run ... command`. You MUST override the entrypoint itself.

### Solution: Override Entry Point Completely

Use `--entrypoint` flag to replace the default entrypoint entirely:

### Solution: Override Entry Point Completely

Use `--entrypoint` flag to replace the default entrypoint entirely:

```bash
docker run -d \
  --name hermes \
  -e PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e PYTHONPATH=/opt/hermes \
  -e HERMES_HOME=/opt/data \
  -v hermes-data:/opt/data \
  --entrypoint /bin/bash \
  nousresearch/hermes-agent:latest \
  -c 'source /opt/hermes/.venv/bin/activate && tail -f /dev/null'
```

**Key Points**:
1. `--entrypoint /bin/bash` completely replaces `/entrypoint.sh`
2. Use `-c` to pass command to bash
3. `tail -f /dev/null` keeps container running indefinitely
4. Environment variables persist inside container
5. **After this setup, `hermes` command works immediately without `source`!**

### Alternative: Run Service Mode

If you want the container to run `hermes gateway` as a service:

### Alternative: Run Service Mode

If you want the container to run `hermes gateway` as a service:

```bash
docker run -d \
  --name hermes \
  -e PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e PYTHONPATH=/opt/hermes \
  -e HERMES_HOME=/opt/data \
  -v hermes-data:/opt/data \
  --entrypoint /bin/bash \
  nousresearch/hermes-agent:latest \
  -c 'source /opt/hermes/.venv/bin/activate && hermes gateway run'
```

### Usage After Creation

Once container is running with the correct entrypoint:

```bash
# Enter interactive shell
docker exec -it hermes bash

# hermes command works immediately (no need to source!)
hermes --version
hermes chat
hermes gateway run

# Exit
exit
```

**Important**: With `--entrypoint /bin/bash` and PATH configured, the `hermes` binary is found automatically without needing to activate the virtual environment inside the container.

### Complete Workflow

```bash
# 1. Remove old container
docker stop hermes 2>/dev/null
docker rm hermes 2>/dev/null

# 2. Create new container with correct entrypoint
docker run -d --name hermes \
  -e PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e PYTHONPATH=/opt/hermes \
  -e HERMES_HOME=/opt/data \
  -v hermes-data:/opt/data \
  --entrypoint /bin/bash \
  nousresearch/hermes-agent:latest \
  -c 'source /opt/hermes/.venv/bin/activate && tail -f /dev/null'

# 3. Verify container is running
docker ps | grep hermes

# 4. Test hermes command (works without source!)
docker exec hermes which hermes
docker exec hermes hermes --version

# 5. Enter interactive shell
docker exec -it hermes bash

# 6. Test inside container
hermes --version  # Should work immediately!
exit
```

### Troubleshooting

**Symptom**: Container exits immediately after starting

**Check logs**:
```bash
docker logs hermes
```

**Look for**: `hermes: error: argument command: invalid choice: '...'`

**Fix**: Container is using default entrypoint. Recreate with `--entrypoint /bin/bash` flag.

---

## Summary Checklist

Before declaring success, verify:

- [ ] Container is running: `docker ps | grep hermes`
- [ ] hermes command found: `docker exec hermes which hermes`
- [ ] hermes version works: `docker exec hermes hermes --version`
- [ ] PATH includes venv: `docker exec hermes env | grep PATH`
- [ ] Interactive shell works: `docker exec -it hermes bash` → `hermes --version`
- [ ] Gateway auto-starts on container restart
- [ ] Data volume permissions correct

If all checks pass, the container is properly configured!

**Symptom**: `hermes: command not found` inside container

**Check**:\n```bash\ndocker exec hermes env | grep PATH\ndocker exec hermes which hermes
```

**Fix**: PATH not configured. Recreate with `-e PATH=/opt/hermes/.venv/bin:...` flag.

**Symptom**: `PermissionError: [Errno 13] Permission denied: '/opt/data/gateway.pid'`

**Check**:\n```bash\ndocker logs hermes | grep PermissionError
```

**Fix**: Data volume permissions incorrect. Run:\n```bash\ndocker run --rm -v hermes-data:/opt/data alpine chown -R root:root /opt/data
```

**Symptom**: Container exits immediately after starting

**Check**:\n```bash\ndocker logs hermes | grep "invalid choice"
```

**Fix**: Default entrypoint is overriding command. Recreate with `--entrypoint /bin/bash` flag.

## Auto-Start Configuration

To ensure the container automatically starts `hermes gateway run` on every boot/restart:

```bash
docker run -d --name hermes \
  --restart unless-stopped \
  -e PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e PYTHONPATH=/opt/hermes \
  -e HERMES_HOME=/opt/data \
  -v hermes-data:/opt/data \
  --entrypoint /bin/bash \
  nousresearch/hermes-agent:latest \
  -c 'source /opt/hermes/.venv/bin/activate && hermes gateway run'
```

**Key flags**:
- `--restart unless-stopped` - Auto-restart on Docker daemon restart or container crash
- `--entrypoint /bin/bash` - Override default entrypoint that would fail
- `-c '...hermes gateway run'` - Automatically start gateway service

**Verification after restart**:\n```bash\ndocker restart hermes\nsleep 5\ndocker logs hermes | grep "Gateway Starting"\n```

## Related Skills

- `troubleshoot-feishu-bot-connection` - Similar debugging approach
- `system-environment-diagnostics` - General container troubleshooting

## Related Skills

- `troubleshoot-feishu-bot-connection` - Similar debugging approach
- `system-environment-diagnostics` - General container troubleshooting

## Notes

- The wrapper script `/opt/hermes/hermes` is a Python script that imports from `hermes_cli.main`
- Always use the virtual environment's Python and executables, not system-wide installations
- Environment variables persist only for the duration of the `docker exec` command unless set in Dockerfile or docker-compose.yml
---
name: hermes-docker-deployment
category: devops
description: Complete guide for deploying and configuring Hermes Agent Docker container with PATH configuration, automatic gateway startup, and restart policies
---

# Hermes Agent Docker Container Deployment and Configuration

Complete guide for deploying and configuring Hermes Agent in a Docker container with proper PATH configuration, automatic gateway startup, and restart policies.

## Overview

This skill covers the complete process of deploying Hermes Agent in Docker on a remote server, ensuring:
- `hermes` command is directly accessible without manual virtual environment activation
- Container automatically starts `hermes gateway run` on boot/restart
- Proper environment variable configuration
- Persistent data volume with correct permissions

## Prerequisites

- Docker installed on target server
- `nousresearch/hermes-agent:latest` image pulled
- SSH access to remote server
- Password or SSH key authentication

## Deployment Steps

### 0. Verify Docker Availability

**Important:** If running from a different machine, you need SSH access to the target server.

```bash
# Check if docker is available locally
which docker

# If not available, you need to SSH to the target server first
ssh user@target-server "docker ps -a | grep hermes"
```

### 1. Check Existing Container Status

```bash
docker ps -a | grep hermes
docker logs hermes 2>&1 | tail -30
```

**Common Issues to Check:**
- Permission errors on data volume: `PermissionError: [Errno 13] Permission denied: '/opt/data/gateway.pid'`
- Container exited unexpectedly
- Gateway service not starting
- Docker daemon not running on target server

### 2. Fix Data Volume Permissions (If Needed)

If encountering permission errors:

```bash
docker run --rm -v hermes-data:/opt/data alpine chown -R root:root /opt/data
```

### 3. Stop and Remove Existing Container

```bash
docker stop hermes
docker rm hermes
```

### 4. Create New Container with Proper Configuration

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

### 5. Wait and Verify Container Started

```bash
sleep 3
docker ps | grep hermes
```

### 6. Verify Gateway Service

```bash
docker logs hermes 2>&1 | tail -20
```

Expected output:
```
┌─────────────────────────────────────────────────────────┐
│           ⚕ Hermes Gateway Starting...                 │
├─────────────────────────────────────────────────────────┤
│  Messaging platforms + cron scheduler                    │
│  Press Ctrl+C to stop                                   │
└─────────────────────────────────────────────────────────┘
```

### 7. Test hermes Command Accessibility

```bash
docker exec hermes which hermes
docker exec hermes hermes --version
```

Expected output:
```
/opt/hermes/.venv/bin/hermes
Hermes Agent v0.9.0 (2026.4.13)
Project: /opt/hermes
Python: 3.13.5
OpenAI SDK: 2.32.0
```

### 8. Test Full Environment

```bash
docker exec hermes bash -c 'echo "=== Testing environment ===" && which hermes && hermes --version && which python && python --version && echo "=== Success ==="'
```

## Configuration Details

### Required Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PATH` | `/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` | Makes `hermes` command accessible without activation |
| `PYTHONPATH` | `/opt/hermes` | Python module path |
| `HERMES_HOME` | `/opt/data` | Data directory for Hermes |

### Key Configuration Flags

- `--restart unless-stopped`: Automatically restart container on Docker daemon restart or crash
- `--entrypoint /bin/bash`: Override default entrypoint to prevent automatic `hermes chat` execution
- `-c 'source ... && hermes gateway run'`: Command to run on container startup

## Troubleshooting

### Issue: "hermes: command not found"

**Cause**: PATH not configured or virtual environment not activated

**Solution**: 
1. Verify PATH includes `/opt/hermes/.venv/bin`
2. Use `docker exec hermes bash -c 'which hermes'` to check
3. Recreate container with proper PATH environment variable

### Issue: "docker: command not found"

**Cause:** Running Docker commands from a machine without Docker installed, or from a container without Docker access

**Solution:**
1. Check if Docker is available: `which docker`
2. If not available, SSH to the target server first:
   ```bash
   ssh user@target-server "docker ps -a | grep hermes"
   ```
3. Or use SSH remote execution to manage the container from your machine
4. Or copy the container management script to the target server and run it there

### Issue: Permission denied on gateway.pid

**Cause:** Running Docker commands from a machine without Docker installed, or from a container without Docker access

**Solution:**
1. Check if Docker is available: `which docker`
2. If not available, SSH to the target server first:
   ```bash
   ssh user@target-server "docker ps -a | grep hermes"
   ```
3. Or use SSH remote execution to manage the container from your machine
4. Or copy the container management script to the target server and run it there

### Issue: Permission denied on gateway.pid

**Cause**: Data volume permissions incorrect

**Solution**:
```bash
docker run --rm -v hermes-data:/opt/data alpine chown -R root:root /opt/data
```

### Issue: Container exits immediately

**Cause**: Default entrypoint runs `hermes chat` which fails without TTY

**Solution**: Use `--entrypoint /bin/bash` and specify custom command

### Issue: Gateway not starting

**Cause**: Container didn't start properly or permission issues

**Solution**:
1. Check logs: `docker logs hermes`
2. Verify data volume permissions
3. Restart container: `docker restart hermes`

### Issue: Container doesn't auto-restart after Docker daemon restart

**Cause**: Missing `--restart unless-stopped` flag

**Solution**: Recreate container with restart policy:
```bash
docker run -d --name hermes --restart unless-stopped ...
```

## Usage

### Enter Container

```bash
docker exec -it hermes bash
```

Once inside, `hermes` command works immediately without activation.

### Run Specific Commands

```bash
# Check version
docker exec hermes hermes --version

# Start chat interface
docker exec -it hermes hermes chat

# View logs
docker logs hermes

# Stop container
docker stop hermes

# Restart container (auto-starts gateway)
docker restart hermes
```

## Verification Checklist

- [ ] Container running: `docker ps | grep hermes`
- [ ] hermes command accessible: `docker exec hermes which hermes`
- [ ] Gateway service running: `docker logs hermes | grep "Gateway Starting"`
- [ ] Environment variables correct: `docker inspect hermes --format '{{.Config.Env}}'`
- [ ] Restart policy set: `docker inspect hermes --format '{{.HostConfig.RestartPolicy.Name}}'`
- [ ] Data volume permissions correct
- [ ] Auto-restart works: `docker restart hermes` and verify gateway starts automatically

## Common Commands Reference

```bash
# Check container status
docker ps -a | grep hermes

# View logs
docker logs hermes

# Test hermes command
docker exec hermes hermes --version

# Restart container
docker restart hermes

# Stop container
docker stop hermes

# Remove container
docker rm -f hermes

# Check environment variables
docker inspect hermes --format '{{json .Config.Env}}' | python3 -m json.tool
```

## Notes

- The `--entrypoint /bin/bash` is critical to prevent the default entrypoint from running `hermes chat`
- The PATH configuration must prepend `/opt/hermes/.venv/bin` to make hermes accessible
- Data volume permissions must be correct for gateway to write pid files
- Container will automatically restart on Docker daemon restart or crash (unless manually stopped)
---
title: SSH Password Authentication with sshpass
description: Connect to remote servers using SSH password authentication via sshpass tool
name: ssh-password-authentication
---

# SSH Password Authentication with sshpass

## Overview
When you need to connect to remote servers via SSH using password authentication (not key-based), use the `sshpass` tool for automated or scripted connections.

## Prerequisites
- `sshpass` must be installed on the local system
- SSH server must allow password authentication

## Installation

### Debian/Ubuntu
```bash
apt-get install -y sshpass
```

### RHEL/CentOS
```bash
yum install -y sshpass
```

## Usage

### Basic Connection
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host
```

### Execute Remote Command
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host "command1 && command2"
```

### Key Options
- `-p 'password'` - Password for authentication
- `-o StrictHostKeyChecking=no` - Skip host key verification (for automation)
- `-o BatchMode=no` - Allow password prompts if needed

## Common Patterns

### Check System Information
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host "whoami && hostname && uname -a"
```

### Test Multiple Commands
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host << 'EOF'
whoami
hostname
date
pwd
EOF
```

### Verify GPU Status (NVIDIA)
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host "nvidia-smi"
```

## Troubleshooting

### Connection Refused
```bash
# Check if SSH port is accessible
timeout 5 bash -c "echo '' > /dev/tcp/host/22" && echo "Port 22 open" || echo "Port 22 closed"
```

### Permission Denied
- Verify username and password are correct
- Check if SSH server allows password authentication (`PasswordAuthentication yes` in `/etc/ssh/sshd_config`)
- Try with `-o PreferredAuthentications=password -o PasswordAuthentication=yes`

### Command Timeout
- Increase timeout value in terminal command
- Check network connectivity
- Verify SSH service is running on remote host

## Security Notes
⚠️ **Warning**: Using passwords in scripts has security risks:
- Passwords may be visible in process lists
- Passwords may be logged in shell history
- Consider using SSH keys for production environments

For better security, use SSH key authentication when possible:
```bash
ssh -i /path/to/private/key user@host
```

## Related Skills
- `ssh-remote-connection` - SSH remote connection and troubleshooting
- `troubleshoot-feishu-bot-connection` - Connection diagnostic patterns
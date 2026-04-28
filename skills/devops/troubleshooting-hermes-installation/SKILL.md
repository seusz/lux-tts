---
name: troubleshooting-hermes-installation
category: devops
description: Diagnosing and fixing Hermes Agent installation issues in constrained environments
---

# Troubleshooting Hermes Agent Installation

This skill documents the process for diagnosing and fixing Hermes Agent installation issues in constrained environments.

## Problem Pattern

When encountering "Unknown provider" or "hermes: command not found" errors:

1. **Check if hermes command exists in PATH**
   ```bash
   which hermes || find /usr -name "hermes*" 2>/dev/null | head -5
   ```

2. **Check for Python package installation**
   ```bash
   pip show hermes-agent 2>/dev/null || pip show hermes 2>/dev/null
   python3 -c "import hermes_agent; print(hermes_agent.__file__)" 2>/dev/null
   ```

3. **Check for configuration directory**
   ```bash
   ls -la ~/.hermes/ 2>/dev/null || echo "No .hermes directory"
   ```

## Common Installation Roadblocks

### 1. Missing pip
**Symptoms:** `pip: command not found` or `No module named pip`

**Solutions (in order of preference):**
```bash
# Try ensurepip (if available)
python3 -m ensurepip --upgrade

# Download get-pip.py (if curl/wget available)
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user

# Or use wget
wget -qO /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
python3 /tmp/get-pip.py --user

# System package (requires sudo/root)
apt-get update && apt-get install -y python3-pip
```

### 2. No sudo/root privileges
**Symptoms:** `Permission denied` or `sudo: command not found`

**Workarounds:**
- Use `--user` flag for pip installs: `pip install --user package`
- Set `PIP_USER=1` environment variable
- Install to virtual environment: `python3 -m venv venv && source venv/bin/activate`
- Request system admin assistance

### 3. Missing download tools
**Symptoms:** `curl: command not found` or `wget: command not found`

**Alternatives:**
- Use Python to download: `python3 -c "import urllib.request; urllib.request.urlretrieve('url', 'file')"`
- Check if `apt-get` works without sudo (unlikely)
- Manually transfer package files

## Environment Assessment Checklist

Before attempting installation, verify:
- [ ] Python3 is available: `which python3`
- [ ] pip is available: `which pip3` or `python3 -m pip`
- [ ] Download tools available: `which curl` or `which wget`
- [ ] Sufficient permissions: `id` and `whoami`
- [ ] Package manager access: `apt-get` or similar

## Recovery Strategy

1. **Assess environment constraints** (permissions, available tools)
2. **Choose appropriate installation method** based on constraints
3. **Use user-level installs** when root access unavailable
4. **Consider containerized/virtual environments** for isolation
5. **Document findings** for future reference

## Key Learnings

- Always check for `sudo` availability before attempting system-wide installs
- User-level pip installs (`--user`) work in permission-constrained environments
- Missing basic tools (curl/wget/pip) often indicates a minimal/containerized environment
- Hermes Agent requires proper Python environment setup before use
- Environment assessment is critical before troubleshooting installation issues

## Related Commands

```bash
# Check Python environment
python3 --version
python3 -m pip --version

# Check available package managers
which apt-get yum dnf apk 2>/dev/null

# Check user permissions
id
whoami
echo $SUDO_USER

# List installed packages
pip list
pip list --user
```
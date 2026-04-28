---
name: system-environment-diagnostics
category: devops
description: Systematic approach to diagnose and troubleshoot Hermes Agent environment issues, particularly when tools fail due to missing dependencies or configuration problems.
---

# System Environment Diagnostics and Troubleshooting

## Purpose
Systematic approach to diagnose and troubleshoot Hermes Agent environment issues, particularly when tools fail due to missing dependencies or configuration problems.

## Trigger Conditions
- Tool calls fail with authentication errors or missing dependencies
- User reports "command not found" or "module not found" errors
- System appears to be missing expected tools or packages
- Need to determine if environment can be fixed or requires admin intervention

## Diagnostic Workflow

### Step 1: Identify the Problem
1. **Check tool output** - Look for specific error messages
2. **Identify missing component** - Determine what's failing (pip, curl, wget, etc.)
3. **Check user context** - Run `id && whoami` to understand permissions

### Step 2: Assess Environment Capabilities
```bash
# Check Python availability
which python3 python pip pip3 2>/dev/null
python3 --version

# Check available package managers
which apt-get yum dnf 2>/dev/null

# Check download tools
which curl wget 2>/dev/null

# Check sudo/admin access
which sudo 2>/dev/null
```

### Step 3: Attempt Installation (if possible)
**Priority order for installing pip:**
1. `python3 -m pip install package` (if pip module exists)
2. `python3 -m ensurepip --upgrade` (if ensurepip available)
3. `wget -qO /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && python3 /tmp/get-pip.py --user`
4. `curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python3 /tmp/get-pip.py --user`

**If system package manager available:**
```bash
# With sudo
sudo apt-get update && sudo apt-get install -y python3-pip

# Without sudo (may fail)
apt-get update && apt-get install -y python3-pip
```

### Step 4: Document Limitations
If installation fails, document:
- Missing tools/commands
- Permission issues (no sudo, read-only filesystem)
- Available alternatives
- Recommendations for user

## Common Failure Patterns

### Pattern A: No pip, no ensurepip, no download tools
**Symptoms:**
- `pip: command not found`
- `python3: No module named ensurepip`
- `curl: command not found`
- `wget: command not found`

**Resolution:** Cannot fix in sandboxed environment. Recommend:
- Contact system administrator
- Use pre-configured container/VM
- Use alternative environment with tools pre-installed

### Pattern B: No sudo/admin privileges
**Symptoms:**
- `sudo: command not found`
- `Permission denied` on apt-get
- User is non-root (e.g., `uid=10000(hermes)`)

**Resolution:** Cannot install system packages. Recommend:
- Use `--user` flag for pip installs
- Use virtual environments
- Request admin access if needed

### Pattern C: Network restrictions
**Symptoms:**
- Browser navigation timeouts
- Package installation fails with connection errors
- External API calls fail

**Resolution:** Check network configuration, firewall rules, or proxy settings

## Safety Considerations

### ⚠️ NEVER:
- Accept or store user passwords in conversation
- Attempt to escalate privileges without authorization
- Modify system files without proper permissions
- Share sensitive credentials in logs or outputs

### ✅ ALWAYS:
- Document what was attempted
- Clearly communicate limitations
- Provide actionable recommendations
- Maintain security best practices

## Output Format
When reporting diagnostics, include:
1. **Problem identified** - What failed and why
2. **Attempts made** - Commands tried and results
3. **Current state** - What works, what doesn't
4. **Recommendations** - Actionable next steps for user

## Example Usage

**Scenario:** User reports "hermes model" authentication error

**Diagnostic approach:**
1. Check if hermes-agent package is installed: `pip list | grep hermes`
2. If not installed, attempt installation
3. If installation fails due to missing pip, document limitation
4. Recommend alternative approaches or admin intervention

## Related Skills
- `troubleshooting-hermes-installation` - Specific hermes-agent installation issues
- `github-auth` - GitHub authentication setup
- Any environment-specific setup skill

## Notes
- This approach is reusable across different environment types
- Always prioritize security - never accept passwords
- Document findings for future reference
- Consider whether the environment is appropriate for the task
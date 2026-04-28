---
title: NVIDIA GPU Driver Verification
description: Check if NVIDIA GPU drivers are properly installed and functioning on remote servers
name: nvidia-gpu-verification
---

# NVIDIA GPU Driver Verification

## Overview
Comprehensive guide for verifying NVIDIA GPU driver installation and functionality on remote servers, particularly useful for AI/ML workstations and GPU-enabled systems.

## Quick Check

### Primary Method - nvidia-smi
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host "nvidia-smi"
```

## Detailed Verification Steps

### 1. Driver Version Check
```bash
nvidia-smi --query-gpu=driver_version --format=csv
```

### 2. GPU Information
```bash
nvidia-smi --query-gpu=name,memory.total --format=csv
```

### 3. Kernel Modules
```bash
lsmod | grep nvidia
```

Expected modules:
- `nvidia` - Main driver
- `nvidia_modeset` - Display mode setting
- `nvidia_uvm` - Unified memory management
- `drm` - Direct rendering manager

### 4. PCI Device Detection
```bash
lspci | grep -i nvidia
```

### 5. CUDA Version (from nvidia-smi)
Check the "CUDA Version" line in `nvidia-smi` output

## Success Criteria

✅ **Driver Properly Installed If:**
- `nvidia-smi` executes without errors
- Shows GPU name, driver version, and CUDA version
- Displays memory usage and GPU utilization
- All kernel modules are loaded
- PCI device is detected

## Common Issues

### "command not found"
**Problem**: `nvidia-smi` command not found
**Solution**: 
```bash
# Install NVIDIA driver
apt-get install -y nvidia-driver-535

# Or check if NVIDIA tools are in PATH
which nvidia-smi
```

### "Permission denied"
**Problem**: User doesn't have permission to access GPU
**Solution**:
```bash
# Add user to video group
usermod -aG video $USER

# Or check permissions
ls -l /dev/nvidia*
```

### "No devices found"
**Problem**: GPU not detected
**Solution**:
```bash
# Check if GPU is detected by system
lspci | grep -i nvidia

# Check kernel modules
lsmod | grep nvidia

# Reload modules if needed
modprobe nvidia
```

### "CUDA Version mismatch"
**Problem**: Driver version incompatible with CUDA toolkit
**Solution**:
- Check driver supports required CUDA version
- Refer to NVIDIA CUDA compatibility matrix
- Update driver or CUDA toolkit accordingly

## Remote Server Verification

### Complete Diagnostic Script
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host << 'EOF'
echo "=== NVIDIA Driver Information ==="
nvidia-smi

echo ""
echo "=== GPU Model ==="
lspci | grep -i nvidia

echo ""
echo "=== Kernel Modules ==="
lsmod | grep nvidia

echo ""
echo "=== Device Files ==="
ls -l /dev/nvidia*
EOF
```

## Python Verification

### Using pynvml
```bash
# Install PyNVIDIA Management Library
pip install pynvml

# Verify in Python
python3 -c "
import pynvml
pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)
print('GPU:', pynvml.nvmlDeviceGetName(handle))
print('Driver Version:', pynvml.nvmlSystemGetDriverVersion())
pynvml.nvmlShutdown()
"
```

## Performance Check

### GPU Utilization Test
```bash
# Run a simple GPU computation
nvidia-smi dmon -c 5 -s p  # Monitor for 5 seconds
```

### Memory Test
```bash
# Check if GPU memory is accessible
nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv
```

## Security Considerations

⚠️ **Important Notes:**
- NVIDIA drivers require root privileges for installation
- GPU access may be restricted by system policies
- Remote verification requires SSH access with appropriate permissions
- Consider using SSH keys instead of passwords for automation

## Related Skills
- `ssh-password-authentication` - SSH connection with password
- `system-environment-diagnostics` - General system health checks
- `troubleshooting-hermes-installation` - Installation troubleshooting patterns
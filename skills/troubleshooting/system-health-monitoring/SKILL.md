---
title: System Health Monitoring
description: Comprehensive system heartbeat and health check procedures
name: system-health-monitoring
---

# System Health Monitoring

## Overview
Systematic approach to monitor and verify system health through comprehensive heartbeat checks. Essential for maintaining server reliability and detecting issues early.

## Quick Health Check

### One-Liner Summary
```bash
echo "=== System Health ===" && \
df -h / | tail -1 | awk '{print "Disk: "$4" available"}' && \
free -h | grep Mem | awk '{print "Memory: "$4" available"}' && \
uptime | awk -F'load average:' '{print "Load: "$2}'
```

## Comprehensive Health Check

### Complete Diagnostic Script
```bash
echo "=================================================="
echo "🔍 System Health Check"
echo "=================================================="
echo ""
echo "1. System Time"
date '+%Y-%m-%d %H:%M:%S'
echo ""
echo "2. Disk Space"
df -h /
echo ""
echo "3. Memory Usage"
free -h
echo ""
echo "4. CPU Load"
uptime
echo ""
echo "5. Network Connectivity"
timeout 5 bash -c "echo '' > /dev/tcp/8.8.8.8/53" && echo "✅ DNS accessible" || echo "❌ DNS unreachable"
echo ""
echo "6. Docker Status"
docker ps -a --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "Docker not running"
echo ""
echo "7. Process Count"
ps aux | wc -l
echo ""
echo "8. System Load Average"
cat /proc/loadavg
echo ""
echo "=================================================="
echo "✅ Health Check Complete"
echo "=================================================="
```

## Individual Checks

### Disk Space Monitoring
```bash
# Check root partition
df -h /

# Check all mounted filesystems
df -h

# Find large directories
du -sh /* 2>/dev/null | sort -hr | head -10
```

**Thresholds:**
- ⚠️ Warning: >80% used
- 🚨 Critical: >90% used

### Memory Monitoring
```bash
# Detailed memory info
free -h

# Memory usage by process
ps aux --sort=-%mem | head -10

# Check for memory pressure
cat /proc/meminfo | grep -E "MemAvailable|MemFree|Buffers|Cached"
```

**Thresholds:**
- ⚠️ Warning: >80% used
- 🚨 Critical: >95% used

### CPU Load Monitoring
```bash
# Load average
uptime

# Detailed CPU info
cat /proc/loadavg

# Per-core utilization
mpstat 1 5  # Requires sysstat package
```

**Thresholds:**
- ⚠️ Warning: Load > number of CPU cores
- 🚨 Critical: Load > 2x number of CPU cores

### Network Connectivity
```bash
# Test DNS
timeout 5 bash -c "echo '' > /dev/tcp/8.8.8.8/53"

# Test external connectivity
timeout 5 bash -c "echo '' > /dev/tcp/1.1.1.1/443"

# Check network interfaces
ip addr show

# Check routing
ip route show
```

### Service Status
```bash
# Check specific service
systemctl status ssh

# List failed services
systemctl --failed

# Check Docker
docker ps -a

# Check custom services
systemctl list-units --type=service --state=running
```

### Process Monitoring
```bash
# Total process count
ps aux | wc -l

# Top memory consumers
ps aux --sort=-%mem | head -10

# Top CPU consumers
ps aux --sort=-%cpu | head -10

# Check for zombie processes
ps aux | awk '$8 == "Z" {print}'
```

### System Uptime
```bash
# System uptime
uptime

# Boot time
cat /proc/uptime

# Last reboot time
last reboot | head -1
```

## Automated Monitoring

### Cron Job for Regular Checks
```bash
# Add to crontab (run every hour)
0 * * * * /opt/scripts/health-check.sh >> /var/log/system-health.log 2>&1
```

### Health Check Script Template
```bash
#!/bin/bash
# /opt/scripts/health-check.sh

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/var/log/system-health.log"

echo "[$TIMESTAMP] Health Check Started" >> "$LOG_FILE"

# Disk check
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "[$TIMESTAMP] 🚨 CRITICAL: Disk usage at ${DISK_USAGE}%" >> "$LOG_FILE"
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] ⚠️ WARNING: Disk usage at ${DISK_USAGE}%" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ✅ Disk usage at ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Memory check
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
if [ $(echo "$MEM_USAGE > 90" | bc) -eq 1 ]; then
    echo "[$TIMESTAMP] 🚨 CRITICAL: Memory usage at ${MEM_USAGE}%" >> "$LOG_FILE"
elif [ $(echo "$MEM_USAGE > 80" | bc) -eq 1 ]; then
    echo "[$TIMESTAMP] ⚠️ WARNING: Memory usage at ${MEM_USAGE}%" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ✅ Memory usage at ${MEM_USAGE}%" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Health Check Complete" >> "$LOG_FILE"
```

## Alert Thresholds Reference

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Disk Usage | >80% | >90% | Clean up files |
| Memory Usage | >80% | >95% | Kill processes |
| CPU Load | >cores | >2xcores | Investigate load |
| Uptime | >30 days | >90 days | Plan reboot |
| Failed Services | 1+ | 3+ | Restart services |

## Remote System Monitoring

### SSH-Based Health Check
```bash
sshpass -p 'password' ssh -o StrictHostKeyChecking=no user@host << 'EOF'
echo "=== Remote System Health ==="
df -h / | tail -1
free -h | grep Mem
uptime
ps aux | wc -l
EOF
```

## Related Skills
- `ssh-password-authentication` - Remote system access
- `troubleshooting-hermes-installation` - System diagnostics
- `system-environment-diagnostics` - Environment verification
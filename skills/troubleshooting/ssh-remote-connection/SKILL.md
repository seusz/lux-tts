---
name: ssh-remote-connection
description: SSH 远程连接与故障排查 - 在 Hermes Agent 环境中通过 SSH 连接到远程服务器
version: 1.0.0
metadata:
  hermes:
    tags: [ssh, remote, connection, troubleshooting, linux]
    related_skills: [troubleshoot-feishu-bot-connection, troubleshooting-hermes-installation, hermes-agent]
---

# SSH 远程连接与故障排查

> Version 1.0 | 2026-04-16
> 场景：在 Hermes Agent 环境中通过 SSH 连接到远程服务器，处理安装依赖、认证失败等常见问题

---

## 触发条件

**主动调用：**
- 「SSH 连接 [主机]」「远程登录 [主机]」「ssh [用户]@[主机]」
- 「测试 SSH 连接」「远程执行命令」

**自然触发：**
- 需要远程执行命令
- 需要传输文件到远程服务器
- 需要检查远程服务器状态

---

## 标准流程

### 1️⃣ 检查 SSH 客户端是否已安装

```bash
which ssh
```

**如果未安装：**
```bash
apt-get update && apt-get install -y openssh-client
```

**⚠️ 常见问题处理：**
- **dpkg 锁冲突**：先运行 `dpkg --configure -a` 修复中断的包管理
- **apt 进程占用**：等待现有 apt 进程完成，或检查 `pgrep -x apt`
- **锁文件占用**：使用 `fuser -v /var/lib/dpkg/lock-frontend` 查看占用进程

---

### 2️⃣ 准备认证方式

#### 选项 A：密码认证（需要 sshpass）

**安装 sshpass：**
```bash
apt-get install -y sshpass
```

**测试连接：**
```bash
sshpass -p '密码' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=no 用户@主机 "whoami"
```

**参数说明：**
- `-o StrictHostKeyChecking=no` - 自动接受主机密钥
- `-o ConnectTimeout=10` - 连接超时 10 秒
- `-o BatchMode=no` - 允许交互式认证

#### 选项 B：SSH 密钥认证

**使用密钥文件：**
```bash
ssh -i /path/to/private_key -o StrictHostKeyChecking=no 用户@主机
```

---

### 3️⃣ 执行远程命令

**单条命令：**
```bash
ssh -o StrictHostKeyChecking=no 用户@主机 "命令 1; 命令 2"
```

**多条命令：**
```bash
ssh -o StrictHostKeyChecking=no 用户@主机 << 'EOF'
命令 1
命令 2
命令 3
EOF
```

---

### 4️⃣ 文件传输

**上传文件：**
```bash
scp -o StrictHostKeyChecking=no local_file 用户@主机:/remote/path/
```

**下载文件：**
```bash
scp -o StrictHostKeyChecking=no 用户@主机:/remote/path/file /local/path/
```

---

## 故障排查

### ❌ "Permission denied (publickey,password)"

**可能原因：**
1. 密码错误
2. 用户名错误
3. 服务器禁止密码登录
4. SSH 服务未运行

**解决方案：**
1. 确认用户名和密码正确
2. 检查服务器配置 `/etc/ssh/sshd_config`
3. 确认 `PasswordAuthentication yes` 已启用
4. 尝试使用 SSH 密钥认证

### ❌ "Connection timed out"

**可能原因：**
1. 网络不可达
2. 防火墙阻止
3. 主机不存在

**解决方案：**
1. 检查网络连接：`ping 主机`
2. 检查端口：`telnet 主机 22`
3. 确认 IP 地址正确

### ❌ "dpkg was interrupted"

**解决方案：**
```bash
dpkg --configure -a
```

**如果仍然失败：**
```bash
# 等待 2-3 分钟让现有进程完成
sleep 120
dpkg --configure -a
```

### ❌ "Could not get lock /var/lib/dpkg/lock"

**可能原因：**
- 另一个 apt 进程正在运行

**解决方案：**
```bash
# 等待现有进程完成
for i in {1..180}; do
    if ! pgrep -x apt > /dev/null; then
        echo "✅ apt finished after $i seconds"
        break
    fi
    sleep 1
done

# 然后重新安装
apt-get install -y 包名
```

---

## Python 自动化连接（使用 paramiko）

```python
import paramiko

# 创建 SSH 客户端
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 连接
try:
    client.connect(
        hostname='192.168.255.8',
        username='seusz',
        password='fn7912131',
        timeout=10
    )
    print("✅ SSH 连接成功！")
    
    # 执行命令
    stdin, stdout, stderr = client.exec_command("whoami")
    output = stdout.read().decode().strip()
    print(f"用户：{output}")
    
except Exception as e:
    print(f"❌ SSH 连接失败：{e}")
finally:
    client.close()
```

**安装 paramiko：**
```bash
pip install paramiko
```

---

## 最佳实践

1. **使用密钥认证** - 比密码更安全
2. **设置连接超时** - 避免长时间等待
3. **禁用主机密钥检查** - 仅用于测试环境
4. **使用 sshpass 时注意安全性** - 不要将密码硬编码在脚本中
5. **检查网络连接** - 先 ping 确认可达性
6. **处理包管理锁** - 遇到锁冲突时耐心等待或修复

---

## 安全注意事项

⚠️ **不要在生产环境中使用：**
- `StrictHostKeyChecking=no` - 可能遭受中间人攻击
- 硬编码密码 - 使用环境变量或密钥管理工具
- 开放端口 22 - 考虑使用非标准端口或 VPN

✅ **推荐做法：**
- 使用 SSH 密钥认证
- 配置 SSH 堡垒主机
- 启用双因素认证
- 限制 SSH 访问 IP 白名单

---

## 相关技能

- `troubleshoot-feishu-bot-connection` - Feishu 机器人连接问题
- `troubleshooting-hermes-installation` - Hermes 安装问题
- `hermes-agent` - Hermes Agent 使用指南
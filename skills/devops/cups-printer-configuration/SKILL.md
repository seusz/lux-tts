---
name: cups-printer-configuration
category: devops
description: 为无官方 Linux 驱动的打印机配置 CUPS（如 Brother DCP-T700W）
---

# CUPS 打印机配置 - 无官方驱动设备

## 场景
为 Debian/Ubuntu 系统配置 Brother DCP-T700W 等没有官方 Linux PPD 驱动的打印机，使用 CUPS 的 `driverless`/`raw` 驱动。

## 前提条件
- 系统：Debian 12+ 或 Ubuntu 20.04+
- CUPS 已安装 (`cups`, `cups-client`, `cups-ppdc`)
- 打印机通过 USB 连接并识别 (`lsusb` 可见)
- 用户权限：SSH 用户 + CUPS admin 用户

## 核心步骤

### 1. 安装依赖
```bash
sudo apt update
sudo apt install cups cups-browsed ipp-usb cups-ppdc
```

### 2. 修复 CUPS 配置
**常见问题**：`cupsd.conf` 包含重复的 `Listen`、`Location` 块或无效指令导致服务崩溃

**检查配置**：
```bash
sudo grep -n "Listen\|Location\|Require" /etc/cups/cupsd.conf
```

**手动修复**（如果服务无法启动）：
```bash
# 备份当前配置
sudo cp /etc/cups/cupsd.conf /etc/cups/cupsd.conf.backup

# 使用文本编辑器修复（删除重复块和无效指令）
sudo nano /etc/cups/cupsd.conf
```

**有效配置要点**：
```apache
Listen 0.0.0.0:631
BrowseAddress @LOCAL
BrowseLocalProtocols dnssd
DefaultAuthType Basic
Require @OWNER
<Location />
  Order allow,deny
  Allow @LOCAL
</Location>
<Location /admin>
  Order allow,deny
  Allow @LOCAL
</Location>
```

### 3. 重启 CUPS 服务
```bash
sudo systemctl restart cups
sudo systemctl status cups
```

### 4. 添加打印机（使用 raw 驱动）
```bash
# 获取 USB 设备信息
lsusb | grep -i brother

# 添加打印机（使用 raw 驱动绕过 PPD 缺失）
sudo lpadmin -p Brother_T700W -v usb://Brother/DCP-T700W?serial=BROM5H388367 -m raw -E

# 启用并共享打印机
sudo cupsctl --share-printers
sudo lpadmin -p Brother_T700W -o Shared=Yes
```

### 5. 验证配置
```bash
# 检查打印机状态
lpstat -p Brother_T700W

# 测试打印
echo "测试打印内容" | lp -d Brother_T700W

# 检查 CUPS 管理页面
# 访问 http://192.168.255.8:631/printers
```

## 常见问题

### 问题 1：CUPS 服务无法启动
**症状**：`service cups status` 显示 inactive/dead，错误日志包含 "Duplicate" 或 "Unknown Require"

**解决**：
1. 检查 `/var/log/cups/error_log`
2. 手动修复 `/etc/cups/cupsd.conf` 中的重复块
3. 确保没有无效的 `Require @OWNER` 在 `<Location>` 块外

### 问题 2：打印机在管理页面不显示
**原因**：
- 浏览器缓存（清除缓存或强制刷新）
- CUPS 模板问题（检查 `/usr/share/cups/model/`）
- 打印机未启用（`lpadmin -p Brother_T700W -o printer-is-shared=true`）

**解决**：
```bash
# 直接访问打印机页面
curl http://localhost:631/printers/Brother_T700W

# 检查打印机是否在 CUPS 内部
lpstat -p
```

### 问题 3：raw 驱动文件缺失
**症状**：`cups-driverd` 报错 "No such file or directory"

**解决**：
```bash
sudo apt install cups-bsd cups-ppdc
# 确保 /usr/share/cups/model/application/vnd.cups-raw 存在
```

### 问题 4：网络共享不可见
**原因**：`cups-browsed` 未运行或 mDNS 配置错误

**解决**：
```bash
sudo systemctl enable cups-browsed
sudo systemctl start cups-browsed
sudo netstat -tuln | grep 631
```

## 通过 Web 管理页面检查打印机状态

### 访问 CUPS 管理界面
```bash
# 在浏览器中访问
http://<服务器IP>:631/
http://<服务器IP>:631/admin (需要登录)
http://<服务器IP>:631/printers/ (查看打印机列表)
```

### 管理页面登录
- **普通用户**：使用 SSH 用户（如 `seusz`）
- **管理员**：使用 CUPS admin 账户（如 `admin/admin`）

### 关键检查点
1. **打印机列表** (`/printers/`)：
   - 查看已配置的打印机队列
   - 检查状态：Idle、Accepting Jobs、Shared

2. **打印机详情** (`/printers/<打印机名>`)：
   - **Driver**: 使用的驱动类型（raw、PPD 等）
   - **Connection**: 连接方式（USB、网络、IPP）
   - **Defaults**: 默认纸张、质量设置

3. **管理操作**：
   - 打印测试页
   - 暂停/恢复打印机
   - 修改配置
   - 查看作业队列

### 常见问题诊断
- **打印机不显示**：清除浏览器缓存，直接访问 `/printers/`
- **权限拒绝**：检查 CUPS 用户权限和 `cupsd.conf` 配置
- **状态异常**：查看 `/var/log/cups/error_log`

## 注意事项
- **CUPS 版本**：2.2.10 为旧版本，某些新功能可能不支持
- **ipp-usb**：需要较新内核（4.10+）支持
- **网络发现**：确保防火墙允许 631 端口和 mDNS (5353/udp)
- **测试打印**：先发送小文件测试，避免浪费纸张

## 参考
- CUPS 官方文档：https://www.cups.org/doc/
- Brother DCP-T700W: https://support.brother.com/g/b/downloadlist.aspx?c=us&lang=en&prod=dct700wus
**Hermes Agent Docker 配置经验：**

当在 Docker 容器中使用 Hermes Agent 时，`hermes` 命令不在默认 PATH 中，需要使用完整路径或设置环境变量：

**正确路径：**
- 主命令：`/opt/hermes/.venv/bin/hermes`
- 包装脚本：`/opt/hermes/hermes`
- 项目目录：`/opt/hermes`

**必需环境变量：**
```bash
export PATH="/opt/hermes/.venv/bin:/opt/hermes:$PATH"
export PYTHONPATH="/opt/hermes:$PYTHONPATH"
```

**使用方式：**
1. 使用完整路径：`docker exec hermes /opt/hermes/.venv/bin/hermes gateway run`
2. 设置环境变量：`docker exec -e PATH=/opt/hermes/.venv/bin:/opt/hermes:$PATH -e PYTHONPATH=/opt/hermes:$PYTHONPATH hermes /opt/hermes/.venv/bin/hermes gateway run`
3. 进入容器激活虚拟环境：`docker exec -it hermes bash` → `source /opt/hermes/.venv/bin/activate` → `hermes gateway run`

**常见问题：**
- "hermes: command not found" - PATH 未配置，使用完整路径
- "ModuleNotFoundError" - 未激活虚拟环境，使用 `.venv/bin/python`
§
Hermes Agent Docker 容器配置：
- 容器镜像：nousresearch/hermes-agent:latest
- 容器名称：hermes
- 数据卷：hermes-data:/opt/data
- 必需环境变量：
  - PATH=/opt/hermes/.venv/bin:/opt/hermes:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  - PYTHONPATH=/opt/hermes
  - HERMES_HOME=/opt/data
- 启动命令：docker run -d --name hermes -e PATH=... -e PYTHONPATH=... -e HERMES_HOME=... -v hermes-data:/opt/data nousresearch/hermes-agent:latest
- 进入容器：docker exec -it hermes bash
- 在容器内使用 hermes 命令前需激活虚拟环境：source /opt/hermes/.venv/bin/activate

**默认消息发送频道：**
- 当前：飞书 (feishu:oc_1d576234426b22d8c6b1303cd26337f7)
- 之前：QQ Bot (qqbot:6DEAF2F03CBA3FFDB36ADA1F90610BBA)
- 使用方式：发送消息时指定 `target='feishu'` 即可发送到飞书 DM 频道
§
**自检记录：**
- 时间：2026-04-16 23:30
- 技能总数：83 个，覆盖 19 个类别
- 记忆系统：正常运行，存储了 Docker 配置经验
- 工具可用性：全部正常
- 会话状态：正常，已连接 feishu 和 qqbot
- 配置：无异常
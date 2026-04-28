#!/usr/bin/env python3
"""
Soul Profile Auto-Loader Hook

在每次 session:start 或 session:reset 时自动加载 soul-profile 技能。
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 定义要自动加载的技能列表
AUTO_LOAD_SKILLS = ["soul-profile"]

async def handle(event_type: str, context: dict) -> None:
    """
    处理会话开始/重置事件，自动加载 soul-profile 技能。
    
    Args:
        event_type: 事件类型 ("session:start" 或 "session:reset")
        context: 事件上下文，包含会话信息等
    """
    logger.info(f"[soul-loader] 检测到事件：{event_type}")
    
    # 检查是否是我们要处理的事件
    if event_type not in ["session:start", "session:reset"]:
        return
    
    # 获取会话 ID 和平台信息
    session_id = context.get("session_id", "unknown")
    platform = context.get("platform", "unknown")
    
    logger.info(f"[soul-loader] 正在为会话 {session_id} ({platform}) 加载 soul-profile 技能...")
    
    # 这里我们使用 hermes skills 命令来加载技能
    # 注意：在实际环境中，这个钩子会被调用，但技能加载需要通过 CLI 或 API
    # 所以我们在这里记录日志，并在配置中设置默认技能
    
    # 实际上，更好的方式是在配置文件中设置默认技能列表
    # 让我们修改 config.yaml 来添加默认技能
    try:
        from hermes_cli.config import load_config, save_config
        
        config = load_config()
        
        # 确保 skills 配置存在
        if "skills" not in config:
            config["skills"] = {}
        
        # 添加默认技能列表
        if "default" not in config["skills"]:
            config["skills"]["default"] = []
        
        # 合并自动加载的技能（去重）
        current_skills = config["skills"]["default"]
        for skill in AUTO_LOAD_SKILLS:
            if skill not in current_skills:
                current_skills.append(skill)
        
        # 保存配置
        save_config(config)
        
        logger.info(f"[soul-loader] 已更新默认技能列表：{config['skills']['default']}")
        logger.info(f"[soul-loader] ✓ soul-profile 技能将在每次新会话时自动加载")
        
    except Exception as e:
        logger.error(f"[soul-loader] 更新配置失败：{e}", exc_info=True)

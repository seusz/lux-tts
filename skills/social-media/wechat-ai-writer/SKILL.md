---
name: wechat-ai-writer
category: social-media
description: 微信内容创作助手 - 使用 AI 生成微信公众号文章、朋友圈文案等内容
---

# WeChat AI Writer 技能

## 功能描述

使用 AI 生成和创作微信相关内容，包括：
- 微信公众号文章
- 朋友圈文案
- 微信群消息
- 微信推文

## 使用方式

### 1. 生成微信公众号文章

```python
# 使用终端调用 AI 生成文章
terminal(command="echo '写一篇关于人工智能的公众号文章，风格轻松幽默，字数 2000 字' | hermes ai write --platform wechat --type article")
```

### 2. 生成朋友圈文案

```python
# 生成朋友圈文案
terminal(command="echo '分享一个技术会议的经历，配图 3 张，表达收获和感悟' | hermes ai write --platform wechat --type moment")
```

### 3. 生成微信群消息

```python
# 生成群消息
terminal(command="echo '在技术群里分享一个有趣的 Python 技巧' | hermes ai write --platform wechat --type group")
```

### 4. 提取微信公众号文章

```python
# 使用 Python 脚本提取 WeChat 文章
execute_code(code="""
import requests
import re
from html import unescape

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

response = requests.get('https://mp.weixin.qq.com/s/ARTICLE_ID', headers=headers, timeout=30)
html_content = response.text

# 提取标题
title_match = re.search(r'<meta property="og:title" content="(.*?)"', html_content)
title = title_match.group(1) if title_match else "未知标题"

# 提取作者
author_match = re.search(r'<meta name="author" content="(.*?)"', html_content)
author = author_match.group(1) if author_match else "未知作者"

# 提取正文
content_match = re.search(r'id="js_content".*?>(.*?)</div>', html_content, re.DOTALL)
if content_match:
    raw_content = content_match.group(1)
    clean_content = re.sub(r'<[^>]+>', ' ', raw_content)
    clean_content = re.sub(r'\s+', ' ', clean_content)
    clean_content = unescape(clean_content).strip()
""")
```

**提取技巧说明**:
- 使用 `User-Agent` 模拟浏览器访问
- 微信文章标题通常在 `<meta property="og:title">` 中
- 作者信息在 `<meta name="author">` 中
- 正文内容在 `id="js_content"` 的 div 中
- 需要清理 HTML 标签并解码 HTML 实体

## 参数说明

- `--platform wechat`: 指定平台为微信
- `--type {article,moment,group}`: 内容类型
  - `article`: 公众号文章
  - `moment`: 朋友圈
  - `group`: 群消息

## 输出格式

### 公众号文章
- 标题（1-2 个备选）
- 摘要
- 正文（包含小标题、段落）
- 标签（3-5 个）
- 推荐配图建议

### 朋友圈文案
- 文案内容（200 字以内）
- 配图建议
- 表情符号建议

### 群消息
- 消息内容
- 回复建议

## 注意事项

1. 微信文章需要符合平台规范，避免敏感内容
2. 朋友圈文案要简洁生动，适合移动端阅读
3. 群消息要注意语气和场合
4. 可以结合具体场景和受众调整风格

## 示例

### 示例 1：生成技术类公众号文章

```
输入：写一篇关于 Rust 编程语言的公众号文章，面向 Python 开发者，风格专业但易懂，字数 2500 字

输出：
标题：《从 Python 到 Rust：一位数据工程师的转型之旅》
摘要：告别 GIL，拥抱内存安全，Rust 如何改变我的开发体验

正文：
## 为什么选择 Rust？
...（详细文章）

标签：#Rust #Python #编程 #内存安全 #数据工程
配图建议：Rust 和 Python 代码对比图、性能对比图表
```

### 示例 2：生成朋友圈文案

```
输入：分享参加 QCon 技术大会的经历，配图 3 张

输出：
文案：
三天 QCon，干货满满！🎉
听了 5 场演讲，认识了一群志同道合的朋友
最大的收获：AI 工程化的最佳实践
感谢组织方，期待明年再见！💪

配图：会场照片、演讲 PPT、大会合影
```

## 扩展功能

- 支持多轮对话优化内容
- 可以引用历史文章风格
- 支持 A/B 测试不同版本
- 可以生成内容大纲供审核

## 依赖

- 需要配置 AI 模型（建议使用支持长文本的模型）
- 需要网络连接

## 故障排查

如果生成内容不符合预期：
1. 检查 AI 模型配置
2. 调整提示词，提供更多细节
3. 尝试不同的风格参数
4. 使用多轮对话优化

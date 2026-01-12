# GNewsBot - Google News 实时推送机器人

一个基于 **GNews** 库的 Python 应用，实时推送 Google News 新闻到电报机器人。

## 功能特性

- 🌐 **Google News 支持**：基于 GNews 库，支持 141+ 国家，41+ 语言
- 📰 **多主题支持**：商业、科技、世界、娱乐、体育、科学、健康
- 🚀 **实时推送**：定期检查最新新闻，自动推送到电报
- 🔄 **智能去重**：自动记录已推送新闻，避免重复
- ⚙️ **灵活配置**：支持自定义语言、国家、检查间隔
- 📊 **历史记录**：保存推送历史，便于追踪

## 支持的新闻主题

- 📈 **商业** (BUSINESS)
- 💻 **科技** (TECHNOLOGY)
- 🌍 **世界** (WORLD)
- 🎬 **娱乐** (ENTERTAINMENT)
- ⚽ **体育** (SPORTS)
- 🔬 **科学** (SCIENCE)
- 🏥 **健康** (HEALTH)

## 系统要求

- Python 3.7+
- 有效的电报机器人 Token
- 互联网连接

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Howe813/GNewsBot.git
cd GNewsBot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制配置模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 电报机器人配置（必需）
TELEGRAM_TOKEN=8475548110:AAG9geUaI8Ekqq5VcLLdqIrK4FMjo6nJTKs
TELEGRAM_CHAT_ID=-1003465767625

# GNews 配置
GNEWS_LANGUAGE=en
GNEWS_COUNTRY=US
GNEWS_MAX_RESULTS=5

# 检查间隔（秒）
CHECK_INTERVAL=300
```

### 获取电报机器人 Token

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令创建新机器人
3. 按照提示设置机器人名称和用户名
4. 获取 Token

### 获取 Chat ID

1. 创建一个电报频道或群组
2. 将机器人添加到频道/群组
3. 发送一条消息
4. 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. 在返回的 JSON 中找到 `chat` -> `id`

## 使用方法

### 直接运行

```bash
python main.py
```

### 后台运行（使用 nohup）

```bash
nohup python main.py > gnewsbot.log 2>&1 &
```

### 使用 systemd 服务

创建服务文件 `/etc/systemd/system/gnewsbot.service`：

```ini
[Unit]
Description=GNewsBot - Google News Push Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/GNewsBot
Environment="PATH=/path/to/GNewsBot/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/path/to/GNewsBot/.env
ExecStart=/path/to/GNewsBot/venv/bin/python /path/to/GNewsBot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable gnewsbot
sudo systemctl start gnewsbot
sudo systemctl status gnewsbot
```

查看日志：

```bash
sudo journalctl -u gnewsbot -f
```

## 配置说明

### 语言和国家

GNews 支持多种语言和国家组合。常见配置：

| 语言 | 国家 | 配置 |
|------|------|------|
| 英语 | 美国 | `GNEWS_LANGUAGE=en`, `GNEWS_COUNTRY=US` |
| 英语 | 英国 | `GNEWS_LANGUAGE=en`, `GNEWS_COUNTRY=GB` |
| 中文 | 中国 | `GNEWS_LANGUAGE=zh-Hans`, `GNEWS_COUNTRY=CN` |
| 中文 | 香港 | `GNEWS_LANGUAGE=zh-Hant`, `GNEWS_COUNTRY=HK` |
| 日语 | 日本 | `GNEWS_LANGUAGE=ja`, `GNEWS_COUNTRY=JP` |

完整列表请参考 [GNews 文档](https://github.com/ranahaani/GNews)。

### 检查间隔

- 推荐：300 秒（5 分钟）
- 最小：60 秒（1 分钟）
- 注意：间隔太短可能被 Google 限流

### 每次获取数量

- 默认：5 条
- 范围：1-100 条
- 注意：机器人只推送每个主题的最新一条

## 推送格式

```
📈 商业
Apple's stock can climb 35% this year

Apple Inc. is expected to see significant growth...

📰 来源: MarketWatch
🕒 2026-01-12 10:30

阅读原文
```

## 工作原理

1. **定期检查**：每隔指定时间（默认 5 分钟）检查一次
2. **获取新闻**：从 Google News 获取各主题的最新新闻
3. **去重判断**：检查新闻 URL 是否已推送过
4. **推送新闻**：将新新闻推送到电报
5. **记录历史**：保存已推送的新闻 URL

## 日志说明

日志文件：`gnewsbot.log`

```
2026-01-12 10:30:00 - INFO - GNewsBot - Google News 实时推送机器人
2026-01-12 10:30:01 - INFO - 获取 BUSINESS 主题新闻...
2026-01-12 10:30:05 - INFO - 从 Google News BUSINESS 获取了 5 条新闻
2026-01-12 10:30:06 - INFO - BUSINESS 有新新闻: Apple's stock can climb 35%...
2026-01-12 10:30:07 - INFO - ✓ 已推送 BUSINESS 最新新闻
```

## 故障排除

### 1. 无法获取新闻

**原因**：可能被 Google 限流

**解决**：
- 增加检查间隔（如 600 秒）
- 减少 `GNEWS_MAX_RESULTS`
- 使用代理（需修改代码）

### 2. 电报推送失败

**原因**：Token 或 Chat ID 错误

**解决**：
- 检查 `.env` 文件配置
- 确认机器人已添加到群组
- 确认机器人有发送消息权限

### 3. 重复推送

**原因**：历史记录文件损坏

**解决**：
```bash
rm gnews_history.json
# 重启机器人
```

## 性能指标

- **内存占用**：约 50-80 MB
- **CPU 占用**：检查时 < 10%，空闲时 < 1%
- **网络流量**：约 1-2 MB/小时
- **推送频率**：每 5 分钟最多 7 条（每个主题 1 条）

## 与 QuickFinews 的区别

| 特性 | GNewsBot | QuickFinews |
|------|----------|-------------|
| 新闻源 | Google News | TuShare + Finnhub |
| 覆盖范围 | 全球 141+ 国家 | 中国 + 国际财经 |
| 主题 | 7 个通用主题 | 财经专注 |
| API Key | 不需要 | 需要 |
| 响应速度 | 较慢（爬虫） | 快（API） |
| 语言支持 | 41+ 语言 | 主要英文/中文 |

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- [GNews](https://github.com/ranahaani/GNews) - Google News RSS 爬虫库
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API 封装

## 联系方式

- GitHub: [@Howe813](https://github.com/Howe813)
- 项目地址: https://github.com/Howe813/GNewsBot

---

**祝您使用愉快！** 🎉

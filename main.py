#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNewsBot - Google News 实时推送机器人
基于 GNews 库，推送 Google News 到电报
"""

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

import os
import sys
import time
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Set
import asyncio
from gnews import GNews
from telegram import Bot
from telegram.error import TelegramError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gnewsbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# GNews 新闻主题
GNEWS_TOPICS = ['BUSINESS', 'TECHNOLOGY', 'WORLD', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']

# 主题名称映射
TOPIC_NAMES = {
    'BUSINESS': '📈 商业',
    'TECHNOLOGY': '💻 科技',
    'WORLD': '🌍 世界',
    'ENTERTAINMENT': '🎬 娱乐',
    'SPORTS': '⚽ 体育',
    'SCIENCE': '🔬 科学',
    'HEALTH': '🏥 健康'
}


class NewsTracker:
    """新闻追踪器 - 记录已推送的新闻，避免重复"""
    
    def __init__(self, history_file: str = 'gnews_history.json'):
        self.history_file = history_file
        self.news_urls: Set[str] = set()
        self.load_history()
    
    def load_history(self):
        """从文件加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.news_urls = set(data.get('urls', []))
                    logger.info(f"加载了 {len(self.news_urls)} 条历史新闻记录")
            except Exception as e:
                logger.error(f"加载历史记录失败: {e}")
                self.news_urls = set()
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            # 只保留最近 1000 条记录
            if len(self.news_urls) > 1000:
                self.news_urls = set(list(self.news_urls)[-1000:])
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({'urls': list(self.news_urls)}, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def is_new(self, news_url: str) -> bool:
        """检查新闻是否已推送过"""
        return news_url not in self.news_urls
    
    def mark_as_sent(self, news_url: str):
        """标记新闻为已推送"""
        self.news_urls.add(news_url)
        self.save_history()


class TelegramNotifier:
    """电报通知器"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
    
    async def send_message(self, text: str) -> bool:
        """发送消息到电报"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            logger.info(f"消息已发送到电报 (Chat ID: {self.chat_id})")
            return True
        except TelegramError as e:
            logger.error(f"发送电报消息失败: {e}")
            return False
    
    async def send_news(self, news: Dict, topic: str) -> bool:
        """发送新闻到电报"""
        try:
            topic_name = TOPIC_NAMES.get(topic, topic)
            title = news.get('title', '无标题')
            description = news.get('description', '')
            url = news.get('url', '')
            publisher = news.get('publisher', {})
            
            # 提取发布者名称
            if isinstance(publisher, dict):
                publisher_name = publisher.get('title', '未知来源')
            else:
                publisher_name = str(publisher) if publisher else '未知来源'
            
            # 提取发布时间
            published_date = news.get('published date', '')
            
            # 清理 HTML 标签和多余空格
            title = re.sub(r'<[^>]+>', '', title).strip()
            description = re.sub(r'<[^>]+>', '', description).strip()
            
            # 限制描述长度
            if len(description) > 300:
                description = description[:300] + "..."
            
            # 格式化时间
            try:
                if published_date:
                    dt = datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %Z')
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = '时间未知'
            except:
                time_str = published_date if published_date else '时间未知'
            
            message = f"""
<b>{topic_name}</b>
<b>{title}</b>

{description}

📰 来源: {publisher_name}
🕒 {time_str}

<a href="{url}">阅读原文</a>
"""
            
            await self.send_message(message)
            return True
        except Exception as e:
            logger.error(f"发送新闻失败: {e}")
            return False


class GNewsCollector:
    """GNews 新闻收集器"""
    
    def __init__(self, language: str = 'en', country: str = 'US', max_results: int = 5):
        self.gnews = GNews(
            language=language,
            country=country,
            max_results=max_results,
            period='1h'  # 获取最近1小时的新闻
        )
        logger.info(f"GNews 收集器初始化: language={language}, country={country}, max_results={max_results}")
    
    def get_news_by_topic(self, topic: str) -> List[Dict]:
        """获取指定主题的新闻"""
        try:
            logger.info(f"获取 {topic} 主题新闻...")
            news_list = self.gnews.get_news_by_topic(topic)
            
            if news_list and len(news_list) > 0:
                logger.info(f"从 Google News {topic} 获取了 {len(news_list)} 条新闻")
                return news_list
            else:
                logger.info(f"未发现 {topic} 新闻")
                return []
                
        except Exception as e:
            logger.error(f"获取 {topic} 新闻失败: {e}")
            return []


class GNewsBot:
    """GNews 机器人 - 主控制器"""
    
    def __init__(self, telegram_token: str, telegram_chat_id: str, 
                 language: str = 'en', country: str = 'US', max_results: int = 5):
        self.collector = GNewsCollector(language, country, max_results)
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        self.tracker = NewsTracker()
        self.running = False
    
    async def check_and_push_topic_news(self, topic: str):
        """检查并推送指定主题的新闻（只推送最新一条）"""
        try:
            # 获取该主题的新闻
            news_list = self.collector.get_news_by_topic(topic)
            
            if not news_list or len(news_list) == 0:
                logger.debug(f"未发现 {topic} 新闻")
                return
            
            # 只取最新的一条
            latest_news = news_list[0]
            news_url = latest_news.get('url', '')
            
            if not news_url:
                logger.warning(f"{topic} 新闻缺少 URL，跳过")
                return
            
            # 检查是否已推送
            if self.tracker.is_new(news_url):
                title = latest_news.get('title', '')
                logger.info(f"{topic} 有新新闻: {title[:50]}...")
                
                # 推送新闻
                success = await self.notifier.send_news(latest_news, topic)
                if success:
                    self.tracker.mark_as_sent(news_url)
                    logger.info(f"✓ 已推送 {topic} 最新新闻")
                
                # 避免请求过快
                await asyncio.sleep(1)
            else:
                logger.debug(f"{topic} 最新新闻已推送过")
                
        except Exception as e:
            logger.error(f"处理 {topic} 新闻时出错: {e}")
    
    async def check_and_push_news(self):
        """检查并推送所有主题的新闻"""
        sent_count = 0
        
        for topic in GNEWS_TOPICS:
            try:
                await self.check_and_push_topic_news(topic)
                sent_count += 1
                
                # 避免请求过快
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"处理 {topic} 时出错: {e}")
                continue
        
        logger.info(f"本次检查完成，处理了 {len(GNEWS_TOPICS)} 个主题")
    
    async def run(self, check_interval: int = 300):
        """运行机器人"""
        self.running = True
        logger.info(f"GNews 机器人启动，检查间隔: {check_interval} 秒")
        logger.info(f"监听主题: {', '.join(GNEWS_TOPICS)}")
        
        try:
            while self.running:
                await self.check_and_push_news()
                logger.info(f"等待 {check_interval} 秒后进行下次检查...")
                await asyncio.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            self.running = False
        except Exception as e:
            logger.error(f"机器人运行出错: {e}")
            self.running = False
    
    def stop(self):
        """停止机器人"""
        self.running = False
        logger.info("机器人已停止")


async def main():
    """主函数"""
    # 从环境变量读取配置
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 默认 5 分钟
    language = os.getenv('GNEWS_LANGUAGE', 'en')
    country = os.getenv('GNEWS_COUNTRY', 'US')
    max_results = int(os.getenv('GNEWS_MAX_RESULTS', '5'))
    
    # 验证配置
    if not telegram_token:
        logger.error("未设置 TELEGRAM_TOKEN 环境变量")
        sys.exit(1)
    
    if not telegram_chat_id:
        logger.error("未设置 TELEGRAM_CHAT_ID 环境变量")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("GNewsBot - Google News 实时推送机器人")
    logger.info("=" * 50)
    logger.info(f"语言: {language}")
    logger.info(f"国家: {country}")
    logger.info(f"每次获取: {max_results} 条新闻")
    logger.info(f"Telegram Chat ID: {telegram_chat_id}")
    logger.info(f"检查间隔: {check_interval} 秒")
    logger.info("=" * 50)
    
    # 创建机器人
    bot = GNewsBot(telegram_token, telegram_chat_id, language, country, max_results)
    
    # 运行机器人
    try:
        await bot.run(check_interval=check_interval)
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        bot.stop()


if __name__ == '__main__':
    asyncio.run(main())

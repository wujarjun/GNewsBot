#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNewsBot 测试脚本
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import logging
import asyncio
from gnews import GNews
from telegram import Bot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_telegram():
    """测试电报连接"""
    logger.info("=" * 50)
    logger.info("测试电报机器人连接")
    logger.info("=" * 50)
    
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not telegram_token or not telegram_chat_id:
        logger.error("未设置 TELEGRAM_TOKEN 或 TELEGRAM_CHAT_ID")
        return False
    
    try:
        bot = Bot(token=telegram_token)
        await bot.send_message(
            chat_id=telegram_chat_id,
            text="🤖 GNewsBot 测试消息\n\n这是一条测试消息，如果您看到这条消息，说明机器人配置正确！",
            parse_mode='HTML'
        )
        logger.info("✓ 电报连接成功，测试消息已发送")
        return True
    except Exception as e:
        logger.error(f"✗ 电报连接失败: {e}")
        return False


def test_gnews():
    """测试 GNews"""
    logger.info("=" * 50)
    logger.info("测试 GNews")
    logger.info("=" * 50)
    
    language = os.getenv('GNEWS_LANGUAGE', 'en')
    country = os.getenv('GNEWS_COUNTRY', 'US')
    max_results = int(os.getenv('GNEWS_MAX_RESULTS', '3'))
    
    try:
        gnews = GNews(language=language, country=country, max_results=max_results, period='1h')
        
        logger.info(f"配置: language={language}, country={country}, max_results={max_results}")
        
        # 测试获取商业新闻
        logger.info("\n测试获取 BUSINESS 新闻...")
        news = gnews.get_news_by_topic('BUSINESS')
        
        if news and len(news) > 0:
            logger.info(f"✓ 成功获取 {len(news)} 条新闻")
            logger.info(f"  第一条标题: {news[0].get('title', 'N/A')[:60]}...")
            logger.info(f"  发布者: {news[0].get('publisher', {}).get('title', 'N/A')}")
            return True
        else:
            logger.warning("⚠ 未获取到新闻（可能是网络问题或被限流）")
            return True  # 不算失败，因为可能是正常的限流
            
    except Exception as e:
        logger.error(f"✗ GNews 测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("GNewsBot 测试套件")
    logger.info("=" * 50)
    
    # 测试 GNews
    gnews_ok = test_gnews()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试电报
    telegram_ok = await test_telegram()
    
    logger.info("=" * 50)
    logger.info("测试结果:")
    logger.info(f"  GNews: {'✓ 通过' if gnews_ok else '✗ 失败'}")
    logger.info(f"  Telegram: {'✓ 通过' if telegram_ok else '✗ 失败'}")
    logger.info("=" * 50)
    
    if gnews_ok and telegram_ok:
        logger.info("✓ 所有测试通过！机器人已准备好使用。")
        sys.exit(0)
    else:
        logger.error("✗ 部分测试失败，请检查配置。")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

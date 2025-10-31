#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号新闻发布示例（配置文件优先版）
演示如何使用WeChatPublicationManager将新闻内容发布到微信公众号
优先从配置文件读取认证信息，降低环境配置复杂度
"""

import os
import json
from modules.config import configparser
from datetime import datetime
from modules.publisher.wechat_publication_manager import WeChatPublicationManager

def load_wechat_config():
    """
    从配置文件加载微信公众号配置信息
    优先级：配置文件 > 环境变量
    
    Returns:
        tuple: (app_id, app_secret) AppID和AppSecret
    """
    # 首先尝试从配置文件读取
    config_files = ['wechat_config.ini', 'config/wechat_config.ini']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if 'wechat' in config:
                app_id = config['wechat'].get('app_id')
                app_secret = config['wechat'].get('app_secret')
                
                if app_id and app_secret:
                    print(f"从配置文件 {config_file} 读取微信认证信息")
                    return app_id, app_secret
    
    # 如果配置文件不存在或没有有效配置，则回退到环境变量
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if app_id and app_secret:
        print("从环境变量读取微信认证信息")
        return app_id, app_secret
    
    return None, None

def load_processed_news(file_path):
    """
    加载已处理的新闻内容
    
    Args:
        file_path (str): 新闻内容文件路径
        
    Returns:
        dict: 新闻内容数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"新闻内容文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_for_wechat(news_data):
    """
    将新闻数据格式化为适合微信公众号发布的格式
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        tuple: (title, content) 标题和HTML格式内容
    """
    # 使用第一条新闻作为标题
    news_items = news_data.get('news_items', [])
    if news_items:
        title = f"【新闻联播】{news_items[0].get('title', '今日要闻')}"
    else:
        title = "今日新闻联播摘要"
    
    # 构建文章内容
    content = "<h1>新闻联播摘要</h1>\n"
    date_str = news_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    content += f"<p><strong>日期：</strong>{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日</p>\n"
    content += "<hr>\n"
    
    for i, news in enumerate(news_items, 1):
        content += f"<h3>{i}. {news.get('title', '')}</h3>\n"
        content += f"<p>{news.get('content', '')}</p>\n"
        content += "<hr>\n"
    
    return title, content

def main():
    """
    主函数：演示微信公众号发布流程
    """
    # 从配置文件获取微信公众号配置信息（优先）或环境变量（备选）
    app_id, app_secret = load_wechat_config()
    
    if not app_id or not app_secret:
        print("请配置微信公众号认证信息")
        print("方式一：编辑 wechat_config.ini 文件，配置 app_id 和 app_secret")
        print("方式二：设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("示例：")
        print("  export WECHAT_APP_ID='your_app_id'")
        print("  export WECHAT_APP_SECRET='your_app_secret'")
        return
    
    # 初始化发布管理器
    manager = WeChatPublicationManager(app_id, app_secret)
    
    # 加载新闻内容（请根据实际情况修改文件路径）
    news_file = "xinwenlianbo_20251023.json"  # 示例文件名，请根据实际文件名修改
    
    try:
        # 加载新闻内容
        news_data = load_processed_news(news_file)
        
        # 格式化为微信公众号文章
        title, content = format_for_wechat(news_data)
        
        # 封面图片路径（请根据实际情况修改）
        cover_image_path = "./zi_yuan/cover.png"  # 请确保此图片存在
        
        if os.path.exists(cover_image_path):
            # 发布文章
            print(f"正在发布文章：{title}")
            result = manager.publish_article(title, content, cover_image_path)
            
            print("文章发布成功！")
            print(f"封面图片media_id: {result['thumb_media_id']}")
            print(f"草稿media_id: {result['draft_media_id']}")
            print(f"发布结果: {result['publish_result']}")
        else:
            print("封面图片不存在，仅展示格式化后的内容：")
            print(f"标题：{title}")
            print(f"内容预览：{content[:300]}...")
        
    except FileNotFoundError as e:
        print(f"文件错误: {e}")
        print("请确保新闻内容文件存在且路径正确")
    except Exception as e:
        print(f"发布失败: {e}")

if __name__ == "__main__":
    main()
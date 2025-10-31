#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号新闻发布示例
演示如何将处理好的新闻内容发布到微信公众号
"""

import os
import json
from datetime import datetime
from wechat_publisher import WeChatPublisher

def load_news_content(file_path):
    """
    加载处理好的新闻内容
    
    Args:
        file_path (str): 新闻内容文件路径
        
    Returns:
        dict: 新闻内容数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"新闻内容文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_news_for_wechat(news_data):
    """
    将新闻数据格式化为微信公众号文章格式
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        tuple: (title, content) 标题和HTML格式内容
    """
    # 使用第一条新闻作为标题
    title = news_data['news_list'][0]['title'] if news_data['news_list'] else "今日新闻摘要"
    
    # 构建文章内容
    content = "<h1>新闻联播摘要</h1>\n"
    content += f"<p><strong>日期：</strong>{news_data['date']}</p>\n"
    content += "<hr>\n"
    
    for i, news in enumerate(news_data['news_list'], 1):
        content += f"<h3>{i}. {news['title']}</h3>\n"
        content += f"<p>{news['content']}</p>\n"
        if 'url' in news and news['url']:
            content += f"<p><a href='{news['url']}' target='_blank'>查看详情</a></p>\n"
        content += "<hr>\n"
    
    return title, content

def main():
    """
    主函数：演示微信公众号发布流程
    """
    # 从环境变量获取微信公众号配置信息
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if not app_id or not app_secret:
        print("请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("示例：")
        print("  export WECHAT_APP_ID='your_app_id'")
        print("  export WECHAT_APP_SECRET='your_app_secret'")
        return
    
    # 初始化发布器
    publisher = WeChatPublisher(app_id, app_secret)
    
    # 加载新闻内容（请根据实际情况修改文件路径）
    news_file = "processed_news_20251023.json"  # 示例文件名，请根据实际文件名修改
    
    try:
        # 加载新闻内容
        news_data = load_news_content(news_file)
        
        # 格式化为微信公众号文章
        title, content = format_news_for_wechat(news_data)
        
        # 封面图片路径（请根据实际情况修改）
        cover_image_path = "cover.jpg"  # 请确保此图片存在
        
        # 发布文章
        print(f"正在发布文章：{title}")
        result = publisher.publish_article(title, content, cover_image_path)
        
        print("文章发布成功！")
        print(f"封面图片media_id: {result['thumb_media_id']}")
        print(f"草稿media_id: {result['draft_media_id']}")
        print(f"发布结果: {result['publish_result']}")
        
    except FileNotFoundError as e:
        print(f"文件错误: {e}")
        print("请确保新闻内容文件存在且路径正确")
    except Exception as e:
        print(f"发布失败: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新闻内容微信公众号发布示例
展示如何将处理好的新闻内容发布到微信公众号
"""

import os
import json
from datetime import datetime
from wechat_publisher import WeChatPublisher

def load_news_data(file_path):
    """
    加载新闻数据
    
    Args:
        file_path (str): 新闻数据文件路径
        
    Returns:
        dict: 新闻数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"新闻数据文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_news_content(news_data):
    """
    将新闻数据格式化为微信公众号文章
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        tuple: (title, content) 文章标题和内容
    """
    # 使用日期作为标题前缀
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    title = f"{date_str} 新闻联播摘要"
    
    # 构建文章内容
    content = f"<h1>新闻联播摘要</h1>\n"
    content += f"<p><strong>日期：</strong>{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日</p>\n"
    content += "<hr>\n"
    
    # 处理新闻条目
    news_items = news_data.get('news_items', [])
    for i, item in enumerate(news_items, 1):
        content += f"<h3>{i}. {item.get('title', '')}</h3>\n"
        content += f"<p>{item.get('content', '')}</p>\n"
        content += "<hr>\n"
    
    return title, content

def main():
    """
    主函数：演示完整的新闻发布流程
    """
    # 从环境变量获取微信公众号配置
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if not app_id or not app_secret:
        print("请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("示例：")
        print("  export WECHAT_APP_ID='your_app_id'")
        print("  export WECHAT_APP_SECRET='your_app_secret'")
        return
    
    # 新闻数据文件路径
    news_file = "xinwenlianbo_20251023.json"
    
    try:
        # 加载新闻数据
        print(f"正在加载新闻数据: {news_file}")
        news_data = load_news_data(news_file)
        print(f"成功加载 {len(news_data.get('news_items', []))} 条新闻")
        
        # 格式化为微信文章
        print("正在格式化新闻内容...")
        title, content = format_news_content(news_data)
        print(f"文章标题: {title}")
        
        # 初始化微信发布器
        print("正在初始化微信发布器...")
        publisher = WeChatPublisher(app_id, app_secret)
        
        # 注意：这里需要一个实际的封面图片路径
        # 在实际使用中，请替换为真实的图片路径
        cover_image_path = "example_cover.jpg"
        
        if os.path.exists(cover_image_path):
            # 发布文章
            print("正在发布文章到微信公众号...")
            result = publisher.publish_article(title, content, cover_image_path)
            
            print("文章发布成功！")
            print(f"封面图片media_id: {result['thumb_media_id']}")
            print(f"草稿media_id: {result['draft_media_id']}")
            print(f"发布结果: {result['publish_result']}")
        else:
            print(f"警告：封面图片 {cover_image_path} 不存在，跳过发布")
            print("请提供一个有效的封面图片路径进行实际发布")
            print("\n格式化后的文章内容预览：")
            print(f"标题: {title}")
            print(f"内容预览: {content[:200]}...")
            
    except FileNotFoundError as e:
        print(f"文件错误: {e}")
        print("请确保新闻数据文件存在")
    except Exception as e:
        print(f"发布失败: {e}")

if __name__ == "__main__":
    main()
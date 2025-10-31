#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将full_result_*.json文件内容转换为易于理解的Markdown格式文章
"""

import os
import json
import glob
from datetime import datetime

def load_latest_full_result():
    """
    加载最新的full_result_*.json文件
    
    Returns:
        dict: 加载的数据
    """
    # 查找最新的full_result文件
    full_result_files = glob.glob("full_result_*.json")
    
    if not full_result_files:
        raise FileNotFoundError("未找到full_result_*.json文件")
    
    # 选择最新的文件
    latest_file = sorted(full_result_files)[-1]
    print(f"处理文件: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date(date_str):
    """
    格式化日期字符串
    
    Args:
        date_str (str): YYYYMMDD格式的日期字符串
        
    Returns:
        str: 格式化后的日期
    """
    return f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"

def generate_easy_read_summary(news_data):
    """
    生成易于理解的摘要文章
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: Markdown格式的文章
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = format_date(date_str)
    
    # 构建文章
    article = f"# {formatted_date} 新闻联播简明摘要\n\n"
    
    article += f"## 一、国内要闻\n\n"
    
    domestic_news = news_data.get('domestic', [])
    if domestic_news:
        for i, item in enumerate(domestic_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i}')
            summary_text = summary.get('summary', '')
            
            article += f"### {i}. {title}\n\n"
            article += f"{summary_text}\n\n"
    else:
        article += "无国内新闻条目。\n\n"
    
    article += f"## 二、国际动态\n\n"
    
    international_news = news_data.get('international', [])
    if international_news:
        for i, item in enumerate(international_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i}')
            summary_text = summary.get('summary', '')
            
            article += f"### {i}. {title}\n\n"
            article += f"{summary_text}\n\n"
    else:
        article += "无国际新闻条目。\n\n"
    
    # 添加详细内容部分
    article += f"## 三、详细内容\n\n"
    
    if domestic_news or international_news:
        all_news = domestic_news + international_news
        for i, item in enumerate(all_news, 1):
            text_content = item.get('text', '')
            if len(text_content) > 500:
                text_content = text_content[:500] + "..."
            
            article += f"### 新闻 {i} 详细内容\n\n"
            article += f"{text_content}\n\n"
    
    # 添加实体识别部分
    article += f"## 四、实体识别\n\n"
    
    if domestic_news or international_news:
        all_news = domestic_news + international_news
        for i, item in enumerate(all_news, 1):
            entities = item.get('entities', {})
            locations = entities.get('locations', [])
            persons = entities.get('persons', [])
            organizations = entities.get('organizations', [])
            
            article += f"### 新闻 {i} 实体识别结果\n\n"
            if locations:
                article += f"- **地点**：{', '.join(locations)}\n"
            if persons:
                article += f"- **人物**：{', '.join(persons[:5])}{'...' if len(persons) > 5 else ''}\n"
            if organizations:
                article += f"- **组织**：{', '.join(organizations[:5])}{'...' if len(organizations) > 5 else ''}\n"
            article += "\n"
    
    return article

def main():
    """
    主函数：生成易于理解的摘要文章
    """
    try:
        # 加载数据
        news_data = load_latest_full_result()
        
        # 生成文章
        article = generate_easy_read_summary(news_data)
        
        # 保存结果
        date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
        output_file = f"easy_read_summary_{date_str}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"文章已保存到: {output_file}")
        print("\n文章预览:")
        print(article[:1000] + "..." if len(article) > 1000 else article)
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
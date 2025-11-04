#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新闻总结文章生成器
将processed_xinwenlianbo_*.json文件内容转换为总结性文章并输出为HTML格式
"""

import os
import sys
import json
import glob
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_processed_data(file_path):
    """
    加载processed_xinwenlianbo_*.json文件
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 加载的数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date(date_str):
    """
    格式化日期字符串
    
    Args:
        date_str (str): YYYYMMDD格式的日期字符串
        
    Returns:
        str: 格式化后的日期字符串
    """
    return f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"

def generate_summary_content(news_data):
    """
    生成新闻总结内容
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: 生成的HTML内容
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = format_date(date_str)
    
    # 构建带样式的HTML文章
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新闻联播总结 | {formatted_date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .article-container {{
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 15px;
            font-size: 24px;
        }}
        .summary {{
            background-color: #e3f2fd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
            padding-bottom: 5px;
            border-bottom: 1px dashed #bdc3c7;
        }}
        h3 {{
            color: #34495e;
            margin-top: 20px;
        }}
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        .keywords {{
            background-color: #f1f8e9;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
        }}
        hr {{
            border: none;
            height: 1px;
            background-color: #ecf0f1;
            margin: 30px 0;
        }}
        .editor-note {{
            background-color: #fff8e1;
            border-left: 4px solid #f39c12;
            padding: 15px;
            border-radius: 0 5px 5px 0;
        }}
        .date {{
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .stats {{
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <h1>新闻联播总结 | {formatted_date}</h1>
        <div class="date">{formatted_date}</div>
        
        <div class="summary">
            <p><strong>今日总结：</strong>{formatted_date}新闻联播主要内容总结</p>
        </div>
        
        <div class="stats">
            <p><strong>统计信息：</strong></p>
            <p>国内新闻条目: {len(news_data.get('domestic', []))} 条</p>
            <p>国际新闻条目: {len(news_data.get('international', []))} 条</p>
        </div>
"""

    # 添加国内新闻
    domestic_news = news_data.get('domestic', [])
    if domestic_news:
        html_content += "        <h2>【国内要闻】</h2>\n"
        for i, item in enumerate(domestic_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            # 完整显示原始标题，不做截断处理（按用户需求）
            # 完整显示原始标题，不做截断处理（按用户需求）
            html_content += f"        <h3>{i}. {title}</h3>\n"
            html_content += f"        <p>{summary_text}</p>\n"
            if keywords and any(keywords):
                html_content += f"        <div class=\"keywords\"><strong>关键词：</strong>{'、'.join(keywords)}</div>\n"
            html_content += "\n"
    
    # 添加国际新闻
    international_news = news_data.get('international', [])
    if international_news:
        html_content += "        <h2>【国际动态】</h2>\n"
        for i, item in enumerate(international_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            html_content += f"        <h3>{i}. {title}</h3>\n"
            html_content += f"        <p>{summary_text}</p>\n"
            if keywords and any(keywords):
                html_content += f"        <div class=\"keywords\"><strong>关键词：</strong>{'、'.join(keywords)}</div>\n"
            html_content += "\n"
    
    html_content += """
        <hr>
        <div class="editor-note">
            <p><strong>编辑总结：</strong>以上是今日新闻联播的主要内容总结。通过对重要新闻的梳理，我们可以看到国内外在政治、经济、社会等多个领域的重要动态。建议持续关注相关政策动向，以获取更深入的解读。</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def find_latest_processed_file():
    """
    查找最新的processed_xinwenlianbo_*.json文件
    
    Returns:
        str: 最新文件路径，如果未找到则返回None
    """
    # 搜索路径模式
    search_patterns = [
        "processed_xinwenlianbo_*.json",
        "datas/processed_xinwenlianbo_*.json",
        "../datas/processed_xinwenlianbo_*.json",
        "../../datas/processed_xinwenlianbo_*.json"
    ]
    
    processed_files = []
    for pattern in search_patterns:
        processed_files.extend(glob.glob(pattern))
    
    if not processed_files:
        return None
    
    # 返回最新的文件
    return sorted(processed_files)[-1]

def main():
    """
    主函数：生成新闻总结文章
    """
    # 查找最新的processed_xinwenlianbo文件
    latest_file = find_latest_processed_file()
    
    if not latest_file:
        print("未找到processed_xinwenlianbo_*.json文件")
        print("请确保在项目根目录运行此脚本，或确保已生成processed_xinwenlianbo_*.json文件")
        return
    
    print(f"处理文件: {latest_file}")
    
    try:
        # 加载数据
        news_data = load_processed_data(latest_file)
        
        # 生成文章内容
        print("正在生成总结文章...")
        content = generate_summary_content(news_data)
        
        # 创建输出目录
        output_dir = "wechat_articles"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存结果
        date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
        output_file = os.path.join(output_dir, f"news_summary_{date_str}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"文章已保存到: {output_file}")
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
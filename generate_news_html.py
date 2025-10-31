#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将新闻数据JSON文件转换为HTML格式，适用于微信公众号发布
"""

import json
import os
from datetime import datetime


def load_latest_json():
    """
    加载最新的full_result_*.json文件
    """
    datas_dir = "datas"
    json_files = [f for f in os.listdir(datas_dir) if f.startswith("full_result_") and f.endswith(".json")]
    
    if not json_files:
        raise FileNotFoundError("在datas目录中未找到任何full_result_*.json文件")
    
    # 按文件名排序，获取最新的文件
    json_files.sort(reverse=True)
    latest_file = json_files[0]
    
    file_path = os.path.join(datas_dir, latest_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"已加载文件: {latest_file}")
    return data


def generate_html(news_data):
    """
    根据新闻数据生成HTML内容，适用于微信公众号
    """
    date_str = news_data['date']
    # 将日期格式化为更友好的形式
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        formatted_date = date_obj.strftime("%Y年%m月%d日")
    except ValueError:
        formatted_date = date_str

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新闻联播摘要 - {formatted_date}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }}
        .date {{
            color: #666;
            font-size: 16px;
        }}
        .news-section {{
            background-color: #fff;
            margin-bottom: 25px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #d43c33;
            border-bottom: 2px solid #d43c33;
            padding-bottom: 10px;
            margin-top: 0;
            font-size: 20px;
        }}
        .news-item {{
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px dashed #eee;
        }}
        .news-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        .news-title {{
            color: #333;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 18px;
            font-weight: bold;
        }}
        .summary {{
            background-color: #f8f8f8;
            padding: 15px;
            border-left: 4px solid #d43c33;
            margin: 15px 0;
        }}
        .keywords {{
            color: #7f8c8d;
            font-size: 14px;
            margin: 10px 0;
        }}
        .keywords span {{
            background-color: #ecf0f1;
            padding: 3px 8px;
            border-radius: 12px;
            margin-right: 5px;
            display: inline-block;
            margin-bottom: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>新闻联播摘要</h1>
        <div class="date">{formatted_date}</div>
    </div>

    <div class="news-section">
        <h2>国内要闻</h2>
"""

    # 添加国内新闻
    domestic_news = [item for item in news_data['domestic'] if item.get('summary', {}).get('category') != 'international']
    for i, item in enumerate(domestic_news, 1):
        summary = item.get('summary', {})
        
        html_content += f"""
        <div class="news-item">
            <h3 class="news-title">{i}. {summary.get('title', '无标题')}</h3>
            <div class="summary">
                <p>{summary.get('summary', '无摘要')}</p>
            </div>
"""
        
        # 添加关键词
        keywords = summary.get('keywords', [])
        if keywords:
            html_content += f"""
            <div class="keywords">
"""
            for keyword in keywords:
                html_content += f"                <span>{keyword}</span>\n"
            html_content += "            </div>\n"
        
        html_content += "        </div>\n"

    html_content += """
    </div>

    <div class="news-section">
        <h2>国际动态</h2>
"""

    # 添加国际新闻（包括分类错误的）
    international_news = news_data['international'] + [item for item in news_data['domestic'] if item.get('summary', {}).get('category') == 'international']
    for i, item in enumerate(international_news, 1):
        summary = item.get('summary', {})
        
        html_content += f"""
        <div class="news-item">
            <h3 class="news-title">{i}. {summary.get('title', '无标题')}</h3>
            <div class="summary">
                <p>{summary.get('summary', '无摘要')}</p>
            </div>
"""
        
        # 添加关键词
        keywords = summary.get('keywords', [])
        if keywords:
            html_content += f"""
            <div class="keywords">
"""
            for keyword in keywords:
                html_content += f"                <span>{keyword}</span>\n"
            html_content += "            </div>\n"
        
        html_content += "        </div>\n"

    html_content += """
    </div>

    <div class="footer">
        <p>© 2025 新闻联播摘要 | 数据来源：央视新闻</p>
    </div>
</body>
</html>
"""
    
    return html_content


def save_html(html_content, date_str):
    """
    保存HTML内容到文件，按照规范应保存到datas目录
    """
    # 确保输出目录存在
    output_dir = "datas"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"news_summary_{date_str}.html"
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML文件已保存到: {file_path}")
    return file_path


def main():
    """
    主函数
    """
    try:
        # 加载最新的JSON数据
        news_data = load_latest_json()
        
        # 生成HTML内容
        html_content = generate_html(news_data)
        
        # 保存HTML文件
        date_str = news_data['date']
        file_path = save_html(html_content, date_str)
        
        print(f"成功生成新闻摘要HTML文件: {file_path}")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")


if __name__ == "__main__":
    main()
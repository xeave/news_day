#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号HTML生成器
将full_result_*.json文件内容转换为适合微信公众号发布的HTML格式
"""

import os
import sys
import json
import glob
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_latest_data():
    """
    加载最新的full_result_*.json文件
    
    Returns:
        dict: 加载的数据
    """
    # 搜索路径模式
    search_patterns = [
        "full_result_*.json",
        "datas/full_result_*.json",
        "../datas/full_result_*.json",
        "../../datas/full_result_*.json"
    ]
    
    data_files = []
    for pattern in search_patterns:
        data_files.extend(glob.glob(pattern))
    
    if not data_files:
        raise FileNotFoundError("未找到full_result_*.json文件")
    
    # 返回最新的文件
    latest_file = sorted(data_files)[-1]
    print(f"处理文件: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
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

def generate_wechat_html(news_data):
    """
    生成适合微信公众号的HTML内容
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: 生成的HTML内容
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = format_date(date_str)
    
    # 构建HTML内容
    html_content = f'''<section style="background-color: #fff; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px; color: #333;">
  <section style="text-align: center; margin-bottom: 20px;">
    <h1 style="font-size: 24px; color: #2c3e50; margin: 0 0 10px 0; font-weight: bold;">新闻联播 | {formatted_date}</h1>
    <p style="font-size: 14px; color: #7f8c8d; margin: 0;">每日要闻速览</p>
  </section>

  <section style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
    <p style="margin: 0 0 5px 0; font-weight: bold;"><strong>统计信息：</strong></p>
    <p style="margin: 0;">国内新闻条目: {len(news_data.get('domestic', []))} 条</p>
    <p style="margin: 0;">国际新闻条目: {len(news_data.get('international', []))} 条</p>
  </section>

  <section>
'''

    # 添加国内新闻
    domestic_news = news_data.get('domestic', [])
    if domestic_news:
        html_content += '    <h2 style="font-size: 20px; color: #2980b9; margin: 20px 0 15px 0; padding-bottom: 8px; border-bottom: 1px dashed #bdc3c7;">【国内要闻】</h2>\n'
        for i, item in enumerate(domestic_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i}')
            summary_text = summary.get('summary', '')
            
            html_content += f'''    <section style="margin-bottom: 15px; padding: 12px; background-color: #fafafa; border-radius: 6px;">
      <h3 style="font-size: 17px; color: #34495e; margin: 0 0 10px 0;">{i}. {title}</h3>
      <p style="margin: 0; line-height: 1.6; text-align: justify;">{summary_text}</p>
    </section>
'''

    # 添加国际新闻
    international_news = news_data.get('international', [])
    if international_news:
        html_content += '    <h2 style="font-size: 20px; color: #2980b9; margin: 20px 0 15px 0; padding-bottom: 8px; border-bottom: 1px dashed #bdc3c7;">【国际动态】</h2>\n'
        for i, item in enumerate(international_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i}')
            summary_text = summary.get('summary', '')
            
            html_content += f'''    <section style="margin-bottom: 15px; padding: 12px; background-color: #fafafa; border-radius: 6px;">
      <h3 style="font-size: 17px; color: #34495e; margin: 0 0 10px 0;">{i}. {title}</h3>
      <p style="margin: 0; line-height: 1.6; text-align: justify;">{summary_text}</p>
    </section>
'''

    html_content += '''  </section>

  <section style="margin-top: 20px; padding: 12px; background-color: #fff8e1; border-left: 4px solid #f39c12; border-radius: 0 6px 6px 0;">
    <p style="margin: 0; font-weight: bold;"><strong>编辑说明：</strong></p>
    <p style="margin: 5px 0 0 0; line-height: 1.5;">以上是今日新闻联播的主要内容总结。通过对重要新闻的梳理，我们可以看到国内外在政治、经济、社会等多个领域的重要动态。所有内容均来自原始数据文件，包含大模型自动生成的摘要信息。</p>
  </section>
</section>'''
    
    return html_content

def main():
    """
    主函数：生成微信公众号HTML文章
    """
    try:
        # 加载数据
        news_data = load_latest_data()
        
        # 生成文章内容
        print("正在生成微信公众号文章...")
        content = generate_wechat_html(news_data)
        
        # 创建输出目录
        output_dir = "wechat_articles"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存结果
        date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
        output_file = os.path.join(output_dir, f"wechat_news_{date_str}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"文章已保存到: {output_file}")
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号文章生成器
将full_result_*.json文件内容转换为符合微信公众号调性的深度解读文章
"""

import os
import sys
import json
import requests
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_full_result(file_path):
    """
    加载full_result_*.json文件
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 加载的数据
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_ollama_connection():
    """
    检查Ollama服务是否可用
    
    Returns:
        bool: 是否可用
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_wechat_article_with_llm(news_data):
    """
    使用大模型生成符合微信公众号调性的深度文章
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: 生成的文章内容
    """
    # 检查Ollama服务
    if not check_ollama_connection():
        print("Ollama服务不可用，使用默认格式化方法")
        return generate_wechat_article_default(news_data)
    
    # 提取关键信息
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    
    # 准备新闻内容
    all_news = []
    all_news.extend(news_data.get('domestic', []))
    all_news.extend(news_data.get('international', []))
    
    # 构建输入给大模型的提示
    news_texts = []
    for i, item in enumerate(all_news):
        summary = item.get('summary', {})
        text = item.get('text', '')
        title = summary.get('title', f'新闻{i+1}')
        summary_text = summary.get('summary', '')
        keywords = summary.get('keywords', [])
        
        news_texts.append(f"新闻标题：{title}\n"
                         f"新闻摘要：{summary_text}\n"
                         f"关键词：{', '.join(keywords)}\n"
                         f"详细内容：{text[:500]}...\n")
    
    news_content = "\n".join(news_texts)
    
    # 构建提示词
    prompt = f"""你是一位资深的新闻评论员和微信公众号编辑，擅长将新闻联播内容转化为深度解读文章。
请根据以下{formatted_date}的新闻联播内容，撰写一篇符合微信公众号调性的深度解读文章。

要求：
1. 文章标题应具有吸引力，能引起读者兴趣
2. 开头要有引导语，简要介绍当天新闻要点
3. 对重要新闻进行深度解读，分析其背后的意义
4. 文章结构清晰，段落分明，便于手机阅读
5. 语言风格权威但不失亲和力
6. 适当使用小标题分隔不同主题内容
7. 文末可添加简短的总结或展望

新闻内容：
{news_content}

请直接输出完整的文章内容，不需要额外说明。
"""
    
    # 调用Ollama API
    payload = {
        "model": "qwen2:7b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json()
        return result['response']
    except Exception as e:
        print(f"调用大模型失败: {e}")
        return generate_wechat_article_default(news_data)

def generate_wechat_article_default(news_data):
    """
    默认方法生成微信公众号文章（不使用大模型）
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: 生成的文章内容
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    
    # 构建文章
    article = f"<h1>新闻联播深度解读 | {formatted_date}</h1>\n"
    article += f"<p><strong>今日重点关注：</strong>{formatted_date}新闻联播主要内容梳理与深度解读</p>\n"
    article += "<hr>\n\n"
    
    # 添加国内新闻
    domestic_news = news_data.get('domestic', [])
    if domestic_news:
        article += "<h2>【国内要闻】</h2>\n"
        for i, item in enumerate(domestic_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            article += f"<h3>{i}. {title}</h3>\n"
            article += f"<p>{summary_text}</p>\n"
            if keywords:
                article += f"<p><strong>关键词：</strong>{'、'.join(keywords)}</p>\n"
            article += "\n"
    
    # 添加国际新闻
    international_news = news_data.get('international', [])
    if international_news:
        article += "<h2>【国际动态】</h2>\n"
        for i, item in enumerate(international_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            article += f"<h3>{i}. {title}</h3>\n"
            article += f"<p>{summary_text}</p>\n"
            if keywords:
                article += f"<p><strong>关键词：</strong>{'、'.join(keywords)}</p>\n"
            article += "\n"
    
    article += "<hr>\n"
    article += "<p><strong>编辑点评：</strong>以上是今日新闻联播的主要内容梳理。随着国家发展进入新阶段，各项政策举措持续发力，经济社会发展呈现良好态势。我们将持续关注相关政策动向，为您带来更深入的解读。</p>\n"
    
    return article

def format_article_title(news_data):
    """
    格式化文章标题
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        str: 文章标题
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    
    # 尝试从重要新闻中提取标题关键词
    all_news = []
    all_news.extend(news_data.get('domestic', []))
    all_news.extend(news_data.get('international', []))
    
    if all_news:
        # 使用第一条新闻的标题作为参考
        first_news_summary = all_news[0].get('summary', {})
        main_topic = first_news_summary.get('title', '重要资讯')
        return f"【深度解读】{formatted_date}新闻联播：{main_topic}"
    else:
        return f"【深度解读】{formatted_date}新闻联播摘要"

def main():
    """
    主函数：生成微信公众号文章
    """
    # 默认处理最新的full_result文件
    import glob
    full_result_files = glob.glob("full_result_*.json")
    
    if not full_result_files:
        print("未找到full_result_*.json文件")
        return
    
    # 选择最新的文件
    latest_file = sorted(full_result_files)[-1]
    print(f"处理文件: {latest_file}")
    
    try:
        # 加载数据
        news_data = load_full_result(latest_file)
        
        # 生成文章标题
        title = format_article_title(news_data)
        print(f"文章标题: {title}")
        
        # 生成文章内容
        print("正在生成文章内容...")
        content = generate_wechat_article_with_llm(news_data)
        
        # 保存结果
        output_file = f"wechat_article_{news_data['date']}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"<h1>{title}</h1>\n")
            f.write(content)
        
        print(f"文章已保存到: {output_file}")
        print("\n文章预览（前500字符）:")
        print(content[:500] + "..." if len(content) > 500 else content)
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
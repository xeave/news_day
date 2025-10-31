#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号文章生成器 (版本2)
根据项目设计要求生成符合微信公众号调性的文章
参考: 项目设计.md 中的微信公众号内容方向要求
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
    使用大模型生成符合项目设计要求的微信公众号文章
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        tuple: (title, content) 文章标题和内容
    """
    # 检查Ollama服务
    if not check_ollama_connection():
        print("Ollama服务不可用，使用默认格式化方法")
        return generate_wechat_article_default(news_data)
    
    # 提取关键信息
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    
    # 准备新闻内容
    domestic_news = news_data.get('domestic', [])
    international_news = news_data.get('international', [])
    
    # 构建输入给大模型的提示
    news_texts = []
    
    if domestic_news:
        news_texts.append("【国内要闻】")
        for i, item in enumerate(domestic_news):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i+1}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            text_content = item.get('text', '')
            
            news_texts.append(f"{i+1}. {title}")
            news_texts.append(f"   摘要: {summary_text}")
            news_texts.append(f"   详细内容: {text_content[:300]}...")
            if keywords:
                news_texts.append(f"   关键词: {', '.join(keywords)}")
            news_texts.append("")
    
    if international_news:
        news_texts.append("【国际动态】")
        for i, item in enumerate(international_news):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i+1}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            text_content = item.get('text', '')
            
            news_texts.append(f"{i+1}. {title}")
            news_texts.append(f"   摘要: {summary_text}")
            news_texts.append(f"   详细内容: {text_content[:300]}...")
            if keywords:
                news_texts.append(f"   关键词: {', '.join(keywords)}")
            news_texts.append("")
    
    news_content = "\n".join(news_texts)
    
    # 构建提示词
    prompt = f"""你是一位资深的新闻编辑和微信公众号运营专家，请根据以下{formatted_date}的新闻联播内容，撰写一篇符合微信公众号调性的文章。

要求严格按照以下结构生成文章：

1. 文章标题应具有吸引力，能引起读者兴趣
2. 开篇引言：用一两段话概括今日新闻联播的总体基调与核心看点
3. 结构化呈现：将新闻清晰地分为"国内要闻"和"国际动态"两大部分
4. 条目化解读：对每一条重要新闻，进行2-3句话的"小编解读"或"影响分析"
5. 今日总结：在文章末尾，提炼出核心关键词，并展望明日可能关注的焦点
6. 文末可设置互动话题，如"你对哪条新闻最感兴趣？评论区聊聊"
7. 使用HTML格式输出，合理运用标题、加粗、引用等格式
8. 不要包含<!DOCTYPE html>、<html>、<head>、<body>等完整HTML文档结构，只需要内容部分
9. 不要使用<ul>、<ol>、<li>等列表标签，使用<p>标签组织内容

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
        content = result['response']
        
        # 生成标题
        title_prompt = f"""根据以下文章内容，为这篇文章生成一个吸引人的标题：

{content[:1000]}

只需要输出标题，不要其他内容。
"""
        
        title_payload = {
            "model": "qwen2:7b",
            "prompt": title_prompt,
            "stream": False
        }
        
        title_response = requests.post("http://localhost:11434/api/generate", json=title_payload, timeout=120)
        title_result = title_response.json()
        title = title_result['response'].strip().strip('"').strip('《').strip('》')
        
        return title, content
    except Exception as e:
        print(f"调用大模型失败: {e}")
        return generate_wechat_article_default(news_data)

def generate_wechat_article_default(news_data):
    """
    默认方法生成微信公众号文章（不使用大模型）
    
    Args:
        news_data (dict): 新闻数据
        
    Returns:
        tuple: (title, content) 文章标题和内容
    """
    date_str = news_data.get('date', datetime.now().strftime('%Y%m%d'))
    formatted_date = f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    
    # 文章标题
    title = f"【新闻联播每日精读】{formatted_date}：聚焦国内国际要闻"
    
    # 构建文章
    article = f"<h1>新闻联播每日精读 | {formatted_date}</h1>\n"
    article += f"<p><strong>今日重点关注：</strong>{formatted_date}新闻联播主要内容梳理与深度解读</p>\n"
    article += "<hr>\n\n"
    
    # 开篇引言
    article += "<h2>【开篇引言】</h2>\n"
    article += "<p>今日新闻联播内容丰富，重点关注了国内重要活动和国际交流合作。以下为您详细梳理。</p>\n\n"
    
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
            article += f"<p><strong>新闻摘要：</strong>{summary_text}</p>\n"
            article += f"<p><strong>小编解读：</strong>该新闻反映了{'、'.join(keywords) if keywords else '相关政策'}的重要进展，对{'相关领域' if not keywords else '、'.join(keywords)}具有积极意义。</p>\n"
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
            article += f"<p><strong>新闻摘要：</strong>{summary_text}</p>\n"
            article += f"<p><strong>影响分析：</strong>该国际合作{'、'.join(keywords) if keywords else '相关领域'}的发展具有重要推动作用，有助于{'相关领域' if not keywords else '、'.join(keywords)}的进一步深化。</p>\n"
            article += "\n"
    
    # 今日总结
    article += "<h2>【今日总结】</h2>\n"
    all_keywords = []
    for item in domestic_news + international_news:
        summary = item.get('summary', {})
        keywords = summary.get('keywords', [])
        all_keywords.extend(keywords)
    
    unique_keywords = list(set(all_keywords))[:5]  # 最多5个关键词
    if unique_keywords:
        article += f"<p>今日关键词：{'、'.join(unique_keywords)}</p>\n"
    article += "<p>明日我们可能会继续关注相关政策的深入实施和国际合作的进一步发展。</p>\n"
    
    # 互动话题
    article += "<hr>\n"
    article += "<p><strong>互动话题：</strong>你对哪条新闻最感兴趣？评论区聊聊吧！</p>\n"
    
    return title, article

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
        return f"【新闻联播每日精读】{formatted_date}：{main_topic}"
    else:
        return f"【新闻联播每日精读】{formatted_date}：今日要闻"

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
        
        # 生成文章标题和内容
        print("正在生成文章内容...")
        title, content = generate_wechat_article_with_llm(news_data)
        
        # 保存结果
        output_file = f"wechat_article_v2_{news_data['date']}.html"
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
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
    
    # 构建带样式的HTML文章
    article = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新闻联播深度解读 | {formatted_date}</title>
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
    </style>
</head>
<body>
    <div class="article-container">
        <h1>新闻联播深度解读 | {formatted_date}</h1>
        <div class="date">{formatted_date}</div>
        
        <div class="summary">
            <p><strong>今日重点关注：</strong>{formatted_date}新闻联播主要内容梳理与深度解读</p>
        </div>
"""
    
    # 添加国内新闻
    domestic_news = news_data.get('domestic', [])
    if domestic_news:
        article += "        <h2>【国内要闻】</h2>\n"
        for i, item in enumerate(domestic_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国内新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            article += f"        <h3>{i}. {title}</h3>\n"
            article += f"        <p>{summary_text}</p>\n"
            if keywords:
                article += f"        <div class=\"keywords\"><strong>关键词：</strong>{'、'.join(keywords)}</div>\n"
            article += "\n"
    
    # 添加国际新闻
    international_news = news_data.get('international', [])
    if international_news:
        article += "        <h2>【国际动态】</h2>\n"
        for i, item in enumerate(international_news, 1):
            summary = item.get('summary', {})
            title = summary.get('title', f'国际新闻{i}')
            summary_text = summary.get('summary', '')
            keywords = summary.get('keywords', [])
            
            article += f"        <h3>{i}. {title}</h3>\n"
            article += f"        <p>{summary_text}</p>\n"
            if keywords:
                article += f"        <div class=\"keywords\"><strong>关键词：</strong>{'、'.join(keywords)}</div>\n"
            article += "\n"
    
    article += """
        <hr>
        <div class="editor-note">
            <p><strong>编辑点评：</strong>以上是今日新闻联播的主要内容梳理。随着国家发展进入新阶段，各项政策举措持续发力，经济社会发展呈现良好态势。我们将持续关注相关政策动向，为您带来更深入的解读。</p>
        </div>
    </div>
</body>
</html>
"""
    
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
    # 默认处理最新的processed_xinwenlianbo文件
    import glob
    # 修改搜索路径，不仅在当前目录查找，也在项目的datas目录查找
    search_patterns = [
        "processed_xinwenlianbo_*.json",
        "datas/processed_xinwenlianbo_*.json",
        "../datas/processed_xinwenlianbo_*.json",
        "../../datas/processed_xinwenlianbo_*.json"
    ]
    
    full_result_files = []
    for pattern in search_patterns:
        full_result_files.extend(glob.glob(pattern))
    
    if not full_result_files:
        print("未找到processed_xinwenlianbo_*.json文件")
        print("请确保在项目根目录运行此脚本，或确保已生成processed_xinwenlianbo_*.json文件")
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
        
        # 创建输出目录
        import os
        output_dir = "wechat_articles"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存结果
        output_file = os.path.join(output_dir, f"wechat_article_{news_data['date']}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            if content.strip().startswith('<!DOCTYPE html'):
                # 如果是完整的HTML内容，直接写入
                f.write(content)
            else:
                # 否则使用旧格式包装
                f.write(f"<h1>{title}</h1>\n")
                f.write(content)
        
        print(f"文章已保存到: {output_file}")
        print("\n文章预览（前500字符）:")
        print(content[:500] + "..." if len(content) > 500 else content)
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    main()
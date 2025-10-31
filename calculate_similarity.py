#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算 wechat_posts.json 和 full_result_20251023.json 内容的相似度
"""

import json
import re
from difflib import SequenceMatcher


def load_json_file(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_text_content(data):
    """从数据中提取文本内容"""
    texts = []
    
    if isinstance(data, dict):
        # 处理 full_result_20251023.json 格式
        for item in data.get('international', []):
            texts.append(item['text'])
        for item in data.get('domestic', []):
            texts.append(item['text'])
    elif isinstance(data, list):
        # 处理 wechat_posts.json 格式
        for item in data:
            # 从微信文章内容中提取原始新闻文本（去掉摘要和实体信息）
            content = item['content']
            # 移除摘要部分
            content = re.sub(r'【要闻摘要】.*?\n\n', '', content, flags=re.DOTALL)
            # 移除实体信息部分
            content = re.sub(r'\n\n【相关实体】.*', '', content, flags=re.DOTALL)
            # 移除关键词部分
            content = re.sub(r'\n\n【关键词】.*', '', content, flags=re.DOTALL)
            texts.append(content)
    
    return texts


def calculate_similarity(text1, text2):
    """计算两个文本的相似度"""
    return SequenceMatcher(None, text1, text2).ratio()


def main():
    # 加载两个文件
    try:
        wechat_data = load_json_file('wechat_posts.json')
        full_result_data = load_json_file('full_result_20251023.json')
    except Exception as e:
        print(f"加载文件时出错: {e}")
        return
    
    # 提取文本内容
    wechat_texts = extract_text_content(wechat_data)
    full_result_texts = extract_text_content(full_result_data)
    
    if not wechat_texts or not full_result_texts:
        print("未能从文件中提取到文本内容")
        return
    
    # 计算相似度
    # 我们假设两个文件中都只有一条新闻内容
    similarity = calculate_similarity(wechat_texts[0], full_result_texts[0])
    
    print("内容相似度分析:")
    print(f"wechat_posts.json 与 full_result_20251023.json 的文本相似度: {similarity:.2%}")
    print(f"相似度评分: {similarity * 100:.1f}/100")
    
    # 详细分析
    print("\n详细信息:")
    print(f"微信文章内容长度: {len(wechat_texts[0])} 字符")
    print(f"原始数据内容长度: {len(full_result_texts[0])} 字符")
    
    # 检查是否包含相同的关键信息
    keywords = ["中国共产党", "中央委员会", "十五五", "规划", "习近平"]
    common_keywords = []
    for keyword in keywords:
        if keyword in wechat_texts[0] and keyword in full_result_texts[0]:
            common_keywords.append(keyword)
    
    print(f"共同关键词: {', '.join(common_keywords)}")
    
    # 置信度评分说明
    print("\n置信度评分说明:")
    print("相似度评分是基于文本内容的匹配程度计算的，范围为0-100分")
    print("评分标准:")
    print("- 90-100分: 内容几乎完全相同")
    print("- 70-89分: 内容高度相似，可能有格式调整")
    print("- 50-69分: 内容中度相似，有部分内容相同")
    print("- 30-49分: 内容低度相似，只有少量相同内容")
    print("- 0-29分: 内容几乎不相关")
    
    # 保存相似度结果
    result = {
        "similarity_score": round(similarity * 100, 1),
        "wechat_content_length": len(wechat_texts[0]),
        "full_result_content_length": len(full_result_texts[0]),
        "common_keywords": common_keywords
    }
    
    with open('similarity_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n相似度结果已保存到 similarity_result.json")


if __name__ == "__main__":
    main()
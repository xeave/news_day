#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import NewsProcessor

def test_numeric_segmentation():
    """
    测试数字标识分割功能
    """
    processor = NewsProcessor()
    
    # 模拟包含数字标识的新闻内容
    test_content = [
        "1: 国内要闻",
        "今天国内发生多起重要事件。首先，北京举行了重要会议。",
        "会议讨论了经济发展问题。其次，上海自贸区迎来新政策。",
        "2: 国际新闻",
        "国际方面，美国和中国进行了高层对话。",
        "对话涉及贸易和安全等多个议题。此外，欧盟也发表了声明。",
        "3: 体育快讯",
        "在体育方面，中国队在国际比赛中获得佳绩。",
        "4: 天气预报",
        "明天全国天气总体良好，部分地区有降雨。"
    ]
    
    print("原始内容:")
    for i, line in enumerate(test_content):
        print(f"{i+1}: {line}")
    
    print("\n清洗后内容:")
    cleaned = processor.clean_news_content(test_content)
    for i, line in enumerate(cleaned):
        print(f"{i+1}: {line}")
    
    print("\n分割后片段:")
    segments = processor.split_news_segments(cleaned)
    for i, segment in enumerate(segments):
        print(f"{i+1}: {segment}")
        print(f"   (长度: {len(segment)} 字符)\n")

def test_real_news_segmentation():
    """
    测试真实新闻内容的分割效果
    """
    processor = NewsProcessor()
    
    # 模拟真实的新闻联播内容
    real_content = [
        "下面来看国内要闻。",
        "1: 经济发展",
        "前三季度GDP增长符合预期，制造业稳步回升。",
        "2: 民生保障",
        "教育、医疗等公共服务持续改善，就业形势总体稳定。",
        "下面来看国际方面。",
        "1: 中美关系",
        "两国在气候问题上达成新的合作共识。",
        "2: 地区安全",
        "中东地区紧张局势有所缓解，各方呼吁通过对话解决争端。"
    ]
    
    print("=== 真实新闻内容测试 ===")
    print("原始内容:")
    for i, line in enumerate(real_content):
        print(f"{i+1}: {line}")
    
    print("\n清洗后内容:")
    cleaned = processor.clean_news_content(real_content)
    for i, line in enumerate(cleaned):
        print(f"{i+1}: {line}")
    
    print("\n分割后片段:")
    segments = processor.split_news_segments(cleaned)
    for i, segment in enumerate(segments):
        print(f"{i+1}: {segment}")
        print(f"   (长度: {len(segment)} 字符)\n")

if __name__ == "__main__":
    test_numeric_segmentation()
    print("\n" + "="*50 + "\n")
    test_real_news_segmentation()
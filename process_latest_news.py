#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from datetime import datetime

def find_latest_news_file():
    """
    查找最新的新闻JSON文件
    """
    xinwen_dir = "xinwen"
    if not os.path.exists(xinwen_dir):
        print("xinwen目录不存在")
        return None
    
    # 查找所有xinwenlianbo_*.json文件
    json_files = [f for f in os.listdir(xinwen_dir) if f.startswith("xinwenlianbo_") and f.endswith(".json")]
    
    if not json_files:
        print("未找到新闻JSON文件")
        return None
    
    # 按日期排序，获取最新的文件
    json_files.sort(reverse=True)
    latest_file = json_files[0]
    return os.path.join(xinwen_dir, latest_file)

def load_news_data(filepath):
    """
    加载新闻数据
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载新闻数据失败: {e}")
        return None

def classify_news(news_items):
    """
    将新闻分类为国内和国际新闻
    """
    domestic_keywords = [
        '中共中央', '国务院', '全国人大', '全国政协', '总书记', '主席', '总理',
        '十四五', '十五五', '规划', '建议', '党中央', '中央政治局', '思想',
        '全国人大常委会', '中央书记处', '中央军委', '人大常委', '政协', '中央纪委',
        '工信部', '财政部', '人社部', '商务部', '农业农村部', '卫健委'
    ]
    
    international_keywords = [
        '国际', '外交', '合作', '联合国', '峰会', '领导人会议', '大使馆', '领事馆',
        '外交部发言人', '外长', '大使', '领事', '国外', '海外', '境外', '外国',
        '东盟', '欧盟', '非盟', '北约', '世贸组织', '世卫组织', '国际货币基金组织',
        '世界银行', '联合国安理会', 'G20', 'G7', 'APEC', '金砖国家'
    ]
    
    foreign_locations = [
        '美国', '俄罗斯', '日本', '韩国', '英国', '法国', '德国', '意大利',
        '加拿大', '澳大利亚', '巴西', '印度', '埃及', '南非', '墨西哥', '马来西亚',
        '以色列', '加沙', '芬兰'
    ]
    
    domestic_news = []
    international_news = []
    
    for item in news_items:
        content = item.get('content', '')
        is_domestic = any(keyword in content for keyword in domestic_keywords)
        is_international = (
            any(keyword in content for keyword in international_keywords) or
            any(location in content for location in foreign_locations)
        )
        
        # 根据关键词判断分类
        if is_international and not is_domestic:
            international_news.append(item)
        else:
            domestic_news.append(item)
    
    return domestic_news, international_news

def simple_summarize(text):
    """
    简单摘要方法
    """
    # 清洗文本
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    
    # 提取前几句作为摘要
    sentences = re.split(r'[。！？；]', cleaned_text)
    summary = ''.join(sentences[:2])[:100]  # 前两句，最多100字符
    
    # 简单关键词提取
    keywords = []
    keyword_candidates = ['经济', '政治', '国际', '国内', '发展', '建设', '会议', '政策', '合作', '科技']
    for keyword in keyword_candidates:
        if keyword in text:
            keywords.append(keyword)
    
    # 简单分类
    category = "domestic"
    international_keywords = ['国际', '外交', '合作', '美国', '俄罗斯', '日本', '韩国', '欧盟', '联合国']
    for keyword in international_keywords:
        if keyword in text:
            category = "international"
            break
    
    # 标题（取前20个字符）
    title = cleaned_text[:20].strip()
    
    return {
        "title": title,
        "summary": summary,
        "keywords": keywords[:3],  # 最多3个关键词
        "category": category
    }

def simple_ner(text):
    """
    简单命名实体识别
    """
    # 预定义的地名列表
    locations = {
        '北京', '上海', '天津', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
        '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
        '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
        '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门', '美国', '英国',
        '法国', '德国', '日本', '韩国', '俄罗斯', '印度', '巴西', '加拿大'
    }
    
    # 预定义的机构名关键词
    org_keywords = [
        '政府', '党委', '委员会', '部门', '局', '厅', '处', '科', '办公室',
        '公司', '集团', '银行', '大学', '学院', '研究所', '协会', '联合会',
        '党中央', '国务院', '全国人大', '全国政协', '中央军委'
    ]
    
    # 常见职务和称谓
    titles = [
        '主席', '总书记', '总理', '省长', '市长', '县长', '局长', '书记',
        '部长', '主任', '委员', '代表', '委员长', '副主席', '总统', '首相'
    ]
    
    # 地名识别
    found_locations = []
    for loc in locations:
        if loc in text and loc not in found_locations:
            found_locations.append(loc)
    
    # 人名识别（基于职务关键词）
    persons = []
    for title in titles:
        if title in text:
            # 提取关键词前后的内容作为人物提及
            start = max(0, text.find(title) - 10)
            end = min(len(text), text.find(title) + len(title) + 5)
            persons.append(text[start:end])
    
    # 组织名识别
    organizations = []
    for keyword in org_keywords:
        if keyword in text:
            # 提取关键词前后的内容作为组织提及
            start = max(0, text.find(keyword) - 5)
            end = min(len(text), text.find(keyword) + len(keyword) + 10)
            org_mention = text[start:end]
            if org_mention not in organizations:
                organizations.append(org_mention)
    
    return {
        "locations": found_locations[:5],  # 最多5个地点
        "persons": persons[:5],  # 最多5个人物
        "organizations": organizations[:5]  # 最多5个组织
    }

def process_news_item(item):
    """
    处理单个新闻条目
    """
    content = item.get('content', '')
    
    # 实体识别
    entities = simple_ner(content)
    
    # 摘要生成
    summary = simple_summarize(content)
    
    return {
        "text": content,
        "entities": entities,
        "summary": summary
    }

def process_news_data(news_data):
    """
    处理新闻数据
    """
    print(f"处理日期: {news_data['date']}")
    print(f"新闻总数: {news_data['news_count']}")
    
    # 分类新闻
    domestic_news, international_news = classify_news(news_data['news_items'])
    print(f"国内新闻: {len(domestic_news)} 条")
    print(f"国际新闻: {len(international_news)} 条")
    
    # 处理每个新闻条目
    processed_domestic = [process_news_item(item) for item in domestic_news]
    processed_international = [process_news_item(item) for item in international_news]
    
    return {
        'date': news_data['date'],
        'domestic': processed_domestic,
        'international': processed_international
    }

def save_processed_data(processed_data, original_filename):
    """
    保存处理后的数据
    """
    # 生成新文件名
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    new_filename = f"processed_{base_name}.json"
    output_path = os.path.join("datas", new_filename)
    
    # 确保datas目录存在
    os.makedirs("datas", exist_ok=True)
    
    # 保存数据
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"处理后的数据已保存到: {output_path}")
    return output_path

def main():
    """
    主函数
    """
    # 查找最新的新闻文件
    news_file = find_latest_news_file()
    if not news_file:
        print("未找到新闻文件")
        return
    
    print(f"找到最新新闻文件: {news_file}")
    
    # 加载新闻数据
    news_data = load_news_data(news_file)
    if not news_data:
        print("无法加载新闻数据")
        return
    
    # 处理新闻数据
    processed_data = process_news_data(news_data)
    
    # 保存处理后的数据
    output_path = save_processed_data(processed_data, news_file)
    
    # 显示处理结果示例
    print("\n=== 处理结果示例 ===")
    if processed_data['domestic']:
        print("\n国内新闻示例:")
        item = processed_data['domestic'][0]
        print(f"  新闻内容: {item['text'][:100]}...")
        print(f"  实体识别 - 地点: {item['entities']['locations']}")
        print(f"  实体识别 - 人物: {[p.strip() for p in item['entities']['persons'][:2]]}")
        print(f"  实体识别 - 组织: {[o.strip() for o in item['entities']['organizations'][:2]]}")
        print(f"  摘要信息 - 标题: {item['summary']['title']}")
        print(f"  摘要信息 - 摘要: {item['summary']['summary']}")
        print(f"  摘要信息 - 关键词: {item['summary']['keywords']}")
        print(f"  摘要信息 - 分类: {item['summary']['category']}")
    
    if processed_data['international']:
        print("\n国际新闻示例:")
        item = processed_data['international'][0]
        print(f"  新闻内容: {item['text'][:100]}...")
        print(f"  实体识别 - 地点: {item['entities']['locations']}")
        print(f"  实体识别 - 人物: {[p.strip() for p in item['entities']['persons'][:2]]}")
        print(f"  实体识别 - 组织: {[o.strip() for o in item['entities']['organizations'][:2]]}")
        print(f"  摘要信息 - 标题: {item['summary']['title']}")
        print(f"  摘要信息 - 摘要: {item['summary']['summary']}")
        print(f"  摘要信息 - 关键词: {item['summary']['keywords']}")
        print(f"  摘要信息 - 分类: {item['summary']['category']}")

if __name__ == "__main__":
    main()
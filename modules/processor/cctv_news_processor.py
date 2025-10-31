import re
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
from simple_ner import SimpleNER, process_news_with_ner

# 定义 boilerplate 模板（新闻联播固定模式）
BOILERPLATE_PATTERNS = [
    r'^今天是\d{4}年\d{1,2}月\d{1,2}日.*?$',          # 日期串词
    r'^各位观众.*?$',                                  # 开场白
    r'^(广告之后|天气预报|稍后回来|下面请看|感谢收看).*?$',  # 广告/天气
    r'^现在播送.+?简历.*$',                            # 简历播报
    r'^现在为您播送.+?公报.*$',                        # 公报播报
    r'^以下是我们刚刚收到的消息.*$',                  # 消息播报
    r'^接下来关注.+?$',                              # 节目过渡语
    r'^下面来看.+?$',                                # 节目过渡语
    r'^现在是.+?新闻.*$',                            # 新闻播报提示
    r'^\d+时\d+分.*$',                               # 时间播报
    r'^现在时间是.*$',                               # 时间播报
    r'^央视网消息.*$',                               # 新闻来源提示
    r'^据新华社消息.*$',                             # 新闻来源提示
]

# 编译正则表达式
BOILERPLATE_REGEX = [re.compile(p) for p in BOILERPLATE_PATTERNS]

# 定义分割点的正则表达式
SPLIT_RE = re.compile(
    r'(?:接下来|下面|稍后|之后).*?(?:关注|来看|连线|播出)|'
    r'^\s*[一二三四五六七八九十]、'  # 中文序号
)

# 国际新闻起始标识
INTERNATIONAL_START = re.compile(r'^下面.*?国际')

def clean_news_content(raw_content):
    """
    清洗单期新闻联播内容
    """
    # 将所有内容连接并按行分割
    lines = '\n'.join(raw_content).splitlines()
    
    # 移除 boilerplate 内容
    cleaned_lines = []
    for line in lines:
        is_boilerplate = False
        for pattern in BOILERPLATE_REGEX:
            if pattern.match(line):
                is_boilerplate = True
                break
        if not is_boilerplate:
            cleaned_lines.append(line)
    
    return cleaned_lines

def split_news_segments(cleaned_lines):
    """
    将清洗后的新闻内容按逻辑分割成独立的新闻片段
    """
    segments = []
    buffer = []
    
    for line in cleaned_lines:
        buffer.append(line)
        # 检查是否有分割点
        if SPLIT_RE.search(line):
            segments.append(' '.join(buffer))
            buffer = []
    
    # 添加最后一段
    if buffer:
        segments.append(' '.join(buffer))
    
    return segments

def classify_domestic_international(segments):
    """
    将新闻片段分为国内和国际两类
    """
    international_start_index = None
    for i, segment in enumerate(segments):
        if INTERNATIONAL_START.search(segment):
            international_start_index = i
            break
    
    if international_start_index is not None:
        domestic = segments[:international_start_index]
        international = segments[international_start_index:]
    else:
        # 如果没找到国际新闻标识，则根据长度大致分割
        split_point = len(segments) * 3 // 4  # 假设国际新闻约占1/4
        domestic = segments[:split_point]
        international = segments[split_point:]
    
    return domestic, international

def process_one_day(date_str):
    """
    处理单日新闻联播数据
    """
    # 获取原始数据
    try:
        raw_data = ak.news_cctv(date=date_str)
        raw_content = raw_data['content'].tolist()
    except Exception as e:
        print(f"获取 {date_str} 的数据失败: {e}")
        return None
    
    # 步骤1: 清洗内容
    cleaned_lines = clean_news_content(raw_content)
    
    # 步骤2: 分割新闻片段
    segments = split_news_segments(cleaned_lines)
    
    # 步骤3: 分类国内/国际新闻
    domestic, international = classify_domestic_international(segments)
    
    return {
        'date': date_str,
        'domestic': domestic,
        'international': international
    }

def save_to_file(result, filename):
    """
    将结果保存到文件
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 示例：处理单日数据
    result = process_one_day("20251023")
    if result:
        print(f"处理完成，日期：{result['date']}")
        print(f"国内新闻条数：{len(result['domestic'])}")
        print(f"国际新闻条数：{len(result['international'])}")
        
        # 使用NER处理
        ner_result = process_news_with_ner(result)
        
        # 显示前两条国内新闻
        print("\n国内新闻示例：")
        for i, item in enumerate(ner_result['domestic'][:2]):
            print(f"{i+1}. {item['text'][:100]}...")
            print(f"   地点: {item['entities']['locations']}")
            print(f"   人物: {item['entities']['persons']}")
            print(f"   组织: {item['entities']['organizations']}\n")
        
        # 显示前两条国际新闻
        print("国际新闻示例：")
        for i, item in enumerate(ner_result['international'][:2]):
            print(f"{i+1}. {item['text'][:100]}...")
            print(f"   地点: {item['entities']['locations']}")
            print(f"   人物: {item['entities']['persons']}")
            print(f"   组织: {item['entities']['organizations']}\n")
        
        # 保存结果到文件
        save_to_file(ner_result, f"processed_news_ner_{result['date']}.json")
        print(f"\n结果已保存到 processed_news_ner_{result['date']}.json")
    else:
        print("处理失败")
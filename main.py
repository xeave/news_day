#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻联播数据处理全流程系统
整合数据获取、清洗、实体识别、模板提取和摘要生成功能
"""

import json
import re
import argparse
from datetime import datetime, timedelta
import akshare as ak
import requests
import os

# 检查是否可以连接到 Ollama
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    LLM_AVAILABLE = response.status_code == 200
    if LLM_AVAILABLE:
        print("Ollama 服务可用，将使用大模型进行摘要")
    else:
        print("Ollama 服务不可用，将使用简化版摘要功能")
except:
    LLM_AVAILABLE = False
    print("提示: 无法连接到 Ollama，将使用简化版摘要功能")


class NewsProcessor:
    def __init__(self):
        """
        初始化新闻处理器
        """
        # 确保 datas 和 xinwen 目录存在
        os.makedirs("datas", exist_ok=True)
        os.makedirs("xinwen", exist_ok=True)
        
        # 定义 boilerplate 模板（新闻联播固定模式）
        self.boilerplate_patterns = [
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
        self.boilerplate_regex = [re.compile(p) for p in self.boilerplate_patterns]

        # 定义分割点的正则表达式（更全面的新闻分割标识）
        self.split_re = re.compile(
            r'(?:接下来|下面|稍后|之后).*?(?:关注|来看|连线|播出)|'
            r'^\s*[一二三四五六七八九十]、|'  # 中文序号
            r'^(?:明天|今天|据新华社|央视网).*?出版|'  # 出版预告、新闻来源等
            r'^(?:国务院总理|国家副主席|中共中央政治局常委|全国人大常委会).*?出席|'  # 高层活动
            r'^(?:当地时间|北京时间).*?，|'  # 国际新闻时间标识
            r'^\s*[\d\.]+、|'  # 数字序号
            r'^\s*\d+[:：]\s*\d*\s*|'  # 数字标识，如"1: 2:"这样的格式
            r'^(?:以色列|美国|俄罗斯|日本|韩国|英国|法国|德国|意大利|加拿大|澳大利亚|巴西|印度|埃及|南非|墨西哥|马来西亚|加沙|联合国|东盟|欧盟).*?'  # 国际地名和组织开头的新闻
        )

        # 国际新闻起始标识
        self.international_start = re.compile(r'^下面.*?国际')

        # 预定义地名列表
        self.location_keywords = [
            '北京', '上海', '天津', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏',
            '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
            '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙古', '广西', '西藏',
            '宁夏', '新疆', '香港', '澳门', '美国', '俄罗斯', '日本', '韩国', '英国', '法国',
            '德国', '意大利', '加拿大', '澳大利亚', '巴西', '印度', '埃及', '南非', '墨西哥',
            '马来西亚', '芬兰', '加沙', '以色列'
        ]
        
        # 预定义组织名关键词
        self.org_keywords = [
            '政府', '党委', '委员会', '公司', '协会', '大学', '研究所', '银行', '集团', '组织',
            '中央委员会', '中央政治局', '国务院', '全国人大', '全国政协', '国防部', '外交部',
            '发改委', '教育部', '科技部', '工信部', '财政部', '人社部', '商务部', '农业农村部',
            '卫健委', '人民银行', '国资委', '税务总局', '市场监管总局', '证监会', '银保监会',
            '联合国', '东盟', '欧盟', '非盟', '北约', '世贸组织', '世卫组织'
        ]
        
        # 国内重要关键词（用于辅助判断国内新闻）
        self.domestic_keywords = [
            '中共中央', '国务院', '全国人大', '全国政协', '总书记', '主席', '总理', 
            '十四五', '十五五', '规划', '建议', '党中央', '中央政治局', '思想',
            '全国人大常委会', '中央书记处', '中央军委', '人大常委', '政协', '中央纪委'
        ]
        
        # 国际新闻关键词
        self.international_keywords = [
            '国际', '外交', '合作', '联合国', '峰会', '领导人会议', '大使馆', '领事馆',
            '外交部发言人', '外长', '大使', '领事', '国外', '海外', '境外', '外国',
            '东盟', '欧盟', '非盟', '北约', '世贸组织', '世卫组织', '国际货币基金组织',
            '世界银行', '联合国安理会', 'G20', 'G7', 'APEC', '金砖国家', '峰会', '会见'
        ]
        
        # 国内重要人物和职位关键词
        self.domestic_person_keywords = [
            '总书记', '主席', '总理', '委员长', '部长', '省长', '市长', '书记', '代表', '委员',
            '中央政治局', '国务院', '全国人大', '全国政协'
        ]
        
        # 国际重要人物和职位关键词
        self.international_person_keywords = [
            '总统', '首相', '总理', '外长', '大使', '联合国秘书长', '欧盟', '北约', '世卫组织'
        ]

    def fetch_news(self, date_str):
        """
        获取指定日期的新闻联播数据
        """
        try:
            print(f"正在获取 {date_str} 的新闻数据...")
            raw_data = ak.news_cctv(date=date_str)
            print(f"获取到 {len(raw_data)} 条数据")
            if len(raw_data) == 0:
                print(f"警告: {date_str} 没有可用的新闻数据")
                # 尝试前一天的数据
                prev_date = (datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
                print(f"尝试获取前一天 {prev_date} 的数据...")
                raw_data = ak.news_cctv(date=prev_date)
                print(f"获取到 {len(raw_data)} 条数据")
                if len(raw_data) == 0:
                    print(f"警告: {prev_date} 也没有可用的新闻数据")
                    return None
                else:
                    print(f"使用 {prev_date} 的数据")
                    return raw_data['content'].tolist()
            return raw_data['content'].tolist()
        except Exception as e:
            print(f"获取 {date_str} 的数据失败: {e}")
            return None

    def clean_news_content(self, raw_content):
        """
        清洗单期新闻联播内容
        """
        # 将所有内容连接并按行分割
        lines = '\n'.join(raw_content).splitlines()
        
        # 移除 boilerplate 内容
        cleaned_lines = []
        for line in lines:
            is_boilerplate = False
            for pattern in self.boilerplate_regex:
                if pattern.match(line):
                    is_boilerplate = True
                    break
            if not is_boilerplate:
                cleaned_lines.append(line)
        
        return cleaned_lines

    def split_news_segments(self, cleaned_lines):
        """
        将清洗后的新闻内容按逻辑分割成独立的新闻片段
        """
        # 先按现有逻辑进行分割
        segments = []
        buffer = []
        
        for line in cleaned_lines:
            # 检查是否有分割点
            if self.split_re.search(line) and buffer:
                # 如果缓冲区有内容，先保存之前的段落
                segments.append(' '.join(buffer))
                buffer = []
            
            buffer.append(line)
        
        # 添加最后一段
        if buffer:
            segments.append(' '.join(buffer))
        
        # 对分割后的片段进一步处理，专门处理数字标识内容
        refined_segments = []
        for segment in segments:
            # 将包含数字标识的内容进一步拆分
            sub_segments = self._split_by_numeric_markers(segment)
            refined_segments.extend(sub_segments)
        
        return refined_segments

    def _split_by_numeric_markers(self, text):
        """
        根据数字标识（如"1: 2:"）将文本进一步分割
        """
        # 匹配数字标识的正则表达式（包括中文数字）
        pattern = r'(?:(?:[一二三四五六七八九十]+|[1-9]\d*)[:：]\s*)'
        matches = list(re.finditer(pattern, text))
        
        # 如果没有找到数字标识，直接返回原文本
        if not matches:
            return [text]
        
        # 分割文本
        sub_segments = []
        last_end = 0
        
        for match in matches:
            # 添加标识前的内容（如果有）
            if match.start() > last_end:
                prev_text = text[last_end:match.start()].strip()
                if prev_text:
                    sub_segments.append(prev_text)
            
            # 添加标识后的内容直到下一个标识或文本结束
            marker = match.group(0)
            marker_end = match.end()
            
            # 查找下一个标识的位置
            next_start = len(text)
            for next_match in matches:
                if next_match.start() > match.end():
                    next_start = next_match.start()
                    break
            
            # 提取从当前标识到下一个标识之间的内容
            segment_content = text[marker_end:next_start].strip()
            if segment_content:
                sub_segments.append(marker + segment_content)
            else:
                sub_segments.append(marker)
            
            last_end = next_start
        
        # 添加剩余内容（如果有）
        if last_end < len(text):
            remaining_text = text[last_end:].strip()
            if remaining_text:
                # 如果最后一个片段是数字标识，则与其合并
                if re.match(r'^(?:[一二三四五六七八九十]+|[1-9]\d*)[:：]\s*$', sub_segments[-1]):
                    sub_segments[-1] = sub_segments[-1] + remaining_text
                else:
                    sub_segments.append(remaining_text)
        
        # 过滤掉空片段
        sub_segments = [seg for seg in sub_segments if seg.strip()]
        
        return sub_segments if sub_segments else [text]

    def classify_domestic_international(self, segments):
        """
        将新闻片段分为国内和国际两类
        优化分类逻辑：
        1. 首先查找明确的国际新闻标识
        2. 如果没有找到，则根据内容特征进行分类
        3. 对于长文本，检查是否包含国内重要关键词
        """
        international_start_index = None
        for i, segment in enumerate(segments):
            if self.international_start.search(segment):
                international_start_index = i
                break
        
        if international_start_index is not None:
            domestic = segments[:international_start_index]
            international = segments[international_start_index:]
        else:
            # 如果没找到国际新闻标识，则根据内容特征分类
            domestic = []
            international = []
            
            for segment in segments:
                # 检查是否明显属于国际新闻
                is_international = self._is_international_news(segment)
                
                # 检查是否明显属于国内新闻
                is_domestic = self._is_domestic_news(segment)
                
                # 根据判断结果分类
                if is_international and not is_domestic:
                    international.append(segment)
                elif is_domestic and not is_international:
                    domestic.append(segment)
                elif is_international and is_domestic:
                    # 如果同时包含国内外特征，根据主要特征判断
                    # 优先考虑国际特征（因为国内新闻通常不会包含国外地名）
                    if self._has_foreign_locations(segment):
                        international.append(segment)
                    else:
                        domestic.append(segment)
                else:
                    # 如果都没有明显特征，默认归为国内
                    domestic.append(segment)
        
        return domestic, international

    def _is_international_news(self, text):
        """
        判断文本是否属于国际新闻
        """
        # 检查是否包含国际关键词
        for keyword in self.international_keywords:
            if keyword in text:
                return True
                
        # 检查是否包含国际人物或职位关键词
        for keyword in self.international_person_keywords:
            if keyword in text:
                return True
                
        # 检查是否包含国际活动标识
        international_indicators = ['当地时间', ' foreign ', ' international ']
        for indicator in international_indicators:
            if indicator in text:
                return True
                
        # 检查是否包含较多国外地名
        foreign_location_count = 0
        for loc in ['美国', '俄罗斯', '日本', '韩国', '英国', '法国', '德国', '意大利', 
                   '加拿大', '澳大利亚', '巴西', '印度', '埃及', '南非', '墨西哥', '马来西亚',
                   '以色列', '加沙', '联合国', '东盟', '欧盟', '芬兰']:
            if loc in text:
                foreign_location_count += 1
                
        # 如果包含多个国外地名，更可能是国际新闻
        if foreign_location_count >= 2:
            return True
            
        return False

    def _is_domestic_news(self, text):
        """
        判断文本是否属于国内新闻
        """
        # 检查是否包含国内关键词
        for keyword in self.domestic_keywords:
            if keyword in text:
                return True
                
        # 检查是否包含国内人物或职位关键词
        for keyword in self.domestic_person_keywords:
            if keyword in text:
                return True
                
        return False

    def _has_foreign_locations(self, text):
        """
        检查文本是否包含国外地名
        """
        foreign_locations = ['美国', '俄罗斯', '日本', '韩国', '英国', '法国', '德国', '意大利', 
                            '加拿大', '澳大利亚', '巴西', '印度', '埃及', '南非', '墨西哥', '马来西亚',
                            '以色列', '加沙', '联合国', '东盟', '欧盟', '芬兰']
        for loc in foreign_locations:
            if loc in text:
                return True
        return False

    def simple_ner(self, text):
        """
        简单命名实体识别
        """
        # 地名识别
        locations = []
        for loc in self.location_keywords:
            if loc in text and loc not in locations:
                locations.append(loc)
        
        # 人名识别（基于职务关键词）
        persons = []
        person_keywords = ['总书记', '主席', '总理', '委员长', '部长', '省长', '市长', '书记', '代表', '委员', '总统', '首相']
        
        for keyword in person_keywords:
            if keyword in text:
                # 提取关键词前后的内容作为人物提及
                start = max(0, text.find(keyword) - 10)
                end = min(len(text), text.find(keyword) + len(keyword) + 5)
                persons.append(text[start:end])
        
        # 组织名识别
        organizations = []
        for keyword in self.org_keywords:
            if keyword in text:
                # 提取关键词前后的内容作为组织提及
                start = max(0, text.find(keyword) - 5)
                end = min(len(text), text.find(keyword) + len(keyword) + 10)
                org_mention = text[start:end]
                if org_mention not in organizations:
                    organizations.append(org_mention)
        
        return {
            "locations": locations,
            "persons": persons,
            "organizations": organizations
        }

    def simple_summarize(self, text):
        """
        简单摘要方法
        """
        # 清洗文本
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        
        # 提取前几句作为摘要
        sentences = re.split(r'[。！？；]', cleaned_text)
        summary = ''.join(sentences[:2])[:120]  # 前两句，最多120字符
        
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

    def llm_summarize(self, text):
        """
        使用 Ollama 进行摘要
        """
        if not LLM_AVAILABLE:
            return self.simple_summarize(text)
        prompt = f"""你是一名央视新闻联播的资深编辑，任务是对下面这段新闻进行「分类 + 摘要 + 关键词」抽取。
输出必须是一段 **合法 JSON**，格式如下（不要添加任何代码块标记）：
{{
  "title": "10字以内",
  "summary": "50字以内",
  "keywords": ["kw1","kw2","kw3"],
  "category": "domestic" 或 "international"
}}
新闻原文：
{text}
"""
        
        payload = {
            "model": "qwen2:7b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
            result = response.json()
            return json.loads(result['response'])
        except Exception as e:
            print(f"Ollama 摘要失败: {e}")
            return self.simple_summarize(text)

    def process_one_day(self, date_str):
        """
        处理单日新闻联播数据
        """
        # 步骤1: 获取原始数据
        print("步骤1: 获取原始数据")
        raw_content = self.fetch_news(date_str)
        if not raw_content:
            print("获取原始数据失败")
            return None
        
        print(f"获取到 {len(raw_content)} 行原始内容")
        
        # 打印原始数据
        print("\n=== 原始数据 ===")
        for i, line in enumerate(raw_content):
            print(f"{i+1}: {line}")
        print("=== 原始数据结束 ===\n")
        
        # 步骤2: 清洗内容
        print("步骤2: 清洗内容")
        cleaned_lines = self.clean_news_content(raw_content)
        print(f"清洗后剩余 {len(cleaned_lines)} 行")
        
        # 步骤3: 分割新闻片段
        print("步骤3: 分割新闻片段")
        segments = self.split_news_segments(cleaned_lines)
        print(f"分割成 {len(segments)} 个片段")
        
        # 打印分割后的片段
        print("\n=== 分割后的新闻片段 ===")
        for i, segment in enumerate(segments):
            print(f"{i+1}: {segment[:100]}...")
        print("=== 分割片段结束 ===\n")
        
        # 步骤4: 分类国内/国际新闻
        print("步骤4: 分类国内/国际新闻")
        domestic, international = self.classify_domestic_international(segments)
        print(f"国内新闻: {len(domestic)} 条, 国际新闻: {len(international)} 条")
        
        # 步骤5: 对每条新闻进行处理
        print("步骤5: 处理每条新闻")
        processed_domestic = []
        for i, item in enumerate(domestic):
            print(f"  处理国内新闻 {i+1}/{len(domestic)}")
            # 根据是否可用大模型选择摘要方法
            if LLM_AVAILABLE:
                summary = self.llm_summarize(item)
                summary_method = "大模型"
            else:
                summary = self.simple_summarize(item)
                summary_method = "简单程序"
                
            processed_domestic.append({
                "text": item,
                "entities": self.simple_ner(item),
                "summary": summary,
                "summary_method": summary_method  # 添加摘要方法信息
            })
        
        processed_international = []
        for i, item in enumerate(international):
            print(f"  处理国际新闻 {i+1}/{len(international)}")
            # 根据是否可用大模型选择摘要方法
            if LLM_AVAILABLE:
                summary = self.llm_summarize(item)
                summary_method = "大模型"
            else:
                summary = self.simple_summarize(item)
                summary_method = "简单程序"
                
            processed_international.append({
                "text": item,
                "entities": self.simple_ner(item),
                "summary": summary,
                "summary_method": summary_method  # 添加摘要方法信息
            })
        
        return {
            'date': date_str,
            'domestic': processed_domestic,
            'international': processed_international
        }

    def save_to_file(self, result, filename):
        """
        将结果保存到文件
        """
        # 统计使用的方法
        llm_count = 0
        simple_count = 0
        
        for item in result['domestic'] + result['international']:
            if item.get('summary_method') == '大模型':
                llm_count += 1
            elif item.get('summary_method') == '简单程序':
                simple_count += 1
        
        print(f"摘要方法统计: 大模型={llm_count}, 简单程序={simple_count}")
        
        # 将文件保存到 datas 目录中
        filepath = os.path.join("datas", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {filepath}")

        # 同时保存到 xinwen 目录中
        xinwen_filepath = os.path.join("xinwen", filename)
        with open(xinwen_filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {xinwen_filepath}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='新闻联播数据处理全流程系统')
    parser.add_argument('--date', type=str, default=datetime.now().strftime("%Y%m%d"), 
                        help='日期 (格式: YYYYMMDD)')
    parser.add_argument('--print-raw', action='store_true', 
                        help='打印原始数据')
    
    args = parser.parse_args()
    
    # 初始化处理器
    processor = NewsProcessor()
    
    # 处理指定日期的新闻
    print(f"正在处理 {args.date} 的新闻...")
    result = processor.process_one_day(args.date)
    
    if result:
        print(f"处理完成，日期：{result['date']}")
        print(f"国内新闻条数：{len(result['domestic'])}")
        print(f"国际新闻条数：{len(result['international'])}")
        
        # 显示示例结果
        print("\n=== 处理结果示例 ===")
        if result['domestic']:
            print("\n国内新闻示例:")
            item = result['domestic'][0]
            print(f"  新闻内容: {item['text'][:100]}...")
            print(f"  实体识别 - 地点: {item['entities']['locations']}")
            print(f"  实体识别 - 人物: {item['entities']['persons']}")
            print(f"  实体识别 - 组织: {item['entities']['organizations']}")
            print(f"  摘要信息 - 标题: {item['summary']['title']}")
            print(f"  摘要信息 - 摘要: {item['summary']['summary']}")
            print(f"  摘要信息 - 关键词: {item['summary']['keywords']}")
            print(f"  摘要信息 - 分类: {item['summary']['category']}")
            print(f"  摘要方法: {item.get('summary_method', '未知')}")
        
        if result['international']:
            print("\n国际新闻示例:")
            item = result['international'][0]
            print(f"  新闻内容: {item['text'][:100]}...")
            print(f"  实体识别 - 地点: {item['entities']['locations']}")
            print(f"  实体识别 - 人物: {item['entities']['persons']}")
            print(f"  实体识别 - 组织: {item['entities']['organizations']}")
            print(f"  摘要信息 - 标题: {item['summary']['title']}")
            print(f"  摘要信息 - 摘要: {item['summary']['summary']}")
            print(f"  摘要信息 - 关键词: {item['summary']['keywords']}")
            print(f"  摘要信息 - 分类: {item['summary']['category']}")
            print(f"  摘要方法: {item.get('summary_method', '未知')}")

        # 保存结果到文件
        processor.save_to_file(result, f"full_result_{args.date}.json")
    else:
        print("处理失败")


if __name__ == "__main__":
    main()
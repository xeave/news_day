#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..analyzer.simple_ner import SimpleNER
from ..analyzer.llm_news_summarizer import NewsSummarizer
import json
import re

class RawDataNewsProcessor:
    """
    处理用户提供原始数据的新闻处理器
    """

    def __init__(self):
        """
        初始化新闻处理器
        """
        self.ner = SimpleNER()
        # 尝试初始化新闻摘要器（如果可用的话）
        model_path = "models/qwen2-7b-instruct-q4_k_m.gguf"
        self.summarizer = NewsSummarizer(model_path) if os.path.exists(model_path) else None

    def parse_raw_data(self, raw_data_text):
        """
        解析原始数据文本，将其分割为单独的新闻条目
        
        Args:
            raw_data_text (str): 包含所有新闻条目的原始文本
            
        Returns:
            list: 新闻条目列表
        """
        # 按行分割并过滤空行
        lines = [line.strip() for line in raw_data_text.strip().split('\n') if line.strip()]
        
        # 提取新闻内容（去掉行号）
        news_items = []
        for line in lines:
            # 移除行首的数字和冒号（如"1: "）
            content = re.sub(r'^\d+:\s*', '', line)
            if content:
                news_items.append(content)
        
        return news_items

    def classify_news(self, news_items):
        """
        将新闻分类为国内和国际新闻
        
        Args:
            news_items (list): 新闻条目列表
            
        Returns:
            tuple: (domestic_news, international_news)
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
            is_domestic = any(keyword in item for keyword in domestic_keywords)
            is_international = (
                any(keyword in item for keyword in international_keywords) or
                any(location in item for location in foreign_locations)
            )
            
            # 根据关键词判断分类
            if is_international and not is_domestic:
                international_news.append(item)
            else:
                domestic_news.append(item)
        
        return domestic_news, international_news

    def process_news_item(self, news_item):
        """
        处理单个新闻条目
        
        Args:
            news_item (str): 单个新闻条目
            
        Returns:
            dict: 包含实体识别和摘要的结果
        """
        # 实体识别
        entities = self.ner.extract_entities(news_item)
        
        # 摘要生成
        if self.summarizer and self.summarizer.llm:
            summary = self.summarizer.summarize_with_llm(news_item)
        else:
            summary = self.summarizer.simple_summarize(news_item) if self.summarizer else {
                "title": news_item[:20],
                "summary": ''.join(re.split(r'[。！？；]', news_item)[:2])[:100],
                "keywords": [],
                "category": "unknown"
            }
        
        return {
            "text": news_item,
            "entities": entities,
            "summary": summary
        }

    def process_raw_data(self, raw_data_text):
        """
        处理原始数据文本
        
        Args:
            raw_data_text (str): 原始数据文本
            
        Returns:
            dict: 处理结果
        """
        # 解析原始数据
        news_items = self.parse_raw_data(raw_data_text)
        
        # 分类新闻
        domestic_news, international_news = self.classify_news(news_items)
        
        # 处理每个新闻条目
        processed_domestic = [self.process_news_item(item) for item in domestic_news]
        processed_international = [self.process_news_item(item) for item in international_news]
        
        return {
            "domestic": processed_domestic,
            "international": processed_international
        }


def main():
    """
    主函数 - 演示如何使用RawDataNewsProcessor
    """
    # 示例原始数据
    sample_data = """1: 当地时间11月1日晚，国家主席习近平结束出席亚太经合组织第三十二次领导人非正式会议和对韩国的国事访问返回北京。离开釜山时，韩国外长赵显等高级官员到机场送行。前往机场途中，中国留学生和中资企业代表在道路两旁挥舞中韩两国国旗，热烈祝贺习近平主席访问圆满成功。
2: 11月1日晚，国家主席习近平结束出席亚太经合组织第三十二次领导人非正式会议和对韩国的国事访问后回到北京。中共中央政治局常委、中央办公厅主任蔡奇，中共中央政治局委员、外交部部长王毅等陪同人员同机返回。
3: 11月1日，国家主席习近平向埃及总统塞西致贺信，祝贺大埃及博物馆开馆。习近平表示，值此大埃及博物馆开馆之际，我谨向塞西总统和埃及人民致以诚挚祝贺。相信大埃及博物馆将在埃及文化史上留下浓墨重彩的一笔，为保护和传承古埃及文明发挥重要作用。习近平强调，中国和埃及友好源远流长。近年来，中埃全面战略伙伴关系蓬勃发展，两国人文交流异彩纷呈。上海博物馆“古埃及文明大展”成功举办，中埃联合考古队正在萨卡拉金字塔下共同探索神秘的古埃及文明。我们高兴地看到，两大古老文明双向奔赴，两国人民日益相知相亲。当前，世界百年未有之大变局加速演进，中埃两大文明古国应当持续深化文明互鉴，为中埃全面战略伙伴关系发展不断注入新动能，为构建人类命运共同体汇聚文明力量。"""

    # 创建处理器实例
    processor = RawDataNewsProcessor()
    
    # 处理原始数据
    result = processor.process_raw_data(sample_data)
    
    # 输出结果
    print("处理结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
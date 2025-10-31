import re
from typing import List, Dict, Tuple

class SimpleNER:
    """
    简单的命名实体识别器
    用于提取中文文本中的人名、地名、机构名等实体
    """
    
    def __init__(self):
        # 预定义的地名列表（示例）
        self.locations = {
            '北京', '上海', '天津', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
            '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
            '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
            '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门', '美国', '英国',
            '法国', '德国', '日本', '韩国', '俄罗斯', '印度', '巴西', '加拿大'
        }
        
        # 预定义的机构名关键词
        self.org_keywords = [
            '政府', '党委', '委员会', '部门', '局', '厅', '处', '科', '办公室',
            '公司', '集团', '银行', '大学', '学院', '研究所', '协会', '联合会',
            '党中央', '国务院', '全国人大', '全国政协', '中央军委'
        ]
        
        # 常见职务和称谓
        self.titles = [
            '主席', '总书记', '总理', '省长', '市长', '县长', '局长', '书记',
            '部长', '主任', '委员', '代表', '委员长', '副主席', '总统', '首相'
        ]
        
        # 编译正则表达式
        self.location_pattern = re.compile('|'.join(self.locations))
        self.org_pattern = re.compile('|'.join(self.org_keywords))
        self.title_pattern = re.compile('|'.join(self.titles))
        
    def extract_locations(self, text: str) -> List[str]:
        """
        提取地名实体
        """
        locations_found = set()
        for match in self.location_pattern.finditer(text):
            locations_found.add(match.group())
        return list(locations_found)
    
    def extract_persons(self, text: str) -> List[str]:
        """
        提取人名实体（基于职务称谓规则）
        """
        persons = []
        # 查找包含职务称谓的短语
        for match in self.title_pattern.finditer(text):
            title = match.group()
            start_pos = match.start()
            # 向前查找可能的人名（通常在职务前）
            # 简化处理：查找2-4个汉字+职务的组合
            for i in range(1, 5):
                if start_pos >= i * 2:
                    potential_name = text[start_pos - i * 2:start_pos]
                    if re.match(r'^[\u4e00-\u9fa5]{2,4}$', potential_name):
                        persons.append(potential_name + title)
                        break
        return persons
    
    def extract_organizations(self, text: str) -> List[str]:
        """
        提取机构名实体
        """
        organizations = set()
        # 查找包含机构关键词的短语
        for match in self.org_pattern.finditer(text):
            keyword = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            # 向前扩展查找完整机构名（最多向前查15个字符）
            start_search = max(0, start_pos - 15)
            possible_org = text[start_search:end_pos]
            
            # 使用简单的规则提取可能的机构名
            parts = possible_org.split()
            for i, part in enumerate(parts):
                if keyword in part and len(part) > 1:
                    organizations.add(part)
        return list(organizations)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取所有类型的实体
        """
        return {
            'locations': self.extract_locations(text),
            'persons': self.extract_persons(text),
            'organizations': self.extract_organizations(text)
        }

def process_news_with_ner(news_data: Dict) -> Dict:
    """
    对新闻数据进行实体识别处理
    """
    ner = SimpleNER()
    
    # 处理国内新闻
    domestic_results = []
    for news_item in news_data.get('domestic', []):
        if isinstance(news_item, str):
            entities = ner.extract_entities(news_item)
            domestic_results.append({
                'text': news_item,
                'entities': entities
            })
        else:
            domestic_results.append(news_item)  # 已经处理过的数据直接添加
    
    # 处理国际新闻
    international_results = []
    for news_item in news_data.get('international', []):
        if isinstance(news_item, str):
            entities = ner.extract_entities(news_item)
            international_results.append({
                'text': news_item,
                'entities': entities
            })
        else:
            international_results.append(news_item)  # 已经处理过的数据直接添加
    
    return {
        'date': news_data.get('date', ''),
        'domestic': domestic_results,
        'international': international_results
    }
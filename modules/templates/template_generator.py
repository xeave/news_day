import akshare as ak
from datetime import datetime, timedelta
from collections import Counter
import re
from difflib import SequenceMatcher

class TemplateGenerator:
    """
    模板自动生成器
    通过多期新闻联播数据对比，自动提取固定模式文本
    """
    
    def __init__(self):
        self.common_patterns = []
        self.date_pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        
    def fetch_multiple_days(self, start_date, days=20):
        """
        获取多期新闻联播数据
        """
        dates = []
        current_date = datetime.strptime(start_date, "%Y%m%d")
        
        # 生成日期列表
        for _ in range(days):
            dates.append(current_date.strftime("%Y%m%d"))
            current_date -= timedelta(days=1)
        
        # 获取多期数据
        news_contents = []
        for date in dates:
            try:
                news_data = ak.news_cctv(date=date)
                content_lines = '\n'.join(news_data['content'].tolist()).split('\n')
                news_contents.append(content_lines)
                print(f"成功获取 {date} 的数据")
            except Exception as e:
                print(f"获取 {date} 的数据失败: {e}")
        
        return news_contents
    
    def find_similar_lines(self, news_contents, similarity_threshold=0.8):
        """
        使用相似度比较查找在多期数据中相似的行
        """
        similar_groups = []
        processed = set()
        
        # 遍历所有行，寻找相似的行
        for i, content1 in enumerate(news_contents):
            for line1 in content1:
                if line1 in processed:
                    continue
                    
                # 寻找与line1相似的行
                similar_lines = [line1]
                for j, content2 in enumerate(news_contents):
                    if i == j:
                        continue
                        
                    for line2 in content2:
                        # 计算相似度
                        similarity = SequenceMatcher(None, line1, line2).ratio()
                        if similarity >= similarity_threshold:
                            similar_lines.append(line2)
                
                # 如果找到足够多的相似行，则加入结果
                if len(similar_lines) > 1:
                    # 去重
                    unique_lines = list(set(similar_lines))
                    if len(unique_lines) > 1:
                        similar_groups.append({
                            'lines': unique_lines,
                            'count': len(unique_lines),
                            'frequency': len(unique_lines) / len(news_contents)
                        })
                        # 标记这些行已处理
                        for line in unique_lines:
                            processed.add(line)
        
        # 按出现次数排序
        similar_groups.sort(key=lambda x: x['count'], reverse=True)
        return similar_groups
    
    def convert_to_patterns(self, similar_groups):
        """
        将相似行组转换为正则表达式模式
        """
        patterns = []
        for group in similar_groups:
            lines = group['lines']
            count = group['count']
            frequency = group['frequency']
            
            if not lines:
                continue
                
            # 使用第一个行作为基础
            base_line = lines[0]
            pattern = re.escape(base_line)
            
            # 将具体日期替换为日期模式
            pattern = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日', r'\\d{4}年\\d{1,2}月\\d{1,2}日', pattern)
            
            # 将具体数字替换为数字模式
            pattern = re.sub(r'\d+', r'\\d+', pattern)
            
            # 将具体百分比数字替换为数字模式
            pattern = re.sub(r'\d+(?:\.\d+)?%', r'\\d+(?:\\.\\d+)?%', pattern)
            
            # 将具体年份替换为年份模式
            pattern = re.sub(r'\d{4}年', r'\\d{4}年', pattern)
            
            patterns.append((pattern, frequency, count))
        
        return patterns
    
    def generate_boilerplate_patterns(self, start_date, days=10, similarity_threshold=0.8):
        """
        生成固定模式模板
        """
        print(f"开始获取 {days} 期新闻联播数据...")
        news_contents = self.fetch_multiple_days(start_date, days)
        
        if len(news_contents) < 2:
            print("数据不足，无法生成模板")
            return []
        
        print("正在分析相似内容...")
        similar_groups = self.find_similar_lines(news_contents, similarity_threshold)
        
        print(f"找到 {len(similar_groups)} 组相似内容，正在转换为模式...")
        patterns = self.convert_to_patterns(similar_groups)
        
        self.common_patterns = patterns
        return patterns
    
    def save_patterns(self, filename="boilerplate_patterns.txt"):
        """
        保存模板到文件
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 新闻联播固定模式模板\n")
            f.write("# 格式: 正则表达式模式 | 出现频率 | 出现次数\n\n")
            for pattern, frequency, count in self.common_patterns:
                f.write(f"{pattern} | {frequency:.2f} | {count}\n")
        
        print(f"模板已保存到 {filename}")
        
    def get_common_patterns(self):
        """
        获取常见模式列表
        """
        return [pattern for pattern, _, _ in self.common_patterns]

def generate_and_save_templates():
    """
    生成并保存模板的主函数
    """
    generator = TemplateGenerator()
    
    # 使用最近日期生成模板
    templates = generator.generate_boilerplate_patterns("20251023", days=10, similarity_threshold=0.9)
    
    print("\n生成的模板:")
    for i, (pattern, frequency, count) in enumerate(templates[:15]):  # 显示前15个
        print(f"{i+1}. {pattern} (频率: {frequency:.2f}, 次数: {count})")
    
    # 保存模板
    generator.save_patterns()
    
    return templates

if __name__ == "__main__":
    generate_and_save_templates()
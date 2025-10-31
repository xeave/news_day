import akshare as ak
from datetime import datetime, timedelta
import re

# 预定义的常见新闻联播模板
PREDEFINED_TEMPLATES = [
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

class SimpleTemplateGenerator:
    """
    简单模板生成器
    基于预定义模板和实际数据样本生成模板
    """
    
    def __init__(self):
        self.templates = PREDEFINED_TEMPLATES.copy()
        
    def analyze_sample_data(self, date="20251023", days=5):
        """
        分析样本数据，提取可能的模板
        """
        print(f"正在分析 {days} 天的样本数据...")
        
        dates = []
        current_date = datetime.strptime(date, "%Y%m%d")
        
        # 生成日期列表
        for _ in range(days):
            dates.append(current_date.strftime("%Y%m%d"))
            current_date -= timedelta(days=1)
        
        # 收集所有行
        all_lines = []
        for date in dates:
            try:
                news_data = ak.news_cctv(date=date)
                content_lines = '\n'.join(news_data['content'].tolist()).split('\n')
                all_lines.extend(content_lines)
                print(f"成功获取 {date} 的数据，共 {len(content_lines)} 行")
            except Exception as e:
                print(f"获取 {date} 的数据失败: {e}")
        
        # 分析行的模式
        self._extract_patterns_from_lines(all_lines)
        
        return self.templates
    
    def _extract_patterns_from_lines(self, lines):
        """
        从行中提取模式
        """
        # 统计包含特定关键词的行
        intro_lines = []      # 开场白相关
        time_lines = []       # 时间相关
        transition_lines = [] # 过渡语
        closing_lines = []    # 结束语
        
        for line in lines:
            # 跳过空行
            if not line.strip():
                continue
                
            # 识别开场白
            if line.startswith("今天是") or line.startswith("各位观众"):
                intro_lines.append(line)
                
            # 识别时间相关
            if re.search(r'\d+时\d+分|现在时间是', line):
                time_lines.append(line)
                
            # 识别过渡语
            if re.search(r'接下来|下面来看|现在为您播送', line):
                transition_lines.append(line)
                
            # 识别结束语
            if re.search(r'感谢收看|再见', line):
                closing_lines.append(line)
        
        # 从样本中提取模式
        self._extract_intro_patterns(intro_lines)
        self._extract_time_patterns(time_lines)
        self._extract_transition_patterns(transition_lines)
        self._extract_closing_patterns(closing_lines)
    
    def _extract_intro_patterns(self, lines):
        """
        提取开场白模式
        """
        if not lines:
            return
            
        # 添加一个通用的开场白模式
        if r'^今天是\d{4}年\d{1,2}月\d{1,2}日.*?$' not in self.templates:
            self.templates.append(r'^今天是\d{4}年\d{1,2}月\d{1,2}日.*?$')
            
        if r'^各位观众.*?$' not in self.templates:
            self.templates.append(r'^各位观众.*?$')
    
    def _extract_time_patterns(self, lines):
        """
        提取时间播报模式
        """
        if not lines:
            return
            
        if r'^\d+时\d+分.*?$' not in self.templates:
            self.templates.append(r'^\d+时\d+分.*?$')
            
        if r'^现在时间是.*?$' not in self.templates:
            self.templates.append(r'^现在时间是.*?$')
    
    def _extract_transition_patterns(self, lines):
        """
        提取过渡语模式
        """
        if not lines:
            return
            
        if r'^接下来关注.+?$' not in self.templates:
            self.templates.append(r'^接下来关注.+?$')
            
        if r'^下面来看.+?$' not in self.templates:
            self.templates.append(r'^下面来看.+?$')
            
        if r'^现在为您播送.+?$' not in self.templates:
            self.templates.append(r'^现在为您播送.+?$')
    
    def _extract_closing_patterns(self, lines):
        """
        提取结束语模式
        """
        if not lines:
            return
            
        if r'^(广告之后|天气预报|稍后回来|下面请看|感谢收看).*?$' not in self.templates:
            self.templates.append(r'^(广告之后|天气预报|稍后回来|下面请看|感谢收看).*?$')
    
    def get_templates(self):
        """
        获取模板列表
        """
        return self.templates.copy()
    
    def save_templates(self, filename="news_templates.txt"):
        """
        保存模板到文件
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 新闻联播文本清洗模板\n")
            f.write("# 用于识别和过滤固定模式文本\n\n")
            for i, template in enumerate(self.templates, 1):
                f.write(f"{i}. {template}\n")
        
        print(f"模板已保存到 {filename}")
        
    def validate_templates(self, test_date="20251023"):
        """
        验证模板的有效性
        """
        print("正在验证模板...")
        try:
            news_data = ak.news_cctv(date=test_date)
            content_lines = '\n'.join(news_data['content'].tolist()).split('\n')
            
            # 编译模板
            compiled_templates = [re.compile(t) for t in self.templates]
            
            # 统计匹配情况
            total_lines = len(content_lines)
            matched_lines = 0
            
            for line in content_lines:
                for pattern in compiled_templates:
                    if pattern.match(line):
                        matched_lines += 1
                        break
            
            print(f"在 {test_date} 的数据中:")
            print(f"  总行数: {total_lines}")
            print(f"  匹配行数: {matched_lines}")
            print(f"  匹配率: {matched_lines/total_lines*100:.2f}%")
            
        except Exception as e:
            print(f"验证过程中出现错误: {e}")

def main():
    """
    主函数
    """
    generator = SimpleTemplateGenerator()
    
    # 分析样本数据
    templates = generator.analyze_sample_data("20251023", days=5)
    
    print(f"\n生成了 {len(templates)} 个模板:")
    for i, template in enumerate(templates, 1):
        print(f"{i:2d}. {template}")
    
    # 保存模板
    generator.save_templates()
    
    # 验证模板
    generator.validate_templates("20251023")
    
    return templates

if __name__ == "__main__":
    main()
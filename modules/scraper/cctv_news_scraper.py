import akshare as ak
import json
from datetime import datetime, timedelta
import sys
import os

class CCTVNewsScraper:
    def __init__(self):
        # 确保xinwen目录存在
        self.output_dir = "xinwen"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_news_list(self, date=None):
        """
        使用akshare获取指定日期的新闻联播内容
        :param date: 日期，格式为YYYYMMDD，如20251024
        :return: 新闻条目列表
        """
        if date is None:
            # 如果没有指定日期，默认为昨天
            yesterday = datetime.now() - timedelta(days=1)
            date = yesterday.strftime("%Y%m%d")
        
        # 使用akshare获取新闻联播文字稿
        df = ak.news_cctv(date=date)
        print(f"获取 {date} 的新闻内容成功")
        
        # 将DataFrame转换为字典列表
        if df is not None and not df.empty:
            return df.to_dict('records')
        else:
            return []

    def scrape_daily_news(self, date=None):
        """ 
        抓取指定日期的新闻联播完整内容
        :param date: 日期，格式为YYYYMMDD
        :return: 完整的新闻内容字典
        """
        print(f"开始抓取 {date if date else '最近一天'} 的新闻联播内容...")
        
        # 获取新闻列表
        news_list = self.get_news_list(date)
        print(f"找到 {len(news_list)} 条新闻")
        
        # 获取每条新闻的详细内容
        full_content = {
            'date': date if date else datetime.now().strftime("%Y%m%d"),
            'news_count': len(news_list),
            'news_items': news_list
        }
        
        return full_content

    def save_to_json(self, data, filename=None):
        """保存为JSON格式"""
        if filename is None:
            filename = f"xinwenlianbo_{data['date']}.json"
        
        # 保存到xinwen目录中
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filepath}")

    def save_to_markdown(self, data, filename=None):
        """保存为Markdown格式"""
        if filename is None:
            filename = f"xinwenlianbo_{data['date']}.md"
        
        # 保存到xinwen目录中
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 新闻联播 {data['date'][:4]}年{data['date'][4:6]}月{data['date'][6:]}日\n\n")
            f.write(f"总条数: {data['news_count']}\n\n")
            
            for i, news in enumerate(data['news_items'], 1):
                f.write(f"## {news['title']}\n\n")
                f.write(f"{news['content']}\n\n")
                f.write("---\n\n")
        print(f"数据已保存到 {filepath}")

def main():
    scraper = CCTVNewsScraper()
    
    # 检查是否有命令行参数指定日期
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[1]
        # 验证日期格式
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            print("日期格式错误，请使用 YYYYMMDD 格式，例如：20251023")
            return
    
    # 抓取指定日期或最近一天的新闻联播内容
    news_data = scraper.scrape_daily_news(date)
    
    # 保存为JSON格式
    scraper.save_to_json(news_data)
    
    # 保存为Markdown格式
    scraper.save_to_markdown(news_data)
    
    print("新闻联播内容抓取完成!")

if __name__ == "__main__":
    main()
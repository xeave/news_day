import json
import akshare as ak
from datetime import datetime
import re
import argparse
import os

# 检查是否可以导入llama_cpp
try:
    from llama_cpp import Llama
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("警告: 未安装llama_cpp_python，将使用简化版摘要功能")

class NewsSummarizer:
    def __init__(self, model_path=None, n_gpu_layers=0):
        """
        初始化新闻摘要器
        
        Args:
            model_path (str): 模型文件路径
            n_gpu_layers (int): 使用GPU的层数，0表示纯CPU
        """
        self.llm = None
        self.n_gpu_layers = n_gpu_layers
        
        if LLM_AVAILABLE and model_path and os.path.exists(model_path):
            try:
                # 加载模型
                self.llm = Llama(
                    model_path=model_path,
                    n_ctx=4096, 
                    n_gpu_layers=n_gpu_layers  # GPU层数
                )
                print(f"成功加载模型: {model_path}")
                if n_gpu_layers > 0:
                    print(f"使用GPU加速，GPU层数: {n_gpu_layers}")
                else:
                    print("使用纯CPU运行")
            except Exception as e:
                print(f"加载模型失败: {e}")
                self.llm = None
        elif LLM_AVAILABLE and model_path:
            print(f"模型文件不存在: {model_path}")
    
    def get_prompt_template(self):
        """
        获取提示词模板
        """
        return """You are a CCTV news editor.
Summarize the following Xinwen Lianbo piece into JSON:
{"title": "<10 words>", "summary": "<40 words>", "keywords": ["kw1"], "category": "domestic|international"}
Text:
{text}
"""
    
    def simple_summarize(self, text):
        """
        简单摘要方法（当没有大模型时使用）
        """
        # 清洗文本
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        
        # 提取前几句作为摘要
        sentences = re.split(r'[。！？；]', cleaned_text)
        summary = ''.join(sentences[:2])[:120]  # 前两句，最多120字符
        
        # 简单关键词提取（基于常见新闻关键词）
        keywords = []
        keyword_candidates = ['经济', '政治', '国际', '国内', '发展', '建设', '会议', '政策', '合作', '科技']
        for keyword in keyword_candidates:
            if keyword in text:
                keywords.append(keyword)
        
        # 简单分类（基于关键词）
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
    
    def summarize_with_llm(self, text):
        """
        使用大模型进行摘要
        """
        if not self.llm:
            return self.simple_summarize(text)
        
        # 截断文本以提高速度
        text = text[:600]
        
        prompt = self.get_prompt_template().format(text=text)
        
        try:
            output = self.llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, 
                max_tokens=200
            )
            
            content = output['choices'][0]['message']['content']
            # 清理可能的markdown格式
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            print(f"大模型摘要失败: {e}")
            return self.simple_summarize(text)
    
    def process_news_by_date(self, date_str):
        """
        处理指定日期的新闻
        """
        try:
            # 获取新闻数据
            df = ak.news_cctv(date=date_str)
            articles = df['content'].tolist()
            
            print(f"获取到 {len(articles)} 条新闻")
            
            # 批量摘要
            results = []
            for i, article in enumerate(articles):
                print(f"正在处理第 {i+1} 条新闻...")
                summary = self.summarize_with_llm(article)
                results.append({
                    "original": article[:100] + "..." if len(article) > 100 else article,
                    "summary": summary
                })
            
            return results
        except Exception as e:
            print(f"处理新闻时出错: {e}")
            return []
    
    def save_results(self, results, date_str, output_format="json"):
        """
        保存结果到文件
        
        Args:
            results (list): 摘要结果列表
            date_str (str): 日期字符串
            output_format (str): 输出格式 ("json" 或 "md")
        """
        if output_format == "json":
            output_file = f"news_summary_{date_str}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        elif output_format == "md":
            output_file = f"news_summary_{date_str}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 新闻联播摘要 - {date_str}\n\n")
                for i, result in enumerate(results):
                    f.write(f"## {i+1}. {result['summary']['title']}\n\n")
                    f.write(f"**摘要**: {result['summary']['summary']}\n\n")
                    f.write(f"**关键词**: {', '.join(result['summary']['keywords'])}\n\n")
                    f.write(f"**分类**: {result['summary']['category']}\n\n")
                    f.write(f"<details>\n<summary>原文预览</summary>\n\n{result['original']}\n\n</details>\n\n")
                    f.write("---\n\n")
        
        print(f"结果已保存到 {output_file}")
        return output_file

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='新闻联播信息提取与总结')
    parser.add_argument('--date', type=str, default=datetime.now().strftime("%Y%m%d"), 
                        help='日期 (格式: YYYYMMDD)')
    parser.add_argument('--model-path', type=str, default="models/qwen2-7b-instruct-q4_k_m.gguf",
                        help='模型文件路径')
    parser.add_argument('--gpu-layers', type=int, default=0,
                        help='GPU加速层数 (0表示纯CPU)')
    parser.add_argument('--format', type=str, default="json", choices=["json", "md"],
                        help='输出格式 (json 或 md)')
    
    args = parser.parse_args()
    
    # 初始化摘要器
    summarizer = NewsSummarizer(args.model_path, args.gpu_layers)
    
    # 处理指定日期的新闻
    print(f"正在处理 {args.date} 的新闻...")
    
    results = summarizer.process_news_by_date(args.date)
    
    if not results:
        print("未获取到新闻数据")
        return
    
    # 输出结果
    print("\n=== 新闻摘要结果 ===")
    for i, result in enumerate(results):
        print(f"\n{i+1}. 原文预览: {result['original']}")
        print(f"   标题: {result['summary']['title']}")
        print(f"   摘要: {result['summary']['summary']}")
        print(f"   关键词: {', '.join(result['summary']['keywords'])}")
        print(f"   分类: {result['summary']['category']}")
    
    # 保存结果到文件
    summarizer.save_results(results, args.date, args.format)

if __name__ == "__main__":
    main()
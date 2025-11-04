#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 检查是否可以连接到 Ollama
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    LLM_AVAILABLE = response.status_code == 200
    if LLM_AVAILABLE:
        print("Ollama 服务可用，将使用大模型进行处理")
    else:
        print("Ollama 服务不可用")
except:
    LLM_AVAILABLE = False
    print("提示: 无法连接到 Ollama")


def process_raw_data_with_llm(raw_data_text):
    """
    直接使用大模型处理原始数据
    
    Args:
        raw_data_text (str): 原始数据文本
        
    Returns:
        dict: 处理结果
    """
    if not LLM_AVAILABLE:
        print("错误: Ollama 服务不可用，无法使用大模型处理")
        return None

    # 分割原始数据为单独的新闻条目
    lines = [line.strip() for line in raw_data_text.strip().split('\n') if line.strip()]
    
    # 提取新闻内容（去掉行号）
    news_items = []
    for line in lines:
        # 移除行首的数字和冒号（如"1: "）
        import re
        content = re.sub(r'^\d+:\s*', '', line)
        if content:
            news_items.append(content)
    
    print(f"共找到 {len(news_items)} 条新闻")
    
    # 处理每条新闻
    processed_news = []
    for i, item in enumerate(news_items):
        print(f"正在处理第 {i+1} 条新闻...")
        
        # 构造提示词
        prompt = f"""你是一名央视新闻联播的资深编辑，任务是对下面这段新闻进行结构化处理。
请将新闻内容进行分析，提取以下信息并以合法的 JSON 格式输出：

要求输出格式：
{{
  "title": "新闻标题（10字以内）",
  "summary": "新闻摘要（50字以内）",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "category": "domestic 或 international",
  "entities": {{
    "locations": ["地点1", "地点2"],
    "persons": ["人物1", "人物2"],
    "organizations": ["组织1", "组织2"]
  }}
}}

新闻原文：
{item}
"""
        
        # 调用 Ollama API
        payload = {
            "model": "qwen2:7b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
            result = response.json()
            
            # 解析结果
            try:
                parsed_result = json.loads(result['response'])
                processed_news.append({
                    "original": item,
                    "processed": parsed_result
                })
            except json.JSONDecodeError:
                print(f"第 {i+1} 条新闻处理失败：无法解析模型输出")
                processed_news.append({
                    "original": item,
                    "processed": None,
                    "error": "无法解析模型输出"
                })
                
        except Exception as e:
            print(f"第 {i+1} 条新闻处理失败: {e}")
            processed_news.append({
                "original": item,
                "processed": None,
                "error": str(e)
            })
    
    return {
        "news_count": len(news_items),
        "processed_news": processed_news
    }


def save_result(result, filename):
    """
    保存结果到文件
    
    Args:
        result (dict): 处理结果
        filename (str): 文件名
    """
    filepath = os.path.join("datas", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到 {filepath}")


def main():
    """
    主函数 - 演示如何使用直接大模型处理
    """
    # 示例原始数据
    sample_data = """1: 当地时间11月1日晚，国家主席习近平结束出席亚太经合组织第三十二次领导人非正式会议和对韩国的国事访问返回北京。离开釜山时，韩国外长赵显等高级官员到机场送行。前往机场途中，中国留学生和中资企业代表在道路两旁挥舞中韩两国国旗，热烈祝贺习近平主席访问圆满成功。
2: 11月1日晚，国家主席习近平结束出席亚太经合组织第三十二次领导人非正式会议和对韩国的国事访问后回到北京。中共中央政治局常委、中央办公厅主任蔡奇，中共中央政治局委员、外交部部长王毅等陪同人员同机返回。
3: 11月1日，国家主席习近平向埃及总统塞西致贺信，祝贺大埃及博物馆开馆。习近平表示，值此大埃及博物馆开馆之际，我谨向塞西总统和埃及人民致以诚挚祝贺。相信大埃及博物馆将在埃及文化史上留下浓墨重彩的一笔，为保护和传承古埃及文明发挥重要作用。习近平强调，中国和埃及友好源远流长。近年来，中埃全面战略伙伴关系蓬勃发展，两国人文交流异彩纷呈。上海博物馆“古埃及文明大展”成功举办，中埃联合考古队正在萨卡拉金字塔下共同探索神秘的古埃及文明。我们高兴地看到，两大古老文明双向奔赴，两国人民日益相知相亲。当前，世界百年未有之大变局加速演进，中埃两大文明古国应当持续深化文明互鉴，为中埃全面战略伙伴关系发展不断注入新动能，为构建人类命运共同体汇聚文明力量。
4: 党的二十届四中全会着眼强国建设、民族复兴伟业，站在时代发展和战略全局的高度，对国防和军队建设提出新的要求。连日来，在大江南北的座座军营，广大官兵认真学习贯彻全会精神，一致表示，要更加紧密地团结在以习近平同志为核心的党中央周围，把思想和行动统一到全会精神上来，把智慧和力量凝聚到落实全会作出的战略部署上来，为如期实现建军一百年奋斗目标，高质量推进国防和军队现代化接续奋斗。全会高度评价“十四五”时期我国发展取得的重大成就，为我军在“十五五”时期开创国防和军队现代化新局面指明了前进方向、提供了根本遵循。全军官兵在学习讨论中深切感到，学习贯彻落实好全会精神，就是要自觉在思想上政治上行动上同以习近平同志为核心的党中央保持高度一致，坚决听从党中央、中央军委和习主席指挥，在革命性锻造中向着实现党在新时代的强军目标砥砺前行。全军官兵表示，“十五五”时期，我军要在实现建军一百年奋斗目标的基础上，高质量推进国防和军队现代化，必须完整准确全面贯彻新发展理念，加快构建新发展格局，推动我军建设发展质量变革、效能变革、动力变革，以硬实改革举措解放和发展战斗力，进一步解放和增强军队活力。全会提出，要加快先进战斗力建设，推进军事治理现代化，巩固提高一体化国家战略体系和能力。广大官兵表示，要把全会精神切实融入练兵备战各领域、全过程，向战略管理要质效，加快推进军事管理革命，加强战建统筹、跨域统筹、军地统筹，坚持战、建、备一体推进，不断提升履行新时代使命任务的能力，全力以赴打好实现建军一百年奋斗目标攻坚战。
5: 连日来，学习贯彻党的二十届四中全会精神中央宣讲团成员在各地各部门宣讲，并深入基层与干部群众互动交流，推动全会精神学习走深走实。中央宣讲团成员、中央办公厅分管日常工作的副主任孟祥锋今天（11月2日）在江西作宣讲报告。孟祥锋紧紧围绕全会召开的重大意义、“十四五”时期取得的重大成就、“十五五”时期经济社会发展的战略任务和重大举措等八个方面，对党的二十届四中全会作了全面宣讲和深入阐释。孟祥锋还深入九江的工厂企业，与企业职工互动交流，深入宣传阐释党的二十届四中全会精神。中央宣讲团成员，应急管理部党委书记、部长王祥喜10月30日在应急管理部部属单位作宣讲报告。王祥喜从深刻认识党的二十届四中全会的重大意义、科学把握全会精神的核心要义、以全会精神为引领开创应急管理事业发展新局面等方面，对党的二十届四中全会精神作了全面宣讲和深入阐释。王祥喜还来到应急管理部党校，与教职员工和学员代表交流互动。中央宣讲团成员，国家市场监督管理总局党组书记、局长罗文10月30日在内蒙古自治区呼和浩特市宣讲。罗文从深入学习领会习近平总书记在全会上的重要讲话精神、深刻认识全会的重大意义等方面，对全会精神作了系统阐释。罗文还走进蒙草生态环境（集团）股份有限公司开展宣讲，与企业职工、当地基层干部等进行互动交流。"""

    # 确保 datas 目录存在
    os.makedirs("datas", exist_ok=True)
    
    # 处理原始数据
    result = process_raw_data_with_llm(sample_data)
    
    if result:
        # 保存结果
        save_result(result, "direct_llm_result.json")
        
        # 打印部分结果
        print("\n处理结果示例:")
        for i, item in enumerate(result["processed_news"][:2]):
            print(f"\n新闻 {i+1}:")
            print(f"原文: {item['original'][:100]}...")
            if item['processed']:
                print(f"标题: {item['processed'].get('title', 'N/A')}")
                print(f"摘要: {item['processed'].get('summary', 'N/A')}")
                print(f"分类: {item['processed'].get('category', 'N/A')}")
            else:
                print("处理失败")


if __name__ == "__main__":
    main()
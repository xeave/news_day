# 使用 Ollama 进行新闻联播摘要

本文档介绍了如何在本项目中使用 Ollama 代替 llama.cpp 来运行大语言模型进行新闻摘要。

## 1. 安装和配置 Ollama

### 1.1 安装 Ollama

访问 [Ollama 官网](https://ollama.com/) 下载并安装适用于您操作系统的版本。

### 1.2 启动 Ollama 服务

安装完成后，Ollama 服务通常会自动启动。您可以通过以下命令确认服务状态：

```bash
ollama serve
```

### 1.3 下载所需模型

项目推荐使用 qwen2:7b 模型，可以通过以下命令下载：

```bash
ollama pull qwen2:7b
```

如果您设备资源有限，也可以使用较小的模型：

```bash
# 使用 1.5b 参数版本
ollama pull qwen2:1.5b
```

### 1.4 查看已安装的模型

```bash
ollama ls
```

## 2. 修改项目代码以使用 Ollama

项目中的 [llm_news_summarizer.py](file:///Users/zxx/Desktop/day_news/llm_news_summarizer.py) 文件需要进行修改以支持 Ollama。

### 2.1 修改导入部分

将原来的 llama_cpp 导入替换为 requests：

```python
import json
import akshare as ak
from datetime import datetime
import re
import argparse
import os
import requests  # 添加 requests 导入
```

### 2.2 修改 NewsSummarizer 类

修改 [NewsSummarizer](file:///Users/zxx/Desktop/day_news/llm_news_summarizer.py#L24-L214) 类的初始化方法：

```python
def __init__(self, model_name="qwen2:7b"):
    """
    初始化新闻摘要器
    
    Args:
        model_name (str): Ollama 模型名称
    """
    self.model_name = model_name
    self.ollama_url = "http://localhost:11434/api/generate"
    
    # 检查 Ollama 服务是否可用
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"Ollama 服务可用，使用模型: {model_name}")
        else:
            print("Ollama 服务不可用，将使用简化版摘要功能")
    except Exception as e:
        print(f"无法连接到 Ollama 服务: {e}")
        print("将使用简化版摘要功能")
```

### 2.3 修改 summarize_with_llm 方法

替换原有的 [summarize_with_llm](file:///Users/zxx/Desktop/day_news/llm_news_summarizer.py#L93-L121) 方法：

```python
def summarize_with_llm(self, text):
    """
    使用 Ollama 进行摘要
    """
    # 检查 Ollama 服务是否可用
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return self.simple_summarize(text)
    except:
        return self.simple_summarize(text)
    
    # 截断文本以提高速度
    text = text[:600]
    
    prompt = self.get_prompt_template().format(text=text)
    
    payload = {
        "model": self.model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(self.ollama_url, json=payload, timeout=120)
        result = response.json()
        return json.loads(result['response'])
    except Exception as e:
        print(f"Ollama 摘要失败: {e}")
        return self.simple_summarize(text)
```

## 3. 运行使用 Ollama 的摘要程序

完成上述修改后，您可以像以前一样运行摘要程序：

```bash
python llm_news_summarizer.py --date 20251023
```

程序会自动使用 Ollama 服务和指定的模型进行新闻摘要。

## 4. 模型选择建议

1. **qwen2:7b** - 推荐模型，摘要质量高，需要约 3.8GB 存储空间
2. **qwen2:1.5b** - 轻量级模型，适合资源有限的设备，需要约 1GB 存储空间

您可以通过修改 [NewsSummarizer](file:///Users/zxx/Desktop/day_news/llm_news_summarizer.py#L24-L214) 初始化时的 `model_name` 参数来切换模型：

```python
# 使用 1.5b 模型
summarizer = NewsSummarizer(model_name="qwen2:1.5b")
```

## 5. 故障排除

### 5.1 Ollama 服务未启动

如果遇到连接错误，请确保 Ollama 服务正在运行：

```bash
ollama serve
```

### 5.2 模型未找到

如果提示模型未找到，请确认模型已下载：

```bash
ollama pull qwen2:7b
```

### 5.3 摘要质量不佳

如果摘要质量不佳，可以尝试：
1. 使用参数更多的模型（如从 1.5b 升级到 7b）
2. 调整提示词模板
3. 增加输入文本长度（当前限制为 600 字符）
# 项目结构说明

## 项目概述
本项目旨在从央视网抓取《新闻联播》的文字稿内容，实现结构化存储与后续处理，便于数据分析、摘要生成和多平台发布。

## 目录结构
```
day_news/
├── modules/
│   ├── scraper/                 # 数据抓取模块
│   ├── processor/               # 数据处理模块
│   ├── publisher/               # 内容发布模块
│   ├── analyzer/                # 数据分析模块
│   ├── templates/               # 模板生成模块
│   ├── config/                  # 配置管理模块
│   ├── tests/                   # 测试模块
│   └── utils/                   # 工具模块
├── 输出数据文件
├── 文档说明
└── 资源文件
```

## 核心功能模块

### 1. 数据抓取模块 (modules/scraper/)
- [cctv_news_scraper.py](file:///Users/zxx/Desktop/day_news/modules/scraper/cctv_news_scraper.py) - 从央视网抓取新闻联播数据的主要脚本
- [main.py](file:///Users/zxx/Desktop/day_news/main.py) - 项目主入口，整合各个功能模块

### 2. 数据处理模块 (modules/processor/)
- [cctv_news_processor.py](file:///Users/zxx/Desktop/day_news/modules/processor/cctv_news_processor.py) - 处理抓取到的原始新闻数据

### 3. 内容发布模块 (modules/publisher/)
- [wechat_publication_manager.py](file:///Users/zxx/Desktop/day_news/modules/publisher/wechat_publication_manager.py) - 微信公众号发布管理器核心类
- [wechat_publish_with_config.py](file:///Users/zxx/Desktop/day_news/modules/publisher/wechat_publish_with_config.py) - 使用配置文件发布文章的脚本
- [wechat_publish_example.py](file:///Users/zxx/Desktop/day_news/wechat_publish_example.py) - 微信发布示例脚本
- [wechat_publisher.py](file:///Users/zxx/Desktop/day_news/modules/publisher/wechat_publisher.py) - 微信发布器实现
- [publish_to_wechat.py](file:///Users/zxx/Desktop/day_news/modules/publisher/publish_to_wechat.py) - 发布到微信的脚本
- [example_publish_news.py](file:///Users/zxx/Desktop/day_news/modules/publisher/example_publish_news.py) - 新闻发布示例

### 4. 数据分析模块 (modules/analyzer/)
- [llm_news_summarizer.py](file:///Users/zxx/Desktop/day_news/modules/analyzer/llm_news_summarizer.py) - 使用大语言模型进行新闻摘要
- [simple_ner.py](file:///Users/zxx/Desktop/day_news/modules/analyzer/simple_ner.py) - 简单命名实体识别
- [calculate_similarity.py](file:///Users/zxx/Desktop/day_news/calculate_similarity.py) - 相似度计算
- [setup_llm_env.py](file:///Users/zxx/Desktop/day_news/setup_llm_env.py) - LLM环境设置

### 5. 模板生成模块 (modules/templates/)
- [template_generator.py](file:///Users/zxx/Desktop/day_news/modules/templates/template_generator.py) - 模板生成器
- [simple_template_generator.py](file:///Users/zxx/Desktop/day_news/modules/templates/simple_template_generator.py) - 简单模板生成器
- [news_templates.txt](file:///Users/zxx/Desktop/day_news/modules/templates/news_templates.txt) - 新闻模板文件
- [boilerplate_patterns.txt](file:///Users/zxx/Desktop/day_news/modules/templates/boilerplate_patterns.txt) - 样板模式文件

### 6. 配置管理模块 (modules/config/)
- [config.py](file:///Users/zxx/Desktop/day_news/modules/config/config.py) - 配置加载和管理模块
- [wechat_config.ini](file:///Users/zxx/Desktop/day_news/modules/config/wechat_config.ini) - 微信公众号配置文件（AppID和AppSecret）
- [wechat_config_example.ini](file:///Users/zxx/Desktop/day_news/modules/config/wechat_config_example.ini) - 微信配置文件示例

### 7. 测试模块 (modules/tests/)
- [test_wechat_functionality.py](file:///Users/zxx/Desktop/day_news/modules/tests/test_wechat_functionality.py) - 微信功能测试
- [test_wechat_publish.py](file:///Users/zxx/Desktop/day_news/modules/tests/test_wechat_publish.py) - 微信发布测试
- [test_wechat_with_config.py](file:///Users/zxx/Desktop/day_news/modules/tests/test_wechat_with_config.py) - 带配置的微信测试

### 8. 工具模块 (modules/utils/)
- 待添加的通用工具函数

## 输出数据文件
- `xinwenlianbo_YYYYMMDD.json` - 原始新闻数据JSON文件
- `xinwenlianbo_YYYYMMDD.md` - 原始新闻数据Markdown文件
- `news_summary_YYYYMMDD.json` - 新闻摘要JSON文件
- `news_summary_YYYYMMDD.md` - 新闻摘要Markdown文件
- `processed_news_YYYYMMDD.json` - 处理后的新闻数据
- `processed_news_ner_YYYYMMDD.json` - 带命名实体识别的新闻数据
- `wechat_posts.json` - 微信发布内容JSON
- `wechat_posts.md` - 微信发布内容Markdown

## 文档说明
- [README.md](file:///Users/zxx/Desktop/day_news/README.md) - 项目主说明文档
- [项目设计.md](file:///Users/zxx/Desktop/day_news/项目设计.md) - 项目详细设计文档
- [WECHAT_CONFIG_USAGE.md](file:///Users/zxx/Desktop/day_news/WECHAT_CONFIG_USAGE.md) - 微信配置使用说明
- [WECHAT_PUBLISHING_GUIDE.md](file:///Users/zxx/Desktop/day_news/WECHAT_PUBLISHING_GUIDE.md) - 微信发布指南
- [README_Python微信公众号SDK.md](file:///Users/zxx/Desktop/day_news/README_Python微信公众号SDK.md) - Python微信SDK说明
- [README_个人认证与微信公众号权限.md](file:///Users/zxx/Desktop/day_news/README_个人认证与微信公众号权限.md) - 个人认证与权限说明
- [README_微信接口权限说明.md](file:///Users/zxx/Desktop/day_news/README_微信接口权限说明.md) - 微信接口权限说明
- [使用Ollama进行新闻摘要.md](file:///Users/zxx/Desktop/day_news/使用Ollama进行新闻摘要.md) - Ollama新闻摘要说明
- [分发到各个平台的文案.md](file:///Users/zxx/Desktop/day_news/分发到各个平台的文案.md) - 多平台分发文案
- [发布到小红书和微信公众号的实现.md](file:///Users/zxx/Desktop/day_news/发布到小红书和微信公众号的实现.md) - 多平台发布实现
- [微信公众号自动发布.md](file:///Users/zxx/Desktop/day_news/微信公众号自动发布.md) - 微信自动发布详细说明
- [微信公众号自动发布说明.md](file:///Users/zxx/Desktop/day_news/微信公众号自动发布说明.md) - 微信自动发布说明
- [怎么获取稳定的文字稿.md](file:///Users/zxx/Desktop/day_news/怎么获取稳定的文字稿.md) - 获取稳定文字稿说明
- [清洗数据.md](file:///Users/zxx/Desktop/day_news/清洗数据.md) - 数据清洗说明
- [零预算信息提取与总结.md](file:///Users/zxx/Desktop/day_news/零预算信息提取与总结.md) - 信息提取与总结说明
- [PROJECT_STRUCTURE.md](file:///Users/zxx/Desktop/day_news/PROJECT_STRUCTURE.md) - 项目结构说明（本文档）

## 资源文件
- [zi_yuan/](file:///Users/zxx/Desktop/day_news/zi_yuan/) - 资源文件目录
- [资源/](file:///Users/zxx/Desktop/day_news/资源/) - 资源文件目录
- cover.png - 封面图片示例

## 使用建议

### 日常使用流程
1. 运行 [cctv_news_scraper.py](file:///Users/zxx/Desktop/day_news/modules/scraper/cctv_news_scraper.py) 抓取最新新闻数据
2. 使用 [llm_news_summarizer.py](file:///Users/zxx/Desktop/day_news/modules/analyzer/llm_news_summarizer.py) 生成摘要（可选）
3. 使用 [wechat_publish_with_config.py](file:///Users/zxx/Desktop/day_news/modules/publisher/wechat_publish_with_config.py) 发布到微信公众号

### 微信公众号发布问题处理
如果遇到48001权限错误：
1. 申请微信测试号进行开发测试
2. 检查正式号的认证状态和接口权限
3. 参考 [README_个人认证与微信公众号权限.md](file:///Users/zxx/Desktop/day_news/README_个人认证与微信公众号权限.md) 进行处理
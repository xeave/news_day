# 新闻联播文字稿爬虫

这个项目用于从央视网抓取新闻联播的文字稿内容，并将其保存为结构化的JSON和Markdown格式文件。

## 项目结构

- `cctv_news_scraper.py`: 主要的爬虫脚本
- `requirements.txt`: 项目依赖
- `怎么获取稳定的文字稿.md`: 获取文字稿的技术方案
- `项目设计.md`: 项目的整体设计方案
- `wechat_publisher.py`: 微信公众号发布模块
- `publish_to_wechat.py`: 微信公众号发布示例脚本

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```bash
python cctv_news_scraper.py
```

这将默认抓取最近一天的新闻联播内容，并保存为JSON和Markdown格式。

### 修改代码适配网站结构

由于央视网的页面结构可能会发生变化，你可能需要根据实际情况调整代码中的选择器：

1. 打开[cctv_news_scraper.py](file:///Users/zxx/Desktop/day_news/cctv_news_scraper.py)
2. 找到[get_news_list](file:///Users/zxx/Desktop/day_news/cctv_news_scraper.py#L29-L67)方法，修改其中的CSS选择器以正确获取新闻列表
3. 找到[get_news_content](file:///Users/zxx/Desktop/day_news/cctv_news_scraper.py#L69-L110)方法，修改其中的CSS选择器以正确获取新闻内容

### 输出文件

程序会生成两个文件：
- `xinwenlianbo_YYYYMMDD.json`: JSON格式的完整数据
- `xinwenlianbo_YYYYMMDD.md`: Markdown格式的可读版本

### 微信公众号自动发布

项目支持将处理好的新闻内容自动发布到微信公众号，需要以下步骤：

1. 获取微信公众号的AppID和AppSecret
2. 将你的服务器IP地址添加到微信公众号的IP白名单中
3. 设置环境变量：
   ```bash
   export WECHAT_APP_ID='你的AppID'
   export WECHAT_APP_SECRET='你的AppSecret'
   ```
4. 运行发布脚本：
   ```bash
   python publish_to_wechat.py
   ```

## 注意事项

1. 请遵守网站的robots.txt规则和使用条款
2. 不要过于频繁地请求，避免给网站造成压力
3. 央视网可能会更新页面结构，需要定期维护选择器
4. 如果遇到反爬虫机制，可能需要添加更多headers或使用代理
5. 微信公众号素材有效期为3天，建议获取后立即使用

## 后续扩展

根据[项目设计.md](file:///Users/zxx/Desktop/day_news/项目设计.md)中的规划，下一步可以：
1. 添加定时任务，每天自动抓取
2. 集成大语言模型进行内容摘要
3. 添加更多的数据清洗和结构化功能
4. 开发Web界面展示历史数据
5. 扩展到更多平台的自动发布（如小红书、微博等）# news_day

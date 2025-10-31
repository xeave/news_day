# 微信公众号自动发布功能说明

## 功能概述

本项目新增了独立的微信公众号自动发布功能，可以将处理好的新闻内容自动发布到微信公众号。该功能基于微信官方API实现，支持以下操作：

1. 获取访问令牌（access_token）
2. 上传封面图片素材
3. 创建草稿文章
4. 正式发布文章

所有功能都实现在独立的文件中，不会修改您已有的任何代码。

## 配置要求

### 1. 微信公众号账号
- 需要一个认证过的微信公众号（订阅号或服务号）
- 获取AppID和AppSecret
- 将服务器IP地址添加到IP白名单

### 2. 环境变量配置
在使用发布功能前，需要设置以下环境变量：

```bash
export WECHAT_APP_ID='你的AppID'
export WECHAT_APP_SECRET='你的AppSecret'
```

### 3. 获取AppID和AppSecret的步骤

1. 登录微信公众平台：https://mp.weixin.qq.com
2. 在左侧菜单中找到「设置与开发」→「基本配置」
3. AppID会直接显示
4. 点击「查看」按钮获取AppSecret

### 4. 配置IP白名单

1. 在微信公众平台中找到「设置与开发」→「公众号设置」→「功能设置」
2. 找到「IP白名单」设置项
3. 获取你的服务器公网IP地址：
   ```bash
   curl ifconfig.me
   ```
4. 将该IP地址添加到白名单中

## 核心模块

### WeChatPublicationManager 类

位于 [wechat_publication_manager.py](file:///Users/zxx/Desktop/day_news/wechat_publication_manager.py) 文件中，提供以下方法：

1. `get_access_token()` - 获取访问令牌
2. `upload_image(image_path)` - 上传图片素材
3. `create_draft(title, content, thumb_media_id)` - 创建草稿
4. `publish_draft(media_id)` - 发布草稿
5. `publish_article(title, content, cover_image_path)` - 一键发布文章

## 使用示例

### 基本使用

```python
from modules.publisher.wechat_publication_manager import WeChatPublicationManager
import os

# 初始化发布管理器
app_id = os.getenv('WECHAT_APP_ID')
app_secret = os.getenv('WECHAT_APP_SECRET')
manager = WeChatPublicationManager(app_id, app_secret)

# 发布文章
result = manager.publish_article(
    title="文章标题",
    content="<p>文章内容</p>",
    cover_image_path="path/to/cover.jpg"
)

print("发布成功:", result)
```

### 完整示例

参考 [wechat_publish_example.py](file:///Users/zxx/Desktop/day_news/wechat_publish_example.py) 文件，该示例展示了如何：

1. 加载处理好的新闻数据
2. 格式化为微信公众号文章
3. 发布到微信公众号

运行示例：
```bash
python wechat_publish_example.py
```

## 注意事项

1. **素材有效期**：微信素材有效期为3天，建议获取后立即使用
2. **发布频率限制**：
   - 订阅号：每天限1次群发
   - 服务号：每月限4次群发
3. **封面图片**：需要提供有效的封面图片路径
4. **内容格式**：文章内容应为HTML格式
5. **安全存储**：AppSecret是敏感信息，不要硬编码在代码中，建议使用环境变量

## 测试方法

可以使用 [test_wechat_functionality.py](file:///Users/zxx/Desktop/day_news/test_wechat_functionality.py) 脚本测试基本功能：

```bash
python test_wechat_functionality.py
```

## 集成建议

要将此功能集成到现有新闻处理流程中，建议：

1. 在新闻数据处理完成后调用发布功能
2. 添加错误处理和日志记录
3. 考虑添加定时任务实现自动发布
4. 添加发布前的内容预览功能

## 新增文件列表

本功能新增的文件如下：
- [wechat_publication_manager.py](file:///Users/zxx/Desktop/day_news/wechat_publication_manager.py) - 核心发布功能模块
- [wechat_publish_example.py](file:///Users/zxx/Desktop/day_news/wechat_publish_example.py) - 使用示例
- [test_wechat_functionality.py](file:///Users/zxx/Desktop/day_news/test_wechat_functionality.py) - 功能测试脚本
- [WECHAT_PUBLISHING_GUIDE.md](file:///Users/zxx/Desktop/day_news/WECHAT_PUBLISHING_GUIDE.md) - 本说明文档

这些文件都是新增的，没有修改您已有的任何代码文件。
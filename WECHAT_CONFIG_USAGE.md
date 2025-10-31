# 微信公众号配置和使用说明

## 配置方式

本项目支持两种方式配置微信公众号的认证信息：

### 1. 环境变量（推荐）

设置环境变量是推荐的方式，特别是在生产环境中：

```bash
export WECHAT_APP_ID='your_app_id'
export WECHAT_APP_SECRET='your_app_secret'
```

### 2. 配置文件

如果不想使用环境变量，可以使用配置文件：

1. 复制示例配置文件：
   ```bash
   cp wechat_config_example.ini wechat_config.ini
   ```

2. 编辑 `wechat_config.ini` 文件，填入实际的AppID和AppSecret：
   ```ini
   [wechat]
   app_id = your_actual_app_id
   app_secret = your_actual_app_secret
   ```

## 安全注意事项

1. **不要将包含真实凭证的配置文件提交到版本控制系统中**
2. 确保配置文件的访问权限设置正确，只有项目需要的用户可以访问
3. 在生产环境中，强烈推荐使用环境变量而非配置文件

## 使用示例

### 运行测试脚本

```bash
# 使用环境变量
WECHAT_APP_ID='your_app_id' WECHAT_APP_SECRET='your_app_secret' python test_wechat_functionality.py

# 或者如果已设置环境变量
python test_wechat_functionality.py
```

### 运行发布示例

```bash
# 使用环境变量
WECHAT_APP_ID='your_app_id' WECHAT_APP_SECRET='your_app_secret' python wechat_publish_example.py

# 或者如果已设置环境变量或配置了配置文件
python wechat_publish_example.py
```

## 配置优先级

配置的优先级如下：
1. 环境变量（最高优先级）
2. 本地配置文件
3. 默认值（最低优先级，通常为空）

这意味着如果同时设置了环境变量和配置文件，将优先使用环境变量。

## 故障排除

### 1. 配置未生效

确保：
- 环境变量已正确设置并且在当前shell会话中可见
- 配置文件存在于项目的根目录或config目录下
- 配置文件格式正确

### 2. 权限问题

确保配置文件只能被项目需要的用户访问：
```bash
chmod 600 wechat_config.ini
```

### 3. 配置文件未被读取

检查：
- 文件名是否正确（应为 wechat_config.ini）
- 文件是否位于项目根目录或config子目录中
- 文件格式是否符合INI格式要求
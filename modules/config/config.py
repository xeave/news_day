import os
from modules.config import configparser
from typing import Optional

class WeChatConfig:
    """
    微信公众号配置管理类
    用于管理微信公众号的认证信息和相关配置
    """
    
    def __init__(self):
        # 从环境变量获取配置，如果环境变量不存在则使用默认值
        self.app_id: Optional[str] = os.getenv('WECHAT_APP_ID')
        self.app_secret: Optional[str] = os.getenv('WECHAT_APP_SECRET')
        
        # 如果环境变量不存在，尝试从本地配置文件获取
        if not self.app_id or not self.app_secret:
            self._load_from_local_config()
    
    def _load_from_local_config(self):
        """
        从本地配置文件加载配置信息
        注意：在生产环境中不应将敏感信息硬编码在代码中
        """
        config_files = ['wechat_config.ini', 'config/wechat_config.ini']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                config = configparser.ConfigParser()
                config.read(config_file)
                
                if 'wechat' in config:
                    if not self.app_id and 'app_id' in config['wechat']:
                        self.app_id = config['wechat']['app_id']
                    
                    if not self.app_secret and 'app_secret' in config['wechat']:
                        self.app_secret = config['wechat']['app_secret']
                    
                    break
    
    def is_configured(self) -> bool:
        """
        检查是否已配置必要的认证信息
        
        Returns:
            bool: 如果已配置返回True，否则返回False
        """
        return bool(self.app_id and self.app_secret)
    
    def get_app_id(self) -> str:
        """
        获取AppID
        
        Returns:
            str: AppID
            
        Raises:
            ValueError: 如果未配置AppID
        """
        if not self.app_id:
            raise ValueError("未配置微信公众号AppID，请设置环境变量WECHAT_APP_ID或在配置文件中配置")
        return self.app_id
    
    def get_app_secret(self) -> str:
        """
        获取AppSecret
        
        Returns:
            str: AppSecret
            
        Raises:
            ValueError: 如果未配置AppSecret
        """
        if not self.app_secret:
            raise ValueError("未配置微信公众号AppSecret，请设置环境变量WECHAT_APP_SECRET或在配置文件中配置")
        return self.app_secret

# 创建全局配置实例
wechat_config = WeChatConfig()
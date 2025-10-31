import requests
import json
import os
from typing import Optional, Dict, Any
from config import wechat_config

class WeChatPublicationManager:
    """
    微信公众号文章发布管理器
    独立实现以下功能：
    1. 获取access_token
    2. 上传图片素材
    3. 创建草稿
    4. 发布文章
    """
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        初始化微信公众号发布管理器
        
        Args:
            app_id (str, optional): 微信公众号AppID，如果未提供则从配置中获取
            app_secret (str, optional): 微信公众号AppSecret，如果未提供则从配置中获取
        """
        if app_id and app_secret:
            self.app_id = app_id
            self.app_secret = app_secret
        else:
            # 从配置中获取
            self.app_id = wechat_config.get_app_id()
            self.app_secret = wechat_config.get_app_secret()
        
        self.access_token: Optional[str] = None
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
    
    def get_access_token(self) -> str:
        """
        获取微信公众号访问令牌
        
        Returns:
            str: access_token
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "access_token" in data:
            self.access_token = data["access_token"]
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {data}")
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片素材到微信服务器
        
        Args:
            image_path (str): 本地图片路径
            
        Returns:
            str: 图片media_id
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/material/add_material"
        params = {
            "access_token": self.access_token,
            "type": "image"
        }
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        with open(image_path, "rb") as f:
            files = {"media": f}
            response = requests.post(url, params=params, files=files)
            data = response.json()
            
            if "media_id" in data:
                return data["media_id"]
            else:
                raise Exception(f"上传图片失败: {data}")
    
    def create_draft(self, title: str, content: str, thumb_media_id: str) -> str:
        """
        创建草稿文章
        
        Args:
            title (str): 文章标题
            content (str): 文章内容（HTML格式）
            thumb_media_id (str): 封面图片media_id
            
        Returns:
            str: 草稿media_id
            
        Raises:
            Exception: 创建失败时抛出异常
        """
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/draft/add"
        params = {
            "access_token": self.access_token
        }
        
        article_data = {
            "articles": [{
                "title": title,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 1,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
        }
        
        response = requests.post(
            url, 
            params=params,
            data=json.dumps(article_data, ensure_ascii=False).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        if "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"创建草稿失败: {data}")
    
    def publish_draft(self, media_id: str) -> Dict[str, Any]:
        """
        发布草稿文章
        
        Args:
            media_id (str): 草稿media_id
            
        Returns:
            dict: 发布结果
            
        Raises:
            Exception: 发布失败时抛出异常
        """
        if not self.access_token:
            self.get_access_token()
        
        url = f"{self.base_url}/freepublish/submit"
        params = {
            "access_token": self.access_token
        }
        
        data = {
            "media_id": media_id
        }
        
        response = requests.post(
            url,
            params=params,
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        return result
    
    def publish_article(self, title: str, content: str, cover_image_path: str) -> Dict[str, Any]:
        """
        一键发布文章（上传图片 -> 创建草稿 -> 发布文章）
        
        Args:
            title (str): 文章标题
            content (str): 文章内容（HTML格式）
            cover_image_path (str): 封面图片路径
            
        Returns:
            dict: 发布结果
        """
        # 1. 上传封面图片
        thumb_media_id = self.upload_image(cover_image_path)
        
        # 2. 创建草稿
        draft_media_id = self.create_draft(title, content, thumb_media_id)
        
        # 3. 发布文章
        result = self.publish_draft(draft_media_id)
        
        return {
            "thumb_media_id": thumb_media_id,
            "draft_media_id": draft_media_id,
            "publish_result": result
        }
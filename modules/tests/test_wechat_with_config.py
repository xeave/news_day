#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号发布功能测试脚本（使用配置文件方式）
用于测试WeChatPublicationManager类的基本功能，优先使用配置文件
"""

import os
import sys
# 添加上级目录到sys.path以便可以导入config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.publisher.wechat_publication_manager import WeChatPublicationManager
from config import wechat_config

def test_wechat_functionality():
    """
    测试微信公众号发布管理器的基本功能（使用配置文件方式）
    """
    # 检查配置是否已经从配置文件加载
    if not wechat_config.is_configured():
        print("错误：未找到有效的微信配置")
        print("请确保 wechat_config.ini 文件存在且包含正确的 app_id 和 app_secret")
        print("可以参考 wechat_config_example.ini 创建配置文件")
        return False
    
    try:
        # 从配置中获取app_id和app_secret
        app_id = wechat_config.get_app_id()
        app_secret = wechat_config.get_app_secret()
        
        print(f"从配置文件获取到AppID: {app_id[:10]}...")
        print(f"从配置文件获取到AppSecret: {app_secret[:10]}...")
        
        # 初始化管理器
        print("初始化微信公众号发布管理器...")
        manager = WeChatPublicationManager(app_id, app_secret)
        
        # 测试获取access_token
        print("测试获取access_token...")
        token = manager.get_access_token()
        print(f"成功获取access_token: {token[:20]}...")
        
        print("微信公众号发布管理器基础功能测试完成")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def show_usage():
    """
    显示使用说明
    """
    print("微信公众号发布功能测试（配置文件版）")
    print("=" * 40)
    print("使用方法：")
    print("1. 确保 wechat_config.ini 文件存在且配置了正确的参数")
    print("2. 运行测试:")
    print("   python test_wechat_with_config.py")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage()
    else:
        success = test_wechat_functionality()
        if not success:
            sys.exit(1)
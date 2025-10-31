#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号发布功能测试脚本
用于测试WeChatPublicationManager类的基本功能
"""

import os
import sys
from modules.publisher.wechat_publication_manager import WeChatPublicationManager

def test_wechat_functionality():
    """
    测试微信公众号发布管理器的基本功能
    """
    # 从环境变量获取配置
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if not app_id or not app_secret:
        print("错误：请先设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("示例：")
        print("  export WECHAT_APP_ID='your_app_id'")
        print("  export WECHAT_APP_SECRET='your_app_secret'")
        return False
    
    try:
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
    print("微信公众号发布功能测试")
    print("=" * 30)
    print("使用方法：")
    print("1. 设置环境变量:")
    print("   export WECHAT_APP_ID='your_app_id'")
    print("   export WECHAT_APP_SECRET='your_app_secret'")
    print("2. 运行测试:")
    print("   python test_wechat_functionality.py")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage()
    else:
        success = test_wechat_functionality()
        if not success:
            sys.exit(1)
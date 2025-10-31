#!/usr/bin/env python3
"""
新闻联播信息提取与总结 - 本地大模型环境设置脚本
根据"零预算信息提取与总结"文档实现
"""

import os
import sys
import subprocess
from pathlib import Path

def check_conda():
    """检查是否安装了conda"""
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ 检测到 Conda: {result.stdout.strip()}")
            return True
        else:
            print("✗ 未检测到 Conda")
            return False
    except FileNotFoundError:
        print("✗ 未检测到 Conda")
        return False

def install_miniconda():
    """安装Miniconda"""
    print("正在安装 Miniconda...")
    
    # 检查操作系统
    import platform
    system = platform.system()
    
    if system == "Linux":
        script_name = "Miniconda3-latest-Linux-x86_64.sh"
    elif system == "Darwin":
        script_name = "Miniconda3-latest-MacOSX-x86_64.sh"
    else:
        print(f"不支持的操作系统: {system}")
        return False
    
    # 下载Miniconda安装脚本
    try:
        subprocess.run([
            "wget", 
            f"https://repo.anaconda.com/miniconda/{script_name}",
            "-O", script_name
        ], check=True)
        
        # 运行安装脚本
        subprocess.run([
            "bash", script_name, "-b"
        ], check=True)
        
        print("✓ Miniconda 安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Miniconda 安装失败: {e}")
        return False
    except FileNotFoundError:
        print("✗ 未找到 wget 命令，请先安装 wget")
        return False

def create_conda_environment():
    """创建conda环境"""
    print("正在创建conda环境 'llm'...")
    try:
        subprocess.run([
            "conda", "create", "-n", "llm", "python=3.10", "-y"
        ], check=True)
        print("✓ conda环境 'llm' 创建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ conda环境创建失败: {e}")
        return False

def activate_and_install_packages():
    """激活环境并安装依赖包"""
    print("正在安装 llama-cpp-python...")
    try:
        # 在llm环境中安装llama-cpp-python
        subprocess.run([
            "conda", "run", "-n", "llm", 
            "pip", "install", "llama-cpp-python", 
            "--force-reinstall", "--upgrade", "--no-cache-dir",
            "-i", "https://mirrors.aliyun.com/pypi/simple/"
        ], check=True)
        
        print("✓ llama-cpp-python 安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 包安装失败: {e}")
        return False

def download_model():
    """下载模型文件"""
    print("正在下载 Qwen2-7B-Instruct-GGUF 模型...")
    
    # 创建模型目录
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    
    try:
        # 尝试使用huggingface-cli下载模型
        subprocess.run([
            "conda", "run", "-n", "llm",
            "huggingface-cli", "download", 
            "Qwen/Qwen2-7B-Instruct-GGUF", 
            "qwen2-7b-instruct-q4_k_m.gguf",
            "--local-dir", str(models_dir),
            "--local-dir-use-symlinks", "False"
        ], check=True)
        
        print("✓ 模型下载完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 模型下载失败: {e}")
        print("请手动下载模型文件到 ./models 目录")
        return False
    except FileNotFoundError:
        print("✗ 未找到 huggingface-cli，请先安装 transformers 包")
        print("可以运行: conda run -n llm pip install transformers")
        return False

def print_usage_instructions():
    """打印使用说明"""
    instructions = """
====================================================
本地大模型环境设置完成！

使用方法：
1. 激活conda环境:
   conda activate llm

2. 运行新闻摘要脚本:
   python llm_news_summarizer.py

注意事项：
- 首次运行时会自动加载模型，可能需要一些时间
- 模型文件约3.8GB，请确保有足够的磁盘空间
- 如果没有GPU，模型将在CPU上运行（速度较慢但可用）

如需GPU加速（支持CUDA或Metal）：
修改 llm_news_summarizer.py 中的 n_gpu_layers 参数
====================================================
"""
    print(instructions)

def main():
    """主函数"""
    print("新闻联播信息提取与总结 - 本地大模型环境设置")
    print("=" * 50)
    
    # 检查conda
    if not check_conda():
        print("正在安装 Miniconda...")
        if not install_miniconda():
            print("Miniconda 安装失败，退出。")
            return
    
    # 创建conda环境
    if not create_conda_environment():
        print("conda环境创建失败，退出。")
        return
    
    # 安装依赖包
    if not activate_and_install_packages():
        print("依赖包安装失败，退出。")
        return
    
    # 下载模型
    print("\n注意：由于模型文件较大(约3.8GB)，下载可能需要较长时间")
    download_choice = input("是否现在下载模型？(y/n): ")
    if download_choice.lower() == 'y':
        if not download_model():
            print("模型下载失败，请稍后手动下载。")
    
    # 打印使用说明
    print_usage_instructions()

if __name__ == "__main__":
    main()
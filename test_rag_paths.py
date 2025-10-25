#!/usr/bin/env python3
"""
RAG路径测试脚本
用于诊断文档加载问题
"""

import os
import sys
from pathlib import Path

def test_file_path(file_path):
    """测试单个文件路径"""
    print(f"\n=== 测试文件路径: {file_path} ===")

    path = Path(file_path).resolve()

    print(f"原始路径: {file_path}")
    print(f"解析后路径: {path}")

    if not path.exists():
        print("❌ 文件不存在")
        return False

    if not path.is_file():
        print("❌ 路径不是文件")
        return False

    try:
        size = path.stat().st_size
        print(f"✅ 文件存在，大小: {size} bytes")

        # 检查文件扩展名
        ext = path.suffix.lower()
        supported_exts = ['.pdf', '.docx', '.doc', '.md', '.markdown', '.txt', '.json', '.html', '.htm']

        if ext in supported_exts:
            print(f"✅ 支持的文件格式: {ext}")
            return True
        else:
            print(f"❌ 不支持的文件格式: {ext}")
            print(f"支持的格式: {supported_exts}")
            return False

    except Exception as e:
        print(f"❌ 访问文件时出错: {e}")
        return False

def test_directory_path(dir_path):
    """测试目录路径"""
    print(f"\n=== 测试目录路径: {dir_path} ===")

    path = Path(dir_path).resolve()

    print(f"原始路径: {dir_path}")
    print(f"解析后路径: {path}")

    if not path.exists():
        print("❌ 目录不存在")
        return False

    if not path.is_dir():
        print("❌ 路径不是目录")
        return False

    try:
        # 列出目录内容
        items = list(path.iterdir())
        print(f"✅ 目录存在，包含 {len(items)} 个项目")

        # 统计支持的文件
        supported_exts = ['.pdf', '.docx', '.doc', '.md', '.markdown', '.txt', '.json', '.html', '.htm']
        supported_files = []

        for item in items:
            if item.is_file() and item.suffix.lower() in supported_exts:
                supported_files.append(item.name)
                print(f"  📄 支持的文件: {item.name}")

        if supported_files:
            print(f"✅ 找到 {len(supported_files)} 个支持的文档文件")
            return True
        else:
            print("❌ 目录中没有找到支持的文档文件")
            print(f"支持的文件格式: {supported_exts}")
            return False

    except Exception as e:
        print(f"❌ 访问目录时出错: {e}")
        return False

def main():
    print("🔍 RAG文档路径测试工具")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("用法: python test_rag_paths.py <路径1> [路径2] ...")
        print("\n示例:")
        print("  python test_rag_paths.py /path/to/document.pdf")
        print("  python test_rag_paths.py /path/to/documents/")
        print("  python test_rag_paths.py /path/to/file1.pdf /path/to/dir1/")
        return

    # 测试所有提供的路径
    all_paths = sys.argv[1:]

    for path_str in all_paths:
        path = Path(path_str.strip())

        if not path.exists():
            print(f"\n❌ 路径不存在: {path_str}")
            continue

        if path.is_file():
            test_file_path(path_str)
        elif path.is_dir():
            test_directory_path(path_str)
        else:
            print(f"\n❓ 未知路径类型: {path_str}")

if __name__ == "__main__":
    main()

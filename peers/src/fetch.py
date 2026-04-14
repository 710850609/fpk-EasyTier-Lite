#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：整合多个数据源获取 EasyTier 节点列表
"""

import os
import sys

# 添加当前目录到路径，以便导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetchNigger import fetch_nigger
from fetchSbgov import fetch_sbgov


def update_peers():
    """从多个数据源获取节点并合并"""
    print("开始获取节点列表...")
    
    # 并发获取所有数据源
    results = []
    
    try:
        print("\n[1/3] 从 nigger.com.cn 获取...")
        nigger_peers = fetch_nigger()
        print(f"    获取到 {len(nigger_peers)} 个节点")
        results.extend(nigger_peers)
    except Exception as e:
        print(f"    获取失败: {e}")
    
    try:
        print("\n[2/3] 从 sbgov.cn 获取...")
        sbgov_peers = fetch_sbgov()
        print(f"    获取到 {len(sbgov_peers)} 个节点")
        results.extend(sbgov_peers)
    except Exception as e:
        print(f"    获取失败: {e}")
    
    try:
        print("\n[3/3] 从 others.csv 获取...")
        astral_peers = []
        csv_path = os.path.join(os.path.dirname(__file__), 'others.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                # 每行就是一个地址
                if line.startswith(('tcp://', 'udp://')):
                    astral_peers.append(line)
        print(f"    获取到 {len(astral_peers)} 个节点")
        results.extend(astral_peers)
    except Exception as e:
        print(f"    获取失败: {e}")
    
    # 去重并保持顺序
    seen = set()
    unique_peers = []
    for peer in results:
        if peer and peer not in seen:
            seen.add(peer)
            unique_peers.append(peer)
    
    print(f"\n总计获取 {len(results)} 个节点，去重后 {len(unique_peers)} 个")
    
    # 写入文件
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'peer-source.txt')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_peers))
        print(f"文件已成功写入: {output_path}")
    except Exception as e:
        print(f"写入失败: {e}")
    
    print("\n节点列表:")
    for i, peer in enumerate(unique_peers, 1):
        print(f"  {i}. {peer}")
    
    return unique_peers


if __name__ == "__main__":
    update_peers()

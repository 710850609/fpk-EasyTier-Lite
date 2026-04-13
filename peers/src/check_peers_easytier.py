#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 easytier-core 命令检测 EasyTier 节点连通性
通过监控命令输出来判断节点是否可用
"""

import os
import sys
import subprocess
import time
import re
import json
import urllib.request
import zipfile
import shutil

# 设置 Windows 终端 UTF-8 编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# easytier-core 可执行文件路径
# Windows 优先使用 .exe 版本
if sys.platform == 'win32':
    EASYTIER_CORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'bin', 'easytier-core.exe')
    # 如果 .exe 不存在，尝试无扩展名版本
    # if not os.path.exists(EASYTIER_CORE):
    #     EASYTIER_CORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    #                                   'bin', 'easytier-core')
else:
    EASYTIER_CORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'bin', 'easytier-core')


def download_easytier_core():
    """如果本地没有 easytier-core，则从在线下载"""
    if os.path.exists(EASYTIER_CORE):
        return True
    easytier_core_version = '2.6.0'
    github_proxy = "https://ghfast.top/"
    
    print(f"easytier-core 不存在，开始下载...")
    
    # 确定下载地址
    if sys.platform == 'win32':
        download_url = f'{github_proxy}https://github.com/EasyTier/EasyTier/releases/download/v{easytier_core_version}/easytier-windows-x86_64-v{easytier_core_version}.zip'
        executable_name = 'easytier-core.exe'
    else:
        download_url = f'{github_proxy}https://github.com/EasyTier/EasyTier/releases/download/v{easytier_core_version}/easytier-linux-x86_64-v{easytier_core_version}.zip'
        executable_name = 'easytier-core'
    
    # 创建 temp 目录
    peers_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(peers_dir, 'temp')
    bin_dir = os.path.dirname(EASYTIER_CORE)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)
    
    # 下载文件
    zip_path = os.path.join(temp_dir, 'easytier.zip')
    try:
        print(f"下载地址: {download_url}")
        print(f"保存到: {zip_path}")
        urllib.request.urlretrieve(download_url, zip_path)
        print("下载完成，开始解压...")
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        print("解压完成")
        
        # 查找 easytier-core 可执行文件
        extracted_core = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == executable_name:
                    extracted_core = os.path.join(root, file)
                    break
            if extracted_core:
                break
        
        if not extracted_core:
            print(f"错误: 在解压文件中找不到 {executable_name}")
            return False
        
        # 移动到 bin 目录
        shutil.move(extracted_core, EASYTIER_CORE)
        print(f"已移动到: {EASYTIER_CORE}")
        
        # Windows 还需要移动 Packet.dll
        if sys.platform == 'win32':
            extracted_packet_dll = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == 'Packet.dll':
                        extracted_packet_dll = os.path.join(root, file)
                        break
                if extracted_packet_dll:
                    break
            if extracted_packet_dll:
                packet_dll_dest = os.path.join(bin_dir, 'Packet.dll')
                shutil.move(extracted_packet_dll, packet_dll_dest)
                print(f"已移动 Packet.dll 到: {packet_dll_dest}")
        
        # Linux 需要添加执行权限
        if sys.platform != 'win32':
            os.chmod(EASYTIER_CORE, 0o755)
        
        # 清理 temp 目录
        shutil.rmtree(temp_dir)
        print("清理临时文件完成")
        
        return True
        
    except Exception as e:
        print(f"下载或解压失败: {e}")
        return False

# 检测超时时间（秒）
TIMEOUT = 10

# 成功关键字
SUCCESS_KEYWORDS = ['new peer added', 'peer_id:']

# 失败关键字
FAIL_KEYWORDS = ['connect to peer error', 'error', 'failed']


def parse_peer_url(url: str) -> dict:
    """解析 peer URL"""
    match = re.match(r'^(tcp|udp)://([^:]+):(\d+)$', url.strip(), re.IGNORECASE)
    if match:
        return {
            "protocol": match.group(1).upper(),
            "host": match.group(2),
            "port": int(match.group(3)),
            "original": url.strip()
        }
    return None


def check_peer_with_easytier(peer_url: str) -> dict:
    """
    使用 easytier-core 命令检测单个节点
    
    返回: {
        "address": 节点地址,
        "success": 是否成功,
        "latency": 延迟(毫秒),
        "output": 输出日志,
        "error": 错误信息
    }
    """
    result = {
        "address": peer_url,
        "success": False,
        "latency": None,
        "output": [],
        "error": None
    }
    
    # 构建命令
    cmd = [
        EASYTIER_CORE,
        '--console-log-level', 'ERROR',
        '--no-listener',
        '-p', peer_url
    ]
    
    start_time = time.time()
    retry_count = 0
    max_retries = 3  # 最大重试次数
    
    try:
        def start_process():
            if sys.platform == 'win32':
                # Windows: 使用 CREATE_NEW_PROCESS_GROUP 来允许终止进程树
                print(" ".join(cmd))
                return subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                return subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
        
        # 启动进程
        process = start_process()
        
        # 读取输出并监控关键字
        output_lines = []
        success_detected = False
        warned_timeout = False  # 是否已经提示过超时
        last_error = None  # 记录最后的错误信息
        
        while True:
            elapsed = time.time() - start_time
            
            # 超过TIMEOUT强制退出
            if elapsed > TIMEOUT:
                if not success_detected:
                    result["error"] = last_error if last_error else f"检测超时(超过{TIMEOUT}秒)"
                break
            
            # 超过3秒但不到TIMEOUT，提示一下但继续等待
            if elapsed > 3 and not warned_timeout:
                print(f"[等待中{elapsed:.1f}s...]", end='', flush=True)
                warned_timeout = True
            
            # 非阻塞读取输出
            import select
            if sys.platform != 'win32':
                readable, _, _ = select.select([process.stdout], [], [], 0.1)
                if readable:
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        output_lines.append(line)
                        
                        # 检查成功关键字
                        if any(keyword in line.lower() for keyword in SUCCESS_KEYWORDS):
                            result["success"] = True
                            result["latency"] = round((time.time() - start_time) * 1000, 2)
                            success_detected = True
                            break
                        
                        # 检查失败关键字，只记录错误，继续等待
                        if any(keyword in line.lower() for keyword in FAIL_KEYWORDS):
                            last_error = f"连接失败: {line}"
            else:
                # Windows: 使用不同的读取方式
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        line = process.stdout.readline()
                        if line:
                            line = line.strip()
                            output_lines.append(line)
                            
                            if any(keyword in line.lower() for keyword in SUCCESS_KEYWORDS):
                                result["success"] = True
                                result["latency"] = round((time.time() - start_time) * 1000, 2)
                                success_detected = True
                                break
                            
                            # 检查失败关键字，只记录错误，继续等待
                            if any(keyword in line.lower() for keyword in FAIL_KEYWORDS):
                                last_error = f"连接失败: {line}"
                except:
                    pass
                
                # Windows 简单轮询
                time.sleep(0.1)
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    
                    if any(keyword in line.lower() for keyword in SUCCESS_KEYWORDS):
                        result["success"] = True
                        result["latency"] = round((time.time() - start_time) * 1000, 2)
                        success_detected = True
                        break
                    
                    # 检查失败关键字，只记录错误，继续等待
                    if any(keyword in line.lower() for keyword in FAIL_KEYWORDS):
                        last_error = f"连接失败: {line}"
            
            # 检查进程是否已结束，如果结束且还没成功/超时，则重试
            if process.poll() is not None:
                if success_detected:
                    break
                elapsed = time.time() - start_time
                if elapsed < TIMEOUT and retry_count < max_retries:
                    retry_count += 1
                    print(f"[重试 {retry_count}/{max_retries}]", end='', flush=True)
                    # 终止旧进程（如果还没完全结束）
                    try:
                        if sys.platform == 'win32':
                            import signal
                            os.kill(process.pid, signal.CTRL_BREAK_EVENT)
                        else:
                            process.terminate()
                        process.wait(timeout=1)
                    except:
                        pass
                    # 重新启动进程
                    process = start_process()
                    continue
                else:
                    break
        
        # 终止进程
        try:
            if sys.platform == 'win32':
                import signal
                os.kill(process.pid, signal.CTRL_BREAK_EVENT)
            else:
                process.terminate()
            
            # 等待进程结束
            process.wait(timeout=2)
        except:
            try:
                process.kill()
            except:
                pass
        
        result["output"] = output_lines
        
        # 如果没有检测到成功，使用最后的错误信息
        if not success_detected and result["error"] is None:
            result["error"] = last_error if last_error else "未检测到连接结果"
        
        return result
        
    except FileNotFoundError:
        result["error"] = f"找不到 easytier-core: {EASYTIER_CORE}"
        return result
    except Exception as e:
        result["error"] = f"执行错误: {str(e)}"
        return result


def main():
    """主函数"""
    # 检查 easytier-core 是否存在，不存在则下载
    if not download_easytier_core():
        print(f"错误: 无法获取 easytier-core")
        sys.exit(1)
    
    # github_proxy = "https://ghfast.top/"
    # 节点列表文件路径
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    peer_list_path = os.path.join(project_path, 'peers', 'peer-list.txt')
    peer_meta_path = os.path.join(project_path, 'peers', 'peer-meta.json')
    
    # 读取节点列表
    try:
        with open(peer_list_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {peer_list_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)
    
    # 解析所有节点
    peers = []
    for line in lines:
        peer_info = parse_peer_url(line)
        if peer_info:
            peers.append(peer_info["original"])
    
    if not peers:
        print("没有找到有效的 peer 地址")
        sys.exit(0)
    
    print("=" * 60)
    print("    EasyTier Peer 连通性检测 (使用 easytier-core)")
    print("=" * 60)
    print(f"检测节点数: {len(peers)}")
    print(f"超时时间: {TIMEOUT} 秒")
    print()
    
    results = []
    
    # 串行检测（因为 easytier-core 可能会占用端口等资源）
    for peer_url in peers:
        print(f"检测: {peer_url} ... ", end='', flush=True)
        result = check_peer_with_easytier(peer_url)
        results.append(result)
        
        if result["success"]:
            print(f"✓ 连通 ({result['latency']}ms)")
        else:
            error = result.get('error', '未知错误')
            print(f"✗ 不通 [{error}]")
    
    # 统计结果
    connected = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print()
    print("=" * 60)
    print("统计:")
    print(f"  连通: {len(connected)} / {len(results)}")
    print(f"  不通: {len(failed)} / {len(results)}")
    print("=" * 60)
    
    # 输出可用的地址
    if connected:
        print()
        print("可用的地址列表:")
        available_peers = []
        # indexs = {"tcp": 0, "udp": 0}
        index = 0
        
        for r in sorted(connected, key=lambda x: x["latency"] if x["latency"] else float('inf')):
            latency_str = f" ({r['latency']}ms)" if r["latency"] else ""
            print(f"  {r['address']}{latency_str}")
            
            # 解析协议类型
            match = re.match(r'^(tcp|udp)://', r['address'], re.IGNORECASE)
            if match:
                # schema = match.group(1).lower()
                # indexs[schema] += 1
                index += 1
                
                # 保存到文件
                # 使用相对路径，基于项目根目录

                # file_name = f"peer-{index}.txt"
                # file_project_relative_path = f"peers/{file_name}"
                # file_path = os.path.join(project_path, file_project_relative_path)
                # os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # with open(file_path, 'w', encoding='utf-8') as f:
                #     f.write(r['address'])
                
                # available_peers.append({
                #     "url": r['address'], 
                #     "fileName": file_name
                # })
        
        # 保存元数据
        # with open(peer_meta_path, 'w', encoding='utf-8') as f:
        #     meta = {
        #         "count": len(available_peers),
        #         "baseUrl": "https://raw.githubusercontent.com/710850609/EasyTier-Lite/refs/heads/main/peers",
        #         "peers": available_peers,
        #     }
        #     json.dump(meta, f, ensure_ascii=False, indent=2)
    
    # 输出不可用的地址
    if failed:
        print()
        print("不可用的地址列表:")
        for r in failed:
            error_str = f" [{r['error']}]" if r['error'] else ""
            print(f"  {r['address']}{error_str}")


if __name__ == "__main__":
    main()

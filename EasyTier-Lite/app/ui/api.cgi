#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os
import sys
from urllib.parse import quote
import logging


logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 日期格式
    filename='/var/apps/EasyTier-Lite/var/cgi.log',  # 输出到文件
    filemode='a'  # 'a'追加，'w'覆盖
)

def run_cmd(command, *args, shell=False):
    """
    执行命令并返回 JSON 格式结果
    
    Args:
        command: 命令（字符串或列表）
        *args: 命令参数（当 command 为字符串时）
        shell: 是否使用 shell 执行
    
    Returns:
        JSON 字符串: {"code": 状态码, "stdout": 标准输出, "stderr": 错误输出, "success": 是否成功}
    """
    try:
        logging.debug(f"执行命令: {command} {' '.join(args)}")
        # 构建命令列表
        if shell:
            # shell 模式：合并为字符串
            if args:
                full_command = f"{command} {' '.join(args)}"
            else:
                full_command = command
            cmd = full_command
        else:
            # 非 shell 模式：使用列表
            if args:
                cmd = [command] + list(args)
            else:
                cmd = command if isinstance(command, list) else command.split()
        
        # 执行命令
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        if result.returncode == 0:
            output = {
                "code": 0,
                "data": result.stdout.strip() if result.stdout else ""
            }
        else:
            output = {
                "code": result.returncode,
                "data": result.stderr.strip() if result.stderr else "执行失败"
            }
        return output
    except subprocess.TimeoutExpired:
        return {
            "code": -1,
            "data": "命令执行超时"
        }
    except Exception as e:
        logging.error(f"CMD执行错误: {str(e)}\n")
        return {
            "code": -1,
            "data": f"执行错误: {str(e)}"
        }

def http_response(status_code, data):
    """
    返回JSON格式的HTTP响应
    """
    print(f"Status: {status_code}")
    print("Content-Type: application/json; charset=utf-8")
    print("")
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def http_response_file(file_path, mime_type="application/octet-stream", filename=None):
    """CGI 文件下载响应"""
    
    # 检查文件
    if not os.path.isfile(file_path):
        http_response(404, {"code": -1, "data": "File Not Found: " + file_path})
        return
    
    # 文件名处理
    if not filename:
        filename = os.path.basename(file_path)
    
    # RFC 5987 编码（只编码非 ASCII）
    try:
        filename.encode('ascii')
        # 纯 ASCII，简单处理
        disposition = f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        # 含中文，需要编码
        encoded = quote(filename, safe='')
        # 同时提供 filename 和 filename* 兼容所有浏览器
        ascii_name = filename.encode('ascii', 'ignore').decode().replace('"', '')
        disposition = f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded}'
    
    # 文件大小
    file_size = os.path.getsize(file_path)
    
    # ===== 关键：必须先发送状态头 =====
    sys.stdout.buffer.write(b"Status: 200 OK\r\n")
    sys.stdout.buffer.write(f"Content-Type: {mime_type}\r\n".encode())
    sys.stdout.buffer.write(f"Content-Disposition: {disposition}\r\n".encode())
    sys.stdout.buffer.write(f"Content-Length: {file_size}\r\n".encode())
    sys.stdout.buffer.write(b"\r\n")  # 头结束空行
    sys.stdout.buffer.flush()
    
    logging.info(f"下载文件： {file_path}")
    # 流式发送文件
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)  # 64KB 块
                if not chunk:
                    break
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
    except BrokenPipeError:
        pass  # 客户端断开
    except Exception as e:
        logging.error(f"Send file error: {e}\n")
        sys.stderr.write(f"Send file error: {e}\n")
    
    sys.exit(0)  # 确保 CGI 结束

def http_redirect(url, status_code=302):
    """
    重定向到下载URL
    
    Args:
        url: 下载文件的URL地址
        status_code: HTTP状态码，默认为302临时重定向，也可用301永久重定向
    """
    print(f"Status: {status_code}")
    print(f"Location: {url}")
    print("Content-Type: text/html; charset=utf-8")
    print("")

def http_handle():  
    request_uri = os.environ.get('REQUEST_URI', '')
    query_string = os.environ.get('QUERY_STRING', '')
    if 'api.cgi' in request_uri:
        # 提取 api.cgi 后面的路径
        path_part = request_uri.split('api.cgi', 1)[1]
        # 去掉 query string（如果有）
        if '?' in path_part:
            path_info = path_part.split('?', 1)[0]
        else:
            path_info = path_part
        if not path_info:
            path_info = '/'
    else:
        path_info = os.environ.get('PATH_INFO', '/')

    if path_info == '/peer':
        get_peer()
    elif path_info == '/download_win_package':
        download_win_package()
    elif path_info == '/download_android_package':
        download_android_package()
    elif path_info == '/download_config_file':
        download_config_file()
    else:
        http_response(404, {"code": -1, "data": "Not Found: " + path_info})


def get_peer():
    result = run_cmd('/var/apps/EasyTier-Lite/target/bin/easytier-cli --output json peer')
    if result['code'] == 0:
        result['data'] = json.loads(result['data'])
    http_response(200, result)

def download_win_package():
    cmd_file = '/var/apps/EasyTier-Lite/target/ui/cgi/download_win.sh'
    result = run_cmd(f"{cmd_file}")
    if result['code'] != 0:
        http_response(500, f"{result['data']}")
        return
    output_file = result['data'].strip()
    http_response_file(output_file)

def download_android_package():
    http_redirect('https://ghfast.top/https://github.com/EasyTier/EasyTier/releases/latest/download/app-universal-release.apk')

def download_config_file():
    cmd_file = '/var/apps/EasyTier-Lite/target/ui/cgi/download_config.sh'
    result = run_cmd(f"{cmd_file}")
    if result['code'] != 0:
        http_response(500, f"{result['data']}")
        return
    output_file = result['data'].strip()
    http_response_file(output_file, filename='et-fn.toml')


if __name__ == '__main__':
    try:
        http_handle()
    except Exception as e:
        logging.error(f"CGI服务异常: {str(e)}")
        http_response(500, f"CGI服务异常: {str(e)}")

    
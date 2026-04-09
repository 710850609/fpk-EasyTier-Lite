#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import importlib
import json

logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 日期格式
    filename=os.environ.get('LOG_FILE', '/var/apps/EasyTier-Lite/var/cgi.log'),  # 输出到文件
    filemode='a'  # 'a'追加，'w'覆盖
)

# # 激活server虚拟环境
backend_path = os.environ.get('BACKEND_PATH', os.path.join(os.path.dirname(__file__), '..', 'backend'))
backend_path = os.path.abspath(backend_path)
venv_path = os.path.join(backend_path, '.venv')
python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
site_packages = os.path.join(venv_path, 'lib', python_version, 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)
    bin_path = os.path.join(venv_path, 'bin')
    if os.path.exists(bin_path):
        os.environ['PATH'] = bin_path + ':' + os.environ.get('PATH', '')
else:
    logging.error(f"找不到python依赖: {site_packages}")    

# 添加backend目录到Python路径
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
import util.http_util as http_util

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

    path_params = path_info.split('/')
    logging.debug(f"{path_params}")
    if len(path_params) != 3:
        raise AssertionError(f'请求路径有误: {path_info}')
        
    content_type = os.environ.get('CONTENT_TYPE', '')
    content_length_str = os.environ.get('CONTENT_LENGTH', '0')
    content_length = int(content_length_str) if content_length_str else 0
    request_body = ''
    if content_length > 0:
        request_body = sys.stdin.read(content_length)
    request_data = None
    if request_body:
        try:
            request_data = json.loads(request_body)
        except json.JSONDecodeError:
            request_data = None
    if query_string:
        query_params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                query_params[key] = value
        if request_data is None:
            request_data = query_params
        else:
            request_data.update(query_params)
    
    module_name = f"action.{path_params[1]}"
    function_name = path_params[2]
    module = importlib.import_module(module_name)
    func = getattr(module, function_name)    
    # 调用函数，传入解析后的数据
    func(request_data)
   

if __name__ == '__main__':
    try:
        http_handle()
    except AssertionError as e:
        logging.error(f"请求有误",  exc_info=True)
        http_util.http_response_error(f"{str(e)}", 200)
    except Exception as e:
        logging.error(f"CGI服务异常",  exc_info=True)
        http_util.http_response_error(f"CGI服务异常: {str(e)}", 200)
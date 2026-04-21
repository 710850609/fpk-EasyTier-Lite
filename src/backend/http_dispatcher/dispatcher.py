#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CGI模式实现，兼容飞牛CGI应用和普通http服务
"""
import logging
import importlib
import os
import sys
import json
from pathlib import Path
from urllib.parse import quote


class HttpException(Exception):

    def __init__(self, message, status_code=200):
        self.status_code = status_code
        self.message = message

class HttpRequest:

    def __init__(self, method, request_uri, resource_uri, headers=None, query_string=None, request_body=None,
                 module_name=None, function_name=None, function_params=None):
        self.method = method
        self.request_uri = request_uri
        self.resource_uri = resource_uri
        self.headers = headers
        self.query_string = query_string
        self.request_body = request_body
        self.module_name = module_name
        self.function_name = function_name
        self.function_params = self.__build_fun_params()
        pass

    def __build_fun_params(self):
        fun_params = None
        if self.request_body:
            try:
                fun_params = json.loads(self.request_body)
            except json.JSONDecodeError:
                fun_params = None
        query_params = {}
        if self.query_string:
            for param in self.query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
            if fun_params is None:
                fun_params = query_params
            else:
                fun_params.update(query_params)
        return fun_params

class HttpResponse:
    def __init__(self, code=0, data=None, file: str=None, mime_type=None, download_name:str=None, status_code=200, headers={}):
        if data and file:
            raise AssertionError(f"不能同时存在data和file")
        self.code = code
        self.status_code = status_code
        self.headers = headers
        self.data = data
        self.json = {'code': self.code, 'data': self.data}
        self.file = file
        self.download_name = download_name
        self.mime_type = mime_type

    def get_file_disposition(self):
        # 检查文件
        if not self.download_name:
            return None
        disposition = None
        if Path(self.file).is_file():
            # 文件名处理
            filename = self.download_name
            if not filename:
                filename = os.path.basename(self.file)

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
        return disposition

    def output_cgi(self):
        if self.file:
            # 文件大小
            file_size = os.path.getsize(self.file)
            mime_type = self.mime_type or "application/octet-stream"
            # ===== 关键：必须先发送状态头 =====
            sys.stdout.buffer.write(b"Status: 200 OK\r\n")
            sys.stdout.buffer.write(f"Content-Type: {mime_type}\r\n".encode())
            disposition = self.get_file_disposition()
            if disposition:
                sys.stdout.buffer.write(f"Content-Disposition: {disposition}\r\n".encode())
            sys.stdout.buffer.write(f"Content-Length: {file_size}\r\n".encode())
            sys.stdout.buffer.write(b"\r\n")  # 头结束空行
            sys.stdout.buffer.flush()

            # 流式发送文件
            try:
                with open(self.file, "rb") as f:
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
        else:
            sys.stdout.buffer.write(f"Status: {self.status_code}\r\n".encode())
            sys.stdout.buffer.write("Content-Type: application/json; charset=utf-8\r\n".encode())
            sys.stdout.buffer.write("\r\n".encode())
            sys.stdout.buffer.write(json.dumps(self.json, ensure_ascii=False).encode())
        pass

    def to_json(self):
        """返回一个可被 json.dumps 序列化的字典"""
        return json.dumps(self.json, ensure_ascii=False)


def get_request(base_uri="", body_data=None, cgi_module=True) -> HttpRequest:
    # 从环境变量获取http请求参数
    method = os.environ.get('METHOD', '')
    request_uri = os.environ.get('REQUEST_URI', '')
    query_string = os.environ.get('QUERY_STRING', '')

    if not request_uri.startswith(base_uri):
        raise HttpException(f"请求地址必须以{base_uri}开头", 400)
    uri = request_uri.replace(base_uri, '')
    uri_path = uri.split("?", 1)[0].split('/')[1:]

    content_type = os.environ.get('CONTENT_TYPE', '')
    content_length_str = os.environ.get('CONTENT_LENGTH', '0')
    content_length = int(content_length_str) if content_length_str else 0

    request_body = None
    if not cgi_module and body_data:
        request_body = body_data.decode()

    if cgi_module and content_length > 0:
        request_body = sys.stdin.read(content_length)

    request_data = None
    if request_body:
        try:
            request_data = json.loads(request_body)
        except json.JSONDecodeError:
            request_data = None

    query_params = {}
    if query_string:
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                query_params[key] = value
        if request_data is None:
            request_data = query_params
        else:
            request_data.update(query_params)

    module_name = None
    function_name = None
    if len(uri_path) == 3 and uri_path[0] == 'api':
        module_name = f"actions.{uri_path[1]}"
        function_name = uri_path[2]
    return HttpRequest(method=method, request_uri=request_uri, resource_uri = '/'.join(uri_path),
                       headers=None, query_string=query_string, request_body=request_body,
                       module_name=module_name, function_name=function_name, function_params=request_data)

def http_handle(base_uri="/", body_data=None, cgi_module=True) -> HttpResponse:
    response = HttpResponse()
    try:
        request = get_request(base_uri, body_data, cgi_module)
        module_name = request.module_name
        function_name = request.function_name
        if not module_name and not function_name:
            resource_uri = request.resource_uri
            if '..' in resource_uri:
                raise HttpException(status_code=403, message=f"不允许访问资源： {request.request_uri}")
            frontend_path = os.environ.get('FRONTEND_PATH', '')
            if len(resource_uri) == 0:
                resource_uri = 'index.html'
            resource_path = Path(frontend_path).joinpath(resource_uri).absolute()
            if not resource_path.exists() or resource_path.is_dir():
                raise HttpException(status_code=404, message=f"资源不存在： {request.request_uri}")
            response = HttpResponse(file=str(resource_path))
        else:
            function_params = request.function_params
            logging.debug(f"request: {request.__dict__}")
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            response = func(function_params)
            if not isinstance(response, HttpResponse):
                response = HttpResponse(data=response)
    except Exception as e:
        if isinstance(e, HttpException):
            logging.exception(e)
            response = HttpResponse(code=1, status_code=e.status_code, data=e.message)
        else:
            logging.exception("服务异常")
            response = HttpResponse(code=1, data=str(e))
    finally:
        logging.debug(f"response: {response.__dict__}")
        if cgi_module:
            response.output_cgi()
        return response

if __name__ == '__main__':
    http_handle()

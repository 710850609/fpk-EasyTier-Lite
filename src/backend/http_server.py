#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
import http_dispatcher.dispatcher as http_dispatcher

# 配置日志
# Windows 控制台编码处理
if sys.platform == 'win32':
    import io
    # 强制 stdout/stderr 使用 utf-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def setup_env(base_uri: str):
    global BASE_URI, FRONTEND_PATH, CONFIG_DIR, CORE_DIR, DATA_DIR, LOG_DIR
        # BACKEND_PATH, FRONTEND_PATH, LOG_FILE, ET_BIN_DIR, LOG_DIR, CONFIG_DIR, DATA_DIR, PACKAGE_PATH
    BASE_URI = base_uri
    # 是否在 PyInstaller 打包环境中
    WORK_DIR = None
    if getattr(sys, 'frozen', False):
        print("打包模式运行...")
        # _MEIPASS 是 PyInstaller 解压资源的临时目录
        WORK_DIR = str(Path(os.path.dirname(sys.executable)).absolute())
        Path(WORK_DIR).mkdir(parents=True, exist_ok=True)
        FRONTEND_PATH = os.path.abspath(os.path.join(sys._MEIPASS, 'frontend'))
        # BACKEND_PATH = WORK_DIR
        # PACKAGE_PATH = str(sys._MEIPASS)
    else:
        print("本地模式运行...")
        project_root_path = Path(__file__).absolute().parent.parent.parent
        WORK_DIR = str(project_root_path.joinpath('temp').joinpath('EasyTier-Lite').absolute())
        Path(WORK_DIR).mkdir(parents=True, exist_ok=True)
        FRONTEND_PATH = str(project_root_path.joinpath('frontend').joinpath('dist'))
        # BACKEND_PATH = str(Path(__file__).absolute().parent)
        # PACKAGE_PATH = ''

    CORE_DIR = os.path.join(WORK_DIR, 'core')
    CONFIG_DIR = os.path.join(WORK_DIR, 'config')
    DATA_DIR = os.path.join(WORK_DIR, 'data')
    LOG_DIR = os.path.join(WORK_DIR, 'logs')

    Path(CORE_DIR).mkdir(parents=True, exist_ok=True)
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    LOG_FILE = os.path.join(LOG_DIR, 'server.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),  # 输出到文件
            logging.StreamHandler(sys.stdout)  # 输出到控制台
        ]
    )

    logging.info(f"BASE_URI: {BASE_URI}")
    # logging.info(f"BACKEND_PATH: {BACKEND_PATH}")
    logging.info(f"FRONTEND_PATH: {FRONTEND_PATH}")
    logging.info(f"CORE_DIR: {CORE_DIR}")
    logging.info(f"CONFIG_DIR: {CONFIG_DIR}")
    logging.info(f"DATA_DIR: {DATA_DIR}")
    logging.info(f"LOG_FILE: {LOG_FILE}")


class CGIProxyHandler(BaseHTTPRequestHandler):
    """处理 HTTP 请求并转发给 CGI 脚本"""
    
    def do_GET(self):
        """处理 GET 请求"""
        self.handle_request()
    
    def do_POST(self):
        """处理 POST 请求"""
        self.handle_request()
    
    def handle_request(self):
        """处理请求的核心逻辑"""
        try:
            # 解析请求路径
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            # 构建完整的 REQUEST_URI
            request_uri = path
            if parsed_path.query:
                request_uri = f"{path}?{parsed_path.query}"
            self.run_cgi(parsed_path.query, request_uri)
                
        except Exception as e:
            logging.error(f"Request handling error: {e}", exc_info=True)
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def run_cgi(self, query_string, request_uri):
        """执行 CGI 脚本并返回结果"""
        try:
            # 获取请求体（POST 请求）
            stdin_data = None
            content_length = self.headers.get('Content-Length')
            if self.command == 'POST' and content_length:
                try:
                    content_length = int(content_length)
                    if content_length > 0:
                        stdin_data = self.rfile.read(content_length)
                except ValueError:
                    pass
            
            # 构建环境变量
            env = os.environ.copy()
            env.update({
                'FRONTEND_PATH': FRONTEND_PATH,
                # 'PACKAGE_PATH': PACKAGE_PATH,
                # 'BACKEND_PATH': BACKEND_PATH,
                'CONFIG_DIR': CONFIG_DIR,
                'CORE_DIR': CORE_DIR,
                'DATA_DIR': DATA_DIR,
                'LOG_DIR': LOG_DIR,

                'REQUEST_METHOD': self.command,
                'QUERY_STRING': query_string,
                'REQUEST_URI': request_uri,
                'SERVER_PROTOCOL': self.request_version,
                'SERVER_NAME': self.headers.get('Host', 'localhost').split(':')[0],
                'SERVER_PORT': str(self.server.server_port),
                'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                'CONTENT_LENGTH': str(content_length) if content_length else '',
                'HTTP_HOST': self.headers.get('Host', ''),
                'HTTP_USER_AGENT': self.headers.get('User-Agent', ''),
                'HTTP_ACCEPT': self.headers.get('Accept', ''),
                'HTTP_ACCEPT_ENCODING': self.headers.get('Accept-Encoding', ''),
                'HTTP_ACCEPT_LANGUAGE': self.headers.get('Accept-Language', ''),
                'HTTP_COOKIE': self.headers.get('Cookie', ''),
                'HTTP_REFERER': self.headers.get('Referer', ''),
                'HTTP_X_FORWARDED_FOR': self.headers.get('X-Forwarded-For', ''),
                'HTTP_X_REAL_IP': self.headers.get('X-Real-IP', ''),
            })
            
            # 添加所有以 HTTP_ 开头的自定义头
            for header, value in self.headers.items():
                header_key = f"HTTP_{header.upper().replace('-', '_')}"
                if header_key not in env:
                    env[header_key] = value

            for item in env.items():
                os.environ[item[0]] = item[1]

            resp = http_dispatcher.http_handle(base_uri=BASE_URI, body_data=stdin_data, cgi_module=False)
            self.send_response(resp.status_code)
            if resp.file:
                ext = resp.file.split(".")[-1].lower()
                mime_map = {
                    "html": "text/html; charset=utf-8",
                    "css": "text/css; charset=utf-8",
                    "js": "application/javascript; charset=utf-8",
                    "json": "application/json; charset=utf-8",
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "gif": "image/gif",
                    "svg": "image/svg+xml",
                    "woff": "font/woff",
                    "woff2": "font/woff2",
                }
                mime = mime_map.get(ext, "application/octet-stream")
                self.send_header('Content-type', mime)
                disposition = resp.get_file_disposition()
                if disposition:
                    self.send_header('Content-Disposition', disposition)
            else:
                self.send_header('Content-Type', 'application/json; charset=utf-8')

            self.end_headers()
            # 发送内容
            if resp.file:
                with open(resp.file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(json.dumps(resp.json, ensure_ascii=False, indent=2).encode())

        except Exception as e:
            logging.error(f"CGI execution error: {e}", exc_info=True)
            self.send_error(500, f"CGI execution error: {str(e)}")
    
    # def send_cgi_output(self, output):
    #     """解析并发送 CGI 输出"""
    #     try:
    #         # 查找头部和内容的分隔符
    #         header_end = output.find(b'\r\n\r\n')
    #         if header_end == -1:
    #             header_end = output.find(b'\n\n')
    #
    #         if header_end != -1:
    #             headers_part = output[:header_end]
    #             content = output[header_end + 2:]  # 跳过空行
    #
    #             # 解析头部
    #             headers = headers_part.decode('utf-8', errors='ignore').splitlines()
    #             status_code = 200
    #             content_type_sent = False
    #
    #             for line in headers:
    #                 line = line.strip()
    #                 if not line:
    #                     continue
    #
    #                 # 检查状态行
    #                 if line.lower().startswith('status:'):
    #                     try:
    #                         parts = line.split(':', 1)
    #                         status_part = parts[1].strip()
    #                         status_code = int(status_part.split()[0])
    #                     except (ValueError, IndexError):
    #                         pass
    #                 # 检查 Content-Type
    #                 elif line.lower().startswith('content-type'):
    #                     content_type_sent = True
    #                     # 先发送状态码，再发送头部
    #                     self.send_response(status_code)
    #                     header_name = line.split(':', 1)[0].strip()
    #                     header_value = line.split(':', 1)[1].strip()
    #                     # 确保 header 值是 latin-1 编码
    #                     header_value = header_value.encode('utf-8').decode('latin-1', 'replace')
    #                     self.send_header(header_name, header_value)
    #                 elif ':' in line:
    #                     if not content_type_sent:
    #                         self.send_response(status_code)
    #                         content_type_sent = True
    #                     header_name = line.split(':', 1)[0].strip()
    #                     header_value = line.split(':', 1)[1].strip()
    #                     # 确保 header 值是 latin-1 编码
    #                     header_value = header_value.encode('utf-8').decode('latin-1', 'replace')
    #                     self.send_header(header_name, header_value)
    #
    #             # 如果没有找到任何头部，发送默认响应
    #             if not content_type_sent:
    #                 self.send_response(status_code)
    #                 self.send_header('Content-Type', 'text/plain; charset=utf-8')
    #
    #             self.end_headers()
    #
    #             # 发送内容
    #             self.wfile.write(content)
    #         else:
    #             # 没有找到头部，直接输出内容
    #             self.send_response(200)
    #             self.end_headers()
    #             self.wfile.write(output)
                
        except Exception as e:
            logging.error(f"Error sending CGI output: {e}", exc_info=True)
            # 如果解析失败，直接输出原始内容
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output)
            except:
                self.send_error(500, "Failed to process CGI output")
    
    def log_message(self, format, *args):
        """重写日志方法"""
        logging.debug(f"{self.address_string()} - {format % args}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """支持多线程的 HTTP 服务器"""
    daemon_threads = True
    allow_reuse_address = True

def start_server(host='127.0.0.1', port=18080, base_uri=None):
    """启动 HTTP 服务器"""
    if base_uri is None:
        base_uri = "/cgi/ThirdParty/EasyTier-Lite/index.cgi"
    setup_env(base_uri)
    logging.info(f"HTTP服务启动中....")
    server = ThreadedHTTPServer((host, port), CGIProxyHandler)
    logging.info(f"Starting HTTP server on {host}:{port}")
    logging.info(f"Virtual base URI: {BASE_URI}")
    acc_host = host
    if acc_host == '0.0.0.0':
        acc_host = '127.0.0.1'
    logging.info(f"local access http://{acc_host}:{port}{base_uri}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='CGI Proxy HTTP Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=18080, help='Port to bind to (default: 18080)')
    args = parser.parse_args()
    start_server(args.host, args.port)
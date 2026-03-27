#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging


# 虚拟 base URI
BASE_URI = "/cgi/ThirdParty/EasyTier-Lite"
PARENT_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# CGI 文件真实路径
CGI_INDEX = os.path.join(PARENT_PROJECT_PATH, 'EasyTier-Lite', 'app', 'ui', 'index.cgi')
CGI_API = os.path.join(PARENT_PROJECT_PATH, 'EasyTier-Lite', 'app', 'ui', 'api.cgi')
BACKEND_PATH = os.path.join(PARENT_PROJECT_PATH, 'server')
LOG_FILE = os.path.join(PARENT_PROJECT_PATH, 'server.log')
BIN_DIR = os.path.join(PARENT_PROJECT_PATH, 'EasyTier-Lite', 'app', 'bin')


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=LOG_FILE,  # 输出到文件
)

logging.info(f"BACKEND_PATH: {BACKEND_PATH}")
logging.info(f"LOG_FILE: {LOG_FILE}")
logging.info(f"BIN_DIR: {BIN_DIR}")

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
            
            # 检查是否以 BASE_URI 开头
            if not path.startswith(BASE_URI):
                self.send_error(404, f"Path must start with {BASE_URI}")
                return
            
            # 提取 BASE_URI 之后的路径作为 PATH_INFO
            path_info = path[len(BASE_URI):]
            if not path_info or path_info == "/":
                path_info = "/"
            
            # 构建完整的 REQUEST_URI
            request_uri = path
            if parsed_path.query:
                request_uri = f"{path}?{parsed_path.query}"
            
            # logging.debug(f"Request: path={path}, path_info={path_info}, query={parsed_path.query}")
            
            # 根据路径决定调用哪个 CGI
            # 如果 path_info 以 /index.cgi 开头，使用 index.cgi
            if path_info.startswith("/index.cgi"):
                cgi_script = CGI_INDEX
                # 保持原有的 path_info 不变，让 index.cgi 自己解析
                cgi_path_info = path_info
            # 如果 path_info 以 /api.cgi 开头，使用 api.cgi
            elif path_info.startswith("/api.cgi"):
                cgi_script = CGI_API
                # 保持原有的 path_info 不变，让 api.cgi 自己解析
                cgi_path_info = path_info
            else:
                # 默认当作 index.cgi 处理（兼容根路径访问）
                cgi_script = CGI_INDEX
                cgi_path_info = path_info
            
            # logging.debug(f"Routing to: {cgi_script}, cgi_path_info={cgi_path_info}")
            self.run_cgi(cgi_script, cgi_path_info, parsed_path.query, request_uri)
                
        except Exception as e:
            logging.error(f"Request handling error: {e}", exc_info=True)
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def run_cgi(self, cgi_script, path_info, query_string, request_uri):
        """执行 CGI 脚本并返回结果"""
        try:
            # 检查 CGI 文件是否存在
            if not os.path.isfile(cgi_script):
                self.send_error(404, f"CGI script not found: {cgi_script}")
                return
            
            # 检查是否可执行
            if not os.access(cgi_script, os.X_OK):
                try:
                    os.chmod(cgi_script, 0o755)
                except Exception as e:
                    logging.warning(f"Failed to chmod {cgi_script}: {e}")
            
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
                'BIN_DIR': BIN_DIR,
                'BACKEND_PATH': BACKEND_PATH,
                'LOG_FILE': LOG_FILE,
                'REQUEST_METHOD': self.command,
                'SCRIPT_NAME': cgi_script,
                'SCRIPT_FILENAME': cgi_script,
                'PATH_INFO': path_info,
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
            
            # logging.debug(f"Running CGI: {cgi_script}")
            # logging.debug(f"PATH_INFO: {path_info}")
            # logging.debug(f"QUERY_STRING: {query_string}")
            
            # 执行 CGI 脚本
            proc = subprocess.Popen(
                [cgi_script],
                stdin=subprocess.PIPE if stdin_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=os.path.dirname(cgi_script)
            )
            
            # 等待执行完成（设置超时）
            try:
                stdout, stderr = proc.communicate(input=stdin_data, timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                logging.error(f"CGI script timeout: {cgi_script}")
                self.send_error(500, "CGI script timeout")
                return
            
            # 记录 stderr 输出
            if stderr:
                stderr_str = stderr.decode('utf-8', errors='ignore')
                logging.warning(f"CGI stderr from {cgi_script}: {stderr_str}")
            
            # 解析 CGI 输出
            self.send_cgi_output(stdout)
                
        except Exception as e:
            logging.error(f"CGI execution error: {e}", exc_info=True)
            self.send_error(500, f"CGI execution error: {str(e)}")
    
    def send_cgi_output(self, output):
        """解析并发送 CGI 输出"""
        try:
            # 查找头部和内容的分隔符
            header_end = output.find(b'\r\n\r\n')
            if header_end == -1:
                header_end = output.find(b'\n\n')
            
            if header_end != -1:
                headers_part = output[:header_end]
                content = output[header_end + 2:]  # 跳过空行
                
                # 解析头部
                headers = headers_part.decode('utf-8', errors='ignore').splitlines()
                status_code = 200
                content_type_sent = False
                
                for line in headers:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查状态行
                    if line.lower().startswith('status:'):
                        try:
                            parts = line.split(':', 1)
                            status_part = parts[1].strip()
                            status_code = int(status_part.split()[0])
                        except (ValueError, IndexError):
                            pass
                    # 检查 Content-Type
                    elif line.lower().startswith('content-type'):
                        content_type_sent = True
                        # 先发送状态码，再发送头部
                        self.send_response(status_code)
                        self.send_header(line.split(':', 1)[0].strip(), line.split(':', 1)[1].strip())
                    elif ':' in line:
                        if not content_type_sent:
                            self.send_response(status_code)
                            content_type_sent = True
                        self.send_header(line.split(':', 1)[0].strip(), line.split(':', 1)[1].strip())
                
                # 如果没有找到任何头部，发送默认响应
                if not content_type_sent:
                    self.send_response(status_code)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                
                self.end_headers()
                
                # 发送内容
                self.wfile.write(content)
            else:
                # 没有找到头部，直接输出内容
                self.send_response(200)
                self.end_headers()
                self.wfile.write(output)
                
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

def start_server(host='0.0.0.0', port=8080):
    """启动 HTTP 服务器"""
    server = HTTPServer((host, port), CGIProxyHandler)
    
    # 验证 CGI 文件是否存在
    if not os.path.exists(CGI_INDEX):
        logging.warning(f"index.cgi not found: {CGI_INDEX}")
    else:
        logging.info(f"index.cgi found: {CGI_INDEX}")
    
    if not os.path.exists(CGI_API):
        logging.warning(f"api.cgi not found: {CGI_API}")
    else:
        logging.info(f"api.cgi found: {CGI_API}")
    
    logging.info(f"Starting HTTP server on {host}:{port}")
    logging.info(f"Virtual base URI: {BASE_URI}")
    logging.info(f"Requests will be proxied to CGI scripts based on path")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        server.shutdown()

if __name__ == '__main__':
    import argparse    
    parser = argparse.ArgumentParser(description='CGI Proxy HTTP Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5666, help='Port to bind to (default: 5666)')    
    args = parser.parse_args()    
    start_server(args.host, args.port)
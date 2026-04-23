# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# import json
# import logging
# import os
# import sys
# from urllib.parse import quote
#
#
# def http_response(status_code, data):
#     """
#     返回JSON格式的HTTP响应
#     """
#     print(f"Status: {status_code}")
#     print("Content-Type: application/json; charset=utf-8")
#     print("")
#     print(json.dumps(data, ensure_ascii=False))
#     sys.exit(0)
#
# def http_response_ok(data):
#     http_response(200, {"code": 0, "data": data})
#
# def http_response_error(data, status_code=200):
#     http_response(status_code, {"code": -1, "data": data})
#
#
# def http_response_file(file_path, mime_type="application/octet-stream", filename=None):
#     """CGI 文件下载响应"""
#
#     logging.info(f"下载文件： {file_path}")
#     # 检查文件
#     if not os.path.isfile(file_path):
#         http_response_error("File Not Found: " + file_path)
#         return
#
#     # 文件名处理
#     if not filename:
#         filename = os.path.basename(file_path)
#
#     # RFC 5987 编码（只编码非 ASCII）
#     try:
#         filename.encode('ascii')
#         # 纯 ASCII，简单处理
#         disposition = f'attachment; filename="{filename}"'
#     except UnicodeEncodeError:
#         # 含中文，需要编码
#         encoded = quote(filename, safe='')
#         # 同时提供 filename 和 filename* 兼容所有浏览器
#         ascii_name = filename.encode('ascii', 'ignore').decode().replace('"', '')
#         disposition = f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded}'
#
#     # 文件大小
#     file_size = os.path.getsize(file_path)
#
#     # ===== 关键：必须先发送状态头 =====
#     sys.stdout.buffer.write(b"Status: 200 OK\r\n")
#     sys.stdout.buffer.write(f"Content-Type: {mime_type}\r\n".encode())
#     sys.stdout.buffer.write(f"Content-Disposition: {disposition}\r\n".encode())
#     sys.stdout.buffer.write(f"Content-Length: {file_size}\r\n".encode())
#     sys.stdout.buffer.write(b"\r\n")  # 头结束空行
#     sys.stdout.buffer.flush()
#
#     # 流式发送文件
#     try:
#         with open(file_path, "rb") as f:
#             while True:
#                 chunk = f.read(65536)  # 64KB 块
#                 if not chunk:
#                     break
#                 sys.stdout.buffer.write(chunk)
#                 sys.stdout.buffer.flush()
#     except BrokenPipeError:
#         pass  # 客户端断开
#     except Exception as e:
#         logging.error(f"Send file error: {e}\n")
#         sys.stderr.write(f"Send file error: {e}\n")
#
#     sys.exit(0)  # 确保 CGI 结束
#
# def http_redirect(url, status_code=302):
#     """
#     重定向到下载URL
#
#     Args:
#         url: 下载文件的URL地址
#         status_code: HTTP状态码，默认为302临时重定向，也可用301永久重定向
#     """
#     print(f"Status: {status_code}")
#     print(f"Location: {url}")
#     print("Content-Type: text/html; charset=utf-8")
#     print("")
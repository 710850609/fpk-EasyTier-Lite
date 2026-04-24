import logging
import os
import sys
import platform
import signal
import webbrowser
import threading

import http_server
from PIL import Image, ImageDraw




# 全局图标引用，用于信号处理
_global_icon = None
_global_server = None


host='127.0.0.1'
port=5666
base_url = '/cgi/ThirdParty/EasyTier-Lite/index.cgi'

def start_web():
    def web_server():
        global _global_server
        _global_server = http_server.build_server(host, port, base_url)
        try:
            _global_server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
            _global_server.shutdown()

    server_thread = threading.Thread(target=web_server, daemon=True)
    server_thread.start()
    return server_thread

def stop_web():
    if _global_server:
        logging.info(f"停止Web服务...")
        _global_server.shutdown()


# --- 1. 定义菜单项的功能 ---
def on_open_browser(icon, item):
    """点击菜单时，用默认浏览器打开指定网址"""
    webbrowser.open(f'http://{host}:{port}{base_url}')

def on_quit(icon, item):
    """点击菜单时，退出程序"""
    stop_web()
    icon.stop()
    _stop_event.set()  # 通知主线程退出

def get_resource_dir():
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys._MEIPASS)
    return os.path.abspath(os.path.dirname(__file__))

# --- 2. 创建托盘图标 ---
def create_image():
    """加载应用图标"""
    import os
    # 获取图标路径（支持开发和打包后的环境）
    icon_path = os.path.join(get_resource_dir(), 'assets', 'icon.png')
    
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    else:
        # 如果找不到图标，生成默认图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'dodgerblue')
        draw = ImageDraw.Draw(image)
        draw.rectangle((width/4, height/4, width*3/4, height*3/4), fill='white')
        return image

def setup_tray_icon():
    global _global_icon

    # 设置 pystray 后端为 gtk 以支持中文（X11 后端使用 latin-1 编码，不支持中文）
    # 可选后端: appindicator, gtk, xorg, darwin, win32
    # os.environ['PYSTRAY_BACKEND'] = 'gtk'
    try:
        import pystray
    except Exception as e:
        if "Namespace AyatanaAppIndicator3 not available" in str(e):
            # 强制使用 GTK 后端（避免 AppIndicator 缺失问题）
            # 必须在 import pystray 之前设置
            if platform.system() == "Linux":
                os.environ['PYSTRAY_BACKEND'] = 'gtk'
                print(f"{e}。强制Linux使用 GTK 环境")
                import pystray
        else:
            print(f"pystray 模块加载失败，无法使用托盘图标功能: {e}")
            raise ImportError("pystray 模块加载失败") from e
    
    # 根据环境选择语言
    use_chinese = not is_x11_backend()
    
    try:
        if use_chinese:
            menu = pystray.Menu(
                pystray.MenuItem('打开主页', on_open_browser),
                pystray.MenuItem('退出', on_quit)
            )
            icon = pystray.Icon("易组网", create_image(), "易组网", menu)
        else:
            menu = pystray.Menu(
                pystray.MenuItem('Open Web', on_open_browser),
                pystray.MenuItem('Quit', on_quit)
            )
            icon = pystray.Icon("EasyTierLite", create_image(), "EasyTierLite", menu)
        
        _global_icon = icon
        icon.run()
    except Exception as e:
        print(f"Tray icon error: {e}")
        print("Note: System tray requires a desktop environment")


# 检测是否为 X11 环境
def is_x11_backend():
    """检测当前是否使用 X11 后端（不支持中文）"""
    # 如果强制使用了 GTK 后端，返回 False（支持中文）
    if os.environ.get('PYSTRAY_BACKEND') == 'gtk':
        return False

    # 检查环境变量
    if os.environ.get('PYSTRAY_BACKEND') == 'xorg':
        return True

    # 检查 DISPLAY 环境变量（X11 特征）
    if os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        return sys.platform.startswith('linux')

    return False

def start_tray():
    """启动托盘图标（如果支持）"""
    try:
        tray_thread = threading.Thread(target=setup_tray_icon, daemon=True)
        tray_thread.start()
        return tray_thread
    except Exception as e:
        print(f"Failed to start tray: {e}")
        return None

# 全局停止标志
_stop_event = threading.Event()

def setup_windows_console_handler():
    """Windows 控制台关闭事件处理"""
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        
        # Windows 控制台控制信号
        CTRL_C_EVENT = 0
        CTRL_BREAK_EVENT = 1
        CTRL_CLOSE_EVENT = 2
        
        handler_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)
        
        def handler(ctrl_type):
            if ctrl_type in (CTRL_C_EVENT, CTRL_BREAK_EVENT, CTRL_CLOSE_EVENT):
                logging.info("收到退出信号，正在关闭...")
                stop_web()
                if _global_icon:
                    _global_icon.stop()
                _stop_event.set()
                return True
            return False
        
        # 设置控制台控制处理程序
        kernel32 = ctypes.windll.kernel32
        SetConsoleCtrlHandler = kernel32.SetConsoleCtrlHandler
        SetConsoleCtrlHandler.argtypes = [handler_type, wintypes.BOOL]
        SetConsoleCtrlHandler.restype = wintypes.BOOL
        
        # 创建处理函数实例并保持引用
        _handler_instance = handler_type(handler)
        SetConsoleCtrlHandler(_handler_instance, True)
        return _handler_instance
    return None

def setup():
    # --- 3. 主程序启动托盘线程 ---
    # 注册 Ctrl+C 信号处理（必须在主线程）
    def signal_handler(sig, frame):
        logging.info("收到退出信号，正在关闭...")
        stop_web()
        if _global_icon:
            _global_icon.stop()
        _stop_event.set()
        sys.exit(0)

    if sys.platform == 'win32':
        # Windows 使用控制台事件处理
        _win_handler = setup_windows_console_handler()
    else:
        # Linux/macOS 使用信号
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    tray_thread = start_tray()
    start_web()
    webbrowser.open(f'http://{host}:{port}{base_url}')
    if tray_thread:
        # 使用事件等待，支持中断
        try:
            while not _stop_event.is_set():
                _stop_event.wait(1)
        except KeyboardInterrupt:
            print("\n收到 KeyboardInterrupt，正在关闭...")
    else:
        print("Running without system tray...")
        # 保持程序运行
        while not _stop_event.is_set():
            try:
                _stop_event.wait(1)
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    setup()
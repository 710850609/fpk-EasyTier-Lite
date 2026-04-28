package main

import (
    "bytes"
	"embed"
	"image"
	"image/color"
	"image/png"
	"log"
	"net/http"
    "fmt"
    "io/ioutil"
    "path/filepath"
    "runtime"
	"os"
	"os/signal"
	"os/exec"
	"syscall"
	"fyne.io/systray"
	"github.com/pkg/browser"
)

//go:embed assets/icon.ico
var embeddedIcon []byte

//go:embed dist/easytier-lite*
var binFS embed.FS

const (
	host     = "127.0.0.1"
	port     = "5666"
	baseURL  = "/cgi/ThirdParty/EasyTier-Lite/index.cgi"
	appName  = "易组网"
// 	runWeb   = "./EasyTier-Lite-Web.exe"
)

var (
	server   *http.Server
	cmd    *exec.Cmd
)

func main() {
	// 信号处理：Ctrl+C 或 SIGTERM 触发退出
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigCh
		systray.Quit()
	}()

	// systray.Run 会阻塞，onReady 中初始化一切
	systray.Run(onReady, onExit)
}

func onReady() {
	systray.SetTitle(appName)
	systray.SetTooltip(appName)

	// 设置图标
	iconData := getIcon()
	systray.SetIcon(iconData)

	// 菜单（中文，无编码问题）
	menuOpen := systray.AddMenuItem("打开主页", "在浏览器中打开管理页面")
	menuQuit := systray.AddMenuItem("退出", "关闭程序")

	// 启动 Web 服务
	startWebServer()

	// 自动打开浏览器
	openBrowser()

	// 菜单事件处理
	go func() {
		for {
			select {
			case <-menuOpen.ClickedCh:
				openBrowser()
			case <-menuQuit.ClickedCh:
				systray.Quit()
				return
			}
		}
	}()
}

func onExit() {
	// 优雅关闭 Web 服务
	stopWebServer()
}

// 根据系统返回要嵌入的文件名
func webBinaryName() string {
    ext := ""
    if runtime.GOOS == "windows" {
        ext = ".exe"
    }
    return fmt.Sprintf("dist/easytier-lite-web%s", ext)
}
// 将嵌入的后端程序提取到临时文件，返回路径
func extractWebBinary() (string, error) {
    name := webBinaryName()
    data, err := binFS.ReadFile(name)
    if err != nil {
        return "", fmt.Errorf("未找到适用于 %s/%s 的 Web 后端: %v", runtime.GOOS, runtime.GOARCH, err)
    }

    // 写入临时目录
    tmpDir := filepath.Join(os.TempDir(), "easytier-lite")
    os.MkdirAll(tmpDir, 0755)
    path := filepath.Join(tmpDir, filepath.Base(name))
    if err := ioutil.WriteFile(path, data, 0755); err != nil {
        return "", err
    }
    return path, nil
}
// --- Web 服务器 ---
func startWebServer() {
	    path, err := extractWebBinary()
    if err != nil {
        log.Printf("无法提取 Web 后端: %v", err)
        return
    }

    cmd = exec.Command(path, "--port", port)
    // 可选：将外部程序的输出重定向到当前程序的输出，方便调试
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr

    log.Println("正在启动外部Web服务...")
    if err := cmd.Start(); err != nil {
        log.Printf("启动Web服务失败: %v", err)
        return
    }
    log.Printf("外部Web服务已启动，PID: %d\n", cmd.Process.Pid)

    // 在后台 Goroutine 中等待进程结束，确保资源释放
    go func() {
        if err := cmd.Wait(); err != nil {
            log.Printf("外部Web服务退出，错误: %v", err)
        } else {
            log.Println("外部Web服务已正常退出")
        }
    }()
}

func stopWebServer() {
	if cmd != nil && cmd.Process != nil {
        log.Println("正在停止外部Web服务...")
        // 在Windows上，Kill() 是唯一终止外部子进程的方式
        if err := cmd.Process.Kill(); err != nil {
            log.Printf("停止Web服务失败: %v", err)
        }
    }
}

func openBrowser() {
	url := "http://" + host + ":" + port + baseURL
	browser.OpenURL(url)
}

// --- 图标处理 ---

func getIcon() []byte {
	// 尝试使用嵌入的图标文件
	if len(embeddedIcon) > 0 {
	    //
	}
    return embeddedIcon
	// 回退：生成默认蓝色图标
// 	return generateDefaultIcon()
}

// 生成一个 64x64 的蓝色 PNG 图标，中间带白色方块
func generateDefaultIcon() []byte {
	width, height := 64, 64
	img := image.NewRGBA(image.Rect(0, 0, width, height))

	// 背景蓝色
	blue := color.RGBA{30, 144, 255, 255}
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			img.Set(x, y, blue)
		}
	}

	// 白色矩形 (中心区域)
	white := color.RGBA{255, 255, 255, 255}
	rectStartX, rectStartY := width/4, height/4
	rectEndX, rectEndY := width*3/4, height*3/4
	for y := rectStartY; y < rectEndY; y++ {
		for x := rectStartX; x < rectEndX; x++ {
			img.Set(x, y, white)
		}
	}

	// 编码为 PNG
	buf := new(bytes.Buffer) // 需要导入 "bytes"
	err := png.Encode(buf, img)
	if err != nil {
		log.Fatal("生成默认图标失败：", err)
	}
	return buf.Bytes()
}
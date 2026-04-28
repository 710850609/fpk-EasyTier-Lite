module easytier-lite

go 1.21

require (
	fyne.io/systray v1.11.0
	github.com/pkg/browser v0.0.0-20240102092130-5ac0b6a4141c
)

require (
	github.com/godbus/dbus/v5 v5.1.0 // indirect
	golang.org/x/sys v0.15.0 // indirect
)

// 添加这一行，将模块路径映射到实际 GitHub 仓库
replace fyne.io/systray => github.com/fyne-io/systray v1.11.0

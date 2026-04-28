@echo off
chcp 65001
echo 开始交叉编译（使用 go env 避免空格）...

REM Windows - AMD64
go-winres make
go env -w GOOS=windows GOARCH=amd64
go build -o dist/easytier-lite-x86_64.exe
echo [✓] Windows x86_64 编译完成

@REM 需要 mac 环境构建
@REM REM macOS - Apple Silicon
@REM go env -w GOOS=darwin GOARCH=arm64
@REM go build -o dist/easytier-lite-darwin-arm64
@REM echo [✓] macOS ARM64 编译完成

REM Linux - x86_64
go env -w GOOS=linux GOARCH=amd64
go build -o dist/easytier-lite-linux-x86_64
echo [✓] Linux x86_64 编译完成

REM Linux - aarch64
go env -w GOOS=linux GOARCH=arm64
go build -o dist/easytier-lite-linux-arm64
echo [✓] Linux ARM64 编译完成

REM 恢复默认
go env -u GOOS GOARCH
echo 全部完成！
pause
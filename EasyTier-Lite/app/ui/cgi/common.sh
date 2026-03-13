#!/bin/bash

### This script is called after the user installs the application.
set -e

TRIM_APPNAME="${TRIM_APPNAME:-EasyTier-Lite}"
TRIM_PKGVAR="${TRIM_PKGVAR:-/var/apps/${TRIM_APPNAME}/var}"
TRIM_APPDEST="${TRIM_APPDEST:-/var/apps/${TRIM_APPNAME}/target}"
TRIM_PKGTMP="${TRIM_PKGTMP:-/var/apps/${TRIM_APPNAME}/tmp}"

LOG_FILE="${TRIM_PKGVAR}/cgi.log"
BIN_DIR="${TRIM_APPDEST}/bin"
CFG_FILE="/var/apps/${TRIM_APPNAME}/shares/${TRIM_APPNAME}/config.toml"


log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - cgi_sh - $1" >> ${LOG_FILE}
}

warm_exit() {
    log_msg "$1"
    echo "$1"
    exit 1
}

run_cmd() {
    log_msg "运行命令: $1"
    # 执行命令并捕获输出，但不打印到标准输出
    local output=$(eval "$1" 2>&1)
    local exit_code=$?    
    # 只将输出写入日志文件，不打印到标准输出
    log_msg "$output"
    # 返回命令的退出码
    return $exit_code
    # bash -c "$1" >> ${LOG_FILE} 2>&1
}
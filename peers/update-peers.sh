#!/bin/bash | /usr/bin/bash
# 检测并更新公共节点
set -e

if ! command -v node &> /dev/null; then
    echo "当前环境未找到 node 命令，设置 node 环境..."
    node_ver=24
    export PATH="/var/apps/nodejs_v$node_ver/target/bin:$PATH"
    if ! command -v node &> /dev/null; then
        echo "nodejs ${node_ver} 不存在"
        exit 1
    fi
    echo "已设置 node ${node_ver} 环境"
fi
echo "使用node版本: $(node -v)"

node fetch.js
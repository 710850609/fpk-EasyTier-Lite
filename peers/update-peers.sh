#!/bin/bash
# 检测并更新公共节点
set -e

export PATH=/var/apps/nodejs_v22/target/bin:$PATH
node fetch.js
#!/bin/bash

# 检查是否存在安装目录
INSTALL_DIR="/usr/local/lib/coma"
if [ -d "$INSTALL_DIR" ]; then
    echo "正在删除安装目录..."
    sudo rm -rf "$INSTALL_DIR"
fi

# 检查是否存在启动脚本
LAUNCHER="/usr/local/bin/coma"
if [ -f "$LAUNCHER" ]; then
    echo "正在删除命令链接..."
    sudo rm "$LAUNCHER"
fi

echo "卸载完成！"
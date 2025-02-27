#!/bin/bash

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip3是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误：未找到pip3，请先安装pip3"
    exit 1
fi

# 安装依赖包
echo "正在安装依赖包..."
pip3 install rich requests

# 创建安装目录
INSTALL_DIR="/usr/local/lib/coma"
echo "正在创建安装目录..."
sudo mkdir -p "$INSTALL_DIR"

# 复制所有文件到安装目录
echo "正在复制文件..."
sudo cp -r ./* "$INSTALL_DIR/"

# 设置可执行权限
sudo chmod +x "$INSTALL_DIR/coma.py"

# 创建启动脚本
echo "正在创建启动脚本..."
LAUNCHER="/usr/local/bin/coma"
sudo tee "$LAUNCHER" > /dev/null << 'EOF'
#!/bin/bash
SCRIPT_DIR="/usr/local/lib/coma"
PYTHONPATH="$SCRIPT_DIR" python3 "$SCRIPT_DIR/coma.py" "$@"
EOF

# 设置启动脚本权限
sudo chmod +x "$LAUNCHER"

echo "安装完成！现在你可以使用coma了。"
echo "请使用 'coma help' 查看帮助信息。"
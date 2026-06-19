#!/bin/bash
# Digital Company 快速设置脚本

set -e

echo "🏢 Digital Company 快速设置"
echo "=============================="
echo ""

# 1. 检查Python版本
echo "📌 检查Python版本..."
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 需要 Python 3.10+，当前版本: $python_version"
    exit 1
fi
echo "✓ Python $python_version"
echo ""

# 2. 安装依赖
echo "📌 安装依赖..."
pip install --upgrade pip
pip install pydantic pyyaml aiohttp

# 尝试安装 agent-framework (如果可用)
pip install agent-framework 2>/dev/null || echo "⚠️ agent-framework 未发布PyPI，将使用内置实现"

echo "✓ 依赖安装完成"
echo ""

# 3. 配置Ollama (如果已安装)
if command -v ollama &> /dev/null; then
    echo "📌 Ollama 已安装"
    echo "   模型列表:"
    ollama list 2>/dev/null | head -10 || echo "   (无模型，请运行: ollama pull llama3.2)"
else
    echo "⚠️ Ollama 未安装"
    echo "   安装命令: brew install ollama"
    echo "   或访问: https://ollama.ai"
    echo "   下载模型: ollama pull llama3.2"
fi
echo ""

# 4. 创建配置
echo "📌 配置文件..."
config_dir="$HOME/.digital-company"
config_file="$config_dir/config.yaml"
if [ ! -f "$config_file" ]; then
    mkdir -p "$config_dir"
    cp "$HOME/digital-company/config.yaml.example" "$config_file" 2>/dev/null || true
    echo "✓ 配置文件已创建: $config_file"
else
    echo "✓ 配置文件已存在: $config_file"
fi
echo ""

# 5. Git仓库
echo "📌 Git仓库状态..."
cd "$HOME/digital-company"
if [ -d ".git" ]; then
    echo "✓ 已是Git仓库"
else
    echo "⚠️ 尚未初始化Git仓库"
    echo "   完成GitHub认证后运行: gh repo create"
fi
echo ""

# 6. 完成
echo "=============================="
echo "✅ 设置完成！"
echo ""
echo "下一步:"
echo "1. 完成GitHub认证: gh auth login --web"
echo "2. 创建GitHub仓库: gh repo create digital-company --public"
echo "3. 启动数字公司: python -m src"
echo ""

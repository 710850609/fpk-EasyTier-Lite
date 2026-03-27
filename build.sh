#!/bin/bash

BUILD_VERSION=01
ET_LATEST_VERSION="unknown"
ET_DOWNLOAD_URL="unknown"
DOWNLOAD_FILE="unknown"
ET_VERSION="unknown"
MIN_ET_VERSION="2.5.0"
BIN_DIR="EasyTier-Lite/app/bin"

declare -A PARAMS
# 默认值
PARAMS[build_all]="false"
PARAMS[build_pre]="true"
PARAMS[download_proxy]="true"
PARAMS[proxy_url]="https://ghfast.top"
PARAMS[arch]="x86_64"
# 解析 key=value 格式的参数
for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    key="${arg%%=*}"
    value="${arg#*=}"
    PARAMS["$key"]="$value"
  else
    # 处理标志参数
    case "$arg" in
      --pre)
        PARAMS[pre]="true"
        ;;
      *)
        echo "忽略未知参数: $arg"
        ;;
    esac
  fi
done

build_all="${PARAMS[build_all]}"
build_pre="${PARAMS[build_pre]}"
download_proxy="${PARAMS[download_proxy]}"
proxy_url="${PARAMS[proxy_url]}"
arch="${PARAMS[arch]}"
echo "build_all: ${build_all}"
echo "build_pre: ${build_pre}"
echo "download_proxy: ${download_proxy}"
echo "proxy_url: ${proxy_url}"
echo "arch: ${arch}"


# platform 取值 x86, arm, risc-v, all
platform=""
et_platform=""
os_min_version="1.0.0"
if [ "${arch}" == "x86_64" ]; then
    platform="x86"
    et_platform="x86_64"
    os_min_version="1.1.8"
    py_platform="manylinux_2_34_x86_64"
elif [ "${arch}" == "aarch64" ]; then
    platform="arm"
    et_platform="aarch64"
    os_min_version="1.0.2"
    py_platform="manylinux_2_34_aarch64"
elif [ "${arch}" == "linux-riscv64" ]; then
    platform="riscv64"
    py_platform="manylinux_2_34_riscv64"
    os_min_version="1.0.0"
else
    echo "不支持的 arch 参数"
    exit 1
fi
echo "设置 platform 为: ${platform}"
echo "---------------------------------------"

compiling_server() {
    echo "下载py依赖"
    rm -rf EasyTier-Lite/app/server 
    mkdir -p EasyTier-Lite/app/server/wheels
    pip download \
        --only-binary=:all: \
        --platform $py_platform \
        --python-version 311 \
        -r server/requirements.txt \
        -d EasyTier-Lite/app/server/wheels
        
    # 下载 wheel 到本地
    app_script_path="EasyTier-Lite/app/server/"
    echo "写入脚本到app"
    rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='main.py' server/ "${app_script_path}"
}

compiling_frontend() {
    echo '编译前端...'
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
    cd frontend
    npm install
    npm run build
    cd ../
    cp -rf frontend/dist/* EasyTier-Lite/app/ui/
    echo '编译并拷贝到app/ui目录'
}

get_et_latest_version() {
    local arch_type=$1
    local featch_url="https://api.github.com/repos/EasyTier/EasyTier/releases/latest"
    if [ "$download_proxy" == "true" ]; then
        featch_url="${proxy_url}/https://api.github.com/repos/EasyTier/EasyTier/releases/latest"
    fi
    local latest_release=$(curl -s "${featch_url}") 
    if [ -z "$latest_release" ]; then
        echo "获取最新EasyTier版本信息失败"
        exit 1
    fi
    # 提取版本号
    local version=$(echo "$latest_release" | jq -r .tag_name | sed 's/^Release//')
    # 检查版本是否符合要求
    if [[ "$(echo "$version" | sed 's/^v//')" < "$MIN_ET_VERSION" ]]; then
        echo "EasyTier release 版本 $version 过低，使用最低构建版本 $MIN_ET_VERSION"
        version="v${MIN_ET_VERSION}"
    fi
    # 提取对应架构的下载地址
    # local zip_file="easytier-linux-${et_platform}-${version}\.zip"
    # download_url=$(echo "$latest_release" | grep -oP '"browser_download_url": "\K[^"]*'"$zip_file" | sed 's/"//g')
    download_url="https://github.com/EasyTier/EasyTier/releases/download/${version}/easytier-linux-${et_platform}-${version}.zip"
    # https://github.com/EasyTier/EasyTier/releases/download/v2.4.5/easytier-linux-x86_64-v2.4.5.zip
    # 检查是否成功获取下载地址
    if [ -z "$download_url" ]; then
        echo "下载EasyTier失败"
        exit 1
    fi
    # 将版本号和下载链接存储在全局变量中
    ET_LATEST_VERSION="$version"
    ET_DOWNLOAD_URL="$download_url"
    echo "EasyTier最新版本: $ET_LATEST_VERSION"
    echo "EasyTier最新版本下载地址: $ET_DOWNLOAD_URL"
}

get_et_version() {
    if [ "${arch}" != "$(uname -m)" ]; then
        echo "非当前系统架构，跳过获取已安装EasyTier版本"
        ET_VERSION=$ET_LATEST_VERSION
        return 0
    fi
    local bin_dir=$BIN_DIR
    if [ -f "${bin_dir}/easytier-core" ]; then
        local version_output=$("${bin_dir}/easytier-core" --version 2>&1)
        local version=$(echo "$version_output" | grep -oP 'easytier-core \K(\d+\.\d+\.\d+)')
        if [ -n "$version" ]; then
            echo "当前 easytier 版本: $version"
            ET_VERSION="$version"
        else
            echo "无法获取当前 easytier 版本"
            exit 1
        fi
    else
        echo "easytier-core 二进制文件不存在，无法获取版本"
        exit 1
    fi
}

download_et() {
    DOWNLOAD_FILE="easytier-linux-${et_platform}-${ET_LATEST_VERSION}.zip"
    # 非当前系统，强制下载最新版本，避免后续版本判断错误
    if [ "${build_all}" == "true" ] || [ ! -f "${DOWNLOAD_FILE}" ]; then
        if [ "$download_proxy" == "true" ]; then
            ET_DOWNLOAD_URL=${proxy_url}/${ET_DOWNLOAD_URL}
        fi
        echo "开始下载: ${ET_DOWNLOAD_URL}"
        rm -f "${DOWNLOAD_FILE}"
        wget -O "${DOWNLOAD_FILE}" "${ET_DOWNLOAD_URL}"
        if [ ! -f "${DOWNLOAD_FILE}" ]; then
            echo "下载 EasyTier 失败"
            exit 1
        fi
    fi
}

update_app() {
    local bin_dir=$BIN_DIR
    local temp_dir="temp"
    bash -c "rm -rf ${bin_dir}" 2>&1
    bash -c "mkdir -p ${bin_dir}" 2>&1
    bash -c "mkdir -p ${temp_dir}" 2>&1
    echo "开始解压 ${DOWNLOAD_FILE}"
    bash -c "unzip -o ${DOWNLOAD_FILE} -d ${temp_dir}" 2>&1
    echo "开始复制应用文件"
    bash -c "cp -rf ${temp_dir}/easytier-linux-${et_platform}/easytier-cli ${bin_dir}" 2>&1
    bash -c "cp -rf ${temp_dir}/easytier-linux-${et_platform}/easytier-core ${bin_dir}" 2>&1
    bash -c "cp -f default.toml $(dirname ${bin_dir})" 2>&1
    echo "更新应用文件完成"
    get_et_version
    { jq ".[0].items |= map(if .field == \"et_version\" then .initValue = \"$ET_VERSION\" else . end)" EasyTier-Lite/wizard/config > temp.json && mv temp.json EasyTier-Lite/wizard/config; } || { echo "更新 wizard config 失败" && exit 1; }
    echo "更新配置向导中的EasyTier版本号为: ${ET_VERSION}"
    bash -c "rm -rf ${temp_dir}" 2>&1
    echo "---------------------------------------"
}


build_fpk() {
    # get_et_version
    local fpk_version="${ET_VERSION}-${BUILD_VERSION}"
    if [ "$build_pre" == 'true' ];then 
        cur_time=$(date +"%Y%m%d_%H%M%S")
        echo "当前时间：$cur_time"
        fpk_version="${fpk_version}-${cur_time}"
    fi
    sed -i "s|^[[:space:]]*version[[:space:]]*=.*|version=${fpk_version}|" 'EasyTier-Lite/manifest'
    echo "设置 manifest 的 version 为: ${fpk_version}"
    sed -i "s|^[[:space:]]*platform[[:space:]]*=.*|platform=${platform}|" 'EasyTier-Lite/manifest'
    echo "设置 manifest 的 platform 为: ${platform}"
    sed -i "s|^[[:space:]]*os_min_version[[:space:]]*=.*|os_min_version=${os_min_version}|" 'EasyTier-Lite/manifest'
    echo "设置 manifest 的 os_min_version 为: ${os_min_version}"

    echo "开始打包 fpk"
    if command -v fnpack >/dev/null 2>&1; then
        echo "使用系统已安装的 fnpack 进行打包"
        fnpack build --directory EasyTier-Lite/  || { echo "打包失败"; exit 1; }
    else
        echo "使用本地 fnpack 脚本进行打包"
        ./fnpack.sh build --directory EasyTier-Lite || { echo "打包失败"; exit 1; }
    fi 

    fpk_name="EasyTier-Lite-${fpk_version}-${platform}.fpk"
    rm -f "${fpk_name}"
    mv EasyTier-Lite.fpk "${fpk_name}"
    echo "打包完成: ${fpk_name}"
}

compiling_server
compiling_frontend
get_et_latest_version $arch
download_et
update_app
build_fpk

exit 0
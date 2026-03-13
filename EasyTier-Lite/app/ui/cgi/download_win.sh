#!/bin/bash

### This script is called after the user installs the application.
set -e
source /var/apps/EasyTier-Lite/target/ui/cgi/common.sh

download_win() {
    local version_output=$("${BIN_DIR}/easytier-core" --version 2>&1)
    local cur_et_version=$(echo "$version_output" | grep -oP 'easytier-core \K(\d+\.\d+\.\d+)')
    local output_file="/var/apps/${TRIM_APPNAME}/shares/${TRIM_APPNAME}/easytier-manager-pro_${cur_et_version}.zip"
    local temp_dir="${TRIM_PKGTMP}"
    run_cmd "mkdir -p ${temp_dir}"
    local unzip_dir="${temp_dir}/tmp-easytier-windows-x86_64"
    run_cmd "mkdir -p ${unzip_dir}"

    local et_zip_file="${temp_dir}/easytier-windows-x86_64-${cur_et_version}.zip"
    if [ -f "${et_zip_file}" ]; then        
        log_msg "已存在 EasyTier Windows 版本: ${et_zip_file}"
    else
        log_msg "不存在 EasyTier Windows 版本，开始下载: ${et_zip_file}"
        local download_url="https://github.com/EasyTier/EasyTier/releases/download/v${cur_et_version}/easytier-windows-x86_64-v${cur_et_version}.zip"
        if [ "$github_proxy_url" != "" ]; then
            download_url=${github_proxy_url}/${download_url}
        fi
        run_cmd "rm -f ${et_zip_file}"
        log_msg "开始下载: ${download_url} , 保存到 ${et_zip_file}"
        local et_zip_file_tmp="${unzip_dir}/et_zip_file.tmp"
        run_cmd "wget -q --show-progress -O ${et_zip_file_tmp} ${download_url}"
        if [ $? != 0 ] || [ ! -f "${et_zip_file_tmp}" ]; then
            warm_exit "下载 Windows EasyTier 失败"
        fi
        # 移动到一定是成功的位置
        run_cmd "mv -f ${et_zip_file_tmp} ${et_zip_file}"
        log_msg "下载 EasyTier 成功: ${et_zip_file}"
    fi
    
    local mgr_ver=$(run_cmd "curl -s https://api.github.com/repos/EasyTier/easytier-manager/releases/latest | grep -o '\"tag_name\": *\"[^\"]*\"' | grep -o '[0-9.]\+'")
    log_msg "easytier-manager-pro最新版本: ${mgr_ver}"
    local et_mgr_zip_file="${temp_dir}/easytier-manager-pro-${mgr_ver}.zip"
    if [ -f "${et_mgr_zip_file}" ]; then
        log_msg "已存在 EasyTier Manager Pro 版本: ${et_mgr_zip_file}"
    else
        log_msg "不存在缓存，下载最新 EasyTier Manager Pro ${mgr_ver}"        
        local et_mgr_download_url="https://github.com/EasyTier/easytier-manager/releases/download/v${mgr_ver}/easytier-manager-pro.zip"
        if [ "$github_proxy_url" != "" ]; then
            et_mgr_download_url=${github_proxy_url}/${et_mgr_download_url}
        fi 
        run_cmd "rm -f ${et_mgr_zip_file}"
        log_msg "开始下载: ${et_mgr_download_url} , 保存到 ${et_mgr_zip_file}"
        local et_mgr_zip_file_tmp="${unzip_dir}/et_mgr_zip_file.tmp"
        run_cmd "wget -q --show-progress -O ${et_mgr_zip_file_tmp} ${et_mgr_download_url}"
        if [ $? != 0 ] || [ ! -f "${et_mgr_zip_file_tmp}" ]; then
            warm_exit "下载 easytier-manager-pro 失败"
        fi
        run_cmd "mv -f ${et_mgr_zip_file_tmp} ${et_mgr_zip_file}"
        log_msg "下载 easytier-manager-pro 成功: ${et_mgr_zip_file}"
    fi

    log_msg "开始解压 EasyTier: ${et_zip_file}"
    run_cmd "unzip -o ${et_zip_file} -d ${unzip_dir}"
    # run_cmd "rm -f ${et_zip_file}"    
    log_msg "开始解压 easytier-manager-pro: ${et_mgr_zip_file}, "
    run_cmd "unzip -o ${et_mgr_zip_file} -d ${unzip_dir}/easytier-manager-pro | grep -v "warning:" || true"
    # run_cmd "rm -rf ${et_mgr_zip_file}"
    
    log_msg "开始打包..."
    # 复制et核心
    run_cmd "cp -rf ${unzip_dir}/easytier-windows-x86_64/* ${unzip_dir}/easytier-manager-pro/resource/"
    # 复制配置文件，并修改成DHCP分配ip
    run_cmd "mkdir -p ${unzip_dir}/easytier-manager-pro/config"
    run_cmd "cp -rf ${CFG_FILE} ${unzip_dir}/easytier-manager-pro/config/et-fnos.toml"
    run_cmd "sed -i 's/^dhcp.*/dhcp = \"true\"/' ${unzip_dir}/easytier-manager-pro/config/et-fnos.toml"
    run_cmd "sed -i 's/^ipv4.*/ipv4 = \"\"/' ${unzip_dir}/easytier-manager-pro/config/et-fnos.toml"

    run_cmd "cd ${unzip_dir} && zip -r ${output_file} ./easytier-manager-pro/"
    log_msg "打包 easytier-manager-pro 成功: ${output_file}"
    run_cmd "rm -rf ${unzip_dir}"
    echo ${output_file}
}

download_win
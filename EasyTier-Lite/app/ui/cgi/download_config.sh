#!/bin/bash

### This script is called after the user installs the application.
set -e
source /var/apps/EasyTier-Lite/target/ui/cgi/common.sh

download_config() {
    local cfg_file='/var/apps/EasyTier-Lite/shares/EasyTier-Lite/config.toml'
    local tmp_file='/tmp/EasyTier-Lite/config-copy.toml'
    run_cmd "mkdir -p $(dirname ${tmp_file})"
    run_cmd "cp -f ${cfg_file} ${tmp_file}"
    run_cmd "cp -f ${cfg_file} ${tmp_file}"
    run_cmd "sed -i 's/^dhcp.*/dhcp = true/' ${tmp_file}"
    run_cmd "sed -i 's/^ipv4.*/ipv4 = \"\"/' ${tmp_file}"
    echo ${tmp_file}
}

download_config
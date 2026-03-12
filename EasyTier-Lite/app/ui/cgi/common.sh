#!/bin/bash

### This script is called after the user installs the application.
set -e

TRIM_APPNAME="${TRIM_APPNAME:-EasyTier-Lite}"
TRIM_PKGVAR="${TRIM_PKGVAR:-/var/apps/${TRIM_APPNAME}/var}"
TRIM_APPDEST="${TRIM_APPDEST:-/var/apps/${TRIM_APPNAME}/target}"
LOG_FILE="${TRIM_PKGVAR}/cgi.log"
BIN_DIR="${TRIM_APPDEST}/bin"
CFG_FILE="/var/apps/${TRIM_APPNAME}/shares/${TRIM_APPNAME}/config.toml"


log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> ${LOG_FILE}
}

warm_exit() {
    log_msg "$1"
    echo "$1" > ${TRIM_TEMP_LOGFILE}
    exit 1
}

run_cmd() {
    log_msg "运行命令: $1"
    bash -c "$1" >> ${LOG_FILE} 2>&1
}

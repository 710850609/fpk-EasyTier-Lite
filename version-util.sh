#!/bin/bash

# 版本号 ↔ 36进制转换工具
# 支持范围: 每段 0-1295 (36进制 2位最大 ZZ=1295)

# ========== 工具函数 ==========

char_to_val() {
    local char="$1"
    local chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    char=$(echo "$char" | tr '[:lower:]' '[:upper:]')
    
    local i
    for ((i=0; i<36; i++)); do
        if [[ "${chars:$i:1}" == "$char" ]]; then
            echo "$i"
            return 0
        fi
    done
    echo "0"
    return 1
}

val_to_char() {
    local val="$1"
    local chars="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if [[ "$val" -ge 0 && "$val" -lt 36 ]]; then
        echo "${chars:$val:1}"
        return 0
    else
        echo "0"
        return 1
    fi
}

is_number() {
    local str="$1"
    local i
    for ((i=0; i<${#str}; i++)); do
        local c="${str:$i:1}"
        if [[ "$c" != "0" && "$c" != "1" && "$c" != "2" && "$c" != "3" && "$c" != "4" && \
              "$c" != "5" && "$c" != "6" && "$c" != "7" && "$c" != "8" && "$c" != "9" ]]; then
            return 1
        fi
    done
    return 0
}

is_valid_version() {
    local version="$1"
    local dot_count=0
    local i
    for ((i=0; i<${#version}; i++)); do
        if [[ "${version:$i:1}" == "." ]]; then
            ((dot_count++))
        fi
    done
    
    if [[ $dot_count -ne 2 ]]; then
        return 1
    fi
    if [[ "${version:0:1}" == "." || "${version: -1}" == "." ]]; then
        return 1
    fi
    if [[ "$version" == *..* ]]; then
        return 1
    fi
    return 0
}

# ========== 核心转换函数 ==========

# 单段10进制转36进制字符串（补零到2位）
dec_to_base36_padded() {
    local num="$1"
    local result=""
    
    if [[ "$num" -eq 0 ]]; then
        echo "00"
        return 0
    fi
    
    local remainder
    while [[ "$num" -gt 0 ]]; do
        remainder=$((num % 36))
        result="$(val_to_char $remainder)${result}"
        num=$((num / 36))
    done
    
    while [[ ${#result} -lt 2 ]]; do
        result="0${result}"
    done
    
    echo "$result"
    return 0
}

# 版本号转36进制字符串（6位）
version_to_base36() {
    local version="$1"
    local parts
    local part
    local base36_str=""
    
    if ! is_valid_version "$version"; then
        echo "Error: 无效版本号格式 '$version'" >&2
        return 1
    fi
    
    IFS='.' read -ra parts <<< "$version"
    
    if [[ ${#parts[@]} -ne 3 ]]; then
        echo "Error: 版本号必须是3段 (x.y.z)" >&2
        return 1
    fi
    
    for part in "${parts[@]}"; do
        if ! is_number "$part"; then
            echo "Error: 版本号包含非数字: '$part'" >&2
            return 1
        fi
        local part_clean=$(echo "$part" | sed 's/^0*//')
        [[ -z "$part_clean" ]] && part_clean="0"
        if [[ "$part_clean" -lt 0 || "$part_clean" -gt 1295 ]]; then
            echo "Error: 版本号段超出范围(0-1295): '$part'" >&2
            return 1
        fi
    done
    
    for part in "${parts[@]}"; do
        base36_str+="$(dec_to_base36_padded "$part")"
    done
    
    echo "$base36_str"
    return 0
}

# 版本号转十进制数字
version_to_num() {
    local version="$1"
    local base36_str
    local result=0
    local i
    local char
    local val
    
    base36_str=$(version_to_base36 "$version")
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    for ((i=0; i<${#base36_str}; i++)); do
        char="${base36_str:$i:1}"
        val=$(char_to_val "$char")
        result=$((result * 36 + val))
    done
    
    echo "$result"
    return 0
}

# 十进制数字转36进制字符串（补零到6位）
num_to_base36_str() {
    local num="$1"
    local result=""
    local remainder
    
    if ! is_number "$num"; then
        echo "Error: 无效数字 '$num'" >&2
        return 1
    fi
    
    if [[ "$num" -eq 0 ]]; then
        echo "000000"
        return 0
    fi
    
    while [[ "$num" -gt 0 ]]; do
        remainder=$((num % 36))
        result="$(val_to_char $remainder)${result}"
        num=$((num / 36))
    done
    
    while [[ ${#result} -lt 6 ]]; do
        result="0${result}"
    done
    
    echo "$result"
    return 0
}

two_char_to_dec() {
    local str="$1"
    local result=0
    local i
    local char
    local val
    
    for ((i=0; i<${#str}; i++)); do
        char="${str:$i:1}"
        val=$(char_to_val "$char")
        result=$((result * 36 + val))
    done
    echo "$result"
    return 0
}

# 36进制字符串（6位）转版本号
base36_to_version() {
    local base36="$1"
    local v1 v2 v3
    
    # 检查长度
    if [[ ${#base36} -ne 6 ]]; then
        echo "Error: 36进制字符串必须是6位" >&2
        return 1
    fi
    
    v1=$(two_char_to_dec "${base36:0:2}")
    v2=$(two_char_to_dec "${base36:2:2}")
    v3=$(two_char_to_dec "${base36:4:2}")
    
    echo "$v1.$v2.$v3"
    return 0
}

# 十进制数字转版本号
num_to_version() {
    local num="$1"
    local base36
    
    base36=$(num_to_base36_str "$num")
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    base36_to_version "$base36"
    return $?
}

# ========== 命令行处理 ==========

show_usage() {
    echo "版本号 ↔ 36进制转换工具"
    echo ""
    echo "用法:"
    echo "  $0 -e <版本号>    # 编码为十进制数字 (如 2.5.0 → 3365712)"
    echo "  $0 -x <版本号>    # 编码为36进制字符串 (如 2.5.0 → 020500)"
    echo "  $0 -d <数字>      # 解码十进制数字为版本号"
    echo "  $0 -b <36进制>    # 解码36进制字符串为版本号 (如 10SDRR → 36.1021.999)"
    echo "  $0 -t             # 运行测试"
    echo ""
    echo "示例:"
    echo "  $0 -e 2.5.0       # 十进制: 3365712"
    echo "  $0 -x 2.5.0       # 36进制: 020500"
    echo "  $0 -x 36.1021.999 # 36进制: 10SDRR"
    echo "  $0 -b 10SDRR      # 版本号: 36.1021.999"
    echo "  $0 -d 61790391    # 版本号: 36.1021.999"
}

run_tests() {
    echo "=== 版本号转换测试 ==="
    echo ""
    
    local test_versions=("0.0.1" "10.20.30" "35.35.35" "1.0.0" "0.0.0" "2.5.0" "36.1021.999")
    local all_passed=true
    local v n b back
    local exit_code
    
    echo "--- 十进制编码/解码测试 ---"
    for v in "${test_versions[@]}"; do
        n=$(version_to_num "$v" 2>&1)
        exit_code=$?
        
        if [[ $exit_code -ne 0 || -z "$n" || "$n" == Error* ]]; then
            echo "✗ $v → 编码失败 (n='$n')"
            all_passed=false
            continue
        fi
        
        back=$(num_to_version "$n" 2>&1)
        exit_code=$?
        
        if [[ $exit_code -ne 0 || -z "$back" || "$back" == Error* ]]; then
            echo "✗ $v → $n → 解码失败"
            all_passed=false
            continue
        fi
        
        if [[ "$v" == "$back" ]]; then
            echo "✓ $v → $n → $back"
        else
            echo "✗ $v → $n → $back (不匹配)"
            all_passed=false
        fi
    done
    
    echo ""
    echo "--- 36进制编码/解码测试 ---"
    for v in "${test_versions[@]}"; do
        b=$(version_to_base36 "$v" 2>&1)
        exit_code=$?
        
        if [[ $exit_code -ne 0 || -z "$b" || "$b" == Error* ]]; then
            echo "✗ $v → 编码失败 (b='$b')"
            all_passed=false
            continue
        fi
        
        back=$(base36_to_version "$b" 2>&1)
        exit_code=$?
        
        if [[ $exit_code -ne 0 || -z "$back" || "$back" == Error* ]]; then
            echo "✗ $v → $b → 解码失败"
            all_passed=false
            continue
        fi
        
        if [[ "$v" == "$back" ]]; then
            echo "✓ $v → $b → $back"
        else
            echo "✗ $v → $b → $back (不匹配)"
            all_passed=false
        fi
    done
    
    echo ""
    if $all_passed; then
        echo "所有测试通过!"
        return 0
    else
        echo "部分测试失败"
        return 1
    fi
}

# 主逻辑
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

case "$1" in
    -e|--encode)
        if [[ -z "$2" ]]; then
            echo "Error: 请提供版本号" >&2
            exit 1
        fi
        version_to_num "$2"
        ;;
    -x|--base36)
        if [[ -z "$2" ]]; then
            echo "Error: 请提供版本号" >&2
            exit 1
        fi
        version_to_base36 "$2"
        ;;
    -d|--decode)
        if [[ -z "$2" ]]; then
            echo "Error: 请提供数字" >&2
            exit 1
        fi
        num_to_version "$2"
        ;;
    -b|--base36-decode)
        if [[ -z "$2" ]]; then
            echo "Error: 请提供36进制字符串" >&2
            exit 1
        fi
        base36_to_version "$2"
        ;;
    -t|--test)
        run_tests
        ;;
    -h|--help)
        show_usage
        ;;
    *)
        # 自动判断
        if [[ "$1" == *.* ]]; then
            version_to_num "$1"
        elif is_number "$1"; then
            num_to_version "$1"
        else
            echo "Error: 无法识别输入 '$1'" >&2
            show_usage
            exit 1
        fi
        ;;
esac
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

from utils import common_util
from utils import run_configs


def list(params, *kwargs):
    """
    获取节点列表
    :param request_data: 请求数据（可选）
    """
    config_file_name = params.get('configFileName') if params else None

    core_dir = run_configs.core_dir()
    ext = ".exe" if sys.platform == "win32" else ""
    result = common_util.run_cmd(f'{core_dir}/easytier-cli{ext} --output json peer')
    peer_list = json.loads(result)
    return peer_list

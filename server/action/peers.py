#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import util.common_util as cmd_util
import util.http_util as http_util
import json
import os

def list():
    BIN_DIR = os.environ.get('BIN_DIR', '/var/apps/EasyTier-Lite/target/bin')
    result = cmd_util.run_cmd(f'{BIN_DIR}/easytier-cli --output json peer')
    peer_list = json.loads(result)
    http_util.http_response_ok(peer_list)

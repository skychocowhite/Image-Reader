# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:55:58 2024

@author: hanks
"""

import os
import json

class ConfigLoader:
    @staticmethod
    def load_config():
        """讀取配置文件"""
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        else:
            return {}

    @staticmethod
    def save_config(config):
        """保存配置文件"""
        config_path = "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

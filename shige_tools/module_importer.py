# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os
import sys
import importlib.util

BUNDLE_FOLDER_NAME = "bundle"

def add_lib_folder_to_sys():
    addon_path = os.path.dirname(os.path.dirname(__file__))
    lib_folder = os.path.join(addon_path, BUNDLE_FOLDER_NAME)

    if lib_folder not in sys.path:
        sys.path.insert(0, lib_folder)

def load_module(module_name="dlib"):
    original_module = sys.modules.get(module_name)

    try:
        # すでにﾓｼﾞｭｰﾙがｲﾝｽﾄｰﾙされていれば削除
        if module_name in sys.modules:
            del sys.modules[module_name]

        # 新しいﾓｼﾞｭｰﾙのPathを取得
        addon_path = os.path.dirname(__file__)
        module_location = os.path.join(addon_path, BUNDLE_FOLDER_NAME, module_name, '__init__.py')

        # 新しいﾓｼﾞｭｰﾙをｲﾝﾎﾟｰﾄ
        module_spec = importlib.util.spec_from_file_location(module_name, module_location)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)

    except Exception as e:
        if original_module is not None:
            # ｴﾗｰが起きた場合は復元
            sys.modules[module_name] = original_module
        elif module_name in sys.modules:
            del sys.modules[module_name]
        raise e


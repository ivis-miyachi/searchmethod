
import redis
import os
import json
from config import (
    SUPER_DECOLATOR, TRACE_END_DECOLATOR, ASYNC_DECOLATOR, 
    INHERITED_DECOLATOR, SIGNAL_DECOLATOR, LIMIT_SAVE_HISTORY,
    REDIS_KEY_OPERATION_HISTORY,MSG_DUPLICATION
)
import contextvars
from datetime import datetime
import sys
from contextlib import contextmanager

@contextmanager
def print_prefix(prefix):
    """print文の文頭にprefixを入れる
    with print_prefix("test_prefix:"):
        print("test_value")
    このように記述すると、"test_prefix:test_value"と出力

    Args:
        prefix (str): 文頭に追加する文字列
    """
    class PrefixWriter:
        def __init__(self, original):
            self.original = original
        def write(self, text):
            # 各行の先頭にprefixを付与
            lines = text.splitlines(keepends=True)
            for line in lines:
                if line.strip() != '':
                    self.original.write(prefix + line)
                else:
                    self.original.write(line)
        def flush(self):
            self.original.flush()
    original_stdout = sys.stdout
    sys.stdout = PrefixWriter(original_stdout)
    try:
        yield
    finally:
        sys.stdout = original_stdout

def get_names_from_path(path,only_class=False):
    """<file>:<class>.<method>形式の文字列からそれぞれに分割して返す

    Args:
        path (str): 対象パス
        only_class (bool, optional): クラス単体、メソッド無しかどうか. Defaults to False.

    Returns:
        str, str, str: 順にファイル、クラス、メソッド
    """
    file = path.split(":")[0].strip()
    method_class = path.split(":")[1]
    if only_class == False:
        if len(method_class.split("."))==2:
            class_name = method_class.split(".")[0].strip()
            method_name = method_class.split(".")[1].strip()
        else:
            class_name = None
            method_name = method_class.strip()
    else:
        class_name = method_class.strip()
        method_name = None
    return file, class_name, method_name

def get_names_from_unstable_path(path):
    
    if ":" in path:
        file = path.split(":")[0].strip()
        method_class = path.split(":")[1]
    else:
        file = None
        method_class = path.strip()
    if "." in method_class:
        class_name = method_class.split(".")[0].strip()
        method_name = method_class.split(".")[1].strip()
    else:
        class_name = None
        method_name = method_class.strip()
    
    return file, class_name, method_name

def build_tree(paths):
    tree = {}
    for path in paths:
        node = tree
        for step in reversed(path):
            node = node.setdefault(step, {})
    return tree

def get_dummuys():
    from classes import get_class
    class_obj, class_id = get_class("<dummy_file>", "<dummyclass>", with_add=True)
    return class_obj, class_obj.file

COLORS = [
    "\033[31m",  # 赤
    "\033[32m",  # 緑
    "\033[33m",  # 黄
    "\033[34m",  # 青
    "\033[35m",  # 紫
    "\033[36m",  # シアン
    "\033[91m",  # 明るい赤
    "\033[92m",  # 明るい緑
    "\033[93m",  # 明るい黄
    "\033[94m",  # 明るい青
    "\033[95m",  # 明るい紫
    "\033[96m",  # 明るいシアン
    "\033[37m",  # 白
    "\033[90m",  # グレー
    "\033[97m",  # 明るい白
    "\033[30m",  # 黒
]
RESET = "\033[0m"
from collections import defaultdict
def count_keys(node, counter=None):
    if counter is None:
        counter = defaultdict(int)
    for key in node.keys():
        counter[key] += 1
        count_keys(node[key], counter)
    return counter

def assign_colors(counter):
    color_map = {}
    color_idx = 0
    for key, count in counter.items():
        if count > 1:
            color_map[key] = COLORS[color_idx % len(COLORS)]
            color_idx += 1
    return color_map

def replace_decolator(target):
    """targetから(xx)の文字列を削除する
    現状削除するのはconfig.py: DECOLATORSに定義されているもの
    Args:
        target (str): 対象文字列

    Returns:
        str: 削除後の文字列
    """
    if SUPER_DECOLATOR in target:
        target = target.replace(SUPER_DECOLATOR, "")
    if TRACE_END_DECOLATOR in target:
        target = target.replace(TRACE_END_DECOLATOR, "")
    if ASYNC_DECOLATOR in target:
        target = target.replace(ASYNC_DECOLATOR, "")
    if INHERITED_DECOLATOR in target:
        target = target.replace(INHERITED_DECOLATOR, "")
    if SIGNAL_DECOLATOR in target:
        target = target.replace(SIGNAL_DECOLATOR, "")
    return target

def print_tree(node, prefix="", db_access = [], color_map={}, seen=None, is_deduplication=True):
    if seen is None:
        seen = set()
    keys = list(node.keys())
    for i, key in enumerate(keys):

        connector = '└─' if i == len(keys) - 1 else '├─'
        color = color_map.get(key, "")
        display_key = f"{color}{key}{RESET}" if color else key
        if key in seen and color:
            display_key = f"{color}{key} {RESET}"
        elif key in seen:
            display_key = f"{key} "
        print(f"{prefix}{connector} {display_key}")
        next_prefix = prefix + ('     ' if i == len(keys) - 1 else '│    ')
        target_key = replace_decolator(key)
        if db_access and target_key in db_access:
            last_db_connector = '└─' if node[key]=={} else '├─'
            accesses = db_access[target_key]
            for ii, access in enumerate(accesses):
                db_connector = last_db_connector if ii == len(accesses) -1 else '├─' # DBアクセスは常に末尾扱い
                print(f"{next_prefix}{db_connector} [{access['type'].upper()}] {access['table']} ({access['operation']})")

        if is_deduplication and key not in seen:
            seen.add(key)
            print_tree(node[key], next_prefix, db_access, color_map, seen, is_deduplication)
        elif is_deduplication and key in seen and node[key]:
            print(f"{next_prefix}└─ {MSG_DUPLICATION}")
        elif not is_deduplication:
            print_tree(node[key], next_prefix, db_access, color_map, seen, is_deduplication)
            
            
def tree_to_text(tree, prefix="", type="child", is_last=True):
    if type=="parent":
        key = "parents"
    elif type=="child":
        key = "children"
    lines = []
    class_str = f"{str(tree['id'])}: {str(tree['class_name'])}"
    if prefix == "":
        lines.append(class_str)
    else:
        branch = "└─ " if is_last else "├─ "
        lines.append(prefix + branch + class_str)
    children = tree.get(key, [])
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        # prefixが空でも必ずインデントを付与
        next_prefix = prefix + ("   " if is_last else "│  ")
        lines.extend(tree_to_text(child, next_prefix, type, is_last_child))
    return lines

class RedisCon:
    def __init__(self, host=None, port=None, db=None):
        host = host if host else os.getenv('REDIS_HOST', 'localhost')
        port = port if port else int(os.getenv('REDIS_PORT', 6379))
        db = db if db else int(os.getenv('REDIS_DB', 0))
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def set(self, key, value):
        self.client.set(key, value)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

    def exists(self, key):
        return self.client.exists(key)
    

class OperationHistory:
    def __init__(self, redis_con=None, ope_id=None):
        self.redis_con = redis_con if redis_con else RedisCon()
        self.key = REDIS_KEY_OPERATION_HISTORY
        self.ope_id = ope_id if ope_id else ope_id_get()

    def add_operation(self, operation_data):
        data = self.redis_con.get(self.key)
        import json
        if not data:
            data = [
                {"operation_id": self.ope_id, "timestamp": str(datetime.now())}
            ]
            data = json.dumps(data)
        data = eval(data)
        
        if self.ope_id not in [r['operation_id'] for r in data]:
            data.append({"operation_id": self.ope_id, "timestamp": str(datetime.now())})
        for r in data:
            if 'operation_id' in r and r['operation_id'] == self.ope_id:
                if 'operations' not in r:
                    r['operations'] = []
                r['operations'].append(operation_data)

        if len(data) > LIMIT_SAVE_HISTORY:
            data = sorted(data, key=lambda x: x['timestamp'], reverse=True)[:LIMIT_SAVE_HISTORY]
        
        self.redis_con.set(self.key, str(data))

    def get_history(self):
        ope_id=self.ope_id
        data = self.redis_con.get(self.key)
        if not data:
            return None
        data = eval(data)

        ope_ids = [record['operation_id'] for record in data if 'operation_id' in record]
        if ope_id not in ope_ids:
            return None
        for record in data:
            if 'operation_id' in record and record['operation_id'] == ope_id:
                return record

    def get_latest_history(self):
        data = self.redis_con.get(self.key)
        if not data:
            return None
        data = eval(data)
        if not data:
            return None
        latest_record = sorted(data, key=lambda x: x['timestamp'], reverse=True)[0]
        return latest_record
    def remove_latest_history(self):
        data = self.redis_con.get(self.key)
        if not data:
            return None
        data = eval(data)
        if not data:
            return None
        data = sorted(data, key=lambda x: x['timestamp'], reverse=True)[1:]
        self.redis_con.set(self.key, str(data))

operation_id_var = contextvars.ContextVar('operation_id')

def ope_id_set(op_id):
    return operation_id_var.set(op_id)

def ope_id_get():
    return operation_id_var.get()

def ope_id_reset(token):
    operation_id_var.reset(token)

import importlib
def restore_operation():
    """redisに保存された操作履歴のうち、最新を打ち消す
    operation=C-> 該当データ削除
    operation=U-> 該当フィールドの値が新しい値なら古い値に更新。それ以外は何もしない

    Returns:
        _type_: _description_
    """
    operation_history = OperationHistory()
    record = operation_history.get_latest_history()
    
    operations = record.get('operations', []) if record else []
    if not operations:
        print("No operations to restore")
        return
    operations = sorted(operations, key=lambda x: x['timestamp'], reverse=True)
    
    models = importlib.import_module('models')
    for ope in operations:
        print("restoreing operation:")
        with print_prefix("  "):
            table = ope.get('table')
            operation = ope.get('operation')
            id= ope.get('id')
            
            table_class = getattr(models, table, None)
            if not table_class:
                continue
            obj = table_class.get_by_id(id)
            if operation=="C":
                obj.delete()
            elif operation=="U":
                changes = ope.get('changes', {})
                for field, values in changes.items():
                    old = values.get('old')
                    new = values.get('new')
                    if obj.__dict__.get(field) == new:
                        obj.__dict__[field] = old
                    else:
                        pass
                obj.merge()
            operation_history.remove_latest_history()





def get_names_from_path(path,only_class=False):
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
# def print_tree(node, prefix="", highlight=None):
#     keys = list(node.keys())
#     for i, key in enumerate(keys):
#         connector = '└─' if i == len(keys) - 1 else '├─'
#         if highlight and key == highlight:
#             colored_key = f"\033[1;31m{key}\033[0m"  # 赤色
#         else:
#             colored_key = key
#         print(f"{prefix}{connector} {colored_key}")
#         next_prefix = prefix + ('     ' if i == len(keys) - 1 else '│    ')
#         print_tree(node[key], next_prefix, highlight)
        

# COLORS = [
#     "\033[1;31m",  # 赤
#     "\033[1;32m",  # 緑
#     "\033[1;33m",  # 黄
#     "\033[1;34m",  # 青
#     "\033[1;35m",  # 紫
#     "\033[1;36m",  # シアン
# ]
# COLORS = [f"\033[38;5;{i}m" for i in range(16, 232)]  # 216色

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

def print_tree(node, prefix="", color_map=None, seen=None):
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
        if key not in seen:
            seen.add(key)
            print_tree(node[key], next_prefix, color_map, seen)
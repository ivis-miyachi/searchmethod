
from models import DBAccess
from method import get_method
from utils import get_names_from_path

def add_db(path, table_name, access_type, condition_method_path=None):
    return add(path, table_name, access_type, type="db", condition_method_path=condition_method_path)

def add_es(path, table_name, access_type, condition_method_path=None):
    return add(path, table_name, access_type, type="es", condition_method_path=condition_method_path)

def add_redis(path, table_name, access_type, condition_method_path=None):
    return add(path, table_name, access_type, type="redis", condition_method_path=condition_method_path)

def add(path, table_name, access_type, type, condition_method_path=None):
    file, class_name, method_name = get_names_from_path(path)
    method, method_id = get_method(file, class_name, method_name, with_class_obj=False, with_add=True)
    if condition_method_path:
        c_file, c_class_name, c_method_name = get_names_from_path(condition_method_path)
        c_method, c_method_id = get_method(c_file, c_class_name, c_method_name, with_class_obj=False, with_add=True)

    old = DBAccess.get(method_id, table_name, access_type, type=type, condition_method_id=c_method_id if condition_method_path else None)
    if old:
        print(f"{type.upper()} Access already exists")
        return old.id
    db_access = DBAccess.create(access_type, table_name, method_id, type=type, condition_method_id=c_method_id if condition_method_path else None)
    return db_access.id

def get_method_by_db_access(table_name, access_type=None):
    """テーブル名とアクセスタイプから、そのアクセスをしているメソッドを取得

    Args:
        table_name (str): 対象テーブル名
        access_type (str, optional): アクセスタイプ. Defaults to None.

    Returns:
        dict: キーにアクセスタイプ、値にMethodTableオブジェクトのリスト
    """
    db_accesses = DBAccess.get_all(table_name=table_name, operation_type=access_type, type="db")
    if not db_accesses:
        print("DB Access not found")
        return None
    methods = {}
    for db_access in db_accesses:
        method = db_access.method
        if db_access.operation_type not in methods:
            methods[db_access.operation_type] = []
        methods[db_access.operation_type].append(method)
    return methods

def get_access_by_method(path):
    file, class_name, method_name = get_names_from_path(path)
    method, method_id = get_method(file, class_name, method_name, with_class_obj=False, with_add=False)
    if not method:
        print("Method not found")
        return None
    db_accesses = DBAccess.get_all(method_id=method_id, type="db")
    return db_accesses


def get_by_method(path,type="db"):
    """メソッドのパスから呼び出し元をたどり、アクセスするdb, es, redisのリストを取得

    Args:
        path (str): 取得したいメソッドのパス
        type (str, optional): アクセスタイプ. Defaults to "db".

    Returns:
        dict: キーにテーブル名、値にアクセスタイプのリスト
            例: {"class_table": ["R", "U"], "method_table": ["C"] }
    """
    from main import trace
    file, class_name, method_name = get_names_from_path(path)
    method, _ = get_method(file, class_name, method_name, with_class_obj=False, with_add=False)
    if not method:
        print("Method not found")
        return None
    
    result = []
    trace(result, method, [], options={'with_db':True,'only_db':True})
    paths = [r["path"] for r in result]
    print(paths)
    db_accesses = [path[-1] for path in paths if f"[{type.upper()}]" in path[-1]]
    result = {}
    db_info_pattern = r"\[(.+?)\] (.+?) \((.+?)\)"
    import re
    print(db_accesses)
    for data in db_accesses:
        m = re.match(db_info_pattern, data)
        if m:
            _type = m.group(1)
            if _type.lower() != type:
                continue
            table_name = m.group(2)
            operation = m.group(3)
            if table_name not in result:
                result[table_name] = []
            if operation not in result[table_name]:
                result[table_name].append(operation)
        # for db in data:
        #     if db.get('type') == type:
        #         if db.get('table') not in result:
        #             result[db.get('table')] = []
        #         if db.get('operation') not in result[db.get('table')]:
        #             result[db.get('table')].append(db.get('operation'))
    return result

def get_endpoint_by_access(table_name, access_type="R", type="db"):
    """テーブル名とアクセスタイプから、そのアクセスをしているエンドポイントを取得

    Args:
        table_name (str): 対象テーブル名
        access_type (str, optional): アクセスタイプ. Defaults to None.
        type (str, optional): アクセスタイプ. Defaults to "db".

    Returns:
        dict: キーにアクセスタイプ、値にEndpointTableオブジェクトのリスト
    """
    from main import trace
    db_accesses = DBAccess.get_all(table_name=table_name, operation_type=access_type, type=type)
    if not db_accesses:
        print(f"{type.upper()} Access not found")
        return None
    result_endpoints = {
        "C": [],
        "R": [],
        "U": [],
        "D": []
    }
    for db_access in db_accesses:
        if db_access.operation_type =="R":
            continue
        method = db_access.method
        result = []
        trace(result, method, [], options={'is_caller': True, 'with_endpoint':True})
        filtered_result = []
        for r in result:
            if r.get('endpoint'):
                filtered_result+=r.get('endpoint')
        result = list(set(filtered_result))
        result_endpoints[db_access.operation_type]+=result
    for key in result_endpoints:
        result_endpoints[key] = list(set(result_endpoints[key]))
    return result_endpoints
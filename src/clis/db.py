
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import db, es, redis, with_operation_id


@db.command()
@click.argument('path')
@click.argument('table_name')
@click.argument('access_type')
@click.option('--condition_method_path', default=None, help='Path of the condition method if any')
@with_operation_id
def add(path, table_name, access_type, condition_method_path=None):
    """DBのアクセス情報を登録

    Args:
        path (str): 呼び出し元メソッド
        table_name (str): 呼び出すテーブル
        access_type (str): アクセスタイプ(C, R, U, D)
        condition_method_path (str, optional): 呼び出し条件.ここに指定したメソッドがそれ以前に呼び出されている場合に使用. Defaults to None.
    """
    from models import OPERATION_TYPES
    if access_type not in OPERATION_TYPES:
        print(f"Invalid access type: {access_type}. Must be one of {OPERATION_TYPES}")
        return
    from db import add_db
    add_db(path, table_name, access_type, condition_method_path)

@db.command()
@click.argument('table_name')
@click.option('--access_type', default=None, help='Filter by access type')
@click.option('--is_trace', '-t', is_flag=True, default=False, help='Trace calls to find endpoints')
@with_operation_id
def get_methods(table_name, access_type, is_trace):
    """テーブル名とアクセスタイプから、そのアクセスをしているメソッドを取得"""
    from db import get_method_by_db_access
    methods = get_method_by_db_access(table_name, access_type)
    if not methods:
        print("No methods found")
    for operation_type, method_list in methods.items():
        print(f"Operation Type: {operation_type}")
        for method in method_list:
            print(f"  {str(method)}")

@db.command()
@click.argument('path')
@with_operation_id
def get_accesses(path):
    """指定したpathから呼ばれるDBアクセスを取得する"""
    from db import get_access_by_method
    accesses = get_access_by_method(path)
    if not accesses:
        print("No DB accesses found")
        return
    for access in accesses:
        print(f"{str(access)}")

@db.command()
@click.argument('path')
@with_operation_id
def get_by_path(path):
    """メソッドのパスから呼び出し元をたどり、アクセスするdbのリストを取得

    Args:
    path (str): 取得したいメソッドのパス
    """
    from db import get_by_method
    accesses = get_by_method(path)
    if not accesses:
        print("No accesses found")
        return
    for table, method in accesses.items():
        print(f"Table: {table}")
        for access in method:
            print(f"  {str(access)}")

@db.command()
@click.argument('table_name')
@click.option('--access_type', default=None, help='Filter by access type')
@with_operation_id
def get_methods_by_table(table_name, access_type):
    """テーブル名とアクセスタイプから、そのアクセスをしているエンドポイントを取得"""
    from db import get_endpoint_by_access
    result = get_endpoint_by_access(table_name,access_type,type="db")
    if not result:
        print("No endpoints found")
        return
    for operation_type, endpoints in result.items():
        print(f"Operation Type: {operation_type}")
        for endpoint in endpoints:
            print(f"  {str(endpoint)}")



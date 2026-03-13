
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import redis, with_operation_id


@redis.command()
@click.argument('path')
@click.argument('index_name')
@click.argument('access_type')
@click.option('--condition_method_path', default=None, help='Path of the condition method if any')
@with_operation_id
def add(path, index_name, access_type, condition_method_path=None):
    from models import OPERATION_TYPES
    if access_type not in OPERATION_TYPES:
        print(f"Invalid access type: {access_type}. Must be one of {OPERATION_TYPES}")
        return
    from db import add_redis
    add_redis(path, index_name, access_type, condition_method_path)

@redis.command()
@click.argument('path')
@with_operation_id
def get_by_path(path):
    """メソッドのパスから呼び出し元をたどり、アクセスするdbのリストを取得

    Args:
    path (str): 取得したいメソッドのパス
    """
    from db import get_by_method
    accesses = get_by_method(path, type="redis")
    if not accesses:
        print("No accesses found")
        return
    for table, method in accesses.items():
        print(f"Table: {table}")
        for access in method:
            print(f"  {str(access)}")
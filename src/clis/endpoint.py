
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import endpoint, with_operation_id
from main import add_endpoint, get_all_endpoints, get_method_by_endpoint

@endpoint.command()
@click.argument('endpoint')
@click.argument('http_method')
@click.argument('path')
@click.option('--type', default='url', help='Type of the endpoint (url, task, tool, cli)')
@with_operation_id
def add(endpoint, http_method, path, type):
    """エンドポイントを追加する

    Args:
        endpoint (str): url, celery-beatのエンドポイント(type=toolの場合は空)
        http_method (str): GET, POSTなど(type=tool,taskの場合は空)
        path (str): 対応するメソッドのパス
        type (str): エンドポイントの種類 (url, task, tool)。デフォルトはurl
    """
    add_endpoint(endpoint, http_method, path, type)


@endpoint.command()
@with_operation_id
def getall():
    endpoints = get_all_endpoints()
    for e in endpoints:
        print(f"{str(e)}: {str(e.method)}")

@endpoint.command()
@click.argument('url')
@click.option('-m','--http_method', help='HTTP method (GET, POST, etc.)')
@click.option('-t', '--type', default='url', help='Type of the endpoint (url, task, tool)')
@click.option('--like', is_flag=True, default=False, help='Use LIKE search for the URL')
def get_method(url, http_method=None, type='url', like=False):
    if like:
        url = f"%{url}%"
    method = get_method_by_endpoint(url, http_method, type)
    if not method:
        print("Method not found")
        return
    for m in method:
        print(f"{str(m)}:{str(m.method)}")
        
@endpoint.command()
@click.argument('endpoint')
@click.option('-m','--http_method', help='HTTP method (GET, POST, etc.)')
@click.option('-t', '--type', default='url', help='Type of the endpoint (url, task, tool)')
@click.option('--like', is_flag=True, default=False, help='Use LIKE search for the URL')
def search(endpoint, http_method=None, type='url', like=False):
    if like:
        endpoint = f"%{endpoint}%"
    accesses = get_method_by_endpoint(endpoint, http_method, type)
    for access in accesses:
        print(access)
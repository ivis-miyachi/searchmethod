import os
import click
import uuid
from utils import ope_id_set, ope_id_reset
from functools import wraps

groups = {}
def with_operation_id(func):
    """Clickコマンドに操作IDを設定するデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        ope_id = uuid.uuid4()
        token = ope_id_set(str(ope_id))
        try:
            return func(*args, **kwargs)
        finally:
            ope_id_reset(token)
    return wrapper

@click.group()
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
@click.option('--profile', is_flag=True, help='Enable cProfile profiling')
def cli(debug, profile):
    if debug:
        if os.environ.get('DEBUGPY_ENABLE', '0') != '1':
            print("Please set DEBUGPY_ENABLE=1 in docker-compose.yml and restart the container.")
        import debugpy
        debugpy.listen(('0.0.0.0', 5678))
        print('debugpy is listening on port 5678...')
        print("Please start the debug feature of vscode")
        debugpy.wait_for_client()
    if profile:
        import cProfile
        import sys
        print("Profiling with cProfile...")
        # プロファイリングはmain関数でラップする必要があるため、sys.argvを使って再実行
        cProfile.run('cli.main()', sort='cumtime')
        sys.exit(0)

@cli.group("class")
def classes():
    pass

groups["classes"] = classes

@cli.group()
def method():
    pass

groups["method"] = method

@cli.group()
def signal():
    pass

groups["signal"] = signal

@cli.group()
def call():
    pass

groups["call"] = call

@cli.group()
def endpoint():
    pass
groups["endpoint"] = endpoint

@cli.group()
@click.option('-c','--with_color', is_flag=True, default=False, help='色付き表示。指定すると同じメソッドに同じ色がつく')
@click.option('-dup','--is_deduplication', is_flag=True, default=False, help='重複表示。指定すると同じメソッドは一度しか表示しない')
@click.pass_context
@with_operation_id
def trace(ctx, with_color, is_deduplication):
    """追跡コマンド"""
    ctx.ensure_object(dict)
    ctx.obj['with_color'] = with_color
    ctx.obj['is_deduplication'] = is_deduplication

groups["trace"] = trace

@cli.group()
def file():
    pass

groups["file"] = file

@cli.group()
def db():
    pass

groups["db"] = db

@cli.group()
def es():
    pass

groups["es"] = es

@cli.group()
def redis():
    pass

groups["redis"] = redis

@cli.command()
@with_operation_id
def restore():
    """直前に行った操作を打ち消す
    ただしconfig.LIMIT_SAVE_HISTORYまで保存される
    また削除操作の打消しはできない
    """
    from utils import restore_operation
    restore_operation()

@cli.group()
def other():
    pass

@other.command()
def not_search():
    from main import not_search_method
    result = not_search_method()
    for r in result:
        method = r['method']
        not_caller = r['not_caller']
        not_callee = r['not_callee']
        print(f"{method.id}: {str(method)} (not_caller={not_caller}, not_callee={not_callee})") 

# @file.command()
# @click.argument('file_path')
# @click.option('--mode', default=1)
# def all_methods(file_path,mode=1):
#     methods = get_all_methods_in_file(file_path)
#     if mode==1:
#         for c, ms in methods.items():
#             print(f"{c}: ")
#             for m in ms:
#                 print(f"  {m.method_name}")
#     elif mode==2:
#         for c, ms in methods.items():
#             for m in ms:
#                 print(f"{str(m)}")
import importlib
import inspect
import pkgutil
import clis
for _, modname, _ in pkgutil.iter_modules(clis.__path__):
    group = groups.get(modname)
    if group is None:
        continue
    module = importlib.import_module(f'clis.{modname}')
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, click.core.Command):
            group.add_command(obj)
            
if __name__ == '__main__':
    cli()
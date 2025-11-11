import click

from method import add_method, get_all_methods_in_file, search_method, delete_method, set_trace_end
from call import add_call
from classes import add_class, get_all_classes
@click.group()
def cli():
    pass

@cli.group("class")
def class_():
    pass

@class_.command()
@click.argument('path')
def add(path):
    add_class(path)

@class_.command()
def getall():
    classes = get_all_classes()
    for c in classes:
        print(f"id={c.id}, path={str(c)}")

@class_.command()
@click.argument('super_class_path')
@click.argument('sub_class_path')
def add_inherit(super_class_path, sub_class_path):
    """クラスの継承情報を追加する
    class A(B)の場合、super_class_pathにBのパス、sub_class_pathにAのパスを指定する
    それぞれのパスは<filepath>:<classname>の形式
    
    Args:
        super_class_path (str): 継承元クラスのパス
        sub_class_path (str): 継承先クラスのパス
    """
    from classes import add_inherit
    add_inherit(super_class_path, sub_class_path)

@class_.command()
@click.argument('before_path')
@click.argument('after_path')
def update(before_path, after_path):
    from classes import update_class
    update_class(before_path, after_path)

@cli.group()
def method():
    pass

@method.command()
@click.argument('path')
def add(path):
    add_method(path)

@method.command()
@click.argument('name')
def search(name):
    search_method(name)

@method.command()
@click.argument('path')
def delete(path):
    delete_method(path)

@method.command()
@click.argument('before_path')
@click.argument('after_path')
def update(before_path, after_path):
    from method import update_method
    update_method(before_path, after_path)

@method.command()
@click.argument('path')
@click.argument('super_class_path')
def move_to_super(path, super_class_path):
    """メソッドに継承元情報を追加する
    pathに登録したクラス.メソッドがクラスになく、
    そのクラスの継承元で定義されているときに使用する

    Args:
        path (str): クラス.メソッドのパス
        super_class_path (str): スーパークラスのパス
    """
    from method import move_method_to_super_class
    move_method_to_super_class(path, super_class_path)

@method.command()
@click.argument('path')
@click.option('--end_flg', default=1, help='Set trace end flag (0 or 1)')
def trace_end(path, end_flg):
    set_trace_end(path, end_flg)

@cli.group()
def signal():
    pass

@signal.command()
@click.argument('path')
def add(path):
    from method import add_signal
    add_signal(path)

@signal.command()
@click.argument('signal_path')
@click.argument('method_path')
def add_connect(signal_path, method_path):
    from method import add_signal_connect
    add_signal_connect(signal_path, method_path)

@cli.group()
def call():
    pass

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.option('--super_class_path', default=None, help='Path of the super class if callee is a super call')
@click.option('--argument_method', default=None, help='Path of the argument method if any')
@click.option('--is_async', default=0, help='Set to 1 if the call is asynchronous')
def add(caller_path, callee_path, super_class_path=None, argument_method=None, is_async=0):
    """メソッドの呼び出し情報を登録する

    Arguments:
        caller_path (str): 呼び出し元パス
        callee_path (str): 呼び出し先パス
        super_class_path (bool, optional): スーパークラスかどうか. Defaults to None.
    """
    add_call(caller_path, callee_path, super_class_path=super_class_path, argument_method=argument_method, is_async=is_async)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.argument('new_caller_path')
def changecaller(caller_path, callee_path, new_caller_path):
    from call import change_caller
    change_caller(caller_path, callee_path, new_caller_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.argument('new_callee_path')
def changecallee(caller_path, callee_path, new_callee_path):
    from call import change_callee
    change_callee(caller_path, callee_path, new_callee_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
def delete(caller_path, callee_path):
    from call import delete_call
    delete_call(caller_path, callee_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_signal_path')
def add_signal_call(caller_path, callee_signal_path):
    from call import add_call_signal
    add_call_signal(caller_path, callee_signal_path)

@cli.group()
def endpoint():
    pass

@endpoint.command()
@click.argument('endpoint')
@click.argument('http_method')
@click.argument('path')
@click.option('--type', default='url', help='Type of the endpoint (url, task, tool)')
def add(endpoint, http_method, path, type):
    from main import add_endpoint
    add_endpoint(endpoint, http_method, path, type)


@endpoint.command()
def getall():
    from main import get_all_endpoints
    endpoints = get_all_endpoints()
    for e in endpoints:
        print(f"{str(e)}: {str(e.method)}")


@cli.group()
def trace():
    pass

@trace.command()
@click.argument('method_path')
@click.option('--mode', default=1)
def method(method_path,mode=1):
    from main import trace_method
    trace_method(method_path,mode)
    
@trace.command()
@click.argument('endpoint')
@click.argument('http_method')
@click.option('--mode', default=1)
def endpoint(endpoint,http_method,mode=1):
    from main import trace_from_endpoint
    trace_from_endpoint(endpoint,http_method)

@trace.command()
@click.argument("caller")
@click.option('--depth', default=1)
def callers(caller,depth=1):
    from main import trace_callers
    trace_callers(caller,depth)

@trace.command()
@click.argument("callee")
@click.option('--depth', default=10)
def callees(callee,depth=1):
    from main import trace_callees
    trace_callees(callee,depth)

@cli.group()
def file():
    pass

@file.command()
@click.argument('file_path')
@click.option('--mode', default=1)
def all_methods(file_path,mode=1):
    methods = get_all_methods_in_file(file_path)
    if mode==1:
        for c, ms in methods.items():
            print(f"{c}: ")
            for m in ms:
                print(f"  {m.method_name}")
    elif mode==2:
        for c, ms in methods.items():
            for m in ms:
                print(f"{str(m)}")

if __name__ == '__main__':
    cli()
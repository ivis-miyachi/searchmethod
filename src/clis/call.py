
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import call, with_operation_id
from call import add_call, search_call, change_caller, change_callee, delete_call, add_call_signal, get_arguments


@call.command()
@click.argument('path')
@with_operation_id
def search(path):
    """指定したメソッドの呼び出し元、呼び出し先をすべて出力

    Args:
        path (_type_): 検索対象のパス
    """
    is_caller=True
    is_callee=True
    print(f"search keyword: {path}")
    result = search_call(path, is_caller=is_caller, is_callee=is_callee)

    for method_path, calls in result.items():
        print(f"Method: {method_path}")
        if is_caller:
            print("  Callers:")
            if calls["caller"]==[]:
                print("    None")
            else:
                for call in calls["caller"]:
                    print(f"    {call.str_with_id()}")
        if is_callee:
            print("  Callees:")
            if calls["callee"]==[]:
                print("    None")
            else:
                for call in calls["callee"]:
                    print(f"    {call.str_with_id()}")

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.option('--super_class_path', default=None, help='Path of the super class if callee is a super call')
@click.option('--argument_method', default=None, help='Path of the argument method if any')
@click.option('--is_async', default=0, help='Set to 1 if the call is asynchronous')
@click.option('--is_recursion', is_flag=True, default=False, help='Set to 1 if the call is a recursion')
@click.option('--is_callee_end', is_flag=True, default=False, help='Set trace end flag on callee method')
@click.option('--is_decorator', is_flag=True, default=False, help='Set to 1 if the call is a decorator call')
@click.option('--is_signal', is_flag=True, default=False, help='Set to 1 if the call is a signal call')
@with_operation_id
def add(caller_path, callee_path, super_class_path=None, argument_method=None, is_async=0, 
        is_recursion=False, is_callee_end=False, is_decorator=False, is_signal=False):
    """メソッドの呼び出し情報を登録する

    Arguments:
        caller_path (str): 呼び出し元パス
        callee_path (str): 呼び出し先パス
        super_class_path (bool, optional): superクラスパス。callee_pathのクラス名が<super>である必要がある. Defaults to None.
        argument_method (str, optional): 指定した呼び出し先となる条件のメソッド.このメソッドがそれより前に呼ばれている場合呼び出し先が使用される. Defaults to None.
        is_async (int, optional): 非同期呼び出しの場合1. Defaults to 0.
        is_recursion (bool, optional): 再帰呼び出しの場合True. Defaults to False.
        is_callee_end (bool, optional): 呼び出し先メソッドにトレース終了フラグを立てる場合True. Defaults to False.
        is_decorator (bool, optional): デコレータ呼び出しの場合True. Defaults to False.
        is_signal (bool, optional): シグナル呼び出しの場合True. Defaults to False.
    """
    is_recursion = 1 if is_recursion else 0
    is_decorator = 1 if is_decorator else 0
    is_signal = 1 if is_signal else 0
    add_call(
        caller_path, callee_path, super_class_path=super_class_path, 
        argument_method=argument_method, is_async=is_async, 
        is_recursion=is_recursion,
        is_callee_end=is_callee_end,
        is_decorator=is_decorator,
        is_signal=is_signal)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.argument('new_caller_path')
@with_operation_id
def changecaller(caller_path, callee_path, new_caller_path):
    """呼び出し元を変更する

    Args:
        caller_path (str): 呼び出し元パス
        callee_path (str): 呼び出し先パス
        new_caller_path (str): 新しい呼び出し元パス
    """
    change_caller(caller_path, callee_path, new_caller_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@click.argument('new_callee_path')
@with_operation_id
def changecallee(caller_path, callee_path, new_callee_path):
    """呼び出し先を変更する
    Args:
        caller_path (str): 呼び出し元パス
        callee_path (str): 呼び出し先パス
        new_callee_path (str): 新しい呼び出し先パス
    """
    change_callee(caller_path, callee_path, new_callee_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_path')
@with_operation_id
def delete(caller_path, callee_path):
    """呼び出し情報を削除する

    Args:
        caller_path (str): 呼び出し元パス
        callee_path (str): 呼び出し先パス
    """
    delete_call(caller_path, callee_path)

@call.command()
@click.argument('caller_path')
@click.argument('callee_signal_path')
@with_operation_id
def add_signal_call(caller_path, callee_signal_path):
    """シグナルの呼び出し情報を登録

    Args:
        caller_path (str): 呼び出し元パス
        callee_signal_path (str): 呼び出されるシグナルパス
    """
    add_call_signal(caller_path, callee_signal_path)

@call.command()
@click.argument('path')
def get_argument(path):
    """そのメソッドに紐づく呼び出し先条件のリスト

    Args:
        path (str): 検索対象
    """
    arguments = get_arguments(path)
    for caller,callee in arguments.items():
        print(f"{caller} -> {callee} ")


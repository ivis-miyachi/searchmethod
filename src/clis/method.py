
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import method, with_operation_id
from method import add_method, get_all_methods_in_file, search_method, set_trace_end, \
    get_delete_targets, delete_method, update_method,move_method_to_super_class, get_by_use,\
        get_method_by_class,set_not_caller
from models import MethodTable

@method.command()
@click.argument('path')
@click.option('--is_signal', is_flag=True, default=False, help='Set to 1 if the call is a signal call')
@with_operation_id
def add(path, is_signal=False):
    """パスからメソッドを登録する"""
    is_signal = 1 if is_signal else 0
    add_method(path, is_signal)
@method.command()
@click.argument('name')
@with_operation_id
def search(name):
    """名前からメソッドを検索する（完全一致)"""
    result = search_method(name)
    print(f"Found {len(result)} methods with name '{name}':")
    for m in result:
        print(f"  id:{m.id}, path:{str(m)}")

@method.command()
@click.argument('path')
@with_operation_id
def delete(path):
    """パスからメソッドを削除する"""
    targets = get_delete_targets(path)
    print(f"delete target: {targets['method_table']}")
    print(f"削除対象")
    for model, target_list in targets.items():
        if model == "method_table":
            continue
        print(f"{model}:")
        if len(target_list) == 0:
            print("  None")
        else:
            for target in target_list:
                print(f"  {str(target)}")
    if click.confirm('本当に削除しますか？', default=False):
        # 4. 削除実行
        delete_method(targets)
        print("deleted")
    else:
        print("canceled")

@method.command()
@click.argument('before_path')
@click.argument('after_path')
@with_operation_id
def update(before_path, after_path):
    update_method(before_path, after_path)

@method.command()
@click.argument('path')
@click.argument('super_class_path')
@with_operation_id
def move_to_super(path, super_class_path):
    """メソッドに継承元情報を追加する
    pathに登録したクラス.メソッドがクラスになく、
    そのクラスの継承元で定義されているときに使用する

    Args:
        path (str): クラス.メソッドのパス
        super_class_path (str): スーパークラスのパス
    """
    move_method_to_super_class(path, super_class_path)

@method.command()
@click.argument('path')
@click.option('--end_flg', default=1, help='Set trace end flag (0 or 1)')
@with_operation_id
def trace_end(path, end_flg):
    """それ以上たどることがないメソッドに設定する"""
    set_trace_end(path, end_flg)

@method.command()
@click.argument('ids', nargs=-1)
def get_by_ids(ids):
    methods = MethodTable.get_by_ids(ids)
    if not methods:
        print("Method not found")
        return
    for method in methods:
        print(f"Method id={method.id}, path={str(method)}")

@method.command()
@click.argument('path')
def get_used(path):
    methods = get_by_use(path)

@method.command()
@click.argument('path')
def get_by_class(path):
    methods = get_method_by_class(path)
    for method in methods:
        print(f"Method id={method.id}, path={str(method)}")

@method.command()
@click.argument('path')
@click.option('--to_false', is_flag=True, default=False, help='Set to 1 if the method has no caller')
@with_operation_id
def set_no_caller(path, to_false):
    """呼び出し元がないメソッドに設定する

    Args:
        path (str): クラス.メソッドのパス
        to_false (bool, optional): 呼び出し元がない場合True. Defaults to False.
    """
    is_not_caller = 1 if not to_false else 0
    set_not_caller(path, is_not_caller)
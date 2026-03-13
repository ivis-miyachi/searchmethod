
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import classes, with_operation_id
from classes import add_class, get_all_classes


@classes.command()
@click.argument('path')
@with_operation_id
def add(path):
    """パスからクラスを登録する"""
    add_class(path)

@classes.command()
@with_operation_id
def getall():
    """登録されているすべてのクラスを取得する"""
    classes = get_all_classes()
    for c in classes:
        print(f"id={c.id}, path={str(c)}")

@classes.command()
@click.argument('super_class_path')
@click.argument('sub_class_path')
@with_operation_id
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

@classes.command()
@click.argument('sub_class_path')
@click.option('--type', default='child', help='Type of inheritance to retrieve (parent or child)')
@with_operation_id
def get_inherit(sub_class_path, type="child"):
    """クラスの継承情報を追加する
    class A(B)の場合、super_class_pathにBのパス、sub_class_pathにAのパスを指定する
    それぞれのパスは<filepath>:<classname>の形式
    
    Args:
        super_class_path (str): 継承元クラスのパス
        sub_class_path (str): 継承先クラスのパス
    """
    from classes import get_inherit
    from utils import tree_to_text
    if type not in ["parent","child"]:
        print("Type must be 'parent' or 'child'")
        return
    inhs = get_inherit(sub_class_path,type=type)
    if not inhs:
        print("No inheritance information found")
        return
    print(f"Inheritance information for {sub_class_path} ({type})")
    print("\n".join(tree_to_text(inhs, type=type,is_last=True)))

@classes.command()
@click.argument('before_path')
@click.argument('after_path')
@with_operation_id
def update(before_path, after_path):
    from classes import update_class
    update_class(before_path, after_path)
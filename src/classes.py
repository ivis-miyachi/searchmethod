from sqlalchemy.orm import Session


from models import ClassTable, InheritTable, MethodTable
from file import get_file
from utils import get_names_from_path

def get_class(file, class_name, with_add=True):
    """クラスnameとfileからクラスid, nameを取得。なければ作成

    Args:
        file (str): クラスがあるファイル
        class_name (str): クラス名
        with_add (bool, optional): なかった場合作成するかどうか. Defaults to True.
    Returns:
        (Class, int): クラスオブジェクトとそのID
    """
    file = get_file(file,with_add=with_add)[0]
    class_obj = ClassTable.get(class_name, file.path)
    if class_name and not class_obj and with_add:
        class_obj = add_class(f"{file}:{class_name}")

    return class_obj, class_obj.id if class_obj else None

def add_class(path=None):
    if path:
        file, class_name, _ = get_names_from_path(path,only_class=True)
    old = ClassTable.get(class_name, file)
    if old:
        print("Class already exists")
        return old.id
    c = ClassTable.create(class_name, file)
    return c

def get_all_classes():
    return ClassTable.get_all()

def add_inherit(super_class_path, sub_class_path):
    sub_file, sub_class_name, _ = get_names_from_path(sub_class_path,only_class=True)
    super_file, super_class_name, _ = get_names_from_path(super_class_path,only_class=True)
    if "." in sub_class_name or "." in super_class_name:
        print("Inherit can only be added between classes, not methods")
        return None
    sub_class_obj, sub_class_id = get_class(sub_file, sub_class_name, with_add=True)
    super_class_obj, super_class_id = get_class(super_file, super_class_name, with_add=True)

    old = InheritTable.get(super_class_id, sub_class_id)
    if old:
        print("Inherit already exists")
        return old.id
    inh = InheritTable.create(super_class_id, sub_class_id)
    print(f"Inherit added: id= {inh.id}, path={str(sub_class_obj)} -> {str(super_class_obj)}")
    return inh

def get_inherit(path,type="parent"):
    file, class_name, _ = get_names_from_path(path,only_class=True)
    class_obj, class_id = get_class(file, class_name, with_add=False)
    if not class_obj:
        print("Class not found")
        return None
    if type=="parent":
        inhs = InheritTable.get_descendants_tree_parent(class_id)
    else:
        inhs = InheritTable.get_descendants_tree_child(class_id)
    return inhs

def delete_class(path):
    from models import InheritTable
    file, class_name, _ = get_names_from_path(path,only_class=True)
    class_obj, class_id = get_class(file, class_name, with_add=False)
    if not class_obj:
        print("Class not found")
        return None
    # クラスに関連する継承情報を削除
    inhs = InheritTable.get_all(child_id=class_id)
    for inh in inhs:
        inh.delete()
    inhs = InheritTable.get_all(parent_id=class_id)
    for inh in inhs:
        inh.delete()
    class_obj.delete()
    print(f"Class deleted: id= {class_id}, path={str(class_obj)}")
    
    
    
    
def update_class(before_path, after_path):
    from models import ClassTable
    before_file, before_class_name, _ = get_names_from_path(before_path,only_class=True)
    after_file, after_class_name, _ = get_names_from_path(after_path,only_class=True)
    
    before_class_obj, before_class_id = get_class(before_file, before_class_name, with_add=False)
    before_file, before_file_id = get_file(before_file, with_add=False)
    if not before_class_obj:
        print("Class not found")
        return None

    target_class, target_id = get_class(after_file, after_class_name, with_add=False)[0]
    
    
    if target_class:
        inhs = InheritTable.get_all(parent_id=before_class_id)
        for i in inhs:
            i.update_parent(target_id)
        inhs = InheritTable.get_all(child_id=before_class_id)
        for i in inhs:
            i.update_child(target_id)

        methods = MethodTable.get_all(class_id=before_class_id,file=before_file_id)
        for m in methods:
            m.update(m.method_name,target_class.file.path, target_id)
        delete_class(before_path)
    else:
        # 変更先のクラスが存在しない場合、クラス自体を更新
        # 新しいファイルを作成した場合、元のファイルを使用しているクラス、メソッドがないならそれを削除
        _, new_file_id = get_file(after_file, with_add=True)
        
        if after_file != before_file and \
            before_file.refs() == 1:
                before_file.delete()
        
        before_class_obj.update(after_class_name, new_file_id)



from models import MethodTable, ClassTable, FileTable, CallMethodTable, EndpointTable, SignalTable, SignalConnectTable
from utils import get_names_from_path
from classes import get_class, add_class
from file import get_file

def get_method(file, class_, method_name, with_class_obj=True, with_add=True):
    """ファイル名、クラス、メソッド名からメソッドを取得

    Args:
        file (str): ファイル名
        class_obj (str, obj): クラス名かクラスオブジェクト
        method_name (str): メソッド名
        with_class_obj (bool, optional): class_objがクラスオブジェクトかどうか. Defaults to True.
        with_add (bool, optional): なかった場合作成するかどうか. Defaults to True.

    Returns:
        (Method, int): メソッドとそのID
    """
    if class_:
        if with_class_obj:
            class_obj = class_
            class_id = class_obj.id
        else:
            class_obj, class_id = get_class(file, class_, with_add=with_add)
    else:
        class_id = None
    method = MethodTable.get(method_name, file, class_id)
    if method_name and not method and with_add:
        method = add_method(f"{file}:{method_name}" if not class_id else f"{file}:{class_obj.name}.{method_name}")
    
    return method, method.id if method else None

def add_method(path=None):
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        _, class_id = get_class(file, class_name)
    old = MethodTable.get(method_name, file, class_id)
    if old:
        print("Method already exists")
        return old.id
    m = MethodTable.create(method_name, file, class_id)
    return m

def get_all_methods():
    return MethodTable.get_all()

def get_all_methods_in_file(file):
    methods = MethodTable.get_all(file=file)
    result = {}
    
    for m in methods:
        class_name = m.class_.name if m.class_id else None
        if class_name not in result:
            result[class_name] = []
        result[class_name].append(m)
    return result

def move_method_to_super_class(method_path, super_class_path):
    """メソッドに継承元情報を追加する
    
    Args:
        method_path (str): 対象メソッドパス
        super_class_path (str): 実際に定義しているメソッドパス
    """
    # それぞれのパスを解析
    file, class_name, method_name = get_names_from_path(method_path)
    super_file, super_class_name, super_method_name = get_names_from_path(super_class_path)
    # 元のメソッドのデータを取得(ないとエラー)
    method, method_id = get_method(file, class_name, method_name, with_class_obj=False, with_add=False)
    if not method:
        print("Method not found")
        return
    # 継承元のメソッドのデータを取得（ないなら作成）
    super_method, super_method_id = get_method(super_file, super_class_name, method_name, with_class_obj=False, with_add=True)
    # 元のメソッドのデータのフラグをTrueにする
    method.set_inherit_flg(1)

def search_method(path):
    if ":" in path:
        file = path.split(":")[0].strip()
        method_class = path.split(":")[1]
    else:
        file = None
        method_class = path.strip()
    if "." in method_class:
        class_name = method_class.split(".")[0].strip()
        method_name = method_class.split(".")[1].strip()
    else:
        class_name = None
        method_name = method_class.strip()
    

    methods = MethodTable.get_all(method_name=method_name,file=file,class_name=class_name)
    print(f"Found {len(methods)} methods with name '{method_name}':")
    for m in methods:
        print(f"  {str(m)}")

def delete_method(path):
    """メソッドを削除する
    削除対象メソッドをcaller, calleeとして参照しているCallMethodも削除する
    もし所属クラス・ファイルに他のメソッドやクラスがなければそれらも削除する
    
    Args:
        path (str): 削除対象のパス
    """
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        class_obj = ClassTable.get(class_name, file)
        if not class_obj:
            print("Class not found")
            return
        class_id = class_obj.id
    method = MethodTable.get(method_name, file, class_id)
    if not method:
        print("Method not found")
        return
    
    call_by_callees = CallMethodTable.get_all_by_callee(method.id)
    call_by_callers = CallMethodTable.get_all_by_caller(method.id)
    for call in call_by_callees:
        call.delete()
    for call in call_by_callers:
        call.delete()
    
    alone_file_class = False
    file_obj = method.file
    if file_obj.class_count() == 1 or class_name is None:
        alone_file_class = True
        
    if class_name:
        if class_obj.method_count() == 1:
            print(f"Also deleting class as it has no other methods: {str(class_obj)}")
            class_obj.delete()

    if file_obj.method_count() == 1 and alone_file_class:
        print(f"Also deleting file as it has no other classes or methods: {str(file_obj)}")
        file_obj.delete()
    method.delete()
    
    print(f"Method deleted: {str(method)}")

def update_method(before_path, after_path):
    """メソッド名などを更新する
    もし更新先のメソッドが存在すれば、そちらに関連するCallMethodやEndpointをすべて移動し、元のメソッドを削除する
    更新先のメソッドが存在しなければ、メソッド自体を更新する
    もとの所属クラス・ファイルに他のメソッドやクラスがなければ削除する
    Args:
        before_path (str): 更新前パス
        after_path (str): 更新後パス
    """
    before_file, before_class_name, before_method_name = get_names_from_path(before_path)
    after_file, after_class_name, after_method_name = get_names_from_path(after_path)

    method, method_id = get_method(before_file,before_class_name,before_method_name,with_class_obj=False,with_add=False)
    if not method:
        print("Method not found")
        return
    target_method,target_method_id = get_method(after_file, after_class_name, after_method_name, with_class_obj=False, with_add=False)
    if target_method:
        # beforeを使用していたcallをすべてafterに変更し、元のメソッドを削除
        calls = CallMethodTable.get_all_by_callee(method_id)
        for call in calls:
            call.change_callee(target_method_id)
        calls = CallMethodTable.get_all_by_caller(method_id)
        for call in calls:
            call.change_caller(target_method_id)
        endpoints = EndpointTable.get_all(method_id=method_id)
        for ep in endpoints:
            ep.update_method(target_method_id)
        delete_method(before_path)
    else:
        # 変更先のメソッドが存在しない場合、メソッド自体を更新
        new_class_id = None
        if after_class_name:
            after_class_obj, new_class_id = get_class(after_file, after_class_name, with_add=True)

        file_obj, new_file_id = get_file(after_file, with_add=True)
    
        alone_file_class = False
        old_file_obj = method.file
        # もとの所属クラス・ファイルに他のメソッドやクラスがなければ削除
        if old_file_obj.refs() == 1 or before_class_name is None:
            alone_file_class = True
        if before_class_name:
            before_class, _ = get_class(before_file, before_class_name, with_add=False)
            if before_class.refs() == 1:
                print(f"Also deleting class as it has no other methods: {str(before_class)}")
                before_class.delete()

        if old_file_obj.refs() == 1 and alone_file_class:
            print(f"Also deleting file as it has no other classes or methods: {str(old_file_obj)}")
            old_file_obj.delete()

        method.update(after_method_name, new_file_id=new_file_id, new_class_id=new_class_id)
        print(f"Method changed: id={method_id}, path={str(method)}")

def set_trace_end(path, flg):
    """メソッドのトレース終了フラグを設定する

    Args:
        path (str): メソッドパス
        flg (int): 0 or 1
    """
    file, class_name, method_name = get_names_from_path(path)
    class_obj = None
    if class_name:
        class_obj = get_class(file, class_name, with_add=False)[0]
        if not class_obj:
            print("Class not found")
            return
    method, _ = get_method(file, class_obj, method_name, with_add=False)
    if not method:
        print("Method not found")
        return
    method.set_is_trace_end(flg)
    
    
    
def get_signal(file, method_name, with_add=True):
    signal = SignalTable.get(method_name, file)
    if not signal and with_add:
        signal = add_signal(f"{file}:{method_name}")
    return signal, signal.id if signal else None


def add_signal(path):
    file, _, method_name = get_names_from_path(path)
    old = SignalTable.get(method_name, file)
    if old:
        print("Signal already exists")
        return old.id
    s = SignalTable.create(method_name, file)
    return s

def add_signal_connect(signal_path, connect_method_path):
    signal_file, _, signal_method_name = get_names_from_path(signal_path)
    signal, signal_id = get_signal(signal_file, signal_method_name, with_add=True)

    connect_file, connect_class_name, connect_method_name = get_names_from_path(connect_method_path)
    connect_class, connect_class_id = get_class(connect_file, connect_class_name)
    connect_method, connect_method_id = get_method(connect_file, connect_class, connect_method_name)

    old = SignalConnectTable.get(signal_id, connect_method_id)
    if old:
        print("Signal Connect already exists")
        return old.id
    sc = SignalConnectTable.create(signal_id=signal_id, connect_method_id=connect_method_id)
    print(f"Signal Connect added: id= {sc.id}, path={str(signal)} -> {str(connect_method)}")
    return sc
    
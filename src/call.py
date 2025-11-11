
from models import CallMethodTable, InheritTable, SignalCallTable
from classes import get_class
from method import get_method, get_signal
from utils import get_names_from_path

def add_call(caller_path, callee_path, super_class_path=None, argument_method=None, is_async=0):
    """
    メソッド呼び出し関係を追加
    super(A).xxxのような呼び出しの場合、super_class_pathで親クラスのパスを指定する
    またcallee_pathのクラス名は<super>とする
    例: クラスAにmethod1があり、クラスBがAを継承していて、Bのmethod2からsuper(A).method1を呼び出している場合
    caller_path: filepath:B.method2
    callee_path: filepath:<super>.method1
    super_class_path: filepath:A
    
    メソッドの引数のメソッドを使用する場合(record.get_recordなど)は、呼び出し元によってクラスが違う
    その場合argument_methodに呼び出し元のメソッドを指定する
    またその際のcellee_pathのクラス名は<argument>とする
    """
    
    caller_file, caller_class_name, caller_method_name = get_names_from_path(caller_path)
    callee_file, callee_class_name, callee_method_name = get_names_from_path(callee_path)
    is_super = 0 if not callee_class_name == "<super>" else 1
    # if argument_method:
    #     if callee_class_name != "<argument>":
    #         print("Callee class name must be <argument> when argument_method is specified")
    #         return
    # クラスが未登録なら追加
    caller_class, caller_class_id = get_class(caller_file, caller_class_name)
    if is_super and super_class_path:
        super_class_file, super_class_name, _ = get_names_from_path(super_class_path, only_class=True)
        callee_class_name = super_class_name
        callee_file = super_class_file
    
    elif is_super and not super_class_path:
        print("Super class path is required for super calls")
        return
    
    
    callee_class, callee_class_id = get_class(callee_file, callee_class_name)
    if is_super:
        old_inh = InheritTable.get(callee_class_id, caller_class_id)
        if not old_inh:
            inh = InheritTable.create(callee_class_id, caller_class_id)
    # メソッドが未登録なら追加
    caller_method, caller_id = get_method(caller_file, caller_class, caller_method_name)
    callee_method, callee_id = get_method(callee_file, callee_class, callee_method_name)

    if not caller_id or not callee_id:
        print(f"Method not found, caller: {caller_id}, callee: {callee_id}")
        return

    old = CallMethodTable.get(caller_id, callee_id, is_super=is_super)
    if old:
        print(f"Call already exists: caller_id={caller_id}, callee_id={callee_id}, is_super={is_super}")
        return
    if argument_method:
        argument_method,_ = get_method(*get_names_from_path(argument_method), with_class_obj=False, with_add=False)
        if not argument_method:
            print("Argument method not found")
            return
    c = CallMethodTable.create(caller_id=caller_id, callee_id=callee_id, is_super=is_super, argument_method=argument_method, is_async=is_async)

def change_caller(caller_path, callee_path, new_caller_path):
    caller_file, caller_class_name, caller_method_name = get_names_from_path(caller_path)
    callee_file, callee_class_name, callee_method_name = get_names_from_path(callee_path)
    new_caller_file, new_caller_class_name, new_caller_method_name = get_names_from_path(new_caller_path)
    is_super = 0 if not callee_class_name == "<super>" else 1
    caller_method = get_method(caller_file, caller_class_name, caller_method_name, 
                               with_class_obj=False, with_add=False)
    callee_method = get_method(callee_file, callee_class_name, callee_method_name, 
                               with_class_obj=False, with_add=False)
    call = CallMethodTable.get(caller_method.id, callee_method.id, is_super=is_super)
    if not call:
        print("Call not found")
        return
    new_caller_method = get_method(new_caller_file, new_caller_class_name, new_caller_method_name, 
                                   with_class_obj=False, with_add=False)
    if not new_caller_method:
        print("New caller method not found")
        return
    call.change_caller(new_caller_method.id)
    print(f"old_call: {caller_method_name} -> {callee_method_name}")
    print(f"new_call: {str(call)}")

def change_callee(caller_path, callee_path, new_callee_path):
    caller_file, caller_class_name, caller_method_name = get_names_from_path(caller_path)
    callee_file, callee_class_name, callee_method_name = get_names_from_path(callee_path)
    new_callee_file, new_callee_class_name, new_callee_method_name = get_names_from_path(new_callee_path)
    is_super = 0 if not callee_class_name == "<super>" else 1
    caller_method = get_method(caller_file, caller_class_name, caller_method_name, 
                               with_class_obj=False, with_add=False)
    callee_method = get_method(callee_file, callee_class_name, callee_method_name, 
                               with_class_obj=False, with_add=False)
    call = CallMethodTable.get(caller_method.id, callee_method.id, is_super=is_super)
    if not call:
        print("Call not found")
        return
    new_callee_method = get_method(new_callee_file, new_callee_class_name, new_callee_method_name, 
                                   with_class_obj=False, with_add=False)
    if not new_callee_method:
        print("New callee method not found")
        return
    call.change_callee(new_callee_method.id)
    print(f"old_call: {caller_method_name} -> {callee_method_name}")
    print(f"new_call: {str(call)}")

def delete_call(caller_path, callee_path):
    caller_file, caller_class_name, caller_method_name = get_names_from_path(caller_path)
    callee_file, callee_class_name, callee_method_name = get_names_from_path(callee_path)
    is_super = 0 if not callee_class_name == "<super>" else 1
    _, caller_id = get_method(caller_file, caller_class_name, caller_method_name, 
                               with_class_obj=False, with_add=False)
    _, callee_id = get_method(callee_file, callee_class_name, callee_method_name, 
                               with_class_obj=False, with_add=False)
    call = CallMethodTable.get(caller_id, callee_id, is_super=is_super)
    if not call:
        print("Call not found")
        return
    print(f"Call deleted: {str(call)}")
    call.delete()


def add_call_signal(caller_path, callee_signal_path):
    caller_file, caller_class_name, caller_method_name = get_names_from_path(caller_path)
    caller_class, caller_class_id = get_class(caller_file, caller_class_name)
    caller_method, caller_id = get_method(caller_file, caller_class, caller_method_name)

    callee_signal_file, callee_signal_class_name, callee_signal_method_name = get_names_from_path(callee_signal_path)
    callee_signal, callee_signal_id = get_signal(callee_signal_file, callee_signal_method_name, with_add=True)
    
    old = SignalCallTable.get(caller_id, callee_signal_id)
    if old:
        print(f"Signal Call already exists: caller_id={caller_id}, callee_signal_id={callee_signal_id}")
        return
    c = SignalCallTable.create(caller_id, callee_signal_id)
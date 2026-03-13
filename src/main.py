
import sys
from models import Base, ClassTable, InheritTable, MethodTable, CallMethodTable, EndpointTable, DecoratorTable, session, MethodArgumentClassMap, SignalCallTable, SignalConnectTable, DBAccess, FileTable
from utils import get_names_from_path, build_tree, print_tree, ope_id_get
from method import get_method, add_method
from classes import get_class, add_class
from config import SUPER_DECOLATOR, TRACE_END_DECOLATOR, ASYNC_DECOLATOR, INHERITED_DECOLATOR, \
    SIGNAL_DECOLATOR, MSG_NOT_REGISTERED_INHERIT, MSG_REACHED_DEPTH_LIMIT,\
    DECOLATOR_DECOLATOR,RECURSION_DECOLATOR, TIMESTAMP_DECOLATOR
import re

def add_endpoint(endpoint, http_method, path, type="url"):
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        class_obj = ClassTable.get(class_name, file)
        class_id = class_obj.id if class_obj else None
    method = MethodTable.get(method_name, file, class_id)
    if not method:
        print("Method not found")
        return
    method_id = method.id
    old = EndpointTable.get(endpoint, http_method, method_id)
    if old:
        print("Endpoint already exists")
        return
    e = EndpointTable.create(endpoint, http_method, method_id, type)
    print(f"Endpoint added: id={e.id}, {str(e)}")

# def trace_method(file, method_name, class_name):
def trace_method(path, mode=1):
    """メソッドから、それを呼び出しているメソッドを追跡
    エンドポイントごとに、メソッドからそこに到達するまでを機構造で出力

    Args:
        path (str): 追跡するメソッドのパス(filepath:(class.)method)
        mode (int, optional): 出力モード. Defaults to 1.
    """
    file, class_name, method_name = get_names_from_path(path)

    # 指定クラス＋親クラスの同名メソッドも対象
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
    # method = method.id
    result = []
    def trace(m, path, is_super=False, is_async=False):
        def trace_super_classes(class_id, method_name, path):
            parent_inherits = InheritTable.get_all(parent_id=None, child_id=class_id)
            for inh in parent_inherits:
                parent = inh.parent
                # 親クラスに同名メソッドがあるか
                parent_method = MethodTable.get(method_name, file=parent.file.path, class_id=parent.id)
                
                if parent_method:
                    if parent_method.is_inherited:
                        trace_super_classes(parent.id, method_name, path + [str(parent_method) + "(inherited)"])
                    else:
                        trace(parent_method, path)

        mid = m.id
        target = str(m) + "(super)" if is_super else str(m)
        if m.is_trace_end:
            target += " (trace end)"
        if is_async:
            target += " (async)"

        if m.is_inherited:
            trace_super_classes(m.class_id, m.method_name, path+[target+"(inherited)"])
        else:
            calls = CallMethodTable.get_all(callee_id=mid)
            eps = EndpointTable.get_all(method_id=mid)
            if eps:
                
                result.append({"endpoint":[str(ep) for ep in eps], "path": path + [str(MethodTable.get_by_id(mid))]})
            if not eps and not calls:
                result.append({'path': path + [target]})
            for call in calls:
                
                callee = call.caller
                if call.is_change_by_caller:
                    # callに紐づくmapを取得
                    method_maps = MethodArgumentClassMap.get_by_call(call.id)
                    for map in method_maps:
                        # path内にcaller_methodがあれば、そのmapに対応するクラスでcalleeを取得し直す
                        caller_method = MethodTable.get_by_id(map.caller_method_id)
                        if caller_method:
                            caller_path = str(caller_method)
                            if caller_path in path:
                                class_map_id = map.argument_class_id
                                class_map = ClassTable.get_by_id(class_map_id)
                                if class_map:
                                    callee, _ = get_method(class_map.file.path,class_map,call.callee.method_name,with_add=False)
                is_async = call.is_async
                trace(callee, path + [target], is_super=call.is_super, is_async=is_async)
            signal_calls = SignalCallTable.get_all(caller_id=mid)
            for sc in signal_calls:
                connect_methods = SignalConnectTable.get_by_signal(sc.signal_id)
                for connect_method in connect_methods:
                    trace(connect_method.connect_method, path + [target]+[str(sc.signal)+"(signal)"], is_super=False)

    # def trace(m, path):
    #     def trace_super_classes(class_id, method_name, path, d):
    #         parent_inherits = InheritTable.get_all(parent_id=None, child_id=class_id)
    #         for inh in parent_inherits:
    #             parent = inh.parent
    #             # 親クラスに同名メソッドがあるか
    #             parent_method = MethodTable.get_by_id(method_name, file=parent.file, class_id=parent.id)
    #             if parent_method:
    #                 trace(parent_method.id, path + [str(MethodTable.get_by_id(mid))+"(super)"])
    #                 # 継承元の親クラスもさらにたどる
    #                 trace_super_classes(parent.id, method_name, path, d)
    #     mid = m.id
    #     calls = CallMethodTable.get_all(callee_id=mid)
    #     eps = EndpointTable.get_all(method_id=mid)
    #     if eps:
    #         result.append({"endpoint":[str(ep) for ep in eps], "path": path + [str(MethodTable.get_by_id(mid))]})
    #     if not eps and not calls:
    #         # エンドポイントにも呼び出し元にも到達しなかった場合、その軌跡を記録
    #         result.append({'endpoint': [], 'path': path + [str(MethodTable.get_by_id(mid))]})
    #     for call in calls:
    #         print(call)
    #         trace(call.caller_id, path + [str(MethodTable.get_by_id(mid))+"(super)" if call.is_super else str(MethodTable.get_by_id(mid))])
    #     method_class = MethodTable.get_by_id(mid).class_id
    #     print(f"method_class: {method_class}")
    #     if method_class:
    #         trace_super_classes(method_class.id, m.method_name, path, d=0)


        # method_obj = MethodTable.get_by_id(mid)
        # if method_obj and method_obj.class_id:
        #     trace_super_classes(method_obj.class_id, method_obj.method_name, path, d=0)



    trace(method, [])
    if mode==1:
        r1 = {}
        for r in result:
            if r.get('endpoint') == []:
                if 'No Endpoint' not in r1:
                    r1['No Endpoint'] = []
                r1['No Endpoint'].append(r['path'])
                continue
            for e in r.get('endpoint', []):
                if e not in r1:
                    r1[e] = []
                r1[e].append(r['path'])
        for endpoint, paths in r1.items():
            tree = build_tree(paths)
            from utils import count_keys, assign_colors
            key_counts = count_keys(tree)
            color_map = assign_colors(key_counts)
            print_tree(tree, color_map=color_map)

def is_exist_inherited(class_id, method,is_caller=False):
    """そのメソッドが継承されたものかどうか

    Args:
        class_id (str): クラスID
        method (str): メソッドID
        is_caller (bool, optional): callerかどうか. Defaults to False.

    Returns:
        bool: True: 継承されたもの, False: 継承されていないもの
    """
    is_inherited = False
    if is_caller:
        children = InheritTable.get_all(parent_id=class_id)
        if children:
            for child in children:
                m = MethodTable.get(method.method_name,file=child.child.file.path, class_id=child.child.id)
                if m:
                    is_inherited = True
                    break
    else:
        is_inherited = method.is_inherited
    return is_inherited

def trace(result, method, path, depth=None, options={}, timestamp=""):
    """メソッドから呼び出し元、呼び出し先をたどる

    Args:
        result (list): 結果
        method (MethodTable): たどりたいメソッドオブジェクト
        path (list): たどった結果のパス
        depth (int, optional): たどりたい限界の深さ. Defaults to None.
        options (dict, optional): オプションをまとめたリスト. Defaults to {}.
            例):
                with_db: dbアクセスを取得するか。デフォルトはTrue
                is_super: スーパークラスのメソッドもたどるか。デフォルトはFalse
                is_async: 非同期メソッドもたどるか。デフォルトはFalse
                is_caller: 呼び出し元をたどるか。デフォルトはFalse(呼び出し先をたどる)
                with_endpoint: エンドポイント情報もたどるか。デフォルトはFalse
    """
        #   with_db=True, 
        #   is_super=False, is_async=False, is_caller=False,
        #   with_endpoint=False):
    with_db = options.get('with_db', True)
    is_super = options.get('is_super', False)
    is_async = options.get('is_async', False)
    is_decorator = options.get('is_decorator', False)
    is_signal = options.get('is_signal', False)
    is_caller = options.get('is_caller', False)
    with_endpoint = options.get('with_endpoint', False)
    is_timestamp = options.get('timestamp', False)
    
    def msg_timestamp(call):
        if is_timestamp:
            return TIMESTAMP_DECOLATOR.format(call.created.strftime("%Y-%m-%d"))
        else:
            return ""
        
    def trace_super_classes(res, class_id, mm, path, is_caller=False,d=None):

        id_key = "child_id" if is_caller==False else "parent_id"
        obj_key = "parent" if is_caller==False else "child"
        args = {id_key: class_id}
        inherits = InheritTable.get_all(**args)
        
        if not inherits:
            res.append({'path': path+[MSG_NOT_REGISTERED_INHERIT]})
            return res
        for inh in inherits:
            
            parent = getattr(inh, obj_key)
            method_name = mm.method_name
            # 親クラスに同名メソッドがあるか
            parent_method = MethodTable.get(method_name, file=parent.file.path, class_id=parent.id)
            # is_callee->parent_methodがある
            
            if parent_method:
                if is_exist_inherited(parent.id, parent_method, is_caller):
                    res = trace_super_classes(res, parent.id, mm, path + [str(parent_method) + INHERITED_DECOLATOR], is_caller, d-1 if type(d) is int else None)
                else:
                    new_options = options.copy()
                    new_options['is_super'] = False
                    new_options['is_async'] = False
                    new_options['is_decorator'] = False
                    res = trace(res,parent_method, path, d, options=new_options)
                    
        return res
    mid = method.id
    
    target = str(method) + SUPER_DECOLATOR if is_super else str(method)
    if method.is_trace_end:
        target += TRACE_END_DECOLATOR
    if is_async:
        target += ASYNC_DECOLATOR
    if is_decorator:
        target += DECOLATOR_DECOLATOR
    if is_signal:
        target += SIGNAL_DECOLATOR
    if depth == 0:
        result.append({'path': path + [target, MSG_REACHED_DEPTH_LIMIT]})
        return result
    # if method.is_inherited:
    #     result = trace_super_classes(result, method.class_id, method, path+[target+INHERITED_DECOLATOR], d=depth)
    if is_exist_inherited(method.class_id, method, is_caller):
        result = trace_super_classes(result, method.class_id, method, path+[target+INHERITED_DECOLATOR], is_caller=is_caller, d=depth)
    else:
        key = "callee_id" if is_caller else "caller_id"
        args = {key: mid}
        calls = CallMethodTable.get_all(**args)
        next_path = path + [target + timestamp]
        if with_endpoint:
            eps = EndpointTable.get_all(method_id=mid)
            result.append({"endpoint":[str(ep) for ep in eps], "path": path + [str(MethodTable.get_by_id(mid))+timestamp]+[str(ep)+msg_timestamp(ep) for ep in eps]})
        if ((with_endpoint and not eps) or not with_endpoint) and not calls:
            result.append({'path': next_path})
        
        for call in calls:
            if call.is_recursion:
                result.append({'path': next_path + [str(call.callee) + RECURSION_DECOLATOR + msg_timestamp(call)]})
                continue
            attr_name = "caller" if is_caller else "callee"
            callee = getattr(call, attr_name)
            if call.is_change_by_caller:
                # callに紐づくmapを取得
                method_maps = MethodArgumentClassMap.get_by_call(call.id)
                is_exists_argument = False
                
                for map in method_maps:
                    # path内にcaller_methodがあれば、そのmapに対応するクラスでcalleeを取得し直す
                    caller_method = MethodTable.get_by_id(map.caller_method_id)
                    if not caller_method:
                        callee = callee if is_exists_argument else None
                        continue
                    caller_path = str(caller_method)
                    caller_pattern = re.compile(rf"^{re.escape(caller_path)}(\(.*\))?$")
                    # そのメソッド,クラスとなる条件のメソッドがパスにないかつターゲットでないならスキップ
                    if not (any(caller_pattern.match(s) for s in path) or caller_path == str(method)):
                        callee = callee if is_exists_argument else None
                        continue
                    class_map_id = map.argument_class_id
                    file_map_id = map.argument_file_id
                    class_map = ClassTable.get_by_id(class_map_id)
                    file_map = FileTable.get_by_id(file_map_id)
                    callee, _ = get_method(file_map.path,class_map,call.callee.method_name,with_add=False)
                    is_exists_argument = True
                if not is_exists_argument:
                    callee=None
                    result.append({'path': next_path+["not_exist_argument"]})
            is_async = call.is_async
            is_decorator = call.is_decorator
            is_signal = call.is_signal
            if callee is None:
                continue
            new_options = options.copy()
            new_options['is_super'] = call.is_super
            new_options['is_async'] = is_async
            new_options['is_decorator'] = is_decorator
            new_options['is_signal'] = is_signal
            callee_path = str(callee)
            callee_pattern = re.compile(rf"^{re.escape(callee_path)}(\(.*\))?$")
            if any(callee_pattern.match(s) for s in path) and str(method) != callee_path:
                # すでにたどったメソッドならスキップ
                result.append({'path': next_path + [callee_path + RECURSION_DECOLATOR + msg_timestamp(call)]})
                continue
            result = trace(result, callee, next_path, depth-1 if type(depth) is int else None, options = new_options,timestamp=msg_timestamp(call))
        new_options = options.copy()
        new_options['is_super'] = False
        new_options['is_async'] = False
        new_options['is_decorator'] = False
        new_options['is_signal'] = False
        if with_db:
            dbs = DBAccess.get_all(method_id=mid)
            for db in dbs:
                if db.condition_method_id:
                    condition_method = MethodTable.get_by_id(db.condition_method_id)
                    condition_path = str(condition_method)
                    condition_pattern = re.compile(rf"^{re.escape(condition_path)}(\(.*\))?$")
                    if not any(condition_pattern.match(s) for s in path):
                        continue

                result.append({'path': next_path + [db.output_str()]})
    return result

def get_signal_calls_in_callee(result, mid, path, target, d=None, options={}):
    signal_calls = SignalCallTable.get_all(caller_id=mid)
    for sc in signal_calls:
        connect_methods = SignalConnectTable.get_by_signal(sc.signal_id)
        if not connect_methods:
            result.append({'path': path + [target]+[str(sc.signal)+SIGNAL_DECOLATOR, "no_connect_method"]})
        for connect_method in connect_methods:
            result = trace(result, connect_method.connect_method, path + [target]+[str(sc.signal)+SIGNAL_DECOLATOR], d-1 if type(d) is int else None,options=options)
    return result

def get_signal_calls_in_caller(result, mid, path, target, d=None, options={}):
    signals = SignalConnectTable.get_from_connect_method(mid)
    for signal in signals:
        signalcalls = SignalCallTable.get_all(signal_id=signal.signal_id)
        
        for call in signalcalls:
            result = trace(result, call.caller_method, path + [target]+[str(signal.signal)+"(signal)"], d-1 if type(d) is int else None, options=options)
    return result

# エンドポイントから呼び出し元メソッドをたどる
def trace_from_endpoint(endpoint, http_method):
    eps = EndpointTable.get_all(endpoint=endpoint, http_method=http_method)
    if not eps:
        print("Endpoint not found")
        return
    result = []
    def trace(mid, path):
        calls = CallMethodTable.get_all(caller_id=mid)
        if not calls:
            # 呼び出し元がなければ経路を記録
            result.append({'method_id': mid, 'path': path + [str(MethodTable.get_by_id(mid))]})
        for call in calls:
            trace(call.callee_id, path + [str(MethodTable.get_by_id(mid))])
    for ep in eps:
        trace(ep.method_id, [])
    paths = [list(reversed(r["path"])) for r in result]
    tree = build_tree(paths)
    print_tree(tree)

# 指定メソッドから呼び出し元を指定回数だけ遡る
def trace_callers(path, depth, with_color=True, is_deduplication=True, only_endpoint=False, timestamp=False):
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        class_obj = ClassTable.get(class_name, file)
        class_id = class_obj.id if class_obj else None

    method = MethodTable.get(method_name, file, class_id)
    if not method:
        print("Method not found")
        return
    result = []
    options = {'with_db': False, 'is_caller': True, 'with_endpoint': True}
    trace(result, method, [], int(depth) if depth is not None else None, options=options)
    if only_endpoint:
        filtered_result = []
        for r in result:
            if r.get('endpoint'):
                filtered_result+=r.get('endpoint')
        result = list(set(filtered_result))
        for r in result:
            print(f" * {r}")
    else:
        paths = [list(reversed(r["path"])) for r in result]
        tree = build_tree(paths)
        from utils import count_keys, assign_colors
        if with_color:
            key_counts = count_keys(tree)
            color_map = assign_colors(key_counts)
        else:
            color_map = {}
        print_tree(tree, color_map=color_map, is_deduplication=is_deduplication)

# 指定メソッドから呼び出し先を指定回数だけ遡る
def trace_callees(path, depth=None, with_db=True, with_color=True, is_deduplication=True, timestamp=False):
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        class_obj = ClassTable.get(class_name, file)
        class_id = class_obj.id if class_obj else None

    method = MethodTable.get(method_name, file, class_id)
    if not method:
        print("Method not found")
        return
    result = []
    options = {'with_db': with_db, 'is_caller': False, 'with_endpoint': False, 'timestamp': timestamp}
    trace(result, method, [], int(depth) if depth is not None else None, options=options)
    paths = [list(reversed(r["path"])) for r in result]
    tree = build_tree(paths)
    from utils import count_keys, assign_colors
    if with_color:
        key_counts = count_keys(tree)
        color_map = assign_colors(key_counts)
    else:
        color_map = {}
    print_tree(tree, color_map=color_map, is_deduplication=is_deduplication)
    
    
def get_all_endpoints():
    return EndpointTable.get_all()

def get_method_by_endpoint(url,http_method,type):
    result = EndpointTable.get_all(endpoint=url, http_method=http_method, type=type)
    return result

# def search_endpoint()


def add_inherit(parent_path, child_path):
    parent_file, parent_class_name, _ = get_names_from_path(parent_path)
    child_file, child_class_name, _ = get_names_from_path(child_path)
    parent_class = ClassTable.get(parent_class_name, parent_file)
    if not parent_class:
        print("Parent class not found")
        return
    child_class = ClassTable.get(child_class_name, child_file)
    if not child_class:
        print("Child class not found")
        return
    old = InheritTable.get(parent_class.id, child_class.id)
    if old:
        print("Inherit already exists")
        return
    inh = InheritTable.create(parent_class.id, child_class.id)
    print(f"Inherit added: id={inh.id}, parent={str(parent_class)}, child={str(child_class)}")

def not_search_method():
    
    
    # そのメソッドの
    # 呼び出し元がない + エンドポイントもない
    # 呼び出し先がない + DBアクセスもない
    methods = MethodTable.get_all(is_trace_end=0,is_inherited=0)
    result = []
    for method in methods:

        callers = CallMethodTable.get_all(caller_id=method.id) # そのメソッドを呼び出し元にしているもの→呼び出し先なし
        callees = CallMethodTable.get_all(callee_id=method.id) # そのメソッドを呼び出し先にしているもの→呼び出し元なし
        # 呼び出し先、呼び出し元どちらにも使用されている
        if len(callers) !=0 and len(callees) !=0:
            continue
        
        dbs = DBAccess.get_all(method_id=method.id)
        # 呼び出し先はないが、dbの呼び出しはある
        if len(callers) == 0 and len(dbs) !=0:
            continue

        endpoints = EndpointTable.get_all(method_id=method.id)
        # 呼び出し元はないが、エンドポイントの呼び出しはある
        if len(callees) ==0 and len(endpoints) !=0:
            continue

        # 条件によってこのメソッドが呼ばれる場合があるか
        arguments = MethodArgumentClassMap.get_all(argument_method_id=method.id)
        # 直接的な呼び出し先はないが、条件によって呼び出し先になりうる
        if len(callers) == 0 and len(arguments) !=0:
            continue
        
        sig_calls = SignalCallTable.get_all(caller_id=method.id)
        # 呼び出し先はないが、signalの呼び出しはある
        if len(callers) == 0 and len(sig_calls) !=0:
            continue
        
        connect_signals = SignalConnectTable.get_all(connect_method_id=method.id)
        # 呼び出し元はないが、signalの接続はある
        if len(callees) ==0 and len(connect_signals) !=0:
            continue
        
        # 継承されたメソッドか
        if method.class_id:
            if is_exist_inherited(method.class_id, method, is_caller=True) or is_exist_inherited(method.class_id, method, is_caller=False):
                continue
        # 呼び出し元がないことが確定済み
        if method.is_not_caller:
            continue
        r = {
            "method": method,
            "not_caller": len(callees) == 0 ,
            "not_callee": len(callers) == 0 ,
        }
        result.append(r)
    return result

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'add_class':
        add_class(sys.argv[2])
    elif cmd == 'add_inherit':
        add_inherit(sys.argv[2], sys.argv[3])
    elif cmd == 'add_method':
        add_method(sys.argv[2])
    elif cmd == 'add_call':
        add_call(sys.argv[2], sys.argv[3])
    elif cmd == 'add_endpoint':
        add_endpoint(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "url")
    elif cmd == 'trace_method':
        trace_method(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    elif cmd == 'trace_from_endpoint':
        trace_from_endpoint(sys.argv[2], sys.argv[3])
    elif cmd == 'trace_callers':
        trace_callers(sys.argv[2], sys.argv[3])
    elif cmd == 'trace_callees':
        trace_callees(sys.argv[2], sys.argv[3])
    else:
        print("Usage:\n  add_class <file> <class>\n  add_inherit <parent_class> <child_class>\n  add_method <file> <class> <method>\n  add_call <caller_method> <caller_class> <callee_method> <callee_class>\n  add_endpoint <endpoint> <http_method> <method> <class>\n  trace_method <method> <class>")


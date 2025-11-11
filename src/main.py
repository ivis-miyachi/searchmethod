
import sys
from models import Base, ClassTable, InheritTable, MethodTable, CallMethodTable, EndpointTable, DecoratorTable, session, MethodArgumentClassMap, SignalCallTable, SignalConnectTable
from utils import get_names_from_path, build_tree, print_tree
from method import get_method, add_method
from classes import get_class, add_class
# def add_inherit(parent_file, parent_class, child_file, child_class):
#     parent_id = ClassTable.get(parent_class, parent_file)
#     child_id = ClassTable.get(child_class, child_file)
#     if not parent_id or not child_id:
#         print("Class not found")
#         return
#     inh = InheritTable(parent_id=parent_id, child_id=child_id)
#     session.add(inh)
#     session.commit()
#     print(f"Inherit added: id={inh.id}")

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

# def get_all_parent_ids(class_id):
#     # 再帰的に親クラスIDを取得
#     parents = set()
#     def dfs(cid):
#         for inh in session.query(InheritTable).filter_by(child_id=cid).all():
#             if inh.parent_id not in parents:
#                 parents.add(inh.parent_id)
#                 dfs(inh.parent_id)
#     dfs(class_id)
#     return parents

# def get_all_child_ids(class_id):
#     # 再帰的に子クラスIDを取得
#     children = set()
#     def dfs(cid):
#         for inh in session.query(InheritTable).filter_by(parent_id=cid).all():
#             if inh.child_id not in children:
#                 children.add(inh.child_id)
#                 dfs(inh.child_id)
#     dfs(class_id)
#     return children

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
    def trace(m, path):
        def trace_super_classes(class_id, method_name, path, d):
            parent_inherits = InheritTable.get_all(parent_id=None, child_id=class_id)
            for inh in parent_inherits:
                parent = inh.parent
                # 親クラスに同名メソッドがあるか
                parent_method = MethodTable.get_by_id(method_name, file=parent.file, class_id=parent.id)
                if parent_method:
                    trace(parent_method.id, path + [str(MethodTable.get_by_id(mid))+"(super)"])
                    # 継承元の親クラスもさらにたどる
                    trace_super_classes(parent.id, method_name, path, d)
        mid = m.id
        calls = CallMethodTable.get_all(callee_id=mid)
        eps = EndpointTable.get_all(method_id=mid)
        if eps:
            result.append({"endpoint":[str(ep) for ep in eps], "path": path + [str(MethodTable.get_by_id(mid))]})
        if not eps and not calls:
            # エンドポイントにも呼び出し元にも到達しなかった場合、その軌跡を記録
            result.append({'endpoint': [], 'path': path + [str(MethodTable.get_by_id(mid))]})
        for call in calls:
            print(call)
            trace(call.caller_id, path + [str(MethodTable.get_by_id(mid))+"(super)" if call.is_super else str(MethodTable.get_by_id(mid))])
        method_class = MethodTable.get_by_id(mid).class_id
        print(f"method_class: {method_class}")
        if method_class:
            trace_super_classes(method_class.id, m.method_name, path, d=0)


        # method_obj = MethodTable.get_by_id(mid)
        # if method_obj and method_obj.class_id:
        #     trace_super_classes(method_obj.class_id, method_obj.method_name, path, d=0)



    trace(method, [])
    if mode==1:
        r1 = {}
        print(result)
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
            print(endpoint)
            tree = build_tree(paths)
            print_tree(tree, highlight=str(MethodTable.get_by_id(method)))


        
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
    print(endpoint)
    print_tree(tree)

# 指定メソッドから呼び出し元を指定回数だけ遡る
def trace_callers(path, depth):
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
    result = []
    def trace(mid, path, d):
        if d == 0:
            result.append({'path': path + [str(MethodTable.get_by_id(mid))]})
            return
        calls = CallMethodTable.get_all(callee_id=mid)
        eps = EndpointTable.get_all(method_id=mid)
        if eps:
            result.append({"endpoint":[str(ep) for ep in eps], "path": path + [str(MethodTable.get_by_id(mid))]})
        if not calls:
            result.append({'path': path + [str(MethodTable.get_by_id(mid))]})
        for call in calls:
            trace(call.caller_id, path + [str(MethodTable.get_by_id(mid))], d-1)
    trace(method_id, [], int(depth))
    paths = [list(reversed(r["path"])) for r in result]
    tree = build_tree(paths)
    print_tree(tree)

# 指定メソッドから呼び出し先を指定回数だけ遡る
def trace_callees(path, depth):
    file, class_name, method_name = get_names_from_path(path)
    class_id = None
    if class_name:
        class_obj = ClassTable.get(class_name, file)
        class_id = class_obj.id if class_obj else None

    method = MethodTable.get(method_name, file, class_id)
    if not method:
        print("Method not found")
        return
    # method_id = method.id
    result = []

    def trace(m, path, d, is_super=False, is_async=False):
        def trace_super_classes(class_id, method_name, path, d):
            parent_inherits = InheritTable.get_all(parent_id=None, child_id=class_id)
            for inh in parent_inherits:
                parent = inh.parent
                # 親クラスに同名メソッドがあるか
                parent_method = MethodTable.get(method_name, file=parent.file.path, class_id=parent.id)
                
                if parent_method:
                    if parent_method.is_inherited:
                        trace_super_classes(parent.id, method_name, path + [str(parent_method) + "(inherited)"], d-1)
                    else:
                        trace(parent_method, path, d)

        mid = m.id
        target = str(m) + "(super)" if is_super else str(m)
        if m.is_trace_end:
            target += " (trace end)"
        if is_async:
            target += " (async)"
        if d == 0:
            result.append({'path': path + [target]})
            return

        
        if m.is_inherited:
            trace_super_classes(m.class_id, m.method_name, path+[target+"(inherited)"], d=d)
        else:
            calls = CallMethodTable.get_all(caller_id=mid)
            if not calls:
                result.append({'path': path + [target]})
            for call in calls:
                callee = call.callee
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
                trace(callee, path + [target], d-1, is_super=call.is_super, is_async=is_async)
            signal_calls = SignalCallTable.get_all(caller_id=mid)
            for sc in signal_calls:
                connect_methods = SignalConnectTable.get_by_signal(sc.signal_id)
                for connect_method in connect_methods:
                    trace(connect_method.connect_method, path + [target]+[str(sc.signal)+"(signal)"], d-1, is_super=False)

    trace(method, [], int(depth))
    paths = [list(reversed(r["path"])) for r in result]
    tree = build_tree(paths)
    from utils import count_keys, assign_colors
    key_counts = count_keys(tree)
    color_map = assign_colors(key_counts)
    print_tree(tree, color_map=color_map)


def get_all_endpoints():
    return EndpointTable.get_all()


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

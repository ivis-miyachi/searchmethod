from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Enum, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import alias
from utils import get_dummuys, ope_id_get, OperationHistory
from datetime import datetime
from functools import wraps
Base = declarative_base()

DB_URL = 'postgresql://postgres:postgres@db:5432/methoddb'
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()


def set_ope_history(type=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result,tuple) and type=="U":
                result, changes = result
            elif isinstance(result,tuple) and type=="C":
                return result
            else:
                changes = {}
            result.set_ope_history(type, changes)
            return result
        return wrapper
    return decorator

class TableMixin(Base):
    __abstract__ = True
    created = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def get_tablename(self):
        return self.__class__.__tablename__

    def set_ope_history(self, type, changes={}):
        tablename = self.__class__.__name__
        timestamp = str(datetime.now())

        data = {
            "timestamp": timestamp,
            "table": tablename,
            "operation": type,
            "id": self.id
        }
        if changes and type == "U":
            data["changes"] = changes
        history = OperationHistory()
        history.add_operation(data)

    @classmethod
    def get_by_id(cls, id):
        return session.query(cls).filter_by(id=id).first()

    def delete(self):
        target = str(self)
        target_id = self.id
        session.delete(self)
        session.commit()
        print(f"{self.get_tablename()} deleted: id={target_id}, {target}")

    def merge(self):
        session.merge(self)
        session.commit()
        print(f"{self.get_tablename()} merged: {str(self)}")

    @classmethod
    def get_all(cls, **kwargs):
        q = session.query(cls)
        for key, value in kwargs.items():
            if value is None:
                continue
            q = q.filter(getattr(cls, key) == value)
        return q.all()

    @classmethod
    def get_by_ids(cls, ids):
        return session.query(cls).filter(cls.id.in_(ids)).all()

class FileTable(TableMixin):
    __tablename__ = 'file_table'
    id = Column(Integer, primary_key=True)
    path = Column(String(256), unique=True)
    classes = relationship('ClassTable', back_populates='file')
    methods = relationship('MethodTable', back_populates='file')
    signals = relationship('SignalTable', back_populates='file')
    @classmethod
    def get(cls, path):
        return session.query(cls).filter_by(path=path).first()
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, path):
        new_file = cls(path=path)
        session.add(new_file)
        session.commit()
        print(f"File added: id= {new_file.id}, path={str(new_file)}")
        return new_file

    def __str__(self):
        return self.path
    
    def method_count(self):
        return session.query(MethodTable).filter_by(file_id=self.id).count()
    
    def class_count(self):
        return session.query(ClassTable).filter_by(file_id=self.id).count()
    
    def refs(self):
        count_m = self.method_count()
        count_c = self.class_count()
        return count_m + count_c

    @set_ope_history(type="U")
    def update(self, new_path):
        old_path = self.path
        self.path = new_path
        session.commit()
        print(f"File updated: id= {self.id}, {old_path} -> {new_path}")
        return self, {"path": {"old": old_path, "new": new_path}}

class ClassTable(TableMixin):
    __tablename__ = 'class_table'
    __table_args__ = (
        UniqueConstraint('file_id', 'name', name='uq_class_file_name'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    file_id = Column(Integer, ForeignKey('file_table.id'))
    methods = relationship('MethodTable', back_populates='class_')
    file = relationship('FileTable', back_populates='classes')
    
    def __str__(self):
        return f"{self.file}: {self.name}"
    
    @classmethod
    def get(cls, class_name, file):
        q = session.query(cls).filter_by(name=class_name)
        file_obj = FileTable.get(file)
        if file_obj:
            q = q.filter_by(file_id=file_obj.id)
        else:
            return None
        return q.first()

    @classmethod
    def get_by_name(cls, class_name, file=None):
        q = session.query(cls)
        if file:
            q = q.join(FileTable)
        q = q.filter_by(name=class_name)
        if file:
            q = q.filter(FileTable.path == file)
        c = q.first()
        return c

    @classmethod
    def get_all(cls, class_name=None, file_id=None, file=None):
        """条件に合致するすべてのデータを取得

        Args:
            class_name (str, optional): クラス名. Defaults to None.
            file (str, optional): ファイル名. Defaults to None.

        Returns:
            list: 取得できたデータのリスト
        """
        q = session.query(cls)
        if file_id is None and file is not None:
            q = q.join(FileTable)
            q = q.filter(FileTable.path == file)
        elif file_id is not None:
            q = q.filter(cls.file_id == file_id)
        if class_name:
            q = q.filter(cls.name == class_name)
        return q.all()

    @classmethod
    @set_ope_history(type="C")
    def create(cls, class_name, file=None):
        file_obj = FileTable.get(file) if file else None
        if not file_obj:
            file_obj = FileTable.create(file)
        new_class = cls(name=class_name, file=file_obj)
        session.add(new_class)
        session.commit()
        print(f"Class added: id= {new_class.id}, path={str(new_class)}")
        return new_class

    def method_count(self):
        return session.query(MethodTable).filter_by(class_id=self.id).count()
    
    def inherit_count(self):
        parent_count = session.query(InheritTable).filter_by(parent_id=self.id).count()
        child_count = session.query(InheritTable).filter_by(child_id=self.id).count()
        return parent_count + child_count
    
    def refs(self):
        count_m = self.method_count()
        count_i = self.inherit_count()
        return count_m + count_i
    
    @set_ope_history(type="U")
    def update(self, new_name, new_file_id):
        old_name = self.name
        self.name = new_name
        old_file_id = self.file_id
        self.file_id = new_file_id
        session.commit()
        return self, {"name": {"old": old_name, "new": new_name}, "file_id": {"old": old_file_id, "new": new_file_id}}

class InheritTable(TableMixin):
    __tablename__ = 'inherit_table'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('class_table.id'))
    child_id = Column(Integer, ForeignKey('class_table.id'))
    parent = relationship('ClassTable', foreign_keys=[parent_id])
    child = relationship('ClassTable', foreign_keys=[child_id])
    @classmethod
    def get(cls, parent_id, child_id):
        return session.query(cls).filter_by(parent_id=parent_id, child_id=child_id).first()
    
    @classmethod
    def get_descendants_tree_child(cls, parent_id: int) -> dict:
        """
        指定したparent_idから再帰的に子孫ツリーを取得する。
        戻り値は {"id": parent_id, "children": [...] } のオブジェクト/リスト型。
        """
        def build_tree(pid):
            children = session.query(cls.child_id).filter(cls.parent_id == pid).all()
            return {
                "id": pid,
                "class_name": str(ClassTable.get_by_id(pid)),
                "children": [build_tree(child_id) for (child_id,) in children]
            }
        return build_tree(parent_id)
    
    @classmethod
    def get_descendants_tree_parent(cls, child_id: int) -> dict:
        """
        指定したparent_idから再帰的に子孫ツリーを取得する。
        戻り値は {"id": parent_id, "children": [...] } のオブジェクト/リスト型。
        """
        def build_tree(pid):
            parents = session.query(cls.parent_id).filter(cls.child_id == pid).all()
            return {
                "id": pid,
                "class_name": str(ClassTable.get_by_id(pid)),
                "parents": [build_tree(parent_id) for (parent_id,) in parents]
            }
        return build_tree(child_id)

    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, parent_id, child_id):
        new_inh = cls(parent_id=parent_id, child_id=child_id)
        session.add(new_inh)
        session.commit()
        print(f"Inherit added: id= {new_inh.id}, {str(new_inh.parent)} -> {str(new_inh.child)}")
        return new_inh
    
    def __str__(self):
        return f"Inherit: {self.child}:{self.child_id} -> {self.parent}:{self.parent_id}"
    
    @set_ope_history(type="U")
    def update_parent(self, new_parent_id):
        old_parent_id = self.parent_id
        self.parent_id = new_parent_id
        session.commit()
        print(f"Inherit updated: id= {self.id}, {old_parent_id} -> {new_parent_id}")
        return self, {"parent_id": {"old": old_parent_id, "new": new_parent_id}}

    @set_ope_history(type="U")
    def update_child(self, new_child_id):
        old_child_id = self.child_id
        self.child_id = new_child_id
        session.commit()
        print(f"Inherit updated: id= {self.id}, {old_child_id} -> {new_child_id}")
        return self, {"child_id": {"old": old_child_id, "new": new_child_id}}

class MethodTable(TableMixin):
    __tablename__ = 'method_table'
    __table_args__ = (
        UniqueConstraint('file_id', 'class_id', 'method_name', name='uq_method_file_class_name'),
    )
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_table.id'))
    class_id = Column(Integer, ForeignKey('class_table.id'))
    file = relationship('FileTable', back_populates='methods')
    method_name = Column(String(128))
    class_ = relationship('ClassTable', back_populates='methods')
    is_inherited = Column(Integer, default=0)  # 0: 通常, 1: 継承元からのメソッド
    is_trace_end = Column(Integer, default=0)  # 0: 通常, 1: トレース終了点
    is_task = Column(Integer, default=0)
    is_signal = Column(Integer, default=0)  # 0: 通常, 1: シグナル
    is_not_caller = Column(Integer, default=0)  # 0: 通常, 1: 呼び出し元がない
    
    @classmethod
    def get(cls, method_name, file=None, class_id=None,is_trace_end=None):
        file_obj = FileTable.get(file) if file else None
        q = session.query(cls).filter_by(method_name=method_name, file=file_obj)
        if class_id:
            q = q.filter_by(class_id=class_id)
        if is_trace_end:
            q = q.filter_by(is_trace_end=is_trace_end)
        return q.first()
    
    @classmethod
    def get_all(cls, method_name=None, file=None,file_id=None, 
                class_name=None, class_id=None,is_trace_end=None,
                is_inherited=None):
        q = session.query(MethodTable)
        
        if file_id is None and file is not None:
            q = q.join(FileTable,MethodTable.file_id==FileTable.id)
            q = q.filter(FileTable.path == file)
        elif file_id is not None:
            q = q.filter(MethodTable.file_id == file_id)
        
        if class_id is None and class_name is not None:
            q = q.join(ClassTable, MethodTable.class_id == ClassTable.id, isouter=True)
            q = q.filter(ClassTable.name == class_name)
        elif class_id is not None:
            q = q.filter(MethodTable.class_id == class_id)

        if method_name:
            q = q.filter(MethodTable.method_name == method_name)
        
        if is_trace_end is not None:
            q = q.filter(MethodTable.is_trace_end == is_trace_end)
        if is_inherited is not None:
            q = q.filter(MethodTable.is_inherited == is_inherited)
        return q.all()

    @classmethod
    def get_by_id(cls, method_id):
        return session.query(cls).filter_by(id=method_id).first()

    def __str__(self):
        if self.class_id:
            return f"{self.file}: {self.class_.name}.{self.method_name}"
        else:
            return f"{self.file}: {self.method_name}"
    
    # def __str__(self):
    #     if self.class_id:
    #         return f"{self.file}[{self.file.id}]: {self.class_.name}[{self.class_.id}].{self.method_name}[{self.id}]"
    #     else:
    #         return f"{self.file}[{self.file.id}]: {self.method_name}[{self.id}]"
    
    def str_with_id(self):
        if self.class_id:
            return f"{self.file}: {self.class_.name}.{self.method_name} [id={self.id}]"
        else:
            return f"{self.file}: {self.method_name} [id={self.id}]"
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, method_name, file=None, class_id=None, is_signal=0):
        file_obj = FileTable.get(file) if file else None
        if not file_obj:
            file_obj = FileTable.create(file)

        new_method = cls(method_name=method_name, file=file_obj, class_id=class_id, is_signal=is_signal)
        session.add(new_method)
        session.commit()
        print(f"Method added: id= {new_method.id}, path={str(new_method)}")
        return new_method

    @set_ope_history(type="U")
    def set_inherit_flg(self, flg):
        old_flg = self.is_inherited
        self.is_inherited = flg
        session.commit()
        print(f"Method inherit flag updated: id= {self.id}:{str(self)}, is_inherited= {flg}")
        return self, {"is_inherited": {"old": old_flg, "new": flg}}
    
    @set_ope_history(type="U")
    def update(self, new_method_name, new_file_id=None, new_class_id=None):
        
        is_change_file = new_file_id is not None and self.file_id != new_file_id
        is_change_class = new_class_id is not None and self.class_id != new_class_id
        changes = {}
        messages = []
        if is_change_file:
            old_file_id = self.file_id
            self.file_id = new_file_id
            messages.append(f"file_id: {old_file_id} -> {new_file_id}")
            changes["file_id"] = {"old": old_file_id, "new": new_file_id}
        if is_change_class:
            old_class_id = self.class_id
            self.class_id = new_class_id
            messages.append(f"class_id: {old_class_id} -> {new_class_id}")
            changes["class_id"] = {"old": old_class_id, "new": new_class_id}
        
        old_method_name = self.method_name
        self.method_name = new_method_name
        changes["method_name"] = {"old": old_method_name, "new": new_method_name}
        messages.append(f"method_name: {old_method_name} -> {new_method_name}")
        print(f"Method updated: id= {self.id}, " + ", ".join(messages))
        session.commit()
        return self, changes

    def endpoint_count(self):
        return session.query(EndpointTable).filter_by(method_id=self.id).count()
    
    def call_method_count(self):
        return session.query(CallMethodTable).filter(
            (CallMethodTable.caller_id == self.id) | (CallMethodTable.callee_id == self.id)
        ).count()
    
    def refs(self):
        return self.endpoint_count() + self.call_method_count()

    @set_ope_history(type="U")
    def set_is_trace_end(self, flg):
        before = self.is_trace_end
        self.is_trace_end = flg
        session.commit()
        print(f"Method trace end flag updated: id= {self.id}, is_trace_end= {flg}")
        return self, {"is_trace_end": {"old": before, "new": flg}}

    @set_ope_history(type="U")
    def set_is_not_caller(self, flg):
        before = self.is_not_caller
        self.is_not_caller = flg
        session.commit()
        print(f"Method not caller flag updated: id= {self.id}, is_not_caller= {flg}")
        return self, {"is_not_caller": {"old": before, "new": flg}}

class SignalTable(TableMixin):
    __tablename__ = 'signal_table'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_table.id'))
    file = relationship('FileTable', back_populates='signals')
    name = Column(String(128))

    @classmethod
    def get(cls, name, file_name):
        file_obj = FileTable.get(file_name) if file_name else None
        q = session.query(cls).filter_by(name=name, file=file_obj)
        return q.first()
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, name, file=None):
        file_obj = FileTable.get(file) if file else None
        if not file_obj:
            file_obj = FileTable.create(file)
        new_signal = cls(name=name, file=file_obj)
        session.add(new_signal)
        session.commit()
        print(f"Signal added: id= {new_signal.id}, name={new_signal.name}")
        return new_signal
    
    @classmethod
    def get_all(cls, name=None, file_id=None, file=None):
        q = session.query(cls)
        if file_id is None and file is not None:
            q = q.join(FileTable,SignalTable.file_id==FileTable.id)
            q = q.filter(FileTable.path == file)
        elif file_id is not None:
            q = q.filter(cls.file_id == file_id)
        if name:
            q = q.filter(cls.name == name)
        return q.all()

    def __str__(self):
        return f"{self.file}: {self.name}"

class SignalConnectTable(TableMixin):
    __tablename__ = 'signal_connect_table'
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signal_table.id'))
    signal = relationship('SignalTable', foreign_keys=[signal_id])
    connect_method_id = Column(Integer, ForeignKey('method_table.id'))
    connect_method = relationship('MethodTable', foreign_keys=[connect_method_id])

    @classmethod
    def get(cls, signal_id, connect_method_id):
        return session.query(cls).filter_by(signal_id=signal_id, connect_method_id=connect_method_id).first()
    
    @classmethod
    def get_by_signal(cls, signal_id):
        return session.query(cls).filter_by(signal_id=signal_id).all()
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, signal_id, connect_method_id):
        new_signal = cls(signal_id=signal_id, connect_method_id=connect_method_id)
        session.add(new_signal)
        session.commit()
        print(f"Signal added: id= {new_signal.id}, {str(new_signal)}")
        return new_signal
    
    @classmethod
    def get_all(cls, signal=None, signal_id=None, connect_method=None, connect_method_id=None):
        q = session.query(cls)
        
        if signal is not None and signal_id is None:
            q = q.join(SignalTable, SignalConnectTable.signal_id == SignalTable.id)
            q = q.filter(SignalTable.name == signal)
        elif signal_id is not None:
            q = q.filter_by(signal_id=signal_id)
            
        if connect_method is not None and connect_method_id is None:
            q = q.join(MethodTable, SignalConnectTable.connect_method_id == MethodTable.id)
            q = q.filter(MethodTable.method_name == connect_method)
        elif connect_method_id is not None:
            q = q.filter_by(connect_method_id=connect_method_id)
        return q.all()
    
    @classmethod
    def get_from_connect_method(cls, connect_method_id):
        return session.query(cls).filter_by(connect_method_id=connect_method_id).all()
    
    def __str__(self):
        return f"{self.signal} -> {self.connect_method}"

class SignalCallTable(TableMixin):
    __tablename__ = 'signal_call_table'
    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer, ForeignKey('method_table.id'))
    signal_id = Column(Integer, ForeignKey('signal_table.id'))
    caller_method = relationship('MethodTable', foreign_keys=[caller_id])
    signal = relationship('SignalTable', foreign_keys=[signal_id])

    @classmethod
    def get(cls, caller_id, signal_id):
        return session.query(cls).filter_by(signal_id=signal_id, caller_id=caller_id).first()
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, caller_id, signal_id):
        new_sc = cls(signal_id=signal_id, caller_id=caller_id)
        session.add(new_sc)
        session.commit()
        print(f"SignalCall added: id= {new_sc.id}, {str(new_sc)}")
        return new_sc
    
    @classmethod
    def get_all(cls, caller_id=None, signal_id=None):
        q = session.query(cls)
        if caller_id:
            q = q.filter_by(caller_id=caller_id)
        if signal_id:
            q = q.filter_by(signal_id=signal_id)
        return q.all()
    
    def __str__(self):
        return f"{self.caller_method} -> {self.signal}"

class CallMethodTable(TableMixin):
    """
    super(A).xxxみたいな呼び出し方をしている場合はis_superを1にする
    """
    __tablename__ = 'call_method_table'
    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer, ForeignKey('method_table.id'))
    callee_id = Column(Integer, ForeignKey('method_table.id'))
    caller = relationship('MethodTable', foreign_keys=[caller_id])
    callee = relationship('MethodTable', foreign_keys=[callee_id])
    is_super = Column(Integer, default=0)  # 0: 通常, 1: super呼び出し
    is_change_by_caller = Column(Integer, default=0)  # 0: 通常, 1: argument_methodからの呼び出し
    is_async = Column(Integer, default=0)  # 0: 通常, 1: 非同期呼び出し
    is_recursion = Column(Integer, default=0)  # 0: 通常, 1: 再帰呼び出し
    is_decorator = Column(Integer, default=0)  # 0: 通常, 1: デコレータ呼び出し
    is_signal = Column(Integer, default=0)  # 0: 通常, 1: シグナル
    
    @classmethod
    def get(cls, caller_id, callee_id, is_super=0, is_recursion=0):
        return session.query(cls).filter_by(caller_id=caller_id, callee_id=callee_id, is_super=is_super, is_recursion=is_recursion).first()

    @classmethod
    def get_all(cls, caller_id=None, callee_id=None, is_super=None):
        q = session.query(cls)
        if caller_id:
            q = q.filter_by(caller_id=caller_id)
        if callee_id:
            q = q.filter_by(callee_id=callee_id)
        if is_super is not None:
            q = q.filter_by(is_super=is_super)
        return q.all()
    
    @classmethod
    def get_all_by_callee(cls, callee_id):
        return session.query(cls).filter_by(callee_id=callee_id).all()
    @classmethod
    def get_all_by_caller(cls, caller_id):
        return session.query(cls).filter_by(caller_id=caller_id).all()

    @classmethod
    def _create_dummy_method_by_argument_method(cls, callee_id):
        # argument_methodから呼ばれた時の処理
        callee_method = MethodTable.get_by_id(callee_id) # 呼び出し先メソッドの取得
        callee_class = callee_method.class_id # 呼び出し先クラスの取得
        callee_file = callee_method.file_id
        
        
        # 呼び出し先メソッドのクラスは場合によって変わるためダミーに置換
        # ダミーのクラスとファイルを取得
        dummy_class, dummy_file = get_dummuys()
        # すでにダミーメソッドがないか確認
        dummy_method = MethodTable.get(callee_method.method_name, file=dummy_file.path, class_id=dummy_class.id)
        if not dummy_method: # ダミーメソッドがなければ作成
            callee_method = MethodTable.create(
                method_name=callee_method.method_name,
                file=dummy_file.path,
                class_id=dummy_class.id
            )
        return callee_file, callee_class, callee_method.id
    
    @classmethod
    def _create_argument_method_map(cls, new_call,argument_method, callee_class, callee_id, callee_file):
        # argument_methodから呼ばれた時はcallee_classという情報の保存
        print(f"new_call.id:{new_call.id}, argument_method.id:{argument_method.id}, callee_class:{callee_class}")
        old_methodmap = MethodArgumentClassMap.get(call_id=new_call.id, caller_method_id=argument_method.id, argument_class_id=callee_class, argument_method_id=callee_id, argument_file_id=callee_file)
        if old_methodmap:
            print("MethodArgumentClassMap already exists for argument method call")
        else:
            MethodArgumentClassMap.create(call_id=new_call.id, caller_method_id=argument_method.id, argument_class_id=callee_class, argument_method_id=callee_id, argument_file_id=callee_file)


    @classmethod
    @set_ope_history(type="C")
    def create(cls, caller_id, callee_id, is_super=0, argument_method=None, 
               is_async=0, is_recursion=0, is_decorator=0, only_argument_method=False,
               is_signal=0):
        if argument_method:
            callee_file, callee_class, callee_id= cls._create_dummy_method_by_argument_method(callee_id)
        
        if not only_argument_method:
            new_call = cls(caller_id=caller_id, callee_id=callee_id, 
                        is_super=is_super, is_change_by_caller=1 if argument_method else 0, 
                        is_async=is_async, is_recursion=is_recursion,
                        is_decorator=is_decorator, is_signal=is_signal)
            session.add(new_call)
            session.commit()
            print(f"Method call added: id= {new_call.id}, {str(new_call)}")
        else:
            new_call = cls.get(caller_id=caller_id, callee_id=callee_id, is_super=is_super, is_recursion=is_recursion)
        if argument_method:
            cls._create_argument_method_map(new_call, argument_method, callee_class, callee_id, callee_file)
            session.commit()
        
        return new_call
    
    def __str__(self):
        return f"id:{self.id}, {self.caller} -> {self.callee}"
    
    def str_with_id(self):
        return f"id:{self.id}, {self.caller.str_with_id()} -> {self.callee.str_with_id()}"
    
    def get_info(self):
        return str(self) + f", is_super={self.is_super}, is_change_by_caller={self.is_change_by_caller}, is_async={self.is_async}, is_recursion={self.is_recursion}"
    
    @set_ope_history(type="U")
    def change_caller(self, new_caller_id):
        old_caller_id = self.caller_id
        self.caller_id = new_caller_id
        session.commit()
        print(f"Method call updated: id= {self.id}, {old_caller_id} -> {new_caller_id}")
        return self, {"caller_id": {"old": old_caller_id, "new": new_caller_id}}

    @set_ope_history(type="U")
    def change_callee(self, new_callee_id):
        old_callee_id = self.callee_id
        self.callee_id = new_callee_id
        session.commit()
        print(f"Method call updated: id= {self.id}, {old_callee_id} -> {new_callee_id}")
        return self, {"callee_id": {"old": old_callee_id, "new": new_callee_id}}

class MethodArgumentClassMap(TableMixin):
    """
    call_idの呼び出し状況の時、パスにcaller_method_idがあれば、argument_methodが使用されている
    """
    __tablename__ = 'method_argument_class_map'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer)
    caller_method_id = Column(Integer) # 呼び出し元条件
    argument_class_id = Column(Integer) # 呼び出し先クラス
    argument_method_id = Column(Integer) # 呼び出し先メソッド
    argument_file_id = Column(Integer) # 呼び出し先ファイル
    # call = relationship('CallMethodTable', foreign_keys=[call_id])
    # caller_method = relationship('MethodTable', foreign_keys=[caller_method_id])
    # argument_class = relationship('ClassTable', foreign_keys=[argument_class_id])
    # argument_method = relationship('MethodTable', foreign_keys=[argument_method_id])
    # argument_file = relationship('FileTable', foreign_keys=[argument_file_id])
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, call_id, caller_method_id, argument_class_id, argument_method_id=None, argument_file_id=None):
        new_map = cls(call_id=call_id, caller_method_id=caller_method_id, argument_class_id=argument_class_id, argument_method_id=argument_method_id, argument_file_id=argument_file_id)
        session.add(new_map)
        session.commit()
        print(f"MethodArgumentClassMap added: id= {new_map.id}, caller_method_id={caller_method_id}, argument_class_id={argument_class_id}, argument_method_id={argument_method_id}, argument_file_id={argument_file_id}")
        return new_map
    
    @classmethod
    def get_by_call(cls, call_id):
        return session.query(cls).filter_by(call_id=call_id).all()
    
    @classmethod
    def get(cls, call_id, caller_method_id, argument_class_id, argument_method_id=None, argument_file_id=None):
        return session.query(cls).filter_by(call_id=call_id, caller_method_id=caller_method_id, argument_class_id=argument_class_id, argument_method_id=argument_method_id, argument_file_id=argument_file_id).first()
    
    def __str__(self):
        call = CallMethodTable.get_by_id(self.call_id)
        method = MethodTable.get_by_id(self.argument_method_id)
        caller_method = MethodTable.get_by_id(self.caller_method_id)
        return f"{str(call.caller)} -> {str(method)} (argument of {str(caller_method)})"

EndpointTypeEnum = Enum(
    "url",
    "task",
    "tool",
    "cli",
    "filter"
)
class EndpointTable(TableMixin):
    __tablename__ = 'endpoint_table'
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(128))
    http_method = Column(String(16))
    method_id = Column(Integer, ForeignKey('method_table.id'))
    type = Column(EndpointTypeEnum, default="url")
    
    method = relationship('MethodTable')
    
    def __str__(self):
        if self.type == "url":
            return f"{self.http_method} {self.endpoint}"
        elif self.type == "task":
            return f"Task: {self.endpoint}"
        elif self.type == "tool":
            return f"Tool: {self.method}"
        elif self.type == "cli":
            return f"CLI: {self.endpoint}"
        elif self.type == "filter":
            return f"Filter: {self.method}"
        
    @classmethod
    def get(cls, endpoint, http_method, method_id):
        return session.query(cls).filter_by(endpoint=endpoint, http_method=http_method, method_id=method_id).first()
    
    @classmethod
    def get_all(cls, endpoint=None, http_method=None, type=None, method_id=None):
        q = session.query(cls)
        if endpoint:
            if "%" in endpoint:
                q = q.filter(cls.endpoint.like(endpoint))
            else:
                q = q.filter_by(endpoint=endpoint)
        if http_method:
            q = q.filter_by(http_method=http_method)
        if method_id:
            q = q.filter_by(method_id=method_id)
        if type:
            q = q.filter_by(type=type)
        # type=urlのときはendpointでソート、それ以外はtypeでソート
        if type == "url":
            q = q.order_by(cls.endpoint)
        else:
            q = q.order_by(cls.type)
        return q.all()
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, endpoint, http_method, method_id, type="url"):
        new_endpoint = cls(endpoint=endpoint, http_method=http_method, method_id=method_id, type=type)
        session.add(new_endpoint)
        session.commit()
        print(f"Endpoint added: id= {new_endpoint.id}, {str(new_endpoint)}: {str(new_endpoint.method)}")
        return new_endpoint
    
    @set_ope_history(type="U")
    def update_method(self, new_method_id):
        old_method_id = self.method_id
        self.method_id = new_method_id
        session.commit()
        print(f"Endpoint updated: id= {self.id}, {old_method_id} -> {new_method_id}")
        return self, {"method_id": {"old": old_method_id, "new": new_method_id}}

OPERATION_TYPES = [
    "C", # create
    "R", # read
    "U", # update
    "D"  # delete
]

class DBAccess(TableMixin):
    __tablename__ = 'db_access_table'
    id = Column(Integer, primary_key=True)
    operation_type = Column(Enum(*OPERATION_TYPES, name="operation_type_enum"))  # read, writeなど
    table_name = Column(String(128))
    method_id = Column(Integer, ForeignKey('method_table.id'))
    type = Column(String(2))  # 例: SQLAlchemy, Raw SQLなど
    condition_method_id = Column(Integer, ForeignKey('method_table.id'), nullable=True)
    
    method = relationship('MethodTable', foreign_keys=[method_id])
    condition_method = relationship('MethodTable', foreign_keys=[condition_method_id])
    
    @classmethod
    @set_ope_history(type="C")
    def create(cls, operation_type, table_name, method_id, type="db", condition_method_id=None):
        new_access = cls(operation_type=operation_type, table_name=table_name, method_id=method_id, type=type, condition_method_id=condition_method_id)
        session.add(new_access)
        session.commit()
        print(f"DB Access added: id= {new_access.id}, type={new_access.operation_type}, method={str(new_access.method)}")
        return new_access

    @classmethod
    def get(cls, method_id, table_name, operation_type, type="db", condition_method_id=None):
        return session.query(cls).filter_by(method_id=method_id, table_name=table_name, operation_type=operation_type, type=type, condition_method_id=condition_method_id).first()

    def __str__(self):
        return f"{self.type} Access(id: {self.id}): {str(self.method)} -> {self.table_name} ({self.operation_type})"
    
    def output_str(self):
        return f"[{self.type.upper()}] {self.table_name} ({self.operation_type})"
    
    @classmethod
    def get_all(cls, method_id=None, table_name=None, operation_type=None, type=None):
        q = session.query(cls)
        if method_id:
            q = q.filter_by(method_id=method_id)
        if table_name:
            q = q.filter_by(table_name=table_name)
        if operation_type:
            q = q.filter_by(operation_type=operation_type)
        if type:
            q = q.filter_by(type=type)
        return q.all()
# 仮置き
# copilotに聞いて回答されたやつ
class DecoratorTable(TableMixin):
    __tablename__ = 'decorator_table'
    id = Column(Integer, primary_key=True)
    decorator_name = Column(String(128))
    method_id = Column(Integer, ForeignKey('method_table.id'))
    
# DB初期化用
if __name__ == '__main__':
    engine = create_engine('postgresql://postgres:postgres@db:5432/methoddb')
    Base.metadata.create_all(engine)

    # # 全テーブルのデータ削除
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # session.query(CallMethodTable).delete()
    # session.query(EndpointTable).delete()
    # session.query(MethodTable).delete()
    # session.query(InheritTable).delete()
    # session.query(ClassTable).delete()
    # session.commit()
    print('全テーブルのデータを削除しました')
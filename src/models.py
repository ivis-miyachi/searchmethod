from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Enum
from sqlalchemy.orm import relationship, sessionmaker
from utils import get_dummuys
Base = declarative_base()

DB_URL = 'postgresql://postgres:postgres@db:5432/methoddb'
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()



class FileTable(Base):
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
    def create(cls, path):
        new_file = cls(path=path)
        session.add(new_file)
        session.commit()
        print(f"File added: id= {new_file.id}, path={str(new_file)}")
        return new_file

    def __str__(self):
        return self.path

    def delete(self):
        session.delete(self)
        session.commit()
        print(file=f"File deleted: id= {self.id}, path={str(self)}")
    
    def method_count(self):
        return session.query(MethodTable).filter_by(file_id=self.id).count()
    
    def class_count(self):
        return session.query(ClassTable).filter_by(file_id=self.id).count()
    
    def refs(self):
        count_m = self.method_count()
        count_c = self.class_count()
        return count_m + count_c

    def update(self, new_path):
        old_path = self.path
        self.path = new_path
        session.commit()
        print(f"File updated: id= {self.id}, {old_path} -> {new_path}")

class ClassTable(Base):
    __tablename__ = 'class_table'
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
        q = session.query(cls).filter_by(name=class_name)
        file_obj = FileTable.get(file)
        if file_obj:
            q = q.filter_by(file_id=file_obj.id)
        else:
            return None
        c = q.first()
        return c
    @classmethod
    def get_by_id(cls, class_id):
        return session.query(cls).filter_by(id=class_id).first()

    @classmethod
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
    
    def delete(self):
        session.delete(self)
        session.commit()
        
    def update(self, new_name, new_file_id):
        self.name = new_name
        self.file_id = new_file_id
        session.commit()

class InheritTable(Base):
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
    def create(cls, parent_id, child_id):
        new_inh = cls(parent_id=parent_id, child_id=child_id)
        session.add(new_inh)
        session.commit()
        print(f"Inherit added: id= {new_inh.id}, {str(new_inh.parent)} -> {str(new_inh.child)}")
        return new_inh
    
    @classmethod
    def get_all(cls, parent_id=None, child_id=None):
        q = session.query(cls)
        if parent_id:
            q = q.filter_by(parent_id=parent_id)
        if child_id:
            q = q.filter_by(child_id=child_id)
        return q.all()
    
    def __str__(self):
        return f"Inherit: {self.child}:{self.child_id} -> {self.parent}:{self.parent_id}"
    
    def update_parent(self, new_parent_id):
        old_parent_id = self.parent_id
        self.parent_id = new_parent_id
        session.commit()
        print(f"Inherit updated: id= {self.id}, {old_parent_id} -> {new_parent_id}")

    def update_child(self, new_child_id):
        old_child_id = self.child_id
        self.child_id = new_child_id
        session.commit()
        print(f"Inherit updated: id= {self.id}, {old_child_id} -> {new_child_id}")

class MethodTable(Base):
    __tablename__ = 'method_table'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_table.id'))
    class_id = Column(Integer, ForeignKey('class_table.id'))
    file = relationship('FileTable', back_populates='methods')
    method_name = Column(String(128))
    class_ = relationship('ClassTable', back_populates='methods')
    is_inherited = Column(Integer, default=0)  # 0: 通常, 1: 継承元からのメソッド
    is_trace_end = Column(Integer, default=0)  # 0: 通常, 1: トレース終了点
    is_task = Column(Integer, default=0)
    
    @classmethod
    def get(cls, method_name, file=None, class_id=None):
        file_obj = FileTable.get(file) if file else None
        q = session.query(cls).filter_by(method_name=method_name, file=file_obj)
        if class_id:
            q = q.filter_by(class_id=class_id)
        return q.first()
    
    @classmethod
    def get_by_id(cls, method_id):
        return session.query(cls).filter_by(id=method_id).first()
    @classmethod
    def get_all(cls, method_name=None, file=None, class_name=None):
        q = session.query(MethodTable, ClassTable, FileTable)\
            .join(ClassTable, MethodTable.class_id == ClassTable.id, isouter=True)\
            .join(FileTable, MethodTable.file_id == FileTable.id)
        if method_name:
            q = q.filter(MethodTable.method_name == method_name)
        if file:
            q = q.filter(FileTable.path == file)
        if class_name:
            q = q.filter(ClassTable.name == class_name)
        return q.all()

    @classmethod
    def get_by_id(cls, method_id):
        return session.query(cls).filter_by(id=method_id).first()

    def __str__(self):
        if self.class_id:
            return f"{self.file}: {self.class_.name}.{self.method_name}"
        else:
            return f"{self.file}: {self.method_name}"
    
    @classmethod
    def create(cls, method_name, file=None, class_id=None):
        file_obj = FileTable.get(file) if file else None
        if not file_obj:
            file_obj = FileTable.create(file)

        new_method = cls(method_name=method_name, file=file_obj, class_id=class_id)
        session.add(new_method)
        session.commit()
        print(f"Method added: id= {new_method.id}, path={str(new_method)}")
        return new_method

    def set_inherit_flg(self, flg):
        self.is_inherited = flg
        session.commit()
    
    def delete(self):
        session.delete(self)
        session.commit()
    
    def update(self, new_method_name, new_file_id=None, new_class_id=None):
        self.method_name = new_method_name
        is_change_file = new_file_id is not None and self.file_id != new_file_id
        is_change_class = new_class_id is not None and self.class_id != new_class_id
        if is_change_file:
            old_file_id = self.file_id
            self.file_id = new_file_id
        if is_change_class:
            old_class_id = self.class_id
            self.class_id = new_class_id
        messages = []
        messages.append(f"method_name: {self.method_name} -> {new_method_name}")
        if is_change_file:
            messages.append(f"file_id: {old_file_id} -> {new_file_id}")
        if is_change_class:
            messages.append(f"class_id: {old_class_id} -> {new_class_id}")
        print(f"Method updated: id= {self.id}, " + ", ".join(messages))
        session.commit()
        

    def endpoint_count(self):
        return session.query(EndpointTable).filter_by(method_id=self.id).count()
    
    def call_method_count(self):
        return session.query(CallMethodTable).filter(
            (CallMethodTable.caller_id == self.id) | (CallMethodTable.callee_id == self.id)
        ).count()
    
    def refs(self):
        return self.endpoint_count() + self.call_method_count()

    def set_is_trace_end(self, flg):
        self.is_trace_end = flg
        session.commit()
        print(f"Method trace end flag updated: id= {self.id}, is_trace_end= {flg}")

class SignalTable(Base):
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
    def create(cls, name, file=None):
        file_obj = FileTable.get(file) if file else None
        if not file_obj:
            file_obj = FileTable.create(file)
        new_signal = cls(name=name, file=file_obj)
        session.add(new_signal)
        session.commit()
        print(f"Signal added: id= {new_signal.id}, name={new_signal.name}")
        return new_signal

    def __str__(self):
        return f"{self.file}: {self.name}"

class SignalConnectTable(Base):
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
    def create(cls, signal_id, connect_method_id):
        new_signal = cls(signal_id=signal_id, connect_method_id=connect_method_id)
        session.add(new_signal)
        session.commit()
        print(f"Signal added: id= {new_signal.id}, {str(new_signal)}")
        return new_signal
    
    def __str__(self):
        return f"{self.signal} -> {self.connect_method}"

class SignalCallTable(Base):
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

class CallMethodTable(Base):
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
    
    @classmethod
    def get(cls, caller_id, callee_id, is_super=0):
        return session.query(cls).filter_by(caller_id=caller_id, callee_id=callee_id, is_super=is_super).first()

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
    def create(cls, caller_id, callee_id, is_super=0, argument_method=None):
        if argument_method:
            # argument_methodから呼ばれた時の処理
            callee_method = MethodTable.get_by_id(callee_id) # 呼び出し先メソッドの取得
            callee_class = callee_method.class_id # 呼び出し先クラスの取得
            
            
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
            # callee_idをダミーメソッドのidに置換
            callee_id = callee_method.id
        new_call = cls(caller_id=caller_id, callee_id=callee_id, is_super=is_super, is_change_by_caller=1 if argument_method else 0)
        session.add(new_call)
        session.commit()
        if argument_method:
            # argument_methodから呼ばれた時はcallee_classという情報の保存
            print(f"new_call.id:{new_call.id}, argument_method.id:{argument_method.id}, callee_class:{callee_class}")
            method_maps = MethodArgumentClassMap.create(call_id=new_call.id, caller_method_id=argument_method.id, argument_class_id=callee_class)

        session.commit()
        print(f"Method call added: id= {new_call.id}, {str(new_call)}")
        return new_call
    
    def __str__(self):
        return f"id:{self.id}, {self.caller} <- {self.callee}"
    
    def change_caller(self, new_caller_id):
        old_caller_id = self.caller_id
        self.caller_id = new_caller_id
        session.commit()
        print(f"Method call updated: id= {self.id}, {old_caller_id} -> {new_caller_id}")

    def change_callee(self, new_callee_id):
        old_callee_id = self.callee_id
        self.callee_id = new_callee_id
        session.commit()
        print(f"Method call updated: id= {self.id}, {old_callee_id} -> {new_callee_id}")

    def delete(self):
        session.delete(self)
        session.commit()
        print(f"Method call deleted: id= {self.id}")

class MethodArgumentClassMap(Base):
    __tablename__ = 'method_argument_class_map'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer)
    caller_method_id = Column(Integer)
    argument_class_id = Column(Integer)

    # caller_method = relationship('MethodTable', foreign_keys=[caller_method_id])
    # argument_class = relationship('ClassTable', foreign_keys=[argument_class_id])
    @classmethod
    def create(cls, call_id, caller_method_id, argument_class_id):
        old = cls.get(call_id, caller_method_id, argument_class_id)
        if old:
            print("MethodArgumentClassMap already exists")
            return old
        new_map = cls(call_id=call_id, caller_method_id=caller_method_id, argument_class_id=argument_class_id)
        session.add(new_map)
        session.commit()
        # print(f"MethodArgumentClassMap added: id= {new_map.id}, caller_method_id={str(new_map.caller_method)}, argument_class_id={str(new_map.argument_class)}")
        print(f"MethodArgumentClassMap added: id= {new_map.id}, caller_method_id={caller_method_id}, argument_class_id={argument_class_id}")
        return new_map
    @classmethod
    def get_by_call(cls, call_id):
        return session.query(cls).filter_by(call_id=call_id).all()
    @classmethod
    def get(cls, call_id, caller_method_id, argument_class_id):
        return session.query(cls).filter_by(call_id=call_id, caller_method_id=caller_method_id, argument_class_id=argument_class_id).first()

    @classmethod
    def get_by_id(cls, map_id):
        return session.query(cls).filter_by(id=map_id).first()

EndpointTypeEnum = Enum(
    "url",
    "task",
    "tool"
)
class EndpointTable(Base):
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
    @classmethod
    def get(cls, endpoint, http_method, method_id):
        return session.query(cls).filter_by(endpoint=endpoint, http_method=http_method, method_id=method_id).first()
    
    @classmethod
    def get_all(cls, endpoint=None, http_method=None, method_id=None):
        q = session.query(cls)
        if endpoint:
            q = q.filter_by(endpoint=endpoint)
        if http_method:
            q = q.filter_by(http_method=http_method)
        if method_id:
            q = q.filter_by(method_id=method_id)
        return q.all()
    @classmethod
    def create(cls, endpoint, http_method, method_id, type="url"):
        new_endpoint = cls(endpoint=endpoint, http_method=http_method, method_id=method_id, type=type)
        session.add(new_endpoint)
        session.commit()
        print(f"Endpoint added: id= {new_endpoint.id}, {str(new_endpoint)}: {str(new_endpoint.method)}")
        return new_endpoint
    
    def update_method(self, new_method_id):
        old_method_id = self.method_id
        self.method_id = new_method_id
        session.commit()
        print(f"Endpoint updated: id= {self.id}, {old_method_id} -> {new_method_id}")

# 仮置き
# copilotに聞いて回答されたやつ
class DecoratorTable(Base):
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
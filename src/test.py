from models import SignalTable, CallMethodTable, MethodTable, SignalCallTable,SignalConnectTable

for signal in SignalTable.get_all():
    signal_id = signal.id
    signal_name = signal.name
    
    new_method = MethodTable.create(signal_name, file=signal.file.path,is_signal=1)
    for connect in SignalConnectTable.get_by_signal(signal_id):
        connect_method_id = connect.connect_method_id
        CallMethodTable.create(new_method.id, connect_method_id)
    
    for call in SignalCallTable.get_all(signal_id=signal_id):
        caller_method_id = call.caller_id
        CallMethodTable.create(caller_method_id, new_method.id,is_signal=1)
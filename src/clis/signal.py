
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import signal, with_operation_id

@signal.command()
@click.argument('path')
@with_operation_id
def add(path):
    from method import add_signal
    add_signal(path)

@signal.command()
@click.argument('signal_path')
@click.argument('method_path')
@with_operation_id
def add_connect(signal_path, method_path):
    from method import add_signal_connect
    add_signal_connect(signal_path, method_path)
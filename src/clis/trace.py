
import click
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cli import trace, with_operation_id
from main import trace_method, trace_from_endpoint, trace_callers, trace_callees

@trace.command()
@click.argument('method_path')
@click.option('--mode', default=1)
@with_operation_id
def method(method_path,mode=1):
    trace_method(method_path,mode)
    
@trace.command()
@click.argument('endpoint')
@click.argument('http_method')
@click.option('--mode', default=1)
@with_operation_id
def endpoint(endpoint,http_method,mode=1):
    trace_from_endpoint(endpoint,http_method)

@trace.command()
@click.argument("caller")
@click.option('--depth')
@click.option('-e','--only-endpoint', is_flag=True, default=False, help='パスではなくエンドポイントのみを出力')
@click.option('-t', '--timestamp', is_flag=True, default=False, help='データを登録した日付を含む')
@click.pass_context
@with_operation_id
def callers(ctx, caller, depth=None, only_endpoint=False, timestamp=False):
    trace_callers(
        caller,
        depth,
        with_color=ctx.obj['with_color'],
        is_deduplication=ctx.obj['is_deduplication'],
        only_endpoint=only_endpoint,
        timestamp=timestamp
    )


@trace.command()
@click.argument("callee")
@click.option('--depth')
@click.option('-d','--with-db', is_flag=True, default=False, help='DBアクセス情報を表示に含める')
@click.option('-t', '--timestamp', is_flag=True, default=False, help='データを登録した日付を含む')
@click.pass_context
@with_operation_id
def callees(ctx, callee, depth=None, with_db=False, timestamp=False):
    trace_callees(
        callee,
        depth,
        with_db=with_db,
        with_color=ctx.obj['with_color'],
        is_deduplication=ctx.obj['is_deduplication'],
        timestamp=timestamp
    )

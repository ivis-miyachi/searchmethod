# from functools import wraps
# import uuid
# from ..utils import ope_id_set, ope_id_reset
# import click

# def with_operation_id(func):
#     """Clickコマンドに操作IDを設定するデコレータ"""
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         ope_id = uuid.uuid4()
#         token = ope_id_set(str(ope_id))
#         try:
#             return func(*args, **kwargs)
#         finally:
#             ope_id_reset(token)
#     return wrapper

# @click.group()
# @click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
# @click.option('--profile', is_flag=True, help='Enable cProfile profiling')
# def cli(debug, profile):
#     if debug:
#         if os.environ.get('DEBUGPY_ENABLE', '0') != '1':
#             print("Please set DEBUGPY_ENABLE=1 in docker-compose.yml and restart the container.")
#         import debugpy
#         debugpy.listen(('0.0.0.0', 5678))
#         print('debugpy is listening on port 5678...')
#         print("Please start the debug feature of vscode")
#         debugpy.wait_for_client()
#     if profile:
#         import cProfile
#         import sys
#         print("Profiling with cProfile...")
#         # プロファイリングはmain関数でラップする必要があるため、sys.argvを使って再実行
#         cProfile.run('cli.main()', sort='cumtime')
#         sys.exit(0)


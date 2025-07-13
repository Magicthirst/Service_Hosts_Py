import os


def not_found_env(variable_name):
    raise Exception(f'not found env: {variable_name=}')


protocol = 'http'
host = os.environ.get("IP") or not_found_env()
port = int(os.environ.get("PORT")) or not_found_env()
run_url = f'{protocol}://{host}:{port}'

db_path = os.environ.get('DB') or not_found_env()

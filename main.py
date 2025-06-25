from typing import Callable

import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import Response, JSONResponse
from pydantic import create_model

import hosts_repository as hosts


Host = create_model(
    'Host',
    uuid=(str, 'some-uuid'),
    only_friends=(bool, True),
    allow_nonames=(bool, False),
    friends=(list[str], ['this-gui-uuid', 'other-guy-uuid']),
    banlist=(list[str], ['that-guy-uuid'])
)

app = FastAPI()


def run(host: str | None = None, port: int | None = None, db_path: str | None = None):
    import config

    hosts.init(db_path or config.db_path)
    uvicorn.run(app, host=host or config.host, port=port or config.port, log_level='trace')


@app.post('/{host}')
async def create(host: str) -> Host:
    return _err_to_response(hosts.create, host)


@app.get('/{host}')
async def get(host: str) -> Host:
    return _err_to_response(hosts.get, host)


@app.put('/{host}/only_friends')
async def set_only_friends(host: str, only_friends: bool = Body(embed=True)) -> Response:
    return _err_to_response(hosts.set_only_friends, host, only_friends)


@app.put('/{host}/allow_nonames')
async def set_allow_nonames(host: str, allow_nonames: bool = Body(embed=True)) -> Response:
    return _err_to_response(hosts.set_allow_nonames, host, allow_nonames)


@app.post('/{host}/friends/{friend}')
async def befriend(host: str, friend: str) -> Response:
    return _err_to_response(hosts.befriend, host, friend)


@app.delete('/{host}/friends/{former_friend}')
async def unfriend(host: str, former_friend: str) -> Response:
    return _err_to_response(hosts.unfriend, host, former_friend)


@app.post('/{host}/banlist/{banned}')
async def ban(host: str, banned: str) -> Response:
    return _err_to_response(hosts.ban, host, banned)


@app.delete('/{host}/banlist/{banned}')
async def unban(host: str, banned: str) -> Response:
    return _err_to_response(hosts.unban, host, banned)


@app.get('/{host}/welcomes/{guest}')
async def welcomes(host: str, guest: str | None = None):
    if guest == 'NONAME':
        guest = None

    return _err_to_response(
        hosts.welcomes, host, guest or None,
        transform=lambda is_welcomes: Response(status_code=(200 if is_welcomes else 404))
    )


def _err_to_response(action: Callable, *args, transform: Callable = None, **kwargs):
    try:
        args = [arg.upper() if arg is str else arg for arg in args]
        got = action(*args, **kwargs)
    except IndexError as e:
        return JSONResponse(status_code=404, content={'message': 'not found this'})
    except LookupError as e:
        return Response(status_code=409)
    except AssertionError as e:
        return JSONResponse(status_code=404, content={'message': 'not found other'})
    except ValueError as e:
        return Response(status_code=400)

    return transform and transform(got) or got or Response(status_code=200)


if __name__ == '__main__':
    run()

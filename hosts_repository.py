from tinydb import TinyDB, Query
import tinydb.operations as op
from tinydb.table import Table


_db: TinyDB
_hosts: Table
_Host: Query


def init(db_path: str | None = None):
    global _db, _hosts, _Host
    import config

    db_path = db_path or config.db_path

    _db = TinyDB(db_path)
    _hosts = _db.table('hosts')
    _Host = Query()


def create(uuid: str):
    uuid = uuid.upper()

    if _hosts.contains(_Host.uuid == uuid):
        raise LookupError()

    _hosts.insert({
        'uuid': uuid,
        'only_friends': True,
        'allow_nonames': False,
        'friends': [],
        'banlist': []
    })
    return get(uuid)


def get(uuid: str):
    uuid = uuid.upper()

    assert _hosts.contains(_Host.uuid == uuid)
    if got := _hosts.get(_Host.uuid == uuid):
        print(f'{uuid=} {got=}')
        return got


def set_only_friends(uuid: str, only_friends: bool):
    uuid = uuid.upper()

    assert _hosts.contains(_Host.uuid == uuid)
    if not _hosts.update({'only_friends': only_friends}, _Host.uuid == uuid):
        raise IndexError()


def set_allow_nonames(uuid: str, allow_nonames: bool):
    uuid = uuid.upper()

    assert _hosts.contains(_Host.uuid == uuid)
    if not _hosts.update({'allow_nonames': allow_nonames}, _Host.uuid == uuid):
        raise IndexError()


def ban(uuid: str, banned_uuid: str):
    uuid = uuid.upper()
    banned_uuid = banned_uuid.upper()

    if uuid == banned_uuid:
        raise ValueError()
    assert _hosts.contains(_Host.uuid == banned_uuid) and not _hosts.contains(_Host.whitelist.any([banned_uuid]))
    if not _hosts.update(op.add('banlist', [banned_uuid]), _Host.uuid == uuid):
        raise IndexError()


def befriend(uuid: str, friend_uuid: str):
    uuid = uuid.upper()
    friend_uuid = friend_uuid.upper()

    if uuid == friend_uuid:
        raise ValueError()
    assert _hosts.contains(_Host.uuid == friend_uuid)
    if not _hosts.update(op.add('friends', [friend_uuid]), _Host.uuid == uuid):
        raise IndexError()


def unban(uuid: str, banned_uuid: str):
    uuid = uuid.upper()
    banned_uuid = banned_uuid.upper()

    assert _hosts.contains(_Host.uuid == banned_uuid)
    if not _hosts.update(lambda u: u['banlist'].remove(banned_uuid), _Host.uuid == uuid):
        raise IndexError()


def unfriend(uuid: str, former_friend_uuid: str):
    uuid = uuid.upper()
    former_friend_uuid = former_friend_uuid.upper()

    assert _hosts.contains(_Host.uuid == former_friend_uuid)
    if not _hosts.update(lambda u: u['friends'].remove(former_friend_uuid), _Host.uuid == uuid):
        raise IndexError()


def welcomes(this_uuid: str, other_uuid: str | None, this: dict | None = None) -> bool:
    this_uuid = this_uuid.upper()
    other_uuid = other_uuid and other_uuid.upper()

    if this is None:
        this = get(this_uuid)

    if not this['allow_nonames'] and other_uuid is None:
        print('nonames are not allowed')
        return False
    if this['only_friends'] and other_uuid not in this['friends']:
        print('not a friend is not allowed')
        return False
    if other_uuid in this['banlist']:
        print('baddie')
        return False

    return True


def filter_welcomes(this_uuid: str, other_uuids: list[str]) -> list[str]:
    this_uuid = this_uuid.upper()
    other_uuids = [uuid.upper() for uuid in other_uuids]

    this = get(this_uuid)
    return [
        other_uuid
        for other_uuid in other_uuids
        if welcomes(this_uuid, other_uuid, this)
    ]

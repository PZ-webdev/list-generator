import os
from app.utils.ui_state import UIStateStore


def test_ui_state_flags_and_lot(tmp_path):
    path = os.path.join(tmp_path, 'ui_state.json')
    store = UIStateStore(path)

    store.set_flag('1', 'additional', True)
    store.set_flag('1', 'rating', False)
    store.set_last_lot('1', '7')

    flags = store.get_flags('1')
    assert flags['additional'] is True
    assert flags['rating'] is False
    assert store.get_last_lot('1') == '7'


def test_ui_state_remove_branch(tmp_path):
    path = os.path.join(tmp_path, 'ui_state.json')
    store = UIStateStore(path)

    store.set_flag('x', 'additional', True)
    store.set_last_lot('x', '10')
    assert store.get_flags('x')['additional'] is True

    store.remove_branch('x')
    assert store.get_flags('x')['additional'] is False
    assert store.get_last_lot('x') == ''


def test_ui_state_persistence_roundtrip(tmp_path):
    path = os.path.join(tmp_path, 'ui_state.json')
    store = UIStateStore(path)
    store.set_flag('id', 'additional', True)
    store.set_flag('id', 'rating', True)
    store.set_last_lot('id', '42')

    # New store loads from file
    store2 = UIStateStore(path)
    assert store2.get_flags('id') == {'additional': True, 'rating': True}
    assert store2.get_last_lot('id') == '42'

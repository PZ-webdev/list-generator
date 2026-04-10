import os
from app.core.branch_service import BranchService
from app.dto.branch import Branch


def make_service(tmp_path):
    path = os.path.join(tmp_path, 'branches.json')
    return BranchService(path)


def test_add_and_get_all(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    svc.add_branch('B', '200', '/in/b', '/out/b')
    items = svc.get_all()
    assert [b.name for b in items] == ['A', 'B']


def test_update_preserves_order(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    svc.add_branch('B', '200', '/in/b', '/out/b')
    svc.add_branch('C', '300', '/in/c', '/out/c')

    # Update middle element, keep its id
    b_middle = svc.get_all()[1]
    updated = Branch(
        id=b_middle.id,
        name='B-upd',
        number='201',
        input='/in/b2',
        output='/out/b2',
    )
    svc.update_branch(updated)

    items = svc.get_all()
    assert [b.name for b in items] == ['A', 'B-upd', 'C']
    assert items[1].number == '201'


def test_move_up_down_and_bounds(tmp_path):
    svc = make_service(tmp_path)
    for i in range(4):
        svc.add_branch(f'N{i}', str(100 + i), f'/in/{i}', f'/out/{i}')

    ids = [b.id for b in svc.get_all()]
    # Move 2nd up -> becomes first
    svc.move_up(ids[1])
    names = [b.name for b in svc.get_all()]
    assert names[0] == 'N1' and names[1] == 'N0'

    # Move first up (no change)
    svc.move_up(svc.get_all()[0].id)
    assert [b.name for b in svc.get_all()][0] == 'N1'

    # Move last down (no change)
    last_id = svc.get_all()[-1].id
    svc.move_down(last_id)
    assert svc.get_all()[-1].id == last_id


def test_delete_branch(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    svc.add_branch('B', '200', '/in/b', '/out/b')
    b_id = svc.get_all()[0].id
    svc.delete_branch(b_id)
    assert all(b.id != b_id for b in svc.get_all())


def test_load_when_missing_returns_empty_list(tmp_path):
    svc = make_service(tmp_path)
    assert svc.get_all() == []


def test_persistence_roundtrip(tmp_path):
    path = os.path.join(tmp_path, 'branches.json')
    svc = BranchService(path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    svc.add_branch('B', '200', '/in/b', '/out/b')

    # New instance should load two branches
    svc2 = BranchService(path)
    names = [b.name for b in svc2.get_all()]
    assert names == ['A', 'B']


def test_update_nonexistent_appends(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    # ID '999' does not exist -> should append
    from app.dto.branch import Branch
    svc.update_branch(Branch(id='999', name='X', number='999', input='/x', output='/y'))
    names = [b.name for b in svc.get_all()]
    assert names[-1] == 'X'


def test_next_id_increments_even_after_delete(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    svc.add_branch('B', '200', '/in/b', '/out/b')
    # Capture ids
    ids = [b.id for b in svc.get_all()]
    # Delete last, then add new
    svc.delete_branch(ids[-1])
    remaining_ids = [b.id for b in svc.get_all()]
    svc.add_branch('C', '300', '/in/c', '/out/c')
    new_ids = [b.id for b in svc.get_all()]
    new_only = set(new_ids) - set(remaining_ids)
    assert len(new_only) == 1
    new_id = int(next(iter(new_only)))
    # New ID should be max(remaining)+1 (service reuses deleted max)
    assert new_id == max(map(int, remaining_ids)) + 1


def test_move_down_middle_changes_order(tmp_path):
    svc = make_service(tmp_path)
    for i in range(4):
        svc.add_branch(f'N{i}', str(100 + i), f'/in/{i}', f'/out/{i}')
    ids = [b.id for b in svc.get_all()]
    mid_id = ids[1]  # second element
    svc.move_down(mid_id)
    names = [b.name for b in svc.get_all()]
    assert names == ['N0', 'N2', 'N1', 'N3']


def test_move_with_unknown_id_noop(tmp_path):
    svc = make_service(tmp_path)
    for i in range(3):
        svc.add_branch(f'N{i}', str(100 + i), f'/in/{i}', f'/out/{i}')
    before = [b.name for b in svc.get_all()]
    svc.move_up('unknown')
    svc.move_down('unknown')
    after = [b.name for b in svc.get_all()]
    assert after == before


def test_delete_nonexistent_noop(tmp_path):
    svc = make_service(tmp_path)
    svc.add_branch('A', '100', '/in/a', '/out/a')
    before = [b.name for b in svc.get_all()]
    svc.delete_branch('nope')
    assert [b.name for b in svc.get_all()] == before


def test_load_with_invalid_json_returns_empty_list(tmp_path):
    path = os.path.join(tmp_path, 'branches.json')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{ invalid json')
    svc = BranchService(path)
    assert svc.get_all() == []


def test_add_branch_next_id_from_max(tmp_path):
    svc = make_service(tmp_path)
    # Simulate existing non-sequential IDs
    svc.branches = [
        Branch(id='5', name='X', number='005', input='/in/x', output='/out/x'),
        Branch(id='10', name='Y', number='010', input='/in/y', output='/out/y'),
    ]
    svc.save_branches()
    svc.add_branch('Z', '300', '/in/z', '/out/z')
    assert max(int(b.id) for b in svc.get_all()) == 11

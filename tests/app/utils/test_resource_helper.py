import os
import config
from app.utils.resource_helper import resource_path


def test_resource_path_uses_base_dir_for_repo_paths():
    rel = os.path.join('data', 'STERDRUK.TXT')
    path = resource_path(rel)
    assert path == os.path.join(str(config.BASE_DIR), rel)
    assert os.path.exists(path)


def test_resource_path_not_affected_by_cwd(monkeypatch, tmp_path):
    rel = os.path.join('data', 'STERDRUK.TXT')
    monkeypatch.chdir(tmp_path)
    path = resource_path(rel)
    assert path == os.path.join(str(config.BASE_DIR), rel)

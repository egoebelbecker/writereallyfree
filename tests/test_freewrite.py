import os
from freewrite import map_sync_path, FreeWriteDriveManager
import config_store


def test_map_sync_path_basic(tmp_path):
    # no prefix or simple filename returns unchanged
    assert map_sync_path('file.txt', 'pre') == 'file.txt'

    # directory path should be prefixed
    res = map_sync_path(os.path.join('dir', 'file.txt'), 'pre')
    assert res == os.path.join('predir', 'file.txt')


def test_update_sync_settings(monkeypatch):
    # Provide a simple config so the manager can initialise
    monkeypatch.setattr(config_store, 'load_config', lambda: {
        "sync_folder_name": "",
        "copy_empty_folders": False,
        "copy_readme": False,
        "sync_folder_prefix": "",
        "convert_to_docx": False
    })

    mgr = FreeWriteDriveManager()
    mgr.update_sync_settings('name', True, True, 'pre_', True)
    assert mgr.sync_folder_name == 'name'
    assert mgr.copy_empty_folders is True
    assert mgr.convert_to_docx is True

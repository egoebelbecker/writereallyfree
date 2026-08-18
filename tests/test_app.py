import os
import sys
import types
import app as app_module
import config_store


class StubManager:
    def __init__(self):
        self._settings = None

    def get_drives(self):
        return []

    def update_sync_settings(self, *args, **kwargs):
        self._settings = args


def test_home_and_preferences(monkeypatch, tmp_path):
    # Avoid importing/using real webview backend
    monkeypatch.setitem(sys.modules, 'webview', types.SimpleNamespace(create_window=lambda **k: None, start=lambda **k: None))

    monkeypatch.setattr(config_store, 'load_config', lambda: {
        'sync_folder_name': '',
        'copy_empty_folders': False,
        'copy_readme': False,
        'theme': 'system',
        'sync_folder_prefix': ''
    })

    monkeypatch.setattr(app_module, 'FreeWriteDriveManager', StubManager)

    api = app_module.HomeExplorerAPI()
    api.home_dir = str(tmp_path)

    assert api.get_home_path() == str(tmp_path)
    prefs = api.get_preferences()
    assert prefs['success'] is True
    assert 'docx_doublespace' in prefs
    assert 'docx_indent_first_line' in prefs
    assert 'docx_space_before' in prefs
    assert 'docx_space_after' in prefs
    assert 'allowed_labels' in prefs


def test_save_preferences_and_read_preview(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, 'webview', types.SimpleNamespace(create_window=lambda **k: None, start=lambda **k: None))

    monkeypatch.setattr(config_store, 'load_config', lambda: {
        'sync_folder_name': '',
        'copy_empty_folders': False,
        'copy_readme': False,
        'theme': 'system',
        'sync_folder_prefix': ''
    })
    saved_cfg = {}
    monkeypatch.setattr(config_store, 'save_config', lambda cfg: saved_cfg.update(cfg) or True)

    monkeypatch.setattr(app_module, 'FreeWriteDriveManager', StubManager)
    api = app_module.HomeExplorerAPI()
    api.home_dir = str(tmp_path)

    res = api.save_preferences('mysync', True, 'dark', 'pre', True, False, True, True, True, True, 'label1, label2')
    assert res['success'] is True
    assert os.path.exists(os.path.join(str(tmp_path), 'mysync'))
    assert saved_cfg.get('docx_doublespace') is True
    assert saved_cfg.get('docx_indent_first_line') is True
    assert saved_cfg.get('docx_space_before') is True
    assert saved_cfg.get('docx_space_after') is True
    assert saved_cfg.get('allowed_labels') == ['label1', 'label2']

    # create a file and ensure preview reads it
    target = tmp_path / 'mysync' / 'note.txt'
    target.write_text('hello world')

    out = api.read_file_preview(os.path.join('mysync', 'note.txt'))
    assert out['success'] is True
    assert 'hello world' in out['content']


import os
import json
import config_store


def test_get_config_dir_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(config_store.platform, 'system', lambda: 'Linux')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    assert config_store.get_config_dir() == str(tmp_path / 'writereallyfree')


def test_save_and_load_config(monkeypatch, tmp_path):
    # Force config dir to tmp path
    monkeypatch.setattr(config_store, 'get_config_dir', lambda: str(tmp_path))

    cfg = {
        "sync_folder_name": "my_sync",
        "copy_empty_folders": True,
        "copy_readme": False,
        "theme": "dark",
        "sync_folder_prefix": "pre_"
    }

    assert config_store.save_config(cfg) is True

    loaded = config_store.load_config()
    assert loaded["sync_folder_name"] == "my_sync"
    assert loaded["theme"] == "dark"
    # Defaults still present when keys are missing
    # Remove a key and ensure default is supplied
    p = tmp_path / "config.json"
    with open(p, "w") as f:
        json.dump({"sync_folder_name": "x"}, f)

    monkeypatch.setattr(config_store, 'get_config_dir', lambda: str(tmp_path))
    loaded2 = config_store.load_config()
    assert "theme" in loaded2

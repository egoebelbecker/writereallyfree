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
    mgr.update_sync_settings('name', True, True, 'pre_', True, False, True, True, True, True)
    assert mgr.sync_folder_name == 'name'
    assert mgr.copy_empty_folders is True
    assert mgr.convert_to_docx is True
    assert mgr.docx_doublespace is True
    assert mgr.docx_indent_first_line is True
    assert mgr.docx_space_before is True
    assert mgr.docx_space_after is True


def test_sync_drives_strip_date_prefix(monkeypatch, tmp_path):
    monkeypatch.setattr(config_store, 'load_config', lambda: {
        "sync_folder_name": "sync_out",
        "copy_empty_folders": False,
        "copy_readme": False,
        "sync_folder_prefix": "",
        "convert_to_docx": True,
        "strip_date_prefix": True
    })
    monkeypatch.setattr(os.path, 'expanduser', lambda p: str(tmp_path))

    drive_dir = tmp_path / "fake_drive"
    drive_dir.mkdir()
    sample_file = drive_dir / "2026-08-13 jared checked his watch.txt"
    sample_file.write_text("Test content", encoding="utf-8")

    mgr = FreeWriteDriveManager()
    monkeypatch.setattr(mgr, 'get_drives', lambda: [{"name": "FreeWrite", "path": str(drive_dir)}])

    res = mgr.sync_drives()
    assert res["success"] is True

    dest_txt = tmp_path / "sync_out" / "jared checked his watch.txt"
    dest_docx = tmp_path / "sync_out" / "jared checked his watch.docx"
    unstripped_txt = tmp_path / "sync_out" / "2026-08-13 jared checked his watch.txt"

    assert dest_txt.exists()
    assert dest_docx.exists()
    assert not unstripped_txt.exists()


def test_allowed_labels_configuration(monkeypatch):
    monkeypatch.setattr(config_store, 'load_config', lambda: {
        "sync_folder_name": "",
        "copy_empty_folders": False,
        "allowed_labels": ["freewrite", "custom_drive"]
    })

    mgr = FreeWriteDriveManager()
    assert mgr.allowed_labels == {"freewrite", "custom_drive"}

    # Pass explicit custom string labels
    mgr_custom = FreeWriteDriveManager(allowed_labels="drive_a, DRIVE_B")
    assert mgr_custom.allowed_labels == {"drive_a", "drive_b"}

    # Update via update_sync_settings
    mgr.update_sync_settings('name', False, allowed_labels="new_label, another")
    assert mgr.allowed_labels == {"new_label", "another"}


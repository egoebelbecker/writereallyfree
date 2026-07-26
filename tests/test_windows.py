from windows import get_windows_volume_label


def test_windows_volume_label_none():
    # On non-windows systems this should fail gracefully and return None
    assert get_windows_volume_label('C:\\') is None

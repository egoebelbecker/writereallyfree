import sys
from windows import get_windows_volume_label


def test_windows_volume_label():
    if sys.platform != 'win32':
        # On non-Windows systems, this should fail gracefully and return None
        assert get_windows_volume_label('C:\\') is None
    else:
        # On Windows, C:\ returns a string volume label or None
        label = get_windows_volume_label('C:\\')
        assert label is None or isinstance(label, str)


def test_windows_volume_label_invalid_drive():
    # Non-existent drive path returns None on all platforms
    assert get_windows_volume_label('Z:\\NonExistentPath') is None

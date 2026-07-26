def get_windows_volume_label(drive_letter):
    """Gets the volume label for a Windows drive."""
    try:
        import ctypes
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = ctypes.c_ulong(0)
        max_component_length = ctypes.c_ulong(0)
        file_system_flags = ctypes.c_ulong(0)
        rc = ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive_letter),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            ctypes.byref(serial_number),
            ctypes.byref(max_component_length),
            ctypes.byref(file_system_flags),
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )
        if rc:
            return volumeNameBuffer.value
    except Exception:
        pass
    return None

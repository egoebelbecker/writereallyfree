import os
import getpass
import platform
from windows import get_windows_volume_label

class FreeWriteDriveManager:
    def __init__(self):
        self.allowed_labels = {'freewrite', 'traveler', 'alpha'}
        from config_store import load_config
        config = load_config()
        self.sync_folder_name = config.get("sync_folder_name", "")

    def update_sync_folder_name(self, name):
        self.sync_folder_name = name

    def get_drives(self):
        """Scans the system for mounted drives named FreeWrite, Traveler, or Alpha."""
        drives = []
        system = platform.system()
        if system == "Linux":
            username = getpass.getuser()
            for base in [f'/run/media/{username}', f'/media/{username}']:
                if os.path.exists(base):
                    try:
                        for item in os.listdir(base):
                            if item.lower() in self.allowed_labels:
                                drives.append({
                                    "name": item,
                                    "path": os.path.abspath(os.path.join(base, item))
                                })
                    except Exception:
                        pass
        elif system == "Darwin":  # macOS
            base = '/Volumes'
            if os.path.exists(base):
                try:
                    for item in os.listdir(base):
                        if item.lower() in self.allowed_labels:
                            drives.append({
                                "name": item,
                                "path": os.path.abspath(os.path.join(base, item))
                            })
                except Exception:
                    pass
        elif system == "Windows":
            # Check drives via psutil first
            try:
                import psutil
                for part in psutil.disk_partitions(all=False):
                    drive = part.mountpoint
                    volume_label = get_windows_volume_label(drive)
                    if volume_label and volume_label.lower() in self.allowed_labels:
                        drives.append({
                            "name": volume_label,
                            "path": drive
                        })
            except Exception:
                # Fallback scan
                for letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        try:
                            volume_label = get_windows_volume_label(drive)
                            if volume_label and volume_label.lower() in self.allowed_labels:
                                drives.append({
                                    "name": volume_label,
                                    "path": drive
                                })
                        except Exception:
                            pass
        return drives


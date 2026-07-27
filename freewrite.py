import os
import hashlib
import shutil
import getpass
import platform
from windows import get_windows_volume_label

def map_sync_path(rel_path, prefix, is_dir=False):
    if not prefix or not rel_path or rel_path == ".":
        return rel_path
    parts = rel_path.split(os.sep)
    if len(parts) > 1 or is_dir:
        parts[0] = f"{prefix}{parts[0]}"
        return os.path.join(*parts)
    return rel_path

def get_checksum(filepath):
    """Calculate SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


class FreeWriteDriveManager:
    def __init__(self):
        self.allowed_labels = {'freewrite', 'traveler', 'alpha'}
        from config_store import load_config
        config = load_config()
        self.sync_folder_name = config.get("sync_folder_name", "")
        self.copy_empty_folders = config.get("copy_empty_folders", False)
        self.copy_readme = config.get("copy_readme", False)
        self.sync_folder_prefix = config.get("sync_folder_prefix", "")
        self.strip_date_prefix = config.get("strip_date_prefix", False)

    def update_sync_settings(self, name, copy_empty_folders, copy_readme, prefix, convert_to_docx=False, strip_date_prefix=False):
        self.sync_folder_name = name
        self.copy_empty_folders = copy_empty_folders
        self.copy_readme = copy_readme
        self.sync_folder_prefix = prefix
        self.convert_to_docx = convert_to_docx
        self.strip_date_prefix = strip_date_prefix

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

    def sync_drives(self):
        """
        Synchronizes files from all detected FreeWrite drives to the local sync directory.
        Verifies copy success using SHA-256 checksums.
        """

        if not self.sync_folder_name:
            return {"success": False, "error": "No sync folder is currently configured in preferences."}

        home_dir = os.path.expanduser('~')
        dest_base = os.path.join(home_dir, self.sync_folder_name)

        try:
            os.makedirs(dest_base, exist_ok=True)
        except Exception as e:
            return {"success": False, "error": f"Failed to create sync directory: {str(e)}"}

        drives = self.get_drives()
        if not drives:
            return {"success": False, "error": "No FreeWrite, Traveler, or Alpha USB drives detected."}

        synced_files = []
        failed_files = []
        errors = []

        for drive in drives:
            drive_path = drive["path"]
            
            # Pass 1: Handle empty directories copy if enabled
            if self.copy_empty_folders:
                for root, dirs, files in os.walk(drive_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        rel_dir = os.path.relpath(dir_path, drive_path)
                        mapped_rel_dir = map_sync_path(rel_dir, self.sync_folder_prefix, is_dir=True)
                        dest_dir = os.path.join(dest_base, mapped_rel_dir)
                        try:
                            os.makedirs(dest_dir, exist_ok=True)
                        except Exception as e:
                            errors.append(f"Failed to create empty directory {rel_dir}: {str(e)}")

            # Walk the drive files recursively
            for root, dirs, files in os.walk(drive_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if file.startswith('.'):
                        continue

                    if file.lower() == 'readme.txt' and root == drive_path:
                        continue

                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, drive_path)
                    mapped_rel_path = map_sync_path(rel_path, self.sync_folder_prefix, is_dir=False)
                    dest_file = os.path.join(dest_base, mapped_rel_path)
                    dest_dir = os.path.dirname(dest_file)

                    try:
                        os.makedirs(dest_dir, exist_ok=True)

                        src_hash = get_checksum(src_file)
                        if src_hash is None:
                            raise Exception("Could not calculate source file checksum.")

                        dest_hash = None
                        if os.path.exists(dest_file):
                            dest_hash = get_checksum(dest_file)

                        if src_hash == dest_hash:
                            synced_files.append({"file": mapped_rel_path, "status": "identical"})
                            # Strip leading date prefix if enabled
                            if self.strip_date_prefix:
                                import re
                                base = os.path.basename(dest_file)
                                new_base = re.sub(r'^\d{4}-\d{2}-\d{2}\s+', '', base)
                                if new_base != base:
                                    new_path = os.path.join(os.path.dirname(dest_file), new_base)
                                    os.rename(dest_file, new_path)
                                    dest_file = new_path
                            if self.convert_to_docx:
                                ext = os.path.splitext(dest_file)[1].lower()
                                if ext in ('.txt', '.md', '.markdown'):
                                    docx_file = os.path.splitext(dest_file)[0] + '.docx'
                                    if not os.path.exists(docx_file):
                                        from convert_doc import create_word_document
                                        create_word_document(dest_dir, file)
                            continue

                        # Perform the copy
                        shutil.copy2(src_file, dest_file)

                        # Recalculate hash to verify integrity
                        post_dest_hash = get_checksum(dest_file)
                        if src_hash == post_dest_hash:
                            synced_files.append({"file": mapped_rel_path, "status": "copied"})
                            if self.convert_to_docx:
                                ext = os.path.splitext(dest_file)[1].lower()
                                if ext in ('.txt', '.md', '.markdown'):
                                    from convert_doc import create_word_document
                                    create_word_document(dest_dir, file)
                        else:
                            failed_files.append({"file": mapped_rel_path, "error": "Checksum verification failed after copy."})

                    except Exception as e:
                        failed_files.append({"file": mapped_rel_path, "error": str(e)})
                        errors.append(f"Error copying {rel_path}: {str(e)}")

        return {
            "success": True,
            "drives_scanned": [d["name"] for d in drives],
            "synced": synced_files,
            "failed": failed_files,
            "errors": errors
        }



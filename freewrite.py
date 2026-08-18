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


def parse_allowed_labels(labels):
    if labels is None:
        return {'freewrite', 'traveler', 'alpha'}
    if isinstance(labels, str):
        items = labels.split(',')
    elif isinstance(labels, (list, set, tuple)):
        items = labels
    else:
        return {'freewrite', 'traveler', 'alpha'}

    result = set()
    for item in items:
        if isinstance(item, str):
            for sub in item.split(','):
                cleaned = sub.strip().lower()
                if cleaned:
                    result.add(cleaned)
    return result if result else {'freewrite', 'traveler', 'alpha'}


class FreeWriteDriveManager:
    def __init__(self, allowed_labels=None):
        from config_store import load_config
        config = load_config()
        if allowed_labels is None:
            allowed_labels = config.get("allowed_labels", ["freewrite", "traveler", "alpha"])
        self.allowed_labels = parse_allowed_labels(allowed_labels)
        self.sync_folder_name = config.get("sync_folder_name", "")
        self.copy_empty_folders = config.get("copy_empty_folders", False)
        self.copy_readme = config.get("copy_readme", False)
        self.sync_folder_prefix = config.get("sync_folder_prefix", "")
        self.strip_date_prefix = config.get("strip_date_prefix", False)
        self.convert_to_docx = config.get("convert_to_docx", False)
        self.docx_doublespace = config.get("docx_doublespace", False)
        self.docx_indent_first_line = config.get("docx_indent_first_line", False)
        self.docx_space_before = config.get("docx_space_before", False)
        self.docx_space_after = config.get("docx_space_after", False)

    def update_sync_settings(self, name, copy_empty_folders, copy_readme=False, prefix="", convert_to_docx=False, strip_date_prefix=False, docx_doublespace=False, docx_indent_first_line=False, docx_space_before=False, docx_space_after=False, allowed_labels=None):
        self.sync_folder_name = name
        self.copy_empty_folders = copy_empty_folders
        self.copy_readme = copy_readme
        self.sync_folder_prefix = prefix
        self.convert_to_docx = convert_to_docx
        self.strip_date_prefix = strip_date_prefix
        self.docx_doublespace = docx_doublespace
        self.docx_indent_first_line = docx_indent_first_line
        self.docx_space_before = docx_space_before
        self.docx_space_after = docx_space_after
        if allowed_labels is not None:
            self.allowed_labels = parse_allowed_labels(allowed_labels)

    def get_drives(self):
        """Scans the system for mounted drives matching configured allowed labels."""
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

                    # Strip leading date prefix if enabled
                    if self.strip_date_prefix:
                        import re
                        mapped_dir = os.path.dirname(mapped_rel_path)
                        mapped_base = os.path.basename(mapped_rel_path)
                        stripped_base = re.sub(r'^\d{4}[-_.]?\d{2}[-_.]?\d{2}[\s_-]*', '', mapped_base)
                        if stripped_base:
                            unstripped_rel_path = mapped_rel_path
                            mapped_rel_path = os.path.join(mapped_dir, stripped_base) if mapped_dir else stripped_base

                            # Clean up previously synced un-stripped file if it exists
                            old_dest_file = os.path.join(dest_base, unstripped_rel_path)
                            if os.path.exists(old_dest_file) and old_dest_file != os.path.join(dest_base, mapped_rel_path):
                                try:
                                    os.remove(old_dest_file)
                                    old_docx = os.path.splitext(old_dest_file)[0] + '.docx'
                                    if os.path.exists(old_docx):
                                        os.remove(old_docx)
                                except Exception:
                                    pass

                    dest_file = os.path.join(dest_base, mapped_rel_path)
                    dest_dir = os.path.dirname(dest_file)
                    dest_filename = os.path.basename(dest_file)

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
                            if self.convert_to_docx:
                                ext = os.path.splitext(dest_file)[1].lower()
                                if ext in ('.txt', '.md', '.markdown'):
                                    docx_file = os.path.splitext(dest_file)[0] + '.docx'
                                    if not os.path.exists(docx_file):
                                        from convert_doc import create_word_document
                                        create_word_document(
                                            dest_dir,
                                            dest_filename,
                                            doublespace=getattr(self, "docx_doublespace", False),
                                            indent_first_line=getattr(self, "docx_indent_first_line", False),
                                            space_before=getattr(self, "docx_space_before", False),
                                            space_after=getattr(self, "docx_space_after", False)
                                        )
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
                                    create_word_document(
                                        dest_dir,
                                        dest_filename,
                                        doublespace=getattr(self, "docx_doublespace", False),
                                        indent_first_line=getattr(self, "docx_indent_first_line", False),
                                        space_before=getattr(self, "docx_space_before", False),
                                        space_after=getattr(self, "docx_space_after", False)
                                    )
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



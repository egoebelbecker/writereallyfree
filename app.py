import os
import sys

# Ensure pythonnet can find the Python runtime DLL when packaged with PyInstaller on Windows
if sys.platform == "win32" and getattr(sys, "frozen", False):
    if "PYTHONNET_PYDLL" not in os.environ:
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
        search_dirs = [base_dir, os.path.join(base_dir, "_internal")]
        for sdir in search_dirs:
            if os.path.exists(sdir):
                for f in os.listdir(sdir):
                    if f.startswith("python3") and f.endswith(".dll") and not f.startswith("python3-"):
                        os.environ["PYTHONNET_PYDLL"] = os.path.join(sdir, f)
                        break
            if "PYTHONNET_PYDLL" in os.environ:
                break

import webview
import webbrowser
import datetime
from windows import get_windows_volume_label
from freewrite import FreeWriteDriveManager
from config_store import load_config

APP_VERSION = "v0.2.1"
class HomeExplorerAPI:
    def __init__(self):
        self.home_dir = os.path.expanduser('~')
        self.freewrite_manager = FreeWriteDriveManager()
        config = load_config()
        self.version = APP_VERSION
        self.sync_folder_name = config.get("sync_folder_name", "")
        self.copy_empty_folders = config.get("copy_empty_folders", False)
        self.theme = config.get("theme", "system")
        self.sync_folder_prefix = config.get("sync_folder_prefix", "")
        self.convert_to_docx = config.get("convert_to_docx", False)
        self.strip_date_prefix = config.get("strip_date_prefix", False)
        self.docx_doublespace = config.get("docx_doublespace", False)
        self.docx_indent_first_line = config.get("docx_indent_first_line", False)
        self.docx_space_before = config.get("docx_space_before", False)
        self.docx_space_after = config.get("docx_space_after", False)
        self.allowed_labels = config.get("allowed_labels", ["freewrite", "traveler", "alpha"])

    def get_home_path(self):
        """Returns the absolute path of the home directory."""
        return self.home_dir

    def get_startup_path(self):
        """Returns the initial folder path to display on startup."""
        if self.sync_folder_name:
            full_path = os.path.join(self.home_dir, self.sync_folder_name)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                return self.sync_folder_name
        return ""

    def get_preferences(self):
        """Fetch saved configuration preferences, including app version."""
        labels = getattr(self, "allowed_labels", ["freewrite", "traveler", "alpha"])
        if hasattr(self.freewrite_manager, "allowed_labels") and isinstance(self.freewrite_manager.allowed_labels, set):
            labels = list(self.freewrite_manager.allowed_labels)
        return {
            "success": True,
            "sync_folder_name": self.sync_folder_name,
            "copy_empty_folders": self.copy_empty_folders,
            "theme": self.theme,
            "sync_folder_prefix": self.sync_folder_prefix,
            "convert_to_docx": self.convert_to_docx,
            "strip_date_prefix": getattr(self, "strip_date_prefix", False),
            "docx_doublespace": getattr(self, "docx_doublespace", False),
            "docx_indent_first_line": getattr(self, "docx_indent_first_line", False),
            "docx_space_before": getattr(self, "docx_space_before", False),
            "docx_space_after": getattr(self, "docx_space_after", False),
            "allowed_labels": labels,
            "version": getattr(self, "version", "dev")
        }    
    def open_external(self, url):
        """Open a URL in the system's default browser."""
        try:
            # PyInstaller & AppImage override LD_LIBRARY_PATH, PYTHONPATH, etc.,
            # which prevents external binaries like xdg-open/browser from running.
            env = os.environ.copy()
            if "LD_LIBRARY_PATH_ORIG" in env:
                env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
            else:
                env.pop("LD_LIBRARY_PATH", None)

            if "PATH_ORIG" in env:
                env["PATH"] = env["PATH_ORIG"]

            env.pop("PYTHONPATH", None)
            env.pop("PYTHONHOME", None)

            if sys.platform.startswith("linux"):
                import subprocess

                subprocess.Popen(["xdg-open", url], env=env)
            else:
                webbrowser.open(url)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_preferences(self, sync_folder_name, copy_empty_folders=False, theme="system", sync_folder_prefix="", convert_to_docx=False, strip_date_prefix=False, docx_doublespace=False, docx_indent_first_line=False, docx_space_before=False, docx_space_after=False, allowed_labels=None):
        """Save preferences and ensure folders exist."""
        try:
            sync_folder_name = sync_folder_name.strip().strip("/").strip("\\")
            
            # Ensure the directory exists under Home directory if specified
            if sync_folder_name:
                full_path = os.path.join(self.home_dir, sync_folder_name)
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
            
            if allowed_labels is None:
                allowed_labels_list = getattr(self, "allowed_labels", ["freewrite", "traveler", "alpha"])
            elif isinstance(allowed_labels, str):
                allowed_labels_list = [x.strip() for x in allowed_labels.split(",") if x.strip()]
            else:
                allowed_labels_list = list(allowed_labels)
            if not allowed_labels_list:
                allowed_labels_list = ["freewrite", "traveler", "alpha"]

            from config_store import save_config
            save_config({
                "sync_folder_name": sync_folder_name,
                "copy_empty_folders": copy_empty_folders,
                "theme": theme,
                "sync_folder_prefix": sync_folder_prefix,
                "convert_to_docx": convert_to_docx,
                "strip_date_prefix": strip_date_prefix,
                "docx_doublespace": docx_doublespace,
                "docx_indent_first_line": docx_indent_first_line,
                "docx_space_before": docx_space_before,
                "docx_space_after": docx_space_after,
                "allowed_labels": allowed_labels_list
            })
            
            self.sync_folder_name = sync_folder_name
            self.copy_empty_folders = copy_empty_folders
            self.theme = theme
            self.sync_folder_prefix = sync_folder_prefix
            self.convert_to_docx = convert_to_docx
            self.strip_date_prefix = strip_date_prefix
            self.docx_doublespace = docx_doublespace
            self.docx_indent_first_line = docx_indent_first_line
            self.docx_space_before = docx_space_before
            self.docx_space_after = docx_space_after
            self.allowed_labels = allowed_labels_list
            
            self.freewrite_manager.update_sync_settings(
                name=sync_folder_name,
                copy_empty_folders=copy_empty_folders,
                copy_readme=False,
                prefix=sync_folder_prefix,
                convert_to_docx=convert_to_docx,
                strip_date_prefix=strip_date_prefix,
                docx_doublespace=docx_doublespace,
                docx_indent_first_line=docx_indent_first_line,
                docx_space_before=docx_space_before,
                docx_space_after=docx_space_after,
                allowed_labels=allowed_labels_list
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def trigger_sync(self):
        """Trigger drive synchronization."""
        try:
            # Re-read configuration settings first to ensure path matches preferences
            from config_store import load_config
            config = load_config()
            self.freewrite_manager.update_sync_settings(
                name=config.get("sync_folder_name", ""),
                copy_empty_folders=config.get("copy_empty_folders", False),
                copy_readme=False,
                prefix=config.get("sync_folder_prefix", ""),
                convert_to_docx=config.get("convert_to_docx", False),
                strip_date_prefix=config.get("strip_date_prefix", False),
                docx_doublespace=config.get("docx_doublespace", False),
                docx_indent_first_line=config.get("docx_indent_first_line", False),
                docx_space_before=config.get("docx_space_before", False),
                docx_space_after=config.get("docx_space_after", False),
                allowed_labels=config.get("allowed_labels", ["freewrite", "traveler", "alpha"])
            )
            
            return self.freewrite_manager.sync_drives()
        except Exception as e:
            return {"success": False, "error": str(e)}


    def get_freewrite_drives(self):
        """Fetch mounted FreeWrite drives."""
        try:
            return {"success": True, "drives": self.freewrite_manager.get_drives()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, subpath=""):
        """
        Lists files and directories under the specified location
        """
        try:
            # Get list of allowed base paths
            allowed_bases = [self.home_dir]
            drives = self.freewrite_manager.get_drives()
            for drive in drives:
                allowed_bases.append(drive["path"])

            # Resolve target path
            is_absolute = os.path.isabs(subpath) or (len(subpath) > 1 and subpath[1] == ':')
            if is_absolute:
                target_path = os.path.abspath(subpath)
            else:
                target_path = os.path.abspath(os.path.join(self.home_dir, subpath))

            # Security verification: path must be inside one of the allowed bases
            allowed = False
            for base in allowed_bases:
                try:
                    if os.path.commonpath([base, target_path]) == base:
                        allowed = True
                        break
                except ValueError:
                    pass

            if not allowed:
                target_path = self.home_dir

            # Identify if target_path is on a drive or home
            is_drive = False
            drive_name = None
            drive_base = None
            for drive in drives:
                base = drive["path"]
                try:
                    if os.path.commonpath([base, target_path]) == base:
                        is_drive = True
                        drive_name = drive["name"]
                        drive_base = base
                        break
                except ValueError:
                    pass

            # Compute relative path for breadcrumbs rendering
            if is_drive:
                rel_path = os.path.relpath(target_path, drive_base)
                if rel_path == ".":
                    rel_path = ""
            else:
                rel_path = os.path.relpath(target_path, self.home_dir)
                if rel_path == ".":
                    rel_path = ""

            # Compute parent path
            parent_path = None
            is_at_root = (target_path == self.home_dir)
            if is_drive and target_path == drive_base:
                is_at_root = True

            if not is_at_root:
                parent_path = os.path.dirname(target_path)
                # Keep parent relative to home if it resides in home
                try:
                    if os.path.commonpath([self.home_dir, parent_path]) == self.home_dir:
                        parent_path = os.path.relpath(parent_path, self.home_dir)
                        if parent_path == ".":
                            parent_path = ""
                except ValueError:
                    pass

            items = []
            for item in os.listdir(target_path):
                # Filter out hidden files and directories
                if item.startswith('.'):
                    continue

                full_path = os.path.join(target_path, item)
                
                # Determine relative navigation path for this item
                try:
                    if os.path.commonpath([self.home_dir, full_path]) == self.home_dir:
                        item_rel_path = os.path.relpath(full_path, self.home_dir)
                    else:
                        item_rel_path = full_path  # Absolute path for external drive files
                except ValueError:
                    item_rel_path = full_path

                is_dir = os.path.isdir(full_path)
                try:
                    stat_info = os.stat(full_path)
                    size = stat_info.st_size
                    modified = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    size = 0
                    modified = "Unknown"

                items.append({
                    "name": item,
                    "rel_path": item_rel_path,
                    "is_dir": is_dir,
                    "size": size,
                    "modified": modified
                })

            # Sort: directories first, then files alphabetically
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            return {
                "success": True,
                "current_path": target_path,
                "is_drive": is_drive,
                "drive_name": drive_name,
                "drive_base": drive_base,
                "rel_path": rel_path,
                "parent_path": parent_path,
                "sync_folder_name": self.sync_folder_name,
                "copy_empty_folders": self.copy_empty_folders,
                "theme": self.theme,
                "sync_folder_prefix": self.sync_folder_prefix,
                "convert_to_docx": self.convert_to_docx,
                "docx_doublespace": getattr(self, "docx_doublespace", False),
                "docx_indent_first_line": getattr(self, "docx_indent_first_line", False),
                "docx_space_before": getattr(self, "docx_space_before", False),
                "docx_space_after": getattr(self, "docx_space_after", False),
                "items": items
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def read_file_preview(self, rel_path, max_chars=5000):
        """Reads a text file preview from the home directory or a FreeWrite drive."""
        try:
            is_absolute = os.path.isabs(rel_path) or (len(rel_path) > 1 and rel_path[1] == ':')
            if is_absolute:
                target_path = os.path.abspath(rel_path)
            else:
                target_path = os.path.abspath(os.path.join(self.home_dir, rel_path))

            # Security verification
            allowed_bases = [self.home_dir]
            for drive in self.freewrite_manager.get_drives():
                allowed_bases.append(drive["path"])

            allowed = False
            for base in allowed_bases:
                try:
                    if os.path.commonpath([base, target_path]) == base:
                        allowed = True
                        break
                except ValueError:
                    pass

            if not allowed:
                return {"success": False, "error": "Access Denied: Path is outside allowed directories."}

            if os.path.isdir(target_path):
                return {"success": False, "error": "Path is a directory."}

            # Read first chunk of file safely
            with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(max_chars)

            return {
                "success": True,
                "path": target_path,
                "content": content,
                "truncated": len(content) >= max_chars
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    api = HomeExplorerAPI()
    
    # Locate index.html relative to this file.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, 'web', 'index.html')
    
    # Setup window options: nice size, window title
    webview.create_window(
        title='WriteReallyFree',
        url=html_file,
        js_api=api,
        width=1000,
        height=700,
        min_size=(800, 600),
        background_color='#0f172a' # Dark slate background to match dark theme
    )
    
    if sys.platform == "win32":
        try:
            webview.start(gui="qt")
        except Exception:
            webview.start()
    else:
        webview.start()

if __name__ == '__main__':
    main()


import os
import sys
import webview
import datetime

class HomeExplorerAPI:
    def __init__(self):
        self.home_dir = os.path.expanduser('~')

    def get_home_path(self):
        """Returns the absolute path of the home directory."""
        return self.home_dir

    def list_directory(self, subpath=""):
        """
        Lists files and directories under the home directory + subpath.
        Prevents navigating outside the home directory for security.
        """
        try:
            # Secure path resolution: resolve potential parent directory references ('..')
            target_path = os.path.abspath(os.path.join(self.home_dir, subpath))
            if not target_path.startswith(self.home_dir):
                # Out of bounds! Reset to home_dir
                target_path = self.home_dir

            items = []
            for item in os.listdir(target_path):
                full_path = os.path.join(target_path, item)
                rel_path = os.path.relpath(full_path, self.home_dir)
                if rel_path == ".":
                    rel_path = ""
                
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
                    "rel_path": rel_path,
                    "is_dir": is_dir,
                    "size": size,
                    "modified": modified
                })
            
            # Sort: directories first, then files alphabetically
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return {
                "success": True,
                "current_path": target_path,
                "rel_path": os.path.relpath(target_path, self.home_dir) if target_path != self.home_dir else "",
                "items": items
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def read_file_preview(self, rel_path, max_chars=5000):
        """Reads a text file preview from the home directory."""
        try:
            target_path = os.path.abspath(os.path.join(self.home_dir, rel_path))
            if not target_path.startswith(self.home_dir):
                return {"success": False, "error": "Access Denied: Path is outside home directory."}
            
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
        title='ReallyFree - Home Explorer',
        url=html_file,
        js_api=api,
        width=1000,
        height=700,
        min_size=(800, 600),
        background_color='#0f172a' # Dark slate background to match our dark theme
    )
    
    webview.start(debug=True)

if __name__ == '__main__':
    main()

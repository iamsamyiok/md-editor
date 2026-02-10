import webview
import os
import json
import threading
from pathlib import Path
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageFont
import pynput
from pynput import keyboard

class MarkdownEditor:
    def __init__(self):
        self.window = None
        self.tray_icon = None
        self.listener = None
        self.workspace_config = self._load_workspace_config()
        self.history = self._load_history()
        
    def _load_workspace_config(self):
        config_path = os.path.expanduser("~/.markdown_editor_workspace.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"workspace_path": ""}
    
    def _save_workspace_config(self):
        config_path = os.path.expanduser("~/.markdown_editor_workspace.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.workspace_config, f, ensure_ascii=False)
    
    def _load_history(self):
        history_path = os.path.expanduser("~/.markdown_editor_history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"recent_files": []}
    
    def _save_history(self):
        history_path = os.path.expanduser("~/.markdown_editor_history.json")
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False)
    
    def create_tray_icon(self):
        img = Image.new('RGB', (32, 32), color='#2383e2')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 31, 31], outline='white', width=2)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        draw.text((6, 6), "MD", fill='white', font=font)
        
        def show_window(icon, item):
            if self.window:
                self.window.show()
        
        def hide_window(icon, item):
            if self.window:
                self.window.hide()
        
        def toggle_window(icon, item):
            if self.window:
                if self.window.visible:
                    self.window.hide()
                else:
                    self.window.show()
        
        def exit_app(icon, item):
            if self.listener:
                self.listener.stop()
            icon.stop()
            if self.window:
                self.window.destroy()
        
        menu = Menu(
            MenuItem('显示窗口', show_window),
            MenuItem('隐藏窗口', hide_window),
            Menu.SEPARATOR,
            MenuItem('退出', exit_app)
        )
        
        self.tray_icon = Icon('md-editor', img, 'md-editor', menu)
        
        def run_tray():
            self.tray_icon.run()
        
        threading.Thread(target=run_tray, daemon=True).start()
    
    def setup_global_hotkey(self):
        """设置全局快捷键 Ctrl+Alt+N"""
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.n_pressed = False
        
        def toggle_window():
            print('Toggle window hotkey activated')
            if self.window:
                if self.window.visible:
                    print('Hiding window')
                    self.window.hide()
                else:
                    print('Showing window')
                    self.window.show()
        
        def on_press(key):
            try:
                # 使用 keyboard.Key 的名称或字符串
                if hasattr(key, 'name'):
                    key_name = key.name
                else:
                    key_name = str(key)
                
                print(f'Key pressed: {key_name}')
                
                if key_name == 'ctrl' or key_name == 'ctrl_l' or key_name == 'ctrl_r':
                    self.ctrl_pressed = True
                elif key_name == 'alt' or key_name == 'alt_l' or key_name == 'alt_r':
                    self.alt_pressed = True
                elif key_name == 'n':
                    self.n_pressed = True
                
                # 检查是否按下了 Ctrl+Alt+N
                if self.ctrl_pressed and self.alt_pressed and self.n_pressed:
                    toggle_window()
            except Exception as e:
                print(f'Error in on_press: {e}')
        
        def on_release(key):
            try:
                if hasattr(key, 'name'):
                    key_name = key.name
                else:
                    key_name = str(key)
                
                print(f'Key released: {key_name}')
                
                if key_name == 'ctrl' or key_name == 'ctrl_l' or key_name == 'ctrl_r':
                    self.ctrl_pressed = False
                elif key_name == 'alt' or key_name == 'alt_l' or key_name == 'alt_r':
                    self.alt_pressed = False
                elif key_name == 'n':
                    self.n_pressed = False
            except Exception as e:
                print(f'Error in on_release: {e}')
        
        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        
        # 在单独的线程中启动监听器
        import threading
        def run_listener():
            print('Starting keyboard listener...')
            self.listener.start()
            print('Keyboard listener started')
        
        threading.Thread(target=run_listener, daemon=True).start()
    
    def get_file_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return ""
    
    def save_file_content(self, filepath, content):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            return False
    
    def list_directory(self, path):
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                files.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': is_dir
                })
            return files
        except Exception as e:
            return []
    
    def create_file(self, path, name, is_dir=False):
        try:
            full_path = os.path.join(path, name)
            if is_dir:
                os.makedirs(full_path, exist_ok=True)
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("")
            return True
        except Exception as e:
            return False
    
    def delete_item(self, path):
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            return False
    
    def rename_item(self, old_path, new_name):
        try:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            return False
    
    def open_folder_dialog(self):
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            self.workspace_config["workspace_path"] = result[0]
            self._save_workspace_config()
            return result[0]
        return None
    
    def open_file_dialog(self):
        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=('Markdown Files (*.md)', '*.md', 'All Files (*.*)', '*.*')
        )
        if result and len(result) > 0:
            return result[0]
        return None
    
    def save_file_dialog(self):
        result = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            file_types=('Markdown Files (*.md)', '*.md'),
            save_filename='untitled.md'
        )
        if result and len(result) > 0:
            return result[0]
        return None
    
    def add_to_history(self, filepath):
        name = os.path.basename(filepath)
        entry = {
            'path': filepath,
            'name': name,
            'timestamp': os.path.getmtime(filepath)
        }
        self.history['recent_files'].insert(0, entry)
        self.history['recent_files'] = self.history['recent_files'][:20]
        self._save_history()
    
    def get_history(self):
        if isinstance(self.history, dict):
            return self.history.get('recent_files', [])
        elif isinstance(self.history, list):
            return self.history
        return []
    
    def on_loading_complete(self):
        """Called when frontend loading is complete"""
        print('Frontend loading complete')
    
    def start(self):
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'index.html')
        
        self.window = webview.create_window(
            'md-editor',
            html_path,
            width=1400,
            height=900,
            min_size=(900, 600),
            resizable=True,
            frameless=False,
            easy_drag=True,
            js_api=self
        )
        
        def on_closing():
            """窗口关闭事件处理：只隐藏窗口，不退出程序"""
            self.window.hide()
            return False  # 阻止窗口关闭，程序继续在后台运行
        
        self.window.events.closing += on_closing
        
        self.create_tray_icon()
        self.setup_global_hotkey()
        
        webview.start(debug=False)

if __name__ == '__main__':
    app = MarkdownEditor()
    app.start()
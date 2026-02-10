# md-editor 开发总结

## 项目概述
基于 Python 和 PyWebView 开发的桌面 Markdown 编辑器，采用所见即所得(WYSIWYG)的编辑方式，类似于 Notion 的编辑体验。

**程序名称**: md-editor  
**图标**: icon.png  
**打包位置**: dist\md-editor\

---

## 技术栈
- **后端**: Python 3.8+
- **前端框架**: PyWebView (桌面应用容器)
- **前端技术**: HTML5, CSS3, JavaScript (ES6+)
- **主要依赖**:
  - pywebview>=4.0
  - PyInstaller>=5.0
  - pystray>=0.19.0 (系统托盘)
  - Pillow>=9.0.0 (图像处理)
  - pynput>=1.7.0 (全局快捷键)
  - PyQt5 (图形界面)

---

## 项目结构
```
E:\Desktop\md-editor\
├── app.py              # 主程序入口
├── src\
│   ├── index.html     # 主页面结构
│   ├── style.css      # 样式表
│   └── app.js         # JavaScript逻辑
├── icon.png            # 程序图标
├── md-editor.spec     # PyInstaller 配置
├── build.bat           # 打包脚本
└── requirements.txt    # 依赖列表
```

---

## 核心功能实现

### 1. 编辑功能
- **所见即所得编辑**: 实时预览 Markdown 渲染效果
- **格式化支持**: 加粗(Ctrl+B)、斜体(Ctrl+I)、代码、链接、颜色等
- **标题**: H1、H2、H3 支持
- **列表功能**: 无序列表、有序列表、任务列表(支持多级缩进)

### 2. 文件管理
- **工作区管理**: 打开文件夹作为工作区
- **VSCode 风格文件树**: 支持文件/文件夹展开和折叠
- **文件操作**: 新建、打开、保存、重命名、删除
- **历史记录**: 最近文件记录

### 3. 特殊块功能
- **折叠块**: 可展开/折叠的内容块
- **标注块**: [!INFO], [!TIP], [!WARNING], [!ERROR], [!SUCCESS]
- **引用块**: 支持多级引用
- **分割线**: 插入水平分割线
- **表格**: 插入表格(支持指定行列数)
- **目录**: 自动生成文档目录

### 4. 搜索与替换
- 支持区分大小写
- 支持正则表达式
- 显示匹配数量
- 支持上一个/下一个导航
- 快捷键: Ctrl+F

### 5. 主题支持
- 浅色主题(默认)
- 深色主题(护眼模式)
- 主题切换和记忆

### 6. 系统托盘功能
- 程序关闭时最小化到托盘(不真正退出)
- 托盘菜单: 显示窗口、隐藏窗口、退出
- 全局快捷键: Ctrl+Alt+N 显示/隐藏主窗口
- 蓝色背景,白色边框,显示"MD"文字的托盘图标

### 7. 撤销/重做
- 支持最多50步撤销
- 快捷键: Ctrl+Z (撤销), Ctrl+Y (重做)

### 8. 自动保存
- 编辑2秒后自动保存
- 显示保存状态
- 手动保存: Ctrl+S

### 9. 启动加载动画
- 6个加载阶段: DOM加载、PyWebView连接、工具栏、主题、历史记录、文件树
- 实时进度条显示(0%-100%)
- 所有组件加载完成后平滑过渡到主界面

---

## 关键代码修改记录

### 1. 工具栏按钮修复 (app.js)
**问题**: 工具栏按钮使用 `eval(action)` 无法正常工作  
**修复**: 使用动作映射表 + 字符串标识符

```javascript
const actionMap = {
    'new-file': () => newFile(),
    'open-file': () => openFile(),
    'save-file': () => saveFile(),
    'undo': () => undo(),
    'redo': () => redo(),
    // ... 更多动作
};

// 工具栏配置
{ icon: 'icon-bold', title: '加粗 (Ctrl+B)', action: 'bold' }

// 事件绑定
toolbar.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => {
        const action = btn.getAttribute('data-action');
        if (action && actionMap[action]) {
            actionMap[action]();
        }
    });
});
```

### 2. 图标加载优化 (index.html + app.js)
**问题**: 工具栏加载慢,每次都生成完整 SVG  
**修复**: 使用 SVG `<symbol>` 预定义 + `<use>` 引用

```html
<!-- HTML 中预定义 SVG 符号 -->
<svg style="display: none;">
    <symbol id="icon-bold" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"></path>
    </symbol>
    <!-- 更多图标 -->
</svg>

<!-- 按钮使用 -->
<button data-action="bold">
    <svg width="20" height="20"><use href="#icon-bold"></use></svg>
</button>
```

### 3. 文件路径处理 (app.js)
**问题**: 使用了 Python 的 `os.path.basename` 导致错误  
**修复**: 使用 JavaScript 方式提取文件名

```javascript
// 错误的方式
updateStatus(os.path.basename(filepath));  // os is Python module

// 正确的方式
const filename = filepath.split(/[\/\\]/).pop();
updateStatus(filename);
```

### 4. Enter 键增强处理 (app.js)
**功能**: 列表/折叠块/表格的智能退出

```javascript
// 在空列表项中按 Enter: 退出列表模式
if (isLiEmpty) {
    const ul = li.parentElement;
    const parent = ul.parentElement;
    const newP = document.createElement('p');
    newP.innerHTML = '<br>';
    parent.insertBefore(newP, ul.nextSibling);
    li.remove();
}

// 在空折叠块内容中按 Enter: 退出折叠块
if (isContentEmpty) {
    const newP = document.createElement('p');
    newP.innerHTML = '<br>';
    details.parentNode.insertBefore(newP, details.nextSibling);
}

// 在表格最后单元格按 Enter: 退出表格
if (isLastRow && isLastCell) {
    const newP = document.createElement('p');
    newP.innerHTML = '<br>';
    table.parentNode.insertBefore(newP, table.nextSibling);
}
```

### 5. 向下箭头创建新段落 (app.js)
**功能**: 在当前行后创建新段落

```javascript
e.key === 'ArrowDown' => {
    const blockElement = container.closest('p, h1, h2, h3, li, div');
    const newP = document.createElement('p');
    newP.innerHTML = '<br>';
    blockElement.parentNode.insertBefore(newP, blockElement.nextSibling);
}
```

### 6. Markdown 快捷语法 (app.js)
**功能**: 输入 # 自动转换为标题

```javascript
if (text.startsWith('# ')) {
    const level = text.split(' ')[0].length;
    document.execCommand('formatBlock', false, `h${level}`);
}
```

### 7. 颜色选择器 (index.html + app.js)
**功能**: 20种常用颜色,点击选择

```html
<div id="color-picker" class="color-picker">
    <div class="color-picker-header">选择颜色</div>
    <div class="color-palette" id="color-palette"></div>
</div>

// JavaScript 初始化颜色
const colors = [
    '#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
    '#00FFFF', '#FF00FF', '#FFA500', '#800080', '#FFC0CB',
    '#808080', '#A52A2A', '#FFD700', '#FFA07A', '#20B2AA'
];
```

### 8. 表格高度调整 (style.css)
**问题**: 表格单元格高度与光标不一致  
**修复**: 设置最小高度

```css
.editor th, .editor td {
    border: 1px solid var(--border-color);
    padding: 8px 12px;
    text-align: left;
    min-height: 27.2px;  /* 与光标高度一致 */
    line-height: 1.5;
}
```

### 9. 工具栏高度调整 (style.css)
**要求**: 工具栏高度为原来的两倍,与文件管理区对齐

```css
.toolbar {
    display: flex;
    flex-wrap: nowrap;
    gap: 4px;
    padding: 24px 16px 24px 56px;  /* 垂直24px, 左侧56px避免与恢复按钮冲突 */
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    overflow-x: auto;
}
```

### 10. 侧边栏恢复按钮 (index.html + style.css)
**功能**: 侧边栏折叠后可重新展开

```html
<button id="sidebar-restore-btn" class="sidebar-restore-btn" title="展开侧边栏">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
</button>
```

```css
#sidebar-restore-btn {
    position: fixed;
    left: 8px;
    top: 12px;
    z-index: 100;
    display: none;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
    padding: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#sidebar.collapsed ~ #sidebar-restore-btn {
    display: flex;
}
```

### 11. 加载屏幕实现 (index.html + style.css + app.js)
**功能**: 启动时显示加载动画,组件加载完成后消失

```html
<div id="loading-screen" class="loading-screen">
    <div class="loading-content">
        <div class="loading-icon">...</div>
        <h1 class="loading-title">md-editor</h1>
        <div class="loading-spinner"></div>
        <p class="loading-text">正在加载组件...</p>
        <div class="loading-progress">
            <div class="loading-progress-bar"></div>
        </div>
    </div>
</div>
```

```css
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--bg-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

#app {
    display: none;
}

#app.loaded {
    display: flex;
}
```

```javascript
const LoadingManager = {
    components: {
        dom: false,
        pywebview: false,
        toolbar: false,
        theme: false,
        history: false,
        fileTree: false
    },
    updateProgress() {
        const total = Object.keys(this.components).length;
        const loaded = Object.values(this.components).filter(v => v).length;
        const percentage = Math.round((loaded / total) * 100);
        document.querySelector('.loading-progress-bar').style.width = percentage + '%';
    },
    markLoaded(component) {
        if (this.components.hasOwnProperty(component)) {
            this.components[component] = true;
            this.updateProgress();
            if (this.isAllLoaded()) {
                this.finishLoading();
            }
        }
    }
};
```

### 12. 系统托盘功能修复 (app.py)
**问题**: 托盘菜单函数缺少参数、全局快捷键不工作  
**修复**: 修改函数签名、重写全局快捷键实现

```python
# 托盘菜单函数签名修复
def show_window(icon, item):
    if self.window:
        self.window.show()

def toggle_window(icon, item):
    if self.window:
        if self.window.visible:
            self.window.hide()
        else:
            self.window.show()

# 全局快捷键重写 - 直接监听按键
def setup_global_hotkey(self):
    self.ctrl_pressed = False
    self.alt_pressed = False
    self.n_pressed = False
    
    def toggle_window():
        if self.window:
            if self.window.visible:
                self.window.hide()
            else:
                self.window.show()
    
    def on_press(key):
        if key_name == 'ctrl' or key_name == 'ctrl_l' or key_name == 'ctrl_r':
            self.ctrl_pressed = True
        elif key_name == 'alt' or key_name == 'alt_l' or key_name == 'alt_r':
            self.alt_pressed = True
        elif key_name == 'n':
            self.n_pressed =
        
        if self.ctrl_pressed and self.alt_pressed and self.n_pressed:
            toggle_window()
    
    self.listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
```

### 13. 窗口关闭事件 (app.py)
**功能**: 关闭窗口时只隐藏,不退出程序

```python
def on_closing():
    """窗口关闭事件处理：只隐藏窗口，不退出程序"""
    self.window.hide()
    return False  # 阻止窗口关闭

self.window.events.closing += on_closing
```

### 14. 详细帮助文档 (app.js)
**功能**: 完整的使用说明

```javascript
function showHelp() {
    const helpContent = `═════════════════════════════════════════════════════════
                          md-editor 使用帮助
═══════════════════════════════════════════════════════

【快捷键】
─────────────────────────────────────────────────────────────────
基础编辑:
  Ctrl+B    加粗选中文本
  Ctrl+I    斜体选中文本
  Ctrl+Z    撤销操作 (最多50步)
  Ctrl+Y    重做操作
  Ctrl+S    保存当前文件
  Ctrl+F    打开搜索面板
  Ctrl+Alt+N  显示/隐藏主窗口 (全局快捷键)
  Tab       增加缩进
  Shift+Tab 减少缩进
  Enter     新建列表项或新段落
  向下箭头   在当前行后创建新段落

【Markdown 快捷语法】
─────────────────────────────────────────────────────────────────
标题格式:
  # 空格 文本  → 一级标题 (H1)
  ## 碰格 文本 → 二级标题 (H2)
  ### 空格 文本 → 三级标题 (H3)

【工具栏功能详解】
─────────────────────────────────────────────────────────────────
【撤销/重做】用于回退和恢复编辑操作
【文本格式化】加粗、斜体、代码、链接、清除格式、颜色设置
【标题】插入 H1/H2/H3 级标题
【列表与待办】无序列表、有序列表、任务列表、引用、添加待办、层级管理
【插入功能】折叠块、标注块、分割线、表格
【工具与视图】目录、搜索、主题切换、帮助

【退出列表/折叠块/表格】
─────────────────────────────────────────────────────────────────
在空列表项中按 Enter:     退出列表模式
在空折叠块内容中按 Enter: 退出折叠块
在表格最后单元格按 Enter: 退出表格
`;
    
    alert(helpContent);
}
```

---

## 打包配置

### PyInstaller 配置 (md-editor.spec)
```python
# -*- mode: python ; coding: utf-8 -*-
# 单目录模式,无窗口,包含所有必要依赖

a = Analysis(
    ['app.py'],
    datas=[('src', 'src')],
    hiddenimports=[
        'pywebview', 'pywebview.platforms.winforms', 'pywebview.platforms.edgechromium',
        'pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
        'pynput', 'pynput.keyboard', 'pynput.mouse',
        'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtNetwork'
    ],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='md-editor',
    debug=False,
    console=False,
    disable_windowed_traceback=False,
    icon='icon.png'
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False,
    upx=True,
    name='md-editor',
)
```

### 打包命令
```bash
python -m PyInstaller md-editor.spec
```

### 输出文件结构
```
dist\md-editor\
├── md-editor.exe           # 主程序
├── icon.png                # 程序图标
└── _internal\              # 依赖文件
    ├── src\                # 前端文件
    │   ├── index.html
    │   ├── style.css
    │   └── app.js
    ├── PyQt5\              # 图形界面
    ├── webview\            # PyWebView
    ├── PIL\                # 图像处理
    └── ...                 # 其他依赖
```

---

## 问题与修复记录

### 问题1: 打开工作区无法工作
**原因**: `js_api=self` 参数未传递给 `webview.create_window()`  
**修复**: 添加 `js_api=self` 参数

### 问题2: 工具栏按钮无法工作
**原因**: 使用 `eval(action)` 无法正确执行函数  
**修复**: 使用动作映射表 + 字符串标识符

### 问题3: 工具栏加载慢
**原因**: 每次都生成完整 SVG 字符串  
**修复**: 使用 SVG `<symbol>` 预定义 + `<use>` 引用

### 问题4: 文件操作函数错误
**原因**: 使用了 Python 的 `os.path.basename`  
**修复**: 使用 JavaScript 方式提取文件名

### 问题5: Enter 键无法退出列表/折叠块
**原因**: 只处理了任务列表,未处理普通列表和折叠块  
**修复**: 添加空元素检测和退出逻辑

### 问题6: 无法在表格后插入新行
**原因**: 缺少表格的 Enter 键处理  
**修复**: 添加表格单元格位置检测和退出逻辑

### 问题7: 点击编辑器无法定位光标
**原因**: contenteditable 默认行为不够友好  
**修复**: 添加 click 和 mousedown 事件处理,双击创建新段落

### 问题8: 工具栏图标太小
**原因**: SVG 图标尺寸设置为 16px  
**修复**: 调整为 20px,增加按钮内边距

### 问题9: 工具栏高度不足
**原因**: 垂直内边距只有 8px  
**修复**: 调整为 24px,左侧增加到 56px

### 问题10: 侧边栏折叠后无法恢复
**原因**: 没有恢复按钮  
**修复**: 添加独立的恢复按钮,折叠后显示

### 问题11: 程序启动时卡顿
**原因**: 组件加载时无反馈  
**修复**: 添加加载屏幕和进度显示

### 问题12: 关闭窗口时程序完全退出
**原因**: `on_closing` 未返回 `False`  
**修复**: 添加 `return False` 阻止窗口关闭

### 问题13: 全局快捷键不工作
**原因**: keyboard.HotKey 实现不稳定  
**修复**: 直接监听按键按下/释放事件

### 问题14: 托盘菜单"显示/隐藏"无效果
**原因**: 菜单项回调函数缺少参数  
**修复**: 修改函数签名为 `(icon, item)`

---

## 快捷键列表

| 快捷键 | 功能 |
|--------|------|
| Ctrl+B | 加粗 |
| Ctrl+I | 斜体 |
| Ctrl+Z | 撤销 |
| Ctrl+Y | 重做 |
| Ctrl+S | 保存 |
| Ctrl+F | 搜索 |
| Ctrl+Alt+N | 显示/隐藏窗口 (全局) |
| Tab | 增加缩进 |
| Shift+Tab | 减少缩进 |
| Enter | 新建列表项/新段落 |
| 向下箭头 | 在当前行后创建新段落 |

---

## Markdown 快捷语法

| 语法 | 效果 |
|------|------|
| # 文本 | 一级标题 (H1) |
| ## 文本 | 二级标题 (H2) |
| ### 文本 | 三级标题 (H3) |
| **文字** | 加粗 |
| *文字* | 斜体 |
| `代码` | 行内代码 |
| [文字](链接) | 超链接 |

---

## 使用说明

### 启动程序
1. 双击 `dist\md-editor\md-editor.exe`
2. 等待加载动画完成
3. 主界面自动显示

### 退出程序
1. 右键点击系统托盘图标
2. 选择"退出"选项
3. 程序完全关闭

### 隐藏/显示窗口
- 点击窗口关闭按钮 → 窗口隐藏,程序在托盘运行
- 按 Ctrl+Alt+N → 切换窗口显示/隐藏
- 或通过托盘菜单控制

---

## 开发注意事项

1. **错误处理**: 所有 API 调用都需要 try-catch
2. **日志记录**: 使用 print 输出调试信息
3. **性能优化**: 避免频繁的 DOM 操作
4. **兼容性**: 支持 Windows 系统
5. **用户体验**: 提供清晰的状态反馈
6. **代码规范**: 遵循 Python 和 JavaScript 最佳实践

---

## 未来扩展

1. **云同步**: 支持云端存储
2. **协作编辑**: 支持多人实时协作
3. **插件系统**: 支持第三方插件
4. **导出功能**: 支持导出为 PDF、HTML 等格式
5. **模板系统**: 提供常用文档模板
6. **快捷键自定义**: 允许用户自定义快捷键

---

## 文件修改历史

| 文件 | 修改内容 | 修改原因 |
|------|---------|---------|
| app.py | 添加 js_api=self 参数 | 修复文件操作 |
| app.py | 修改 os.path.basename 为 JS 方式 | 修复文件名获取 |
| app.py | 添加 on_closing 返回 False | 修复窗口关闭行为 |
| app.py | 修复托盘菜单函数签名 | 修复托盘菜单 |
| app.py | 重写全局快捷键实现 | 修复 Ctrl+Alt+N |
| app.py | 更新程序名称为 md-editor | 用户要求 |
| app.py | 添加 on_loading_complete 方法 | 加载管理 |
| src/index.html | 添加 SVG 符号定义 | 优化图标加载 |
| src/index.html | 添加加载屏幕 HTML | 启动加载动画 |
| src/index.html | 添加侧边栏恢复按钮 | 恢复折叠侧边栏 |
| src/index.html | 添加颜色选择器 HTML | 颜色选择功能 |
| src/style.css | 添加加载屏幕样式 | 加载动画样式 |
| src/style.css | 修改 #app 和 #app.loaded | 加载完成后显示 |
| src/style.css | 调整工具栏高度和内边距 | 工具栏高度调整 |
| src/style.css | 添加恢复按钮样式 | 侧边栏恢复 |
| src/style.css | 调整表格单元格最小高度 | 表格高度对齐 |
| src/app.js | 添加动作映射表 | 修复工具栏按钮 |
| src/app.js | 重写 getIcon 使用 SVG 符号 | 优化图标加载 |
| src/app.js | 修复文件名获取路径 | 兼容 Windows/Unix 路径 |
| src/app.js | 添加列表/折叠块/表格退出逻辑 | Enter 键增强 |
| src/app.js | 添加向下箭头创建新段落 | 光标导航 |
| src/app.js | 添加 Markdown 快捷语法支持 | # 转换标题 |
| src/app.js | 添加颜色选择器实现 | 颜色选择功能 |
| src/app.js | 实现加载管理器 | 加载进度管理 |
| src/app.js | 扩展帮助文档内容 | 详细使用说明 |
| src/app.js | 修复 click 事件处理 | 光标定位 |
| src/app.js | 修复工具栏图标大小 | 图标尺寸调整 |
| src/app.js | 添加双击创建新段落 | 编辑体验优化 |

---

## 总结

经过多次迭代开发和问题修复,md-editor 已成为功能完整、用户体验良好的桌面 Markdown 编辑器。所有核心功能均已实现并经过测试,包括所见即所得编辑、文件管理、系统托盘、全局快捷键、启动加载动画等功能。程序已成功打包为 exe 文件,可直接分发使用。

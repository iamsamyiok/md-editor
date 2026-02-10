@echo off
chcp 65001 >nul
echo ========================================
echo md-editor 打包脚本
echo ========================================
echo.

echo [1/5] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo 清理完成
echo.

echo [2/5] 检查依赖...
python -c "import pywebview, pystray, PIL, pynput" 2>nul
if errorlevel 1 (
    echo 依赖检查失败，正在安装...
    python -m pip install pywebview pystray Pillow pynput
) else (
    echo 依赖检查通过
)
echo.

echo [3/5] 开始打包...
python -m PyInstaller md-editor.spec
if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)
echo 打包完成
echo.

echo [4/5] 复制图标到输出目录...
copy icon.png dist\md-editor\ >nul 2>&1
echo.

echo [5/5] 打包信息：
echo ----------------------------------------
echo 输出目录: dist\md-editor\
echo 主程序: dist\md-editor\md-editor.exe
echo 图标文件: dist\md-editor\icon.png
echo ----------------------------------------
echo.
echo 打包成功！
echo.
pause
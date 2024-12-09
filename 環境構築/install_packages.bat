@echo off
REM Pythonのパスを設定してください。環境変数にある場合は「python」のままでOK
set PYTHON_PATH=python

REM whlファイルが格納されたディレクトリを指定
set WHL_DIR=whl

REM 指定ディレクトリへ移動
cd %WHL_DIR%

REM すべてのwhlファイルを順番にインストール
for %%W in (*.whl) do (
    echo Installing %%W...
    %PYTHON_PATH% -m pip install %%W
    if errorlevel 1 (
        echo Failed to install %%W
        pause
        exit /b 1
    )
)

echo All packages installed successfully!
pause

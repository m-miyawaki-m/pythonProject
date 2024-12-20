@echo off
setlocal

set VENV_DIR=.venv
set PYTHON=python

:: 仮想環境が存在しなければ作成
if not exist %VENV_DIR% (
    echo 仮想環境を作成します...
    %PYTHON% -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo 仮想環境の作成に失敗しました。
        exit /b 1
    )
)

:: 仮想環境を有効化
call %VENV_DIR%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 仮想環境の有効化に失敗しました。
    exit /b 1
)

:: ライブラリチェック
%PYTHON% comparerequirement.py | findstr /c:"インストールに失敗" >nul
if %errorlevel% equ 0 (
    echo ライブラリが不足しています。インストールを開始します...
    %PYTHON% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ライブラリのインストールに失敗しました。
        exit /b 1
    )
)

:: 再チェック
%PYTHON% comparerequirement.py | findstr /c:"インストールに失敗" >nul
if %errorlevel% equ 0 (
    echo ライブラリチェックでエラーが発生しました。
    exit /b 1
)

echo 処理が正常に完了しました。
exit /b 0
@echo off
REM コマンドプロンプトの文字コードをUTF-8に設定
chcp 65001 >nul

REM Pythonのパスを設定
set PYTHON_PATH=python

REM 各スクリプトの実行
%PYTHON_PATH% step1_parse_mybatis_xml.py
if errorlevel 1 exit /b 1

%PYTHON_PATH% step2_parse_java_code.py
if errorlevel 1 exit /b 1

%PYTHON_PATH% step3_generate_crud_mapping.py
if errorlevel 1 exit /b 1

echo 全ての処理が完了しました！
pause

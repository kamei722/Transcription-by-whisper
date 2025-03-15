#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 仮想環境の有効化
if [ -d "whisper_env" ]; then
    echo "仮想環境を有効化しています..."
    source whisper_env/bin/activate
else
    echo "エラー: 仮想環境が見つかりません。"
    echo "以下のコマンドで仮想環境をセットアップしてください:"
    echo "python3 -m venv whisper_env"
    echo "source whisper_env/bin/activate"
    echo "pip install openai-whisper torch ffmpeg-python"
    exit 1
fi

echo "Whisper文字起こしアプリケーションを起動しています..."
python transcribe.py

deactivate
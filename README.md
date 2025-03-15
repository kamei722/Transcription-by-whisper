# Whisper 音声文字起こしツール

OpenAIWhisperによりオーディオファイルをテキストに変換するためのツール


## 必要環境

- Python 3.8以上
- FFmpeg
- 必要なPythonパッケージ:
  - openai-whisper
  - torch
  - tkinter

## インストール方法

```bash
# 仮想環境を作成
python -m venv whisper_env

# 仮想環境を有効化
source whisper_env/bin/activate  # Linuxおよびmacの場合
# または
whisper_env\Scripts\activate  # Windowsの場合

# 必要なパッケージをインストール
pip install openai-whisper torch ffmpeg-python
```

## 使用方法

```bash
# 起動スクリプトを実行
./start.sh  # Linuxおよびmacの場合
# または
start.bat  # Windowsの場合
```

## 注意事項

- 初回実行時にはWhisperモデルがダウンロードされます


# Whisper 音声文字起こしツール

OpenAIWhisperによりオーディオファイルをテキストに変換するためのツール


## 必要環境

- Python 3.8以上
- FFmpeg
- 必要なPythonパッケージ:
  - openai-whisper
  - torch
  - tkinter

## 使用方法

```bash
./start.sh  # Linuxおよびmacの場合

start.bat  # Windowsの場合
```

## 注意事項

- 初回実行時にはWhisperモデルがダウンロードされます


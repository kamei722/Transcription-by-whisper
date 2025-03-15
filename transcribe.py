#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Whisperを使用した音声文字起こしアプリケーション
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import whisper
import torch

class WhisperTranscribeApp:
    def __init__(self, root):
        # メインウィンドウの設定
        self.root = root
        self.root.title("Whisper 音声文字起こしツール")
        self.root.geometry("800x600")
        
        # モデル関連の変数
        self.model_sizes = ["tiny", "base", "small", "medium", "large"]
        self.model = None
        self.model_size = "medium"
        
        # 出力ディレクトリの設定とデフォルトのパス
        self.default_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(self.default_output_dir, exist_ok=True)
        self.output_dir = self.default_output_dir
        
        # 変数の初期化
        self.timestamps_var = tk.BooleanVar(value=False)
        self.text_only_save_var = tk.BooleanVar(value=True)
        self.auto_save_var = tk.BooleanVar(value=True)
        
        # UIコンポーネントの作成
        self.create_widgets()
        
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部フレーム - ファイル選択
        file_frame = ttk.LabelFrame(main_frame, text="音声ファイル選択", padding=5)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ファイル選択部分
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame, text="ファイル:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(file_frame, text="参照...", command=self.browse_file).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # モデル選択フレーム
        model_frame = ttk.LabelFrame(main_frame, text="モデル設定", padding=5)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # モデル選択
        ttk.Label(model_frame, text="モデル:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value=self.model_size)
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, values=self.model_sizes, state="readonly", width=10)
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 出力ディレクトリ設定
        output_frame = ttk.LabelFrame(main_frame, text="出力設定", padding=5)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(output_frame, text="保存先:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value=self.output_dir)
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(output_frame, text="参照...", command=self.browse_output_dir).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 自動保存オプション
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="文字起こし後に自動保存", variable=self.auto_save_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # 言語設定
        ttk.Label(model_frame, text="言語:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lang_var = tk.StringVar(value="ja")
        ttk.Entry(model_frame, textvariable=self.lang_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(model_frame, text="(空欄=自動検出, ja=日本語, en=英語)").grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # タイムスタンプオプション
        self.timestamps_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(model_frame, text="タイムスタンプを表示", variable=self.timestamps_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # 実行ボタン
        self.transcribe_btn = ttk.Button(model_frame, text="文字起こし開始", command=self.start_transcription)
        self.transcribe_btn.grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)
        
        # ステータスフレーム
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ステータス表示
        ttk.Label(status_frame, text="状態:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="準備完了")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # 進捗バー
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.RIGHT, padx=5)
        
        # 結果表示エリア
        result_frame = ttk.LabelFrame(main_frame, text="文字起こし結果", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="結果をコピー", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ファイルに保存", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="クリア", command=self.clear_output).pack(side=tk.LEFT, padx=5)
    
    def browse_file(self):
        """ファイル選択ダイアログを表示"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.m4a *.flac *.ogg"),
                ("すべてのファイル", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def browse_output_dir(self):
        """出力ディレクトリ選択ダイアログを表示"""
        dir_path = filedialog.askdirectory(
            initialdir=self.output_dir
        )
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.output_dir = dir_path
    
    def load_model(self):
        """Whisperモデルをロード"""
        try:
            model_name = self.model_var.get()
            device = "cuda" if self.use_gpu_var.get() and self.gpu_available else "cpu"
            
            # 進捗状況を更新
            self.status_var.set(f"{model_name}モデルをロード中...")
            self.root.update_idletasks()
            
            # モデルをロード
            start_time = time.time()
            model = whisper.load_model(model_name, device=device)
            load_time = time.time() - start_time
            
            self.status_var.set(f"モデルロード完了: {load_time:.1f}秒")
            return model
            
        except Exception as e:
            self.status_var.set(f"エラー: モデルのロードに失敗")
            messagebox.showerror("エラー", f"モデルのロード中にエラーが発生しました:\n{str(e)}")
            return None
    
    def start_transcription(self):
        """文字起こし処理を開始"""
        # ファイルパスの確認
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "音声ファイルを選択してください")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("エラー", "選択されたファイルが見つかりません")
            return
        
        # ボタンを無効化
        self.transcribe_btn.config(state=tk.DISABLED)
        
        # プログレスバーをリセット
        self.progress["value"] = 0
        self.progress.config(mode="indeterminate")
        self.progress.start(10)
        
        # 言語設定を取得
        language = self.lang_var.get().strip()
        if not language:
            language = None
            
        # 非同期で処理を実行
        threading.Thread(
            target=self.perform_transcription,
            args=(file_path, language),
            daemon=True
        ).start()
    
    def perform_transcription(self, file_path, language):
        """バックグラウンドで文字起こしを実行"""
        try:
            # モデルのロード
            if self.model is None:
                self.model = self.load_model()
                if self.model is None:
                    return
            
            # 言語検出フェーズ
            if language is None:
                self.root.after(0, lambda: self.status_var.set("言語を自動検出中..."))
            
            # 文字起こしオプション
            options = {
                "task": "transcribe",
                "verbose": False
            }
            
            # 言語が指定されている場合は設定
            if language:
                options["language"] = language
            
            # 文字起こし実行
            self.root.after(0, lambda: self.status_var.set("文字起こし処理中..."))
            start_time = time.time()
            result = self.model.transcribe(file_path, **options)
            transcribe_time = time.time() - start_time
            
            # 進捗状況の更新
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.config(mode="determinate", value=100))
            
            # 検出された言語
            detected_lang = result.get("language", "不明")
            
            # 結果のフォーマット
            output_text = ""
            
            # 検出言語の表示
            lang_info = f"検出された言語: {detected_lang}\n\n"
            
            if self.timestamps_var.get() and "segments" in result:
                # タイムスタンプ付き出力
                for segment in result["segments"]:
                    start = self.format_time(segment["start"])
                    end = self.format_time(segment["end"])
                    text = segment["text"].strip()
                    output_text += f"[{start} --> {end}] {text}\n\n"
            else:
                # シンプル出力
                output_text = result["text"]
            
            # 結果の表示
            self.root.after(0, lambda: self.update_output(lang_info + output_text))
            self.root.after(0, lambda: self.status_var.set(
                f"完了: {transcribe_time:.1f}秒 - 言語: {detected_lang}")
            )
            
            # 自動保存が有効な場合、結果を保存
            if self.auto_save_var.get():
                self.root.after(100, lambda: self.auto_save_result(file_path, lang_info + output_text))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"エラーが発生しました"))
            self.root.after(0, lambda: messagebox.showerror("エラー", str(e)))
            
        finally:
            # ボタンを再有効化
            self.root.after(0, lambda: self.transcribe_btn.config(state=tk.NORMAL))
    
    def format_time(self, seconds):
        """秒数を [時:分:秒] 形式でフォーマット"""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:.2f}"
    
    def update_output(self, text):
        """出力テキストエリアを更新"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
    
    def copy_to_clipboard(self):
        """結果をクリップボードにコピー"""
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("情報", "テキストをクリップボードにコピーしました")
        else:
            messagebox.showwarning("警告", "コピーするテキストがありません")
    
    def save_to_file(self):
        """結果をファイルに保存（ダイアログ表示）"""
        text = self.output_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "保存するテキストがありません")
            return
        
        # テキストのみ保存が有効な場合は、タイムスタンプを除去
        if self.text_only_save_var.get():
            text = self.extract_text_only(text)
        
        # ファイル名をタイムスタンプから生成
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"transcription_{timestamp}.txt"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.output_dir,
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        
        if file_path:
            self._save_text_to_file(text, file_path)
    
    def auto_save_result(self, audio_file_path, text):
        """文字起こし結果を自動的に保存"""
        if not text:
            return
        
        # 音声ファイル名を取得して出力ファイル名を生成
        audio_filename = os.path.basename(audio_file_path)
        audio_name = os.path.splitext(audio_filename)[0]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"{audio_name}_{timestamp}.txt"
        
        # 保存先のフルパス
        output_path = os.path.join(self.output_dir, output_filename)
        
        # テキストのみ保存が有効な場合は、タイムスタンプを除去
        if self.text_only_save_var.get():
            text = self.extract_text_only(text)
        
        # ファイルを保存
        success = self._save_text_to_file(text, output_path, show_dialog=False)
        if success:
            self.status_var.set(f"完了: ファイルを自動保存しました: {output_filename}")
            
    def extract_text_only(self, text_with_timestamps):
        """タイムスタンプと言語情報を除去し、テキスト部分のみを抽出"""
        lines = text_with_timestamps.split('\n')
        result_lines = []
        
        # タイムスタンプ行と言語情報を除外し、テキスト部分のみを抽出
        for line in lines:
            # 「検出された言語」の行をスキップ
            if "検出された言語" in line:
                continue
                
            # タイムスタンプ形式 [00:00:0.00 --> 00:00:2.00] を含む行から本文だけ抽出
            if line.strip().startswith('[') and '] ' in line:
                # 最初の ']' の後のテキスト部分を抽出
                text_part = line.split('] ', 1)[1].strip()
                if text_part:  # 空でなければ追加
                    result_lines.append(text_part)
            elif line.strip() and not line.strip().startswith('['):
                # タイムスタンプなしの通常の行
                result_lines.append(line.strip())
        
        # 改行なしで結合（1行のテキストにする）
        return ' '.join(result_lines)
    def _save_text_to_file(self, text, file_path, show_dialog=True):
        """テキストをファイルに保存する共通処理"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            if show_dialog:
                messagebox.showinfo("情報", f"ファイルを保存しました:\n{file_path}")
            return True
        except Exception as e:
            if show_dialog:
                messagebox.showerror("エラー", f"ファイルの保存中にエラーが発生しました:\n{str(e)}")
            return False
    
    def clear_output(self):
        """出力テキストエリアをクリア"""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("準備完了")
        self.progress["value"] = 0

def main():
    """メイン関数"""
    root = tk.Tk()
    app = WhisperTranscribeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
"""API呼び出しクライアント"""

import os
import json
import base64
import requests
import logging
import subprocess
import numpy as np
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from pathlib import Path
import tempfile
from PIL import Image
from faster_whisper import WhisperModel
import torch
import gc
import time
import random

logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()

class GeminiClient:
    def __init__(self):
        """Gemini APIクライアントの初期化"""
        # APIキーのロード
        self.api_keys = []
        
        # 複数のキーを環境変数から取得（GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...）
        i = 1
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                self.api_keys.append(key)
                i += 1
            else:
                break
        
        # 単一キーの環境変数を確認
        key = os.getenv('GEMINI_API_KEY')
        if key:
            self.api_keys.append(key)
        
        if not self.api_keys:
            logger.warning("APIキーが設定されていません")
        else:
            logger.info(f"{len(self.api_keys)}個のAPIキーを読み込みました")
        
        # 現在のAPIキーのインデックス
        self._current_key_index = 0
        
        # 初期化時に最初のAPIキーで設定
        self._initialize_client()
    
    def _initialize_client(self):
        """現在のAPIキーでクライアントを初期化"""
        try:
            import google.generativeai as genai
            if self.api_keys:
                genai.configure(api_key=self.api_keys[self._current_key_index])
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info(f"Gemini 1.5 Flashモデルを初期化しました（APIキー {self._current_key_index + 1}を使用）")
            else:
                logger.error("APIキーが設定されていないためクライアントを初期化できません")
        except ImportError:
            logger.error("google-generativeaiライブラリがインストールされていません")
    
    def _rotate_api_key(self):
        """次のAPIキーに切り替え"""
        self._current_key_index = (self._current_key_index + 1) % len(self.api_keys)
        self._initialize_client()
        logger.info(f"APIキーをローテーション: キー{self._current_key_index + 1}に切り替え")
    
    def text_analysis(self, prompt: str) -> str:
        """テキスト分析リクエストを送信（APIキーのローテーションを含む）"""
        if not self.api_keys:
            logger.error("APIキーが設定されていないためリクエストを送信できません")
            return "{}"  # 空のJSONオブジェクト
        
        # JSON形式のレスポンスを明示的に要求
        if "JSON形式で返して" not in prompt:
            prompt = f"{prompt}\n\n必ず以下のJSON形式で結果を返してください。他の文章は一切含めないでください："
        
        # 最大3回まで異なるAPIキーで試行
        for _ in range(min(3, len(self.api_keys))):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    logger.info(f"APIキー{self._current_key_index + 1}でのテキスト分析が成功しました")
                    
                    # JSON形式に整形
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    return text.strip()
                
            except Exception as e:
                logger.warning(f"APIキー{self._current_key_index + 1}でのテキスト分析に失敗: {str(e)}")
                self._rotate_api_key()
                continue
        
        logger.error("全てのAPIキーでのテキスト分析に失敗しました")
        return "{}"  # 空のJSONオブジェクト
    
    def analyze_image(self, image_path: str, prompt: str = None) -> str:
        """画像分析リクエストを送信"""
        if not self.api_keys:
            logger.error("APIキーが設定されていないためリクエストを送信できません")
            return "{}"  # 空のJSONオブジェクト
        
        if not prompt:
            prompt = "この画像について詳しく分析し、JSONで返してください。"
        
        # JSON形式のレスポンスを明示的に要求
        if "JSON形式で返して" not in prompt:
            prompt = f"{prompt}\n\n必ず以下のJSON形式で結果を返してください。他の文章は一切含めないでください："
        
        # 最大3回まで異なるAPIキーで試行
        for _ in range(min(3, len(self.api_keys))):
            try:
                # 画像の読み込み
                import google.generativeai as genai
                from IPython.display import Image as IPImage
                
                image = IPImage(filename=image_path)
                
                response = self.model.generate_content([prompt, image])
                
                if response.text:
                    logger.info(f"APIキー{self._current_key_index + 1}での画像分析が成功しました")
                    
                    # JSON形式に整形
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    return text.strip()
                
            except Exception as e:
                logger.warning(f"APIキー{self._current_key_index + 1}での画像分析に失敗: {str(e)}")
                self._rotate_api_key()
                continue
        
        logger.error("全てのAPIキーでの画像分析に失敗しました")
        return "{}"  # 空のJSONオブジェクト

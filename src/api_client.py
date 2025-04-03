"""API蜻ｼ縺ｳ蜃ｺ縺励け繝ｩ繧､繧｢繝ｳ繝�"""

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

# 迺ｰ蠅�螟画焚縺ｮ繝ｭ繝ｼ繝�
load_dotenv()

class GeminiClient:
    def __init__(self):
        """Gemini API繧ｯ繝ｩ繧､繧｢繝ｳ繝医�ｮ蛻晄悄蛹�"""
        # API繧ｭ繝ｼ縺ｮ繝ｭ繝ｼ繝�
        self.api_keys = []
        
        # 隍�謨ｰ縺ｮ繧ｭ繝ｼ繧堤腸蠅�螟画焚縺九ｉ蜿門ｾ暦ｼ�GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...�ｼ�
        i = 1
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                self.api_keys.append(key)
                i += 1
            else:
                break
        
        # 蜊倅ｸ繧ｭ繝ｼ縺ｮ迺ｰ蠅�螟画焚繧堤｢ｺ隱�
        key = os.getenv('GEMINI_API_KEY')
        if key:
            self.api_keys.append(key)
        
        if not self.api_keys:
            logger.warning("API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺�縺ｾ縺帙ｓ")
        else:
            logger.info(f"{len(self.api_keys)}蛟九�ｮAPI繧ｭ繝ｼ繧定ｪｭ縺ｿ霎ｼ縺ｿ縺ｾ縺励◆")
        
        # 迴ｾ蝨ｨ縺ｮAPI繧ｭ繝ｼ縺ｮ繧､繝ｳ繝�繝�繧ｯ繧ｹ
        self._current_key_index = 0
        
        # 蛻晄悄蛹匁凾縺ｫ譛蛻昴�ｮAPI繧ｭ繝ｼ縺ｧ險ｭ螳�
        self._initialize_client()
    
    def _initialize_client(self):
        """迴ｾ蝨ｨ縺ｮAPI繧ｭ繝ｼ縺ｧ繧ｯ繝ｩ繧､繧｢繝ｳ繝医ｒ蛻晄悄蛹�"""
        try:
            import google.generativeai as genai
            if self.api_keys:
                genai.configure(api_key=self.api_keys[self._current_key_index])
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info(f"Gemini 1.5 Flash繝｢繝�繝ｫ繧貞�晄悄蛹悶＠縺ｾ縺励◆�ｼ�API繧ｭ繝ｼ {self._current_key_index + 1}繧剃ｽｿ逕ｨ�ｼ�")
            else:
                logger.error("API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺�縺ｪ縺�縺溘ａ繧ｯ繝ｩ繧､繧｢繝ｳ繝医ｒ蛻晄悄蛹悶〒縺阪∪縺帙ｓ")
        except ImportError:
            logger.error("google-generativeai繝ｩ繧､繝悶Λ繝ｪ縺後う繝ｳ繧ｹ繝医�ｼ繝ｫ縺輔ｌ縺ｦ縺�縺ｾ縺帙ｓ")
    
    def _rotate_api_key(self):
        """谺｡縺ｮAPI繧ｭ繝ｼ縺ｫ蛻�繧頑崛縺�"""
        self._current_key_index = (self._current_key_index + 1) % len(self.api_keys)
        self._initialize_client()
        logger.info(f"API繧ｭ繝ｼ繧偵Ο繝ｼ繝�繝ｼ繧ｷ繝ｧ繝ｳ: 繧ｭ繝ｼ{self._current_key_index + 1}縺ｫ蛻�繧頑崛縺�")
    
    def text_analysis(self, prompt: str) -> str:
        """繝�繧ｭ繧ｹ繝亥��譫舌Μ繧ｯ繧ｨ繧ｹ繝医ｒ騾∽ｿ｡�ｼ�API繧ｭ繝ｼ縺ｮ繝ｭ繝ｼ繝�繝ｼ繧ｷ繝ｧ繝ｳ繧貞性繧�ｼ�"""
        if not self.api_keys:
            logger.error("API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺�縺ｪ縺�縺溘ａ繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ騾∽ｿ｡縺ｧ縺阪∪縺帙ｓ")
            return "{}"  # 遨ｺ縺ｮJSON繧ｪ繝悶ず繧ｧ繧ｯ繝�
        
        # JSON蠖｢蠑上�ｮ繝ｬ繧ｹ繝昴Φ繧ｹ繧呈�守､ｺ逧�縺ｫ隕∵ｱ�
        if "JSON蠖｢蠑上〒霑斐＠縺ｦ" not in prompt:
            prompt = f"{prompt}\n\n蠢�縺壻ｻ･荳九�ｮJSON蠖｢蠑上〒邨先棡繧定ｿ斐＠縺ｦ縺上□縺輔＞縲ゆｻ悶�ｮ譁�遶縺ｯ荳蛻�蜷ｫ繧√↑縺�縺ｧ縺上□縺輔＞�ｼ�"
        
        # 譛螟ｧ3蝗槭∪縺ｧ逡ｰ縺ｪ繧帰PI繧ｭ繝ｼ縺ｧ隧ｦ陦�
        for _ in range(min(3, len(self.api_keys))):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    logger.info(f"API繧ｭ繝ｼ{self._current_key_index + 1}縺ｧ縺ｮ繝�繧ｭ繧ｹ繝亥��譫舌′謌仙粥縺励∪縺励◆")
                    
                    # JSON蠖｢蠑上↓謨ｴ蠖｢
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    return text.strip()
                
            except Exception as e:
                logger.warning(f"API繧ｭ繝ｼ{self._current_key_index + 1}縺ｧ縺ｮ繝�繧ｭ繧ｹ繝亥��譫舌↓螟ｱ謨�: {str(e)}")
                self._rotate_api_key()
                continue
        
        logger.error("蜈ｨ縺ｦ縺ｮAPI繧ｭ繝ｼ縺ｧ縺ｮ繝�繧ｭ繧ｹ繝亥��譫舌↓螟ｱ謨励＠縺ｾ縺励◆")
        return "{}"  # 遨ｺ縺ｮJSON繧ｪ繝悶ず繧ｧ繧ｯ繝�
    
    def analyze_image(self, image_path: str, prompt: str = None) -> str:
        """逕ｻ蜒丞��譫舌Μ繧ｯ繧ｨ繧ｹ繝医ｒ騾∽ｿ｡"""
        if not self.api_keys:
            logger.error("API繧ｭ繝ｼ縺瑚ｨｭ螳壹＆繧後※縺�縺ｪ縺�縺溘ａ繝ｪ繧ｯ繧ｨ繧ｹ繝医ｒ騾∽ｿ｡縺ｧ縺阪∪縺帙ｓ")
            return "{}"  # 遨ｺ縺ｮJSON繧ｪ繝悶ず繧ｧ繧ｯ繝�
        
        if not prompt:
            prompt = "縺薙�ｮ逕ｻ蜒上↓縺､縺�縺ｦ隧ｳ縺励￥蛻�譫舌＠縲゛SON縺ｧ霑斐＠縺ｦ縺上□縺輔＞縲�"
        
        # JSON蠖｢蠑上�ｮ繝ｬ繧ｹ繝昴Φ繧ｹ繧呈�守､ｺ逧�縺ｫ隕∵ｱ�
        if "JSON蠖｢蠑上〒霑斐＠縺ｦ" not in prompt:
            prompt = f"{prompt}\n\n蠢�縺壻ｻ･荳九�ｮJSON蠖｢蠑上〒邨先棡繧定ｿ斐＠縺ｦ縺上□縺輔＞縲ゆｻ悶�ｮ譁�遶縺ｯ荳蛻�蜷ｫ繧√↑縺�縺ｧ縺上□縺輔＞�ｼ�"
        
        # 譛螟ｧ3蝗槭∪縺ｧ逡ｰ縺ｪ繧帰PI繧ｭ繝ｼ縺ｧ隧ｦ陦�
        for _ in range(min(3, len(self.api_keys))):
            try:
                # 逕ｻ蜒上�ｮ隱ｭ縺ｿ霎ｼ縺ｿ
                import google.generativeai as genai
                from IPython.display import Image as IPImage
                
                image = IPImage(filename=image_path)
                
                response = self.model.generate_content([prompt, image])
                
                if response.text:
                    logger.info(f"API繧ｭ繝ｼ{self._current_key_index + 1}縺ｧ縺ｮ逕ｻ蜒丞��譫舌′謌仙粥縺励∪縺励◆")
                    
                    # JSON蠖｢蠑上↓謨ｴ蠖｢
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    return text.strip()
                
            except Exception as e:
                logger.warning(f"API繧ｭ繝ｼ{self._current_key_index + 1}縺ｧ縺ｮ逕ｻ蜒丞��譫舌↓螟ｱ謨�: {str(e)}")
                self._rotate_api_key()
                continue
        
        logger.error("蜈ｨ縺ｦ縺ｮAPI繧ｭ繝ｼ縺ｧ縺ｮ逕ｻ蜒丞��譫舌↓螟ｱ謨励＠縺ｾ縺励◆")
        return "{}"  # 遨ｺ縺ｮJSON繧ｪ繝悶ず繧ｧ繧ｯ繝�

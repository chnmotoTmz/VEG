"""AIチップデコレータ"""

import os
import inspect
import ast
from typing import Callable, Any, Dict
from functools import wraps

def EvolveChip(func: Callable) -> Callable:
    """AIチップデコレータ

    開発時にAI支援機能を付与し、リリース時に除去するための
    デコレータ
    
    Args:
        func: デコレートする関数
        
    Returns:
        ラップされた関数
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """ラッパー関数
        
        Args:
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            関数の実行結果
        """
        is_development = os.getenv('DEVELOPMENT_MODE', '1') == '1'
        
        if not is_development:
            # リリースモード：通常の関数として実行
            return func(*args, **kwargs)
            
        # 開発モード：AI支援機能を有効化
        # 関数のソースコードを取得
        source = inspect.getsource(func)
        
        # 関数の引数情報を取得
        sig = inspect.signature(func)
        
        # AI支援情報を生成
        ai_info = {
            'function_name': func.__name__,
            'module_name': func.__module__,
            'args': {k: v for k, v in zip(sig.parameters.keys(), args) if k != 'self'},
            'source_code': source
        }
        
        # AI支援情報をログに出力
        _log_ai_info(ai_info)
        
        # 関数を実行
        return func(*args, **kwargs)
        
    return wrapper

def _log_ai_info(ai_info: Dict[str, Any]) -> None:
    """AI支援情報をログに出力

    Args:
        ai_info: AI支援情報
    """
    # ログディレクトリを作成
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # ログファイルに出力
    log_file = os.path.join(log_dir, 'ai_support.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n=== AI Support Info ===\n")
        f.write(f"Function: {ai_info['function_name']}\n")
        f.write(f"Module: {ai_info['module_name']}\n")
        f.write(f"Arguments: {ai_info['args']}\n")
        f.write(f"Source Code:\n{ai_info['source_code']}\n")
        f.write("=====================\n") 
"""動画編集AIエージェントのCLIインターフェース"""

import argparse
import sys
import json
import os
from typing import Optional, List

from .main import VideoEditAgent
from .content_crawler import ContentCrawler
from .scene_selector import SceneSelector

def main():
    """メインCLIエントリポイント"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
        
    return args.func(args)

def create_parser() -> argparse.ArgumentParser:
    """CLIパーサーを作成"""
    parser = argparse.ArgumentParser(
        description='動画編集AIエージェント - 自動シーン選別とEDL/SRT生成'
    )
    subparsers = parser.add_subparsers(title='サブコマンド')
    
    # メインフローコマンド
    main_parser = subparsers.add_parser(
        'run',
        help='フル処理フローを実行'
    )
    main_parser.add_argument(
        '-c', '--config',
        required=True,
        help='設定ファイルのパス'
    )
    main_parser.set_defaults(func=run_main_flow_command)
    
    # コンテンツ探索コマンド
    crawl_parser = subparsers.add_parser(
        'crawl',
        help='動画コンテンツを探索'
    )
    crawl_parser.add_argument(
        'input_dir',
        help='入力ディレクトリパス'
    )
    crawl_parser.add_argument(
        '-o', '--output',
        help='出力JSONファイルパス'
    )
    crawl_parser.set_defaults(func=run_crawl_command)
    
    # シーン選別コマンド
    select_parser = subparsers.add_parser(
        'select',
        help='シナリオに基づいてシーンを選別'
    )
    select_parser.add_argument(
        'content_file',
        help='コンテンツJSONファイルパス'
    )
    select_parser.add_argument(
        'scenario_file',
        help='シナリオJSONファイルパス'
    )
    select_parser.add_argument(
        '-o', '--output',
        help='出力JSONファイルパス'
    )
    select_parser.set_defaults(func=run_select_command)
    
    return parser

def run_main_flow(config_path: str) -> int:
    """メインフローを実行する関数"""
    try:
        # 設定を読み込む
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        
        # エージェントを作成して実行
        agent = VideoEditAgent(config)
        agent.process()
        
        return 0
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        return 1

def run_main_flow_command(args) -> int:
    """メインフローを実行"""
    return run_main_flow(args.config)

def run_crawl_command(args) -> int:
    """コンテンツ探索を実行"""
    try:
        crawler = ContentCrawler()
        contents = crawler.crawl(args.input_dir)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8-sig') as f:
                json.dump(contents, f, ensure_ascii=False, indent=2)
            print(f"コンテンツデータを {args.output} に保存しました")
        else:
            print(json.dumps(contents, ensure_ascii=False, indent=2))
            
        return 0
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        return 1

def run_select_command(args) -> int:
    """シーン選別を実行"""
    try:
        with open(args.content_file, 'r', encoding='utf-8-sig') as f:
            contents = json.load(f)
        with open(args.scenario_file, 'r', encoding='utf-8-sig') as f:
            scenario = json.load(f)
        
        # API クライアントを初期化
        from .api_client import GeminiClient
        api_client = GeminiClient()
        
        # セレクターを初期化
        selector = SceneSelector(api_client=api_client)
        selected = selector.select(contents, scenario)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8-sig') as f:
                json.dump(selected, f, ensure_ascii=False, indent=2)
            print(f"選別結果を {args.output} に保存しました")
        else:
            print(json.dumps(selected, ensure_ascii=False, indent=2))
            
        return 0
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

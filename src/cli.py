"""CLI繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ"""

import argparse
import json
import os
from typing import Dict, Any
from .main import VideoEditAgent
from .gui import main as gui_main

def load_config(config_path: str) -> Dict[str, Any]:
    """險ｭ螳壹ヵ繧｡繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧"""
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='繝薙ョ繧ｪ邱ｨ髮�謾ｯ謠ｴ繝�繝ｼ繝ｫ')
    
    # 繧ｳ繝槭Φ繝峨�ｮ繧ｵ繝悶ヱ繝ｼ繧ｵ繝ｼ繧剃ｽ懈��
    subparsers = parser.add_subparsers(dest='command', help='螳溯｡後☆繧九さ繝槭Φ繝�')
    
    # GUI繝｢繝ｼ繝�
    gui_parser = subparsers.add_parser('gui', help='GUI繝｢繝ｼ繝峨〒襍ｷ蜍�')
    
    # analyze 繧ｳ繝槭Φ繝�
    analyze_parser = subparsers.add_parser('analyze', help='繧ｳ繝ｳ繝�繝ｳ繝�繧貞��譫舌＠縺ｦ繧ｳ繝ｳ繧ｻ繝励ヨ縺ｨ繧ｷ繝翫Μ繧ｪ繝�繝ｳ繝励Ξ繝ｼ繝医ｒ逕滓��')
    analyze_parser.add_argument('-c', '--config', required=True, help='險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ')
    
    # select 繧ｳ繝槭Φ繝�
    select_parser = subparsers.add_parser('select', help='繧ｷ繝翫Μ繧ｪ縺ｫ蝓ｺ縺･縺�縺ｦ繧ｷ繝ｼ繝ｳ繧帝∈謚�')
    select_parser.add_argument('-c', '--config', required=True, help='險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ')
    
    # generate 繧ｳ繝槭Φ繝�
    generate_parser = subparsers.add_parser('generate', help='EDL縺ｨSRT繝輔ぃ繧､繝ｫ繧堤函謌�')
    generate_parser.add_argument('-c', '--config', required=True, help='險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ')
    
    # run 繧ｳ繝槭Φ繝会ｼ亥�ｨ繝輔ぉ繝ｼ繧ｺ繧貞ｮ溯｡鯉ｼ�
    run_parser = subparsers.add_parser('run', help='縺吶∋縺ｦ縺ｮ繝輔ぉ繝ｼ繧ｺ繧帝�逡ｪ縺ｫ螳溯｡�')
    run_parser.add_argument('-c', '--config', required=True, help='險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'gui':
        gui_main()
        return
    
    try:
        # 險ｭ螳壹ヵ繧｡繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧
        config = load_config(args.config)
        agent = VideoEditAgent(config)
        
        if args.command == 'analyze':
            agent.analyze_contents()
            
        elif args.command == 'select':
            contents = agent.analyze_contents()
            agent.select_scenes(contents)
            
        elif args.command == 'generate':
            contents = agent.analyze_contents()
            selected_scenes, scenario = agent.select_scenes(contents)
            agent.generate_outputs(selected_scenes, scenario)
            
        elif args.command == 'run':
            agent.process()
            
    except Exception as e:
        print(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

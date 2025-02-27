#!/usr/bin/env python3
import os
import argparse
from utils import SharedConsole
from plugins.plugin_manager import PluginManager

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, message)

console = SharedConsole.get_console()
plugin_manager = PluginManager()

def create_argument_parser():
    """创建并配置命令行参数解析器"""
    parser = CustomArgumentParser(description='命令行助手工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 让每个插件配置自己的命令行参数
    for name, plugin in plugin_manager.get_all_plugins().items():
        plugin_parser = subparsers.add_parser(name, help=plugin.get_description())
        plugin.configure(plugin_parser)
    
    return parser

def show_help():
    console.print("[red]命令格式错误[/red]")
    help_plugin = plugin_manager.get_plugin('help')
    help_plugin.execute(None)

def main():
    try:
        # 先加载插件
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        plugin_manager.load_plugins(plugins_dir)
        
        # 然后创建解析器并解析参数
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # 执行对应插件的功能
        plugin = plugin_manager.get_plugin(args.command)
        plugin.execute(args)
            
    except argparse.ArgumentError:
        show_help()
    except SystemExit:
        show_help()

if __name__ == "__main__":
    main()
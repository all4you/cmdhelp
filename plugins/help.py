import os
from typing import List, Tuple
from plugins.base import Plugin
from argparse import ArgumentParser
from rich.panel import Panel
from utils import SharedConsole
from plugins.plugin_manager import PluginManager

class HelpPlugin(Plugin):
    def __init__(self):
        self.console = SharedConsole.get_console()
        self.plugin_manager = PluginManager()

    def get_name(self) -> str:
        return "help"
    
    def get_description(self) -> str:
        return "显示帮助信息"

    def get_help_commands(self) -> List[Tuple[str, str]]:
        return [("coma help", "显示当前工具支持的指令和帮助信息")]
    
    def configure(self, parser: ArgumentParser):
        pass
    
    def execute(self, args):
        # 每次执行时都重新加载插件
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
        self.plugin_manager.load_plugins(plugins_dir)
        
        commands = []
        for plugin in self.plugin_manager.get_all_plugins().values():
            commands.extend(plugin.get_help_commands())
        
        # 自定义排序规则：help在最前，guide在最后，其他按名称排序
        def sort_key(cmd_tuple):
            cmd = cmd_tuple[0]
            if cmd.startswith("coma help"):
                return (0, cmd)
            elif cmd.startswith("coma guide"):
                return (2, cmd)
            return (1, cmd)
        
        commands.sort(key=sort_key)
        
        help_text = ""
        for cmd, desc in commands:
            help_text += f"{cmd} : {desc}\n"
        
        self.console.print(Panel(
            help_text.strip(),
            title="可用命令",
            border_style="blue",
            width=120,
            expand=False
        ))
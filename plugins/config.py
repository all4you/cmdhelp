import os
import json
import requests
from plugins.base import Plugin
from typing import List, Tuple
from argparse import ArgumentParser
from rich.prompt import Prompt
from rich.panel import Panel
from utils import SharedConsole, CONFIG_DIR, CONFIG_FILE

class ConfigPlugin(Plugin):
    def __init__(self):
        self.console = SharedConsole.get_console()

    def get_name(self) -> str:
        return "config"
    
    def get_description(self) -> str:
        return "配置信息管理"
    
    def get_help_commands(self) -> List[Tuple[str, str]]:
        return [
            ("coma config set", "设置ollama服务器地址和模型名称"),
            ("coma config get", "获取当前设置的ollama配置信息")
        ]
    
    def configure(self, parser: ArgumentParser):
        parser.add_argument('action', choices=['set', 'get'], help='配置操作类型')
    
    def execute(self, args):
        if args.action == 'set':
            self._config_set()
        elif args.action == 'get':
            self._config_get(show_config=True)
    
    def _ensure_config_dir(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
    
    def _validate_host(self, host):
        if not host.startswith(('http://', 'https://')):
            return False
        try:
            response = requests.get(f"{host}/api/version")
            return response.status_code == 200
        except:
            return False
    
    def _validate_model(self, host, model_name):
        try:
            response = requests.get(f"{host}/api/tags")
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                return model_name in models
            return False
        except:
            return False
    
    def _config_set(self):
        self._ensure_config_dir()
        
        host = Prompt.ask("请输入ollama的host地址", default="http://localhost:11434")
        while not self._validate_host(host):
            self.console.print("[red]无法连接到ollama服务，请检查host地址是否正确[/red]")
            host = Prompt.ask("请重新输入ollama的host地址", default="http://localhost:11434")
        
        model_name = Prompt.ask("请输入要使用的模型名称")
        while not self._validate_model(host, model_name):
            self.console.print(f"[red]模型 {model_name} 不存在，请检查模型名称是否正确[/red]")
            model_name = Prompt.ask("请重新输入要使用的模型名称")
        
        config = {
            'ollama_host': host,
            'model_name': model_name
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.console.print("[green]配置已保存成功[/green]")
        self._config_get(show_config=True)
    
    def _config_get(self, show_config=False):
        if not os.path.exists(CONFIG_FILE):
            self.console.print("[yellow]配置文件不存在，请先运行 'coma config set' 进行配置[/yellow]")
            return None
        
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        if show_config:
            self.console.print(Panel(
                f"Host: {config['ollama_host']}\nModel: {config['model_name']}",
                title="当前配置",
                border_style="blue",
                width=100,
                expand=False
            ))
        return config
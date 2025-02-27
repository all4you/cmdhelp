import os
import time
import json
import requests
from rich.console import Console

CONFIG_DIR = os.path.expanduser('~/.coma')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'coma.json')

class SharedConsole:
    _instance = None
    
    @classmethod
    def get_console(cls):
        if cls._instance is None:
            cls._instance = Console(color_system="auto", highlight=False)
        return cls._instance

class OllamaAPI:
    @staticmethod
    def generate(prompt: str, debug: bool = False) -> tuple[str, float]:
        """调用 Ollama API 生成响应
        
        Args:
            prompt: 提示词
            debug: 是否开启调试模式
        
        Returns:
            tuple: (响应文本, 使用模型, 耗时)
        """
        console = SharedConsole.get_console()
        start_time = time.time()
        # 获取配置
        if not os.path.exists(CONFIG_FILE):
            console.print("[yellow]配置文件不存在，请先运行 'coma config set' 进行配置[/yellow]")
            return None, "", time.time() - start_time
        
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        host = config['ollama_host']
        model = config['model_name']
        
        console.print(f"[blue]模型正在思考中，请稍候...[/blue]")
        try:
            response = requests.post(
                f"{host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json().get('response')
                if debug:
                    console.print("[yellow]模型原始响应：[/yellow]")
                    console.print(result)
                return result, model, elapsed_time
            else:
                console.print(f"[red]调用模型失败：{response.text}[/red]")
                return None, model, elapsed_time
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            console.print(f"[red]调用模型发生异常：{str(e)}[/red]")
            return None, model, elapsed_time
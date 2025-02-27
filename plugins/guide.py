import os
import json
import requests
from argparse import ArgumentParser
from typing import List, Tuple
from plugins.base import Plugin
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from utils import SharedConsole, OllamaAPI, Utils

class GuidePlugin(Plugin):
    def __init__(self):
        self.console = SharedConsole.get_console()

    def get_name(self) -> str:
        return "guide"
    
    def get_description(self) -> str:
        return "查询如何使用命令行解决特定任务"
    
    def get_help_commands(self) -> List[Tuple[str, str]]:
        return [
            ("coma guide [-d] <question>", "使用命令行解决特定任务，其中-d为可选的调试参数，<question>是你要查询的问题")
        ]
    
    def configure(self, parser: ArgumentParser):
        parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
        parser.add_argument('question', nargs='+', help='你要查询的问题')
    
    def execute(self, args):
        question = ' '.join(args.question)
        self._guide(question, args.debug)
    
    def _print_command_step(self, line, step, total_steps):
        """打印单个命令步骤"""
        cmd_part = line[line.find('<')+1:line.find('>')]
        desc_part = line[line.rfind('<')+1:line.rfind('>')]
        
        if total_steps > 1:
            self.console.print(f"[green]第{step}步：{desc_part}[/green]")
        else:
            self.console.print(f"[green]{desc_part}[/green]")
        
        escaped_cmd = (cmd_part
            .replace('[', '\\[')
            .replace(']', '\\]')
            .replace('<', '\\<')
            .replace('>', '\\>')
            .replace('{', '\\{')
            .replace('}', '\\}')
        )
        command_info = Panel.fit(
            f"{escaped_cmd}",
            border_style="green"
        )
        self.console.print(command_info)

    def _guide(self, question: str, debug: bool):
        """处理用户的命令行查询"""
        
        prompt = f"""请帮我分析如何使用命令行解决以下问题：{question}
            请严格按照以下格式返回结果：
            cmd=<命令>,desc=<描述>

            格式说明：
            1. 每行必须以cmd=<开头，以>,desc=<继续，最后以>结尾
            2. 每个命令占一行
            3. 不要添加任何额外的文字或说明
            4. 根据任务复杂度可以返回多行命令

            示例格式：
            cmd=<ls -l>,desc=<以详细格式列出当前目录的文件>
            cmd=<cd /path/to/dir>,desc=<切换到指定目录>

            请按照上述格式返回命令：
            """
        
        response, model, elapsed_time = OllamaAPI.generate(prompt, debug)
        if response:
            response_text = response.replace('```', '')
            lines = [line.strip() for line in response_text.strip().split('\n') if line.strip()]
            
            valid_lines = []
            for line in lines:
                cmd_start = line.find('cmd=<')
                if cmd_start != -1 and line.count('>,desc=<') == 1:
                    valid_lines.append(line[cmd_start:])
            
            found_command = False
            step = 1
            total_steps = len(valid_lines)
            
            for line in valid_lines:
                found_command = True
                self._print_command_step(line, step, total_steps)
                step += 1
            
            if not found_command:
                self.console.print("[red]未能从模型响应中解析出有效的命令格式[/red]")
            Utils.print_execution_info(model, elapsed_time)
        
        else:
            self.console.print("[red]获取guide结果失败[/red]")
            Utils.print_execution_info(model, elapsed_time)
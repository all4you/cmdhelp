import os
import subprocess
from typing import List, Tuple
from plugins.base import Plugin
from argparse import ArgumentParser
from utils import SharedConsole, OllamaAPI

class GitPlugin(Plugin):
    def __init__(self):
        self.console = SharedConsole.get_console()
    
    def get_name(self) -> str:
        return "git"
    
    def get_description(self) -> str:
        return "Git 助手"
    
    def get_help_commands(self) -> List[Tuple[str, str]]:
        return [
            ("coma git exp", "解释最近的 Git 错误信息"),
            ("coma git cm", "根据当前更改生成 commit message")
        ]
    
    def configure(self, parser: ArgumentParser):
        parser.add_argument('action', choices=['exp', 'cm'], help='Git 操作类型')
        parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
    
    def execute(self, args):
        if args.action == 'exp':
            self._explain_error(args.debug)
        elif args.action == 'cm':
            self._generate_commit_message(args.debug)
    
    def _get_last_git_error(self) -> str:
        """获取最近的 Git 错误信息"""
        try:
            # 从 zsh/bash 历史记录中获取最近的 git 命令及其输出
            cmd = "fc -ln -1 | grep 'git'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                # 重新执行该命令以获取错误信息
                error_cmd = result.stdout.strip()
                error_result = subprocess.run(error_cmd, shell=True, capture_output=True, text=True)
                if error_result.stderr:
                    return f"命令：{error_cmd}\n错误：{error_result.stderr}"
            return None
        except Exception as e:
            self.console.print(f"[red]获取 Git 错误信息失败：{str(e)}[/red]")
            return None
    
    def _get_git_status(self) -> str:
        """获取 Git 状态信息"""
        try:
            # 获取未提交的变更
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout:
                changes = result.stdout.strip()
                # 获取每个变更文件的 diff
                detailed_changes = ""
                for line in changes.split('\n'):
                    status, file = line[:2], line[3:]
                    if status.strip() in ['M', 'A', 'D']:
                        if status.strip() != 'D':  # 如果文件没有被删除
                            diff = subprocess.run(['git', 'diff', '--', file], capture_output=True, text=True)
                            detailed_changes += f"\n文件：{file}\n{diff.stdout}"
                return detailed_changes
            return None
        except Exception as e:
            self.console.print(f"[red]获取 Git 状态失败：{str(e)}[/red]")
            return None
    
    def _explain_error(self, debug: bool):
        """解释 Git 错误信息"""
        error = self._get_last_git_error()
        if not error:
            self.console.print("[yellow]未找到最近的 Git 错误信息[/yellow]")
            return
        
        prompt = f"""请解释以下 Git 错误信息，并给出解决方案：
                    {error}
                    请按照以下格式回答：
                    1. 错误原因：简要说明错误的原因
                    2. 解决方案：提供具体的解决步骤
                    3. 预防建议：如何避免这个错误再次发生
                    """
        
        response, elapsed_time = OllamaAPI.generate(prompt, debug)
        if response:
            self.console.print("\n[green]分析结果：[/green]")
            self.console.print(response)
            self.console.print(f"\n[blue]分析耗时：{elapsed_time:.2f}秒[/blue]")
    
    def _generate_commit_message(self, debug: bool):
        """生成 commit message"""
        changes = self._get_git_status()
        if not changes:
            self.console.print("[yellow]未发现任何待提交的更改[/yellow]")
            return
        
        prompt = f"""请根据以下 Git 变更信息，生成一个符合规范的 commit message：
                    {changes}
                    请按照以下格式生成 commit message：
                    1. type: 提交类型（feat/fix/docs/style/refactor/test/chore）
                    2. scope: 影响范围（可选）
                    3. subject: 简短描述
                    4. body: 详细描述（可选）
                    5. footer: 关联 issue（可选）

                    示例格式：
                    feat(user): add login function

                    - Implement user login API
                    - Add login form validation
                    - Add session management

                    Closes #123
                    """
        
        response, elapsed_time = OllamaAPI.generate(prompt, debug)
        if response:
            self.console.print("\n[green]建议的 commit message：[/green]")
            self.console.print(response)
            self.console.print(f"\n[blue]生成耗时：{elapsed_time:.2f}秒[/blue]")
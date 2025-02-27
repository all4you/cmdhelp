from abc import ABC, abstractmethod
from typing import List, Tuple
from argparse import ArgumentParser

class Plugin(ABC):
    """插件基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取插件描述"""
        pass
    
    @abstractmethod
    def get_help_commands(self) -> List[Tuple[str, str]]:
        """返回插件支持的命令列表，格式为 [(命令, 描述), ...]"""
        pass
    
    @abstractmethod
    def configure(self, parser: ArgumentParser):
        """配置命令行参数"""
        pass
    
    @abstractmethod
    def execute(self, args):
        """执行插件功能"""
        pass
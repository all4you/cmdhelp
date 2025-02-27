import os
import importlib
from typing import Dict
from plugins.base import Plugin

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    def load_plugins(self, plugins_dir: str):
        """加载插件目录下的所有插件"""
        for filename in os.listdir(plugins_dir):
            if filename.startswith('__') or (not filename.endswith('.py')):
                continue
            module_name = filename[:-3]
            module = importlib.import_module(f'plugins.{module_name}')
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                    plugin = attr()
                    self.plugins[plugin.get_name()] = plugin
    
    def get_plugin(self, name: str) -> Plugin:
        """获取指定名称的插件"""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """获取所有已加载的插件"""
        return self.plugins
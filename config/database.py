import os
import yaml
from typing import Dict

class Database:
    def __init__(self):
        self.env = os.environ.get('ENV', 'database')
        self._config = self._load_config()
        
    def _load_config(self) -> Dict:
        # 加载YAML配置文件
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 获取对应环境的配置
        env_config = config[self.env]
        
        # 环境变量优先级高于配置文件
        db_config = env_config['mysql']
        
        # 环境变量覆盖
        env_mapping = {
            'MYSQL_HOST': 'host',
            'MYSQL_USER': 'user',
            'MYSQL_PASSWORD': 'password',
            'MYSQL_DB': 'db',
            'MYSQL_CHARSET': 'charset',
            'AUTOCOMMIT': 'autocommit'
        }
        
        # 如果存在环境变量，则覆盖YAML中的配置
        for env_var, config_key in env_mapping.items():
            if os.environ.get(env_var):
                db_config[config_key] = os.environ.get(env_var)
                
        return db_config
    
    @property
    def db_config(self) -> Dict:
        return self._config

# 使用示例
DB_CONFIG = Database().db_config
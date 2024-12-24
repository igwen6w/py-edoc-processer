# -*- coding: utf-8 -*-
import os
import yaml
from typing import Dict, List, Any

class Settings:
    def __init__(self):
        self.env = os.environ.get('ENV', 'settings')
        self._config = self._load_config()
        self._init_settings()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = os.environ.get('CONFIG_PATH', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)[self.env]

    def _init_settings(self):
        """初始化所有设置"""
        # 文件路径配置
        self.FILE_PATH_PREFIX = os.environ.get(
            'FILE_PATH_PREFIX',
            self._config['paths']['file_prefix']
        )
        
        self.TEMP_DIR_PREFIX = os.environ.get(
            'TEMP_DIR_PREFIX',
            self._config['paths']['temp_dir']
        )
        
        self.DOCUMENT_PAGE_PATH = os.environ.get(
            'DOCUMENT_PAGE_PATH',
            self._config['paths']['document_page']
        )

        # 任务配置
        self.MAX_RETRY_COUNT = int(os.environ.get(
            'MAX_RETRY_COUNT',
            self._config['task']['max_retry']
        ))
        
        self.MAX_WORKERS = int(os.environ.get(
            'MAX_WORKERS',
            self._config['task']['max_workers']
        ))

        # 支持的格式配置
        self.SUPPORTED_IMAGE_FORMATS = tuple(os.environ.get(
            'SUPPORTED_IMAGE_FORMATS',
            self._config['formats']['supported_images']
        ))

    def get_document_page_path(self, document_id: int, page_number: int, title: str) -> str:
        """获取文档页面路径"""
        return self.DOCUMENT_PAGE_PATH.format(
            document_id=document_id,
            page_number=page_number,
            title=title
        )

# 创建全局设置实例
settings = Settings()

# 导出所有设置变量，保持与原代码兼容性
FILE_PATH_PREFIX = settings.FILE_PATH_PREFIX
MAX_RETRY_COUNT = settings.MAX_RETRY_COUNT
MAX_WORKERS = settings.MAX_WORKERS
TEMP_DIR_PREFIX = settings.TEMP_DIR_PREFIX
DOCUMENT_PAGE_PATH = settings.DOCUMENT_PAGE_PATH
SUPPORTED_IMAGE_FORMATS = settings.SUPPORTED_IMAGE_FORMATS
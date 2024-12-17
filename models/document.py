# -*- coding: utf-8 -*-
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DocumentFile:
    """文档文件模型"""
    id: int
    document_id: int
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    created_at: datetime
    updated_at: datetime

@dataclass
class DocumentTask:
    """文档处理任务模型"""
    id: int
    document_id: int
    document_file_id: int
    document_directory_id: int
    status: str
    retry_count: int
    details: Optional[str]
    failure_reason: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @property
    def is_retryable(self) -> bool:
        return self.retry_count < 3

    @property
    def is_processing(self) -> bool:
        return self.status == '处理中'

    @property
    def is_completed(self) -> bool:
        return self.status == '已完成'

    @property
    def is_failed(self) -> bool:
        return self.status == '已失败'

@dataclass
class DocumentDirectory:
    """文档目录模型"""
    id: int
    document_id: int
    parent_directory_id: Optional[int]
    name: str
    number: str
    start_page: int
    created_at: datetime
    updated_at: datetime
    children: List['DocumentDirectory'] = None
    pages: List['DocumentPage'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.pages is None:
            self.pages = []

    def add_child(self, child: 'DocumentDirectory'):
        """添加子目录"""
        if self.children is None:
            self.children = []
        self.children.append(child)

    def add_page(self, page: 'DocumentPage'):
        """添加页面"""
        if self.pages is None:
            self.pages = []
        self.pages.append(page)

    def get_page_count(self) -> int:
        """获取目录下的总页数"""
        total = len(self.pages)
        for child in self.children:
            total += child.get_page_count()
        return total

@dataclass
class DocumentPage:
    """文档页面模型"""
    id: int
    document_id: int
    directory_id: Optional[int]
    page_number: int
    image_path: str
    title: str
    content: str

    @property
    def file_name(self) -> str:
        """获取页面文件名"""
        return self.image_path.split('/')[-1]

    @property
    def directory_path(self) -> str:
        """获取页面所在目录路径"""
        return '/'.join(self.image_path.split('/')[:-1])
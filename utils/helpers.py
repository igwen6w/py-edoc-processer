# -*- coding: utf-8 -*-
import os
import re
from utils.logger import logger

def parse_directory_name(dir_name):
    """解析目录名称，提起始页/名称/序列号"""
    dir_parts = dir_name.split('-')
    number = '-'
    start_page = 1
    name = dir_name
    
    if len(dir_parts) >= 3:
        try:
            start_page = int(dir_parts[0].strip())
            number = dir_parts[-1].strip()
            name = '-'.join(dir_parts[1:-1]).strip()
        except ValueError:
            logger.warning(f"Invalid directory format: {dir_name}, using defaults")
    elif len(dir_parts) == 2:
        try:
            start_page = dir_parts[0].strip()
            name = dir_parts[1].strip()
        except ValueError:
            logger.warning(f"Invalid directory format: {dir_name}, using defaults")
        
    return number, name, start_page

def extract_page_number(file_name):
    """从文件名中提取页码"""
    page_match = re.match(r'.*_(\d+)\..*$', file_name)
    return page_match.group(1) if page_match else '0'

def parse_file_name(file_name):
    """解析文件名称"""
    match = re.match(r'(.+)_(\d+)\.[^.]+$', file_name)
    if match:
        return match.group(2), match.group(1)
    return 0, file_name

# -*- coding: utf-8 -*-

# 文件路径前缀
FILE_PATH_PREFIX = "/var/www/e-doc/public/"

# 任务相关配置
MAX_RETRY_COUNT = 3
MAX_WORKERS = 5

# 临时目录配置
TEMP_DIR_PREFIX = "temp"

# 文档页面存储配置
DOCUMENT_PAGE_PATH = "/uploads/documents/{document_id}/pages/{page_number}_{title}.jpg"

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
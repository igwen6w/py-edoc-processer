# -*- coding: utf-8 -*-
from PIL import Image
import os
from config.settings import FILE_PATH_PREFIX, SUPPORTED_IMAGE_FORMATS
from utils.logger import logger

class ImageService:
    @staticmethod
    def convert_to_jpg(source_path, target_path):
        """将图片转换为JPG格式"""
        try:
            full_target_path = FILE_PATH_PREFIX + target_path
            os.makedirs(os.path.dirname(full_target_path), exist_ok=True)
            
            with Image.open(source_path) as img:
                img.convert('RGB').save(full_target_path, 'JPEG')
            return True
        except Exception as e:
            logger.error(f"Error converting image to JPG: {str(e)}")
            raise

    @staticmethod
    def is_supported_image(file_path):
        """检查是否为支持的图片格式"""
        return file_path.lower().endswith(SUPPORTED_IMAGE_FORMATS)
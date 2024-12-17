# -*- coding: utf-8 -*-
import os
import zipfile
import shutil
from utils.logger import logger
from config.settings import FILE_PATH_PREFIX

class FileService:
    @staticmethod
    async def extract_zip(file_path, temp_dir):
        """解压ZIP文件到临时目录"""
        try:
            os.makedirs(temp_dir, exist_ok=True)
            full_path = FILE_PATH_PREFIX + file_path
            
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    try:
                        # 尝试使用gbk解码
                        filename = file.encode('cp437').decode('gbk')
                    except:
                        try:
                            # 如果gbk解码失败，尝试使用utf-8
                            filename = file.encode('cp437').decode('utf-8')
                        except:
                            filename = file
                    
                    if filename.endswith('/'):
                        os.makedirs(os.path.join(temp_dir, filename), exist_ok=True)
                        continue
                    
                    temp_path = os.path.join(temp_dir, 'temp_' + os.path.basename(file))
                    with zip_ref.open(file) as source, open(temp_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    final_path = os.path.join(temp_dir, filename)
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                    
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    shutil.move(temp_path, final_path)
            
            return True
        except Exception as e:
            logger.error(f"Error extracting zip file: {str(e)}")
            raise

    @staticmethod
    def cleanup_temp_dir(temp_dir):
        """清理临时目录"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {str(e)}")
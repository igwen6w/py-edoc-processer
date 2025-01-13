# -*- coding: utf-8 -*-
import os
import uuid
import zipfile
import shutil
from pdf2image import convert_from_path
from utils.logger import logger
from config.settings import FILE_PATH_PREFIX

class FileService:
    @staticmethod
    async def extract_zip(file_path, temp_dir):
        """解压ZIP文件到临时目录"""
        try:
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

    @staticmethod
    def convert_pdf_to_images(pdf_path, output_dir):
        """将PDF文件转换为图片"""
        logger.info(f"PDF文件路径：{FILE_PATH_PREFIX + pdf_path}")
        logger.info(f"图片文件保存路径：{output_dir}")
        try:
            images = convert_from_path(FILE_PATH_PREFIX + pdf_path)
            for i, image in enumerate(images):
                # 生成一个随机字符串
                random_string = str(uuid.uuid4().hex)[:8]  # 取前8个字符作为随机字符串
                image_path = os.path.join(output_dir, f"{random_string}-page_{i + 1}.jpg")

                # 打印日志
                logger.info(f"第{i+1}页图片路径为：{image_path}")

                # 保存图片
                image.save(image_path, "JPEG")
            return True
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise

# -*- coding: utf-8 -*-
import aiomysql
import asyncio
import os
from datetime import datetime
from config.database import DB_CONFIG
from config.settings import (
    FILE_PATH_PREFIX, MAX_WORKERS, 
    TEMP_DIR_PREFIX, DOCUMENT_PAGE_PATH
)
from services.db_service import DatabaseService
from services.file_service import FileService
from services.image_service import ImageService
from utils.logger import logger
from utils.helpers import parse_directory_name, extract_page_number, parse_file_name

class DocumentProcessor:
    def __init__(self):
        self.running = True
        self.pool = None
        self.db_service = None

    async def init(self):
        """初始化数据库连接池和服务"""
        self.pool = await aiomysql.create_pool(**DB_CONFIG)
        self.db_service = DatabaseService(self.pool)

    async def process_directory_structure(self, document_id, base_dir, initial_parent_id=0, conn=None):
        """处理目录结构"""
        total_pages = 0
        
        async def process_dir(dir_path, parent_id=initial_parent_id, level=0):
            nonlocal total_pages
            
            try:
                entries = sorted(os.listdir(dir_path))
                for entry in entries:
                    full_path = os.path.join(dir_path, entry)
                    
                    if os.path.isdir(full_path):
                        logger.info(f"处理目录: {full_path} at level {level}")
                        # 处理目录
                        dir_name = os.path.basename(full_path)
                        
                        # 解析目录名称
                        number, name, start_page = parse_directory_name(dir_name)

                        # 创建目录
                        dir_id = await self.db_service.insert_directory(document_id, parent_id, name, start_page, number, conn=conn)
                        
                        # 处理子目录
                        sub_pages = await process_dir(full_path, dir_id, level + 1)
                        total_pages += sub_pages
                        
                    elif os.path.isfile(full_path) and ImageService.is_supported_image(full_path):
                        logger.info(f"处理图片文件: {full_path}")

                        # 处理图片文件
                        file_name = os.path.basename(full_path)
                        
                        # 解析文件名称
                        page_number, title = parse_file_name(file_name)
                        page_number = int(page_number)
                        
                        # 检查页面是否已存在
                        if not await self.db_service.check_page_exists(document_id, page_number):
                            target_path = DOCUMENT_PAGE_PATH.format(
                                document_id=document_id,
                                page_number=page_number,
                                title=title
                            )
                            
                            # 转换为jpg
                            ImageService.convert_to_jpg(full_path, target_path)

                            # 插入页面
                            await self.db_service.insert_page(
                                title, document_id, parent_id, page_number, target_path, conn=conn
                            )
                            
                            total_pages += 1
                
                return total_pages
                
            except Exception as e:
                logger.error(f"处理目录失败 {dir_path}: {str(e)}")
                raise
        
        return await process_dir(base_dir)

    async def process_file(self, task):
        """处理单个任务"""
        conn = None
        try:
            logger.info(f"处理任务 {task['id']}")

            # 更新任务状态
            await self.db_service.update_task_status(task['id'], '处理中')

            # 开始事务
            conn = await self.db_service.start_transaction()

            # 解压文件
            temp_dir = f"{TEMP_DIR_PREFIX}/{task['id']}"
            await FileService.extract_zip(task['file_path'], temp_dir)

            # 处理目录
            result = await self.process_directory_structure(
                task['document_id'],
                temp_dir,
                task['document_directory_id'],
                conn
            )

            # 提交事务
            await self.db_service.commit_transaction(conn)

            # 清理临时目录
            FileService.cleanup_temp_dir(temp_dir)

            # 更新任务状态
            await self.db_service.update_task_status(task['id'], '已完成', details=str(result))

        except Exception as e:
            logger.error(f"Error processing task {task['id']}: {str(e)}")

            if conn:
                await self.db_service.rollback_transaction(conn)

            await self.db_service.update_task_status(task['id'], '待重试' if task['retry_count'] < 3 else '已失败', failure_reason=str(e))

    async def run(self):
        """运行文档处理器"""
        await self.init()

        while self.running:
            logger.info(f"开始处理任务 - {datetime.now()}")
            try:
                logger.info(f"获取任务 - {datetime.now()}")
                tasks = await self.db_service.fetch_tasks(MAX_WORKERS)
                if not tasks:
                    logger.info(f"没有可处理的任务 - {datetime.now()}")
                    await asyncio.sleep(5)
                    continue

                logger.info(f"开始处理 {len(tasks)} 个任务 - {datetime.now()}")
                await asyncio.gather(
                    *(self.process_file(task) for task in tasks)
                )

            except Exception as e:
                logger.error(f"处理任务失败 - {datetime.now()}: {str(e)}")
                await asyncio.sleep(5)

    async def shutdown(self):
        """关闭文档处理器"""
        self.running = False

        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

async def main():
    processor = DocumentProcessor()
    try:
        await processor.run()
    except KeyboardInterrupt:
        await processor.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
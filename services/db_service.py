# -*- coding: utf-8 -*-
import aiomysql
from datetime import datetime
from utils.logger import logger

class DatabaseService:
    def __init__(self, pool):
        self.pool = pool

    # 获取待处理任务
    async def fetch_tasks(self, max_workers):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                query = """
                    SELECT t.*, f.file_path
                    FROM ww_document_file_tasks t
                    JOIN ww_document_files f ON t.document_file_id = f.id
                    WHERE t.status IN ('待重试', '未处理')
                    ORDER BY FIELD(t.status, '待重试', '未处理'), t.created_at ASC
                    LIMIT %s
                """
                await cur.execute(query, (max_workers,))
                return await cur.fetchall()

    # 更新任务状态
    async def update_task_status(self, task_id, status, conn=None, **kwargs):
        # 打印日志
        logger.info(f"更新任务状态: task_id={task_id}, status={status}")

        new_connection = conn is None

        if new_connection:
            conn = await self.pool.acquire()

        cur = await conn.cursor()

        try:
            updates = []
            values = []

            updates.append("status = %s")
            values.append(status)

            if status == '处理中':
                updates.append("started_at = %s")
                values.append(datetime.now())
            elif status == '已完成':
                updates.append("completed_at = %s")
                values.append(datetime.now())
            elif status == '已失败':
                updates.append("failed_at = %s")
                values.append(datetime.now())
            elif status == '待重试':
                updates.append("retry_count = retry_count + 1")

            if 'failure_reason' in kwargs:
                updates.append("failure_reason = %s")
                values.append(kwargs['failure_reason'])

            if 'details' in kwargs:
                updates.append("details = %s")
                values.append(kwargs['details'])

            updates.append("updated_at = %s")
            values.append(datetime.now())

            query = f"UPDATE ww_document_file_tasks SET {', '.join(updates)} WHERE id = %s"
            values.append(task_id)
            
            await cur.execute(query, tuple(values))

        finally:
            await cur.close()
            
            if new_connection:
                await conn.commit()
                await self.pool.release(conn)

    # 插入目录
    async def insert_directory(self, document_id, parent_id, name, start_page, number, conn=None):
        # 打印日志
        logger.info(f"插入目录: document_id={document_id}, parent_id={parent_id}, "
                    f"name={name}, start_page={start_page}, number={number}")

        new_connection = conn is None

        if new_connection:
            conn = await self.pool.acquire()

        cur = await conn.cursor()
        
        try:
            await cur.execute("""
                INSERT INTO ww_document_directories 
                (document_id, parent_directory_id, name, start_page, number) 
                VALUES (%s, %s, %s, %s, %s)
            """, (document_id, parent_id, name, start_page, number))

            return cur.lastrowid

        finally:
            await cur.close()

            if new_connection:
                await conn.commit()
                await self.pool.release(conn)


    # 插入页面
    async def insert_page(self, title, document_id, directory_id, page_number, image_path, conn=None):
        # 打印日志
        logger.info(f"插入页面: title={title}, document_id={document_id}, "
                    f"directory_id={directory_id}, page_number={page_number}, image_path={image_path}")
    
        new_connection = conn is None

        if new_connection:
            conn = await self.pool.acquire()

        cur = await conn.cursor()
        
        try:
            await cur.execute("""
                INSERT INTO ww_document_pages 
                (title, document_id, directory_id, page_number, image_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, document_id, directory_id, page_number, image_path))

        finally:
            await cur.close()

            if new_connection:
                await conn.commit()
                await self.pool.release(conn)

    # 检查页面是否已存在
    async def check_page_exists(self, document_id, page_number):
        conn = await self.pool.acquire()
        cur = await conn.cursor()
        
        try:
            await cur.execute("""
                SELECT id FROM ww_document_pages 
                WHERE document_id = %s AND page_number = %s
            """, (document_id, page_number))
            return bool(await cur.fetchone())

        finally:
            await cur.close()
            await self.pool.release(conn)
    
    async def start_transaction(self):
        conn = await self.pool.acquire()
        await conn.begin()
        return conn

    async def commit_transaction(self, conn):
        await conn.commit()
        self.pool.release(conn)

    async def rollback_transaction(self, conn):
        await conn.rollback()
        self.pool.release(conn)
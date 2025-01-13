## 文档处理器

该项目是一个文档处理器，它可以处理 zip 文件中的图片，并将图片信息存储到数据库中。

### 安装依赖

```bash
pip3 install -r requirements.txt
```

### 运行

```bash
python3 main.py
```

### 功能

*   解压 zip 文件
*   将图片转换为 jpg 格式
*   解析文件名和目录名，提取页面编号和标题
*   将图片信息插入到数据库中

### 配置

数据库配置位于 `config/database.py` 文件中。

其他配置位于 `config/settings.py` 文件中，包括：

*   `FILE_PATH_PREFIX`: 文件路径前缀
*   `MAX_WORKERS`: 最大并发任务数
*   `TEMP_DIR_PREFIX`: 临时目录前缀
*   `DOCUMENT_PAGE_PATH`: 文档页面路径

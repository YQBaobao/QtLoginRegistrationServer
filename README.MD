# QtLoginRegistrationServer

### 介绍(Introduction)

使用 PyQt5+FastAPI+SQLAlchemy+Redis+Celery 做的一个登录注册页，使用邮箱注册与验证，前后分离,其中：[QtLoginRegistrationClient](https://github.com/YQBaobao/QtLoginRegistrationClient)仓库存放 GUI，[QtLoginRegistrationServer](https://github.com/YQBaobao/QtLoginRegistrationServer)仓库存放 API

### 项目依赖(Project dependencies)

- Python：你必须安装`requirements.txt`文件中的全部包，包版本大于或等于
- MySQL：你可以使用任何`sqlalchemy`支持的关系型数据库作为存储数据的位置，但是推荐依然推荐使用`MySQL`，因为项目是基于此开发的，并修改`setting.py`中关于数据库连接的相关配置
- Redis：缓存，故需要你安装并修改`setting.py`中相关配置
- Celery：分布式任务队列，用于执行任务，需要你安装(已包含在`requirements.txt`中)并修改`setting.py`中相关配置

### 设置(Setting)

1. 修改： `alembic.ini` 连接数据库 [详见此处](https://docs.sqlalchemy.org/en/21/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql)  
```txt
sqlalchemy.url = mysql+pymysql://username:password@ip:port/database name
```

2. 创建数据库： 进入 `main.py`所在目录，执行命令：
```bash
# 创建迁移脚本
alembic revision --autogenerate -m "creat first table"

# 执行
alembic upgrade head
```

3. 修改 `setting.py`，按照需要修改其中的内容

### 启动(startup)

1. 本地直接启动：`python ./startup.py`
2. 生产部署：
- Linux 系统： 推荐使用 `gunicorn`
详见：[Server Workers - Gunicorn with Uvicorn](https://fastapi.tiangolo.com/deployment/server-workers/)
```bash
# 安装 
pip install "uvicorn[standard]" gunicorn 

# 命令运行
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

- Windows 系统：使用自带的 `Uvicorn` 详见：[Run a Server Manually - Uvicorn](https://fastapi.tiangolo.com/deployment/manually/?h=uvicorn#run-a-server-manually-uvicorn)
```bash
# 安装
pip install uvicorn[standard]

# 命令运行
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

3. 启动 Celery
```bash
# 项目根目录使用命令
celery -A main.celery worker -l info -Q celery,user -P gevent -c 10
```


### 其他(Other)

项目基于 Windows Python3.8.10 x64 开发，若其余 Python 版本无法使用，尝试使用相同 Python 版本

### 许可(License)
 [使用 LGPL-3.0 license](https://www.gnu.org/licenses/lgpl-3.0.html)
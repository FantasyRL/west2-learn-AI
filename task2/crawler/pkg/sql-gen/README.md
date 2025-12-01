# SQL Model Generator (GORM-Gen Style)

一个类似 GORM-Gen 的 Python 数据库模型生成工具，可以从 PostgreSQL 数据库自动生成 SQLAlchemy ORM 模型。

## 功能特性

- 🚀 **自动生成**: 从数据库表结构自动生成 SQLAlchemy 模型
- 📝 **类型映射**: 自动将 PostgreSQL 类型映射为 Python 类型
- 🔗 **关系生成**: 自动识别外键并生成关系定义
- 🎯 **选择性生成**: 支持指定表名，只生成需要的模型
- 📦 **模块化**: 生成规范的 Python 包结构
- ⚙️ **配置驱动**: 通过 YAML 配置文件管理数据库连接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置文件

编辑 `config.yaml` 文件，配置数据库连接信息：

```yaml
pgsql:
  host: "127.0.0.1"      # 数据库地址
  port: 5432             # 端口
  database: "crawler"    # 数据库名
  user: "postgres"       # 用户名
  password: "password"   # 密码
```

## 使用方法

### 1. 列出所有表

```bash
python main.py --list-tables
```

### 2. 生成所有表的模型

```bash
python main.py
```

### 3. 生成指定表的模型

```bash
python main.py -t users posts comments
```

### 4. 指定输出目录

```bash
python main.py -o ../models
```

### 5. 使用自定义配置文件

```bash
python main.py -c /path/to/config.yaml
```

## 命令行参数

```
参数说明:
  -c, --config CONFIG    配置文件路径 (默认: config.yaml)
  -o, --output OUTPUT    输出目录 (默认: generated_models)
  -t, --tables TABLES    指定要生成的表名 (空格分隔)
  --list-tables          仅列出所有表名
  -h, --help            显示帮助信息
```

## 生成的文件结构

```
generated_models/
├── __init__.py          # 包初始化文件
├── base.py              # 基础模型定义
├── users.py             # 用户表模型
├── posts.py             # 文章表模型
└── comments.py          # 评论表模型
```

## 使用生成的模型

```python
from generated_models import Base, Users, Posts

# 在你的应用中使用
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:pass@localhost/dbname')
Session = sessionmaker(bind=engine)
session = Session()

# 查询用户
users = session.query(Users).all()
```

## 支持的数据类型

| PostgreSQL 类型 | SQLAlchemy 类型 | Python 类型 |
|----------------|-----------------|-------------|
| INTEGER        | Integer         | int         |
| BIGINT         | Integer         | int         |
| VARCHAR        | String          | str         |
| TEXT           | Text            | str         |
| BOOLEAN        | Boolean         | bool        |
| TIMESTAMP      | DateTime        | datetime    |
| DATE           | Date            | date        |
| NUMERIC        | Numeric         | Decimal     |
| JSON/JSONB     | JSON/JSONB      | dict        |
| UUID           | UUID            | uuid.UUID   |
| ARRAY          | ARRAY           | list        |

## 生成示例

假设有以下数据库表：

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

生成的模型：

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base

class Users(Base):
    """
    users 表模型
    
    自动生成时间: 2025-12-01 10:00:00
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<Users({self.id})>"
```

## 注意事项

1. **数据库连接**: 确保数据库可访问且配置正确
2. **表权限**: 需要有读取表结构的权限
3. **外键关系**: 外键关系会自动生成，但可能需要手动调整
4. **命名规范**: 表名使用蛇形命名，类名自动转为驼峰命名
5. **类型映射**: 某些特殊类型可能需要手动调整

## 与 GORM-Gen 的对比

| 特性 | GORM-Gen (Go) | SQL-Gen (Python) |
|------|---------------|------------------|
| 语言 | Go | Python |
| ORM | GORM | SQLAlchemy |
| 配置 | 代码配置 | YAML 配置 |
| 生成方式 | 编程式 | 命令行 |
| 类型系统 | Go struct | Python class |
| 关系定义 | 自动推断 | 自动生成 |

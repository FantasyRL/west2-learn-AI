"""sql-gen 工具包"""

__version__ = "1.0.0"
__author__ = "SQL Model Generator"
__description__ = "从 PostgreSQL 数据库生成 SQLAlchemy 模型 (GORM-Gen 风格)"

from .config_loader import load_config, Config, PgsqlConfig
from .db_inspector import DatabaseInspector, AsyncDatabaseInspector
from .model_generator import ModelGenerator

__all__ = [
    "load_config",
    "Config",
    "PgsqlConfig",
    "DatabaseInspector",
    "AsyncDatabaseInspector",
    "ModelGenerator",
]

"""数据库连接和表信息获取模块"""
import asyncio
from typing import List, Dict, Any
from sqlalchemy import create_engine, MetaData, inspect, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from config_loader import PgsqlConfig


class DatabaseInspector:
    """数据库检查器"""
    
    def __init__(self, config: PgsqlConfig):
        """
        初始化数据库检查器
        
        Args:
            config: PostgreSQL 配置
        """
        self.config = config
        self.engine = create_engine(config.connection_string)
        self.metadata = MetaData()
    
    def get_all_tables(self) -> List[str]:
        """
        获取所有表名
        
        Returns:
            List[str]: 表名列表
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表的详细信息
        
        Args:
            table_name: 表名
            
        Returns:
            Dict: 表信息
        """
        inspector = inspect(self.engine)
        
        # 获取列信息
        columns = inspector.get_columns(table_name)
        
        # 获取主键
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', [])
        
        # 获取外键
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        # 获取索引
        indexes = inspector.get_indexes(table_name)
        
        # 获取唯一约束
        unique_constraints = inspector.get_unique_constraints(table_name)
        
        return {
            'table_name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes,
            'unique_constraints': unique_constraints
        }
    
    def get_all_table_info(self) -> List[Dict[str, Any]]:
        """
        获取所有表的信息
        
        Returns:
            List[Dict]: 所有表的信息列表
        """
        tables = self.get_all_tables()
        return [self.get_table_info(table) for table in tables]
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


class AsyncDatabaseInspector:
    """异步数据库检查器"""
    
    def __init__(self, config: PgsqlConfig):
        """
        初始化异步数据库检查器
        
        Args:
            config: PostgreSQL 配置
        """
        self.config = config
        self.engine = create_async_engine(config.async_connection_string)
    
    async def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    async def close(self):
        """关闭数据库连接"""
        await self.engine.dispose()

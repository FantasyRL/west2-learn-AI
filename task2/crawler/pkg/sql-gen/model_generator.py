"""SQLAlchemy 模型生成器"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from config_loader import PgsqlConfig


class ModelGenerator:
    """模型代码生成器"""
    
    # Python 类型映射
    TYPE_MAPPING = {
        'INTEGER': 'int',
        'BIGINT': 'int',
        'SMALLINT': 'int',
        'VARCHAR': 'str',
        'TEXT': 'str',
        'CHAR': 'str',
        'BOOLEAN': 'bool',
        'DATE': 'datetime.date',
        'TIMESTAMP': 'datetime.datetime',
        'TIMESTAMP WITHOUT TIME ZONE': 'datetime.datetime',
        'TIMESTAMP WITH TIME ZONE': 'datetime.datetime',
        'TIME': 'datetime.time',
        'NUMERIC': 'decimal.Decimal',
        'DECIMAL': 'decimal.Decimal',
        'REAL': 'float',
        'DOUBLE PRECISION': 'float',
        'JSON': 'dict',
        'JSONB': 'dict',
        'ARRAY': 'list',
        'UUID': 'uuid.UUID',
    }
    
    def __init__(self, output_dir: str = "generated_models"):
        """
        初始化生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_python_type(self, sql_type: str) -> str:
        """
        获取对应的 Python 类型
        
        Args:
            sql_type: SQL 类型
            
        Returns:
            str: Python 类型
        """
        sql_type_upper = str(sql_type).upper()
        
        for key, value in self.TYPE_MAPPING.items():
            if key in sql_type_upper:
                return value
        
        return 'Any'
    
    def _snake_to_camel(self, snake_str: str) -> str:
        """
        将蛇形命名转换为驼峰命名
        
        Args:
            snake_str: 蛇形命名字符串
            
        Returns:
            str: 驼峰命名字符串
        """
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    def _generate_imports(self, table_info: Dict[str, Any]) -> str:
        """
        生成导入语句
        
        Args:
            table_info: 表信息
            
        Returns:
            str: 导入语句代码
        """
        imports = [
            "from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Float, Date, Time, JSON",
            "from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY",
            "from sqlalchemy.orm import relationship",
            "from sqlalchemy.sql import func",
            "from datetime import datetime, date, time",
            "from decimal import Decimal",
            "from typing import Optional, List",
            "import uuid",
            "",
            "from .base import Base",
        ]
        
        return "\n".join(imports)
    
    def _generate_column_definition(self, column: Dict[str, Any], primary_keys: List[str]) -> str:
        """
        生成列定义
        
        Args:
            column: 列信息
            primary_keys: 主键列表
            
        Returns:
            str: 列定义代码
        """
        col_name = column['name']
        col_type = str(column['type'])
        nullable = column['nullable']
        default = column.get('default')
        
        # 确定 SQLAlchemy 类型
        if 'INTEGER' in col_type.upper():
            sa_type = 'Integer'
        elif 'BIGINT' in col_type.upper():
            sa_type = 'Integer'
        elif 'VARCHAR' in col_type.upper():
            length = self._extract_length(col_type)
            sa_type = f'String({length})' if length else 'String'
        elif 'TEXT' in col_type.upper():
            sa_type = 'Text'
        elif 'BOOLEAN' in col_type.upper():
            sa_type = 'Boolean'
        elif 'TIMESTAMP' in col_type.upper():
            sa_type = 'DateTime(timezone=True)'
        elif 'DATE' in col_type.upper():
            sa_type = 'Date'
        elif 'TIME' in col_type.upper():
            sa_type = 'Time'
        elif 'NUMERIC' in col_type.upper() or 'DECIMAL' in col_type.upper():
            sa_type = 'Numeric'
        elif 'REAL' in col_type.upper() or 'DOUBLE' in col_type.upper():
            sa_type = 'Float'
        elif 'JSON' in col_type.upper():
            sa_type = 'JSONB' if 'JSONB' in col_type.upper() else 'JSON'
        elif 'UUID' in col_type.upper():
            sa_type = 'UUID(as_uuid=True)'
        elif 'ARRAY' in col_type.upper():
            sa_type = 'ARRAY(String)'  # 简化处理
        else:
            sa_type = 'String'
        
        # 构建列定义
        parts = [f'Column({sa_type}']
        
        # 主键
        if col_name in primary_keys:
            parts.append('primary_key=True')
            if col_name == 'id' and 'INTEGER' in col_type.upper():
                parts.append('autoincrement=True')
        
        # 可空性
        if not nullable and col_name not in primary_keys:
            parts.append('nullable=False')
        
        # 默认值
        if default and 'nextval' not in str(default):
            if 'now()' in str(default) or 'CURRENT_TIMESTAMP' in str(default):
                parts.append('server_default=func.now()')
            else:
                parts.append(f'default={default}')
        
        # 注释
        comment = column.get('comment')
        if comment:
            parts.append(f'comment="{comment}"')
        
        column_def = f"    {col_name} = {', '.join(parts)})"
        
        return column_def
    
    def _extract_length(self, col_type: str) -> Optional[int]:
        """
        从类型字符串中提取长度
        
        Args:
            col_type: 列类型
            
        Returns:
            Optional[int]: 长度
        """
        import re
        match = re.search(r'\((\d+)\)', col_type)
        return int(match.group(1)) if match else None
    
    def _generate_relationships(self, table_info: Dict[str, Any]) -> List[str]:
        """
        生成关系定义
        
        Args:
            table_info: 表信息
            
        Returns:
            List[str]: 关系定义代码列表
        """
        relationships = []
        
        for fk in table_info.get('foreign_keys', []):
            # 外键关系
            referred_table = fk['referred_table']
            constrained_columns = fk['constrained_columns']
            
            # 生成关系名称
            rel_name = referred_table.rstrip('s')  # 简单的单数化
            class_name = self._snake_to_camel(referred_table)
            
            rel_def = f'    {rel_name} = relationship("{class_name}", back_populates="{table_info["table_name"]}")'
            relationships.append(rel_def)
        
        return relationships
    
    def generate_model(self, table_info: Dict[str, Any]) -> str:
        """
        生成单个表的模型代码
        
        Args:
            table_info: 表信息
            
        Returns:
            str: 模型代码
        """
        table_name = table_info['table_name']
        class_name = self._snake_to_camel(table_name)
        columns = table_info['columns']
        primary_keys = table_info['primary_keys']
        
        # 生成导入
        imports = self._generate_imports(table_info)
        
        # 生成类定义
        class_def = [
            f"\n\nclass {class_name}(Base):",
            f'    """',
            f'    {table_name} 表模型',
            f'    ',
            f'    自动生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'    """',
            f'    __tablename__ = "{table_name}"',
            f'',
        ]
        
        # 生成列定义
        for column in columns:
            col_def = self._generate_column_definition(column, primary_keys)
            class_def.append(col_def)
        
        # 生成关系
        relationships = self._generate_relationships(table_info)
        if relationships:
            class_def.append('')
            class_def.append('    # 关系')
            class_def.extend(relationships)
        
        # 生成 __repr__ 方法
        class_def.extend([
            '',
            '    def __repr__(self) -> str:',
            f'        return f"<{class_name}({{self.id}})>"'
        ])
        
        code = imports + '\n' + '\n'.join(class_def)
        
        return code
    
    def generate_base_model(self) -> str:
        """
        生成基础模型
        
        Returns:
            str: 基础模型代码
        """
        code = '''"""基础模型定义"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
'''
        return code
    
    def generate_init_file(self, table_names: List[str]) -> str:
        """
        生成 __init__.py 文件
        
        Args:
            table_names: 表名列表
            
        Returns:
            str: __init__.py 内容
        """
        imports = ['from .base import Base, BaseModel']
        
        for table_name in table_names:
            class_name = self._snake_to_camel(table_name)
            module_name = table_name.lower()
            imports.append(f'from .{module_name} import {class_name}')
        
        imports.append('')
        imports.append('__all__ = [')
        imports.append('    "Base",')
        imports.append('    "BaseModel",')
        
        for table_name in table_names:
            class_name = self._snake_to_camel(table_name)
            imports.append(f'    "{class_name}",')
        
        imports.append(']')
        
        return '\n'.join(imports)
    
    def save_model(self, table_name: str, code: str):
        """
        保存模型到文件
        
        Args:
            table_name: 表名
            code: 模型代码
        """
        file_name = f"{table_name.lower()}.py"
        file_path = self.output_dir / file_name
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✓ 生成模型文件: {file_path}")
    
    def save_base_model(self):
        """保存基础模型"""
        code = self.generate_base_model()
        file_path = self.output_dir / "base.py"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✓ 生成基础模型: {file_path}")
    
    def save_init_file(self, table_names: List[str]):
        """
        保存 __init__.py 文件
        
        Args:
            table_names: 表名列表
        """
        code = self.generate_init_file(table_names)
        file_path = self.output_dir / "__init__.py"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✓ 生成 __init__.py: {file_path}")
    
    def generate_all_models(self, tables_info: List[Dict[str, Any]]):
        """
        生成所有模型
        
        Args:
            tables_info: 所有表的信息
        """
        print(f"\n开始生成模型文件到目录: {self.output_dir}")
        print("=" * 60)
        
        # 生成基础模型
        self.save_base_model()
        
        # 生成各个表的模型
        table_names = []
        for table_info in tables_info:
            table_name = table_info['table_name']
            table_names.append(table_name)
            
            try:
                code = self.generate_model(table_info)
                self.save_model(table_name, code)
            except Exception as e:
                print(f"✗ 生成 {table_name} 模型失败: {e}")
        
        # 生成 __init__.py
        self.save_init_file(table_names)
        
        print("=" * 60)
        print(f"✓ 完成! 共生成 {len(table_names)} 个模型文件\n")

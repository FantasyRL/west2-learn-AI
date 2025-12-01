"""配置文件加载器"""
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PgsqlConfig:
    """PostgreSQL 配置"""
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def connection_string(self) -> str:
        """获取连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_string(self) -> str:
        """获取异步连接字符串"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class AIProviderConfig:
    """AI 提供商配置"""
    model: str
    remote: Dict[str, str]


@dataclass
class Config:
    """完整配置"""
    pgsql: PgsqlConfig
    ai_provider: AIProviderConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Config: 配置对象
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # 解析 PostgreSQL 配置
    pgsql_data = data.get('pgsql', {})
    pgsql_config = PgsqlConfig(
        host=pgsql_data.get('host', 'localhost'),
        port=pgsql_data.get('port', 5432),
        database=pgsql_data.get('database', 'crawler'),
        user=pgsql_data.get('user', 'postgres'),
        password=pgsql_data.get('password', '')
    )
    
    # 解析 AI 提供商配置
    ai_data = data.get('ai_provider', {})
    ai_config = AIProviderConfig(
        model=ai_data.get('model', ''),
        remote=ai_data.get('remote', {})
    )
    
    return Config(pgsql=pgsql_config, ai_provider=ai_config)

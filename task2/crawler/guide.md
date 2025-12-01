# 爬虫项目开发指南

## 项目概述

本项目是一个基于 Python 的通用爬虫平台，支持多种爬虫任务的统一管理和调度。采用 **DDD (领域驱动设计) + Clean Architecture** 架构，通过 **Protocol Buffers** 定义 API 接口，数据持久化到 PostgreSQL 数据库。

### 核心特性

- **领域驱动设计 (DDD)**：清晰的业务领域划分和分层架构
- **可复用的爬虫引擎**：抽象出通用的爬虫组件，支持快速扩展新的爬虫任务
- **IDL 驱动开发**：通过 Protocol Buffers 定义接口规范，自动生成 API 代码
- **数据持久化**：使用 PostgreSQL + SQLAlchemy ORM
- **代码生成工具**：类似 GORM-Gen 的模型生成器
- **灵活配置**：支持多种爬虫策略（HTTP、Selenium、API 调用）

## 技术选型

### 1. 架构模式
**DDD (领域驱动设计) + Clean Architecture**

**架构理由**：
- 清晰的分层结构，职责分明
- 业务逻辑与技术实现解耦
- 易于测试和维护
- 支持业务快速迭代

### 2. IDL 定义
**Protocol Buffers (protobuf)**

**选型理由**：
- 强类型约束，接口定义清晰
- 跨语言支持
- 自动生成代码
- 便于前后端协作

### 3. ORM 框架
**SQLAlchemy 2.0**

**选型理由**：
- Python 生态最成熟的 ORM
- 支持异步操作（asyncio）
- 类型提示支持

**自研代码生成工具**：`pkg/sql-gen` (类似 GORM-Gen)
- 从数据库表结构自动生成 SQLAlchemy 模型
- 配置驱动，一键生成
- 智能类型映射

### 4. 爬虫库
- **httpx**: 异步 HTTP 客户端（推荐）
- **lxml**: XPath 解析
- **selenium**: 浏览器自动化（知乎等反爬场景）

### 5. Web 框架
**FastAPI** (可选，用于提供 HTTP API)

**选型理由**：
- 原生支持 async/await
- 自动生成 OpenAPI 文档
- 与 Pydantic 深度集成

## 项目结构 (DDD + Clean Architecture)

```
crawler/
├── __init__.py
├── guide.md                    # 本文档
├── requirements.txt            # 依赖包
├── Makefile                    # 构建脚本
│
├── config/                     # 配置文件
│   ├── __init__.py
│   └── config.yaml            # 统一配置（数据库、AI等）
│
├── idl/                        # IDL 接口定义
│   └── crawler.proto          # Protocol Buffers 定义
│
├── api/                        # API 层（从 IDL 生成）
│   ├── __init__.py
│   └── generated/             # 自动生成的 API 代码
│       ├── __init__.py
│       ├── crawler_pb2.py     # Protobuf 消息
│       └── crawler_pb2_grpc.py # gRPC 服务
│
├── internal/                   # 内部业务逻辑（核心层）
│   ├── __init__.py
│   ├── application/           # 应用服务层
│   │   ├── __init__.py
│   │   ├── fzu_service.py     # 福大通知应用服务
│   │   ├── zhihu_service.py   # 知乎话题应用服务
│   │   └── ospp_service.py    # 开源之夏应用服务
│   │
│   ├── domain/                # 领域层（核心业务逻辑）
│   │   ├── __init__.py
│   │   ├── entity/            # 领域实体
│   │   │   ├── __init__.py
│   │   │   ├── fzu_notice.py  # 福大通知实体
│   │   │   ├── zhihu_topic.py # 知乎话题实体
│   │   │   └── ospp_project.py # 开源之夏实体
│   │   ├── repository/        # 仓储接口（抽象）
│   │   │   ├── __init__.py
│   │   │   ├── fzu_repository.py
│   │   │   ├── zhihu_repository.py
│   │   │   └── ospp_repository.py
│   │   └── service/           # 领域服务
│   │       ├── __init__.py
│   │       └── crawler_service.py
│   │
│   └── infra/                 # 基础设施层
│       ├── __init__.py
│       ├── persistence/       # 持久化实现
│       │   ├── __init__.py
│       │   ├── database.py    # 数据库连接
│       │   ├── fzu_repo_impl.py
│       │   ├── zhihu_repo_impl.py
│       │   └── ospp_repo_impl.py
│       └── external/          # 外部服务
│           ├── __init__.py
│           └── crawler_client.py
│
├── models/                     # 数据库模型（从 sql-gen 生成）
│   ├── __init__.py
│   ├── base.py                # 基础模型
│   ├── users.py               # 示例模型
│   └── ...                    # 其他生成的模型
│
├── pkg/                        # 可复用包
│   ├── __init__.py
│   ├── crawler/               # 爬虫引擎包
│   │   ├── __init__.py
## 架构分层说明

### 1. API 层 (`api/`)
- 从 IDL (Protocol Buffers) 自动生成
- 定义了所有的接口契约
- 包含请求/响应消息定义

### 2. 应用服务层 (`internal/application/`)
- 编排业务流程
- 调用领域服务和仓储
- 处理事务边界
- 数据转换（DTO ↔ Entity）

### 3. 领域层 (`internal/domain/`)
- **Entity**: 领域实体，包含业务逻辑
- **Repository**: 仓储接口（抽象），定义数据访问契约
- **Service**: 领域服务，处理跨实体的业务逻辑

### 4. 基础设施层 (`internal/infra/`)
- **Persistence**: 仓储接口的具体实现
- **External**: 外部服务调用（如爬虫客户端）
- 数据库连接、配置加载等

### 5. 模型层 (`models/`)
- 数据库模型（SQLAlchemy）
- 通过 `pkg/sql-gen` 工具自动生成
- 与领域实体分离，遵循关注点分离原则

### 6. 包层 (`pkg/`)
- 可复用的独立包
- 爬虫引擎（`crawler`）
- 模型生成工具（`sql-gen`）

## 核心设计

### 1. 爬虫基类设计 (pkg/crawler/base_crawler.py)
│   └── sql-gen/               # 模型生成工具（类似 GORM-Gen）
│       ├── __init__.py
│       ├── main.py            # 生成器入口
│       ├── config.yaml        # 生成器配置
│       ├── config_loader.py   # 配置加载
│       ├── db_inspector.py    # 数据库检查
│       ├── model_generator.py # 模型生成器
│       ├── requirements.txt   # 生成器依赖
│       ├── README.md          # 使用文档
│       └── generated_models/  # 生成的模型输出目录
│
├── tests/                      # 测试
│   ├── __init__.py
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
│
└── scripts/                    # 脚本
    ├── generate_proto.sh      # 生成 Protobuf 代码
    └── run_crawler.py         # 运行爬虫脚本
```

## 核心设计

### 1. 爬虫基类设计 (core/base_crawler.py)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

class BaseCrawler(ABC):
    """爬虫抽象基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        获取原始数据
        返回: 原始数据列表
        """
        pass
    
    @abstractmethod
    async def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单条数据
        返回: 解析后的结构化数据
        """
        pass
    
    async def run(self, **kwargs) -> List[Dict[str, Any]]:
        """
        执行完整的爬虫流程
        返回: 解析后的数据列表
        """
        try:
            # 1. 获取数据
            raw_data_list = await self.fetch(**kwargs)
            self.logger.info(f"Fetched {len(raw_data_list)} items")
            
            # 2. 解析数据
            parsed_data_list = []
            for raw_data in raw_data_list:
                try:
                    parsed = await self.parse(raw_data)
                    parsed_data_list.append(parsed)
                except Exception as e:
                    self.logger.error(f"Parse error: {e}")
                    continue
            
            return parsed_data_list
            
        except Exception as e:
            self.logger.error(f"Crawler run error: {e}")
            raise
```

**注意**: 
- 基类不负责数据持久化（遵循单一职责）
- 持久化由仓储层（Repository）负责
- 爬虫只负责数据的获取和解析

### 2. HTTP 爬虫基类 (pkg/crawler/http_crawler.py)

```python
from typing import Optional
import httpx
from core.base_crawler import BaseCrawler

class HttpCrawler(BaseCrawler):
    """HTTP 爬虫基类"""
    
    def __init__(self, db_session: AsyncSession, 
                 headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30):
        super().__init__(db_session)
        self.headers = headers or self._default_headers()
        self.timeout = timeout
        self.client = None
    
    def _default_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """发送 GET 请求"""
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with'")
        return await self.client.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """发送 POST 请求"""
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with'")
        return await self.client.post(url, **kwargs)
```

### 3. Selenium 爬虫基类 (core/selenium_crawler.py)

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from core.base_crawler import BaseCrawler

class SeleniumCrawler(BaseCrawler):
    """Selenium 爬虫基类"""
    
    def __init__(self, db_session: AsyncSession, headless: bool = True):
        super().__init__(db_session)
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """初始化 Chrome 驱动"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def __enter__(self):
        self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
    
    def get_page(self, url: str):
        """访问页面"""
        if not self.driver:
            raise RuntimeError("Driver not initialized. Use 'with'")
        self.driver.get(url)
```

### 4. 数据解析器 (core/parser.py)

```python
from lxml import etree
from typing import List, Union

class Parser:
    """数据解析工具类"""
    
    @staticmethod
    def xpath(html: str, xpath_expr: str) -> List[str]:
        """XPath 解析"""
        tree = etree.HTML(html)
        return tree.xpath(xpath_expr)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本 (去除空白、换行等)"""
        return ' '.join(text.split()).strip()
    
    @staticmethod
    def extract_links(html: str, base_url: str = "") -> List[str]:
        """提取所有链接"""
        tree = etree.HTML(html)
        links = tree.xpath('//a/@href')
        if base_url:
            from urllib.parse import urljoin
            links = [urljoin(base_url, link) for link in links]
        return links
```

## 从 IDL 生成 API 代码

### 1. Protocol Buffers 接口定义

文件位置: `idl/crawler.proto`

### 2. 生成 Python 代码

#### 方法一：使用 protoc 命令

```bash
# 安装 grpcio-tools
pip install grpcio-tools

# 生成 Python 代码
python -m grpc_tools.protoc \
    -I./idl \
    --python_out=./api/generated \
    --grpc_python_out=./api/generated \
    --pyi_out=./api/generated \
    ./idl/crawler.proto
```

#### 方法二：使用 Makefile（推荐）

在 `Makefile` 中添加以下内容：

```makefile
# 生成 API 代码
.PHONY: proto
proto:
	python -m grpc_tools.protoc \
		-I./idl \
		--python_out=./api/generated \
		--grpc_python_out=./api/generated \
		--pyi_out=./api/generated \
		./idl/crawler.proto
	@echo "✓ Protobuf 代码生成完成"

# 生成数据库模型
.PHONY: model
model:
	python pkg/sql-gen/main.py --config $(GEN_CONFIG_PATH)

# 同时生成 API 和模型
.PHONY: gen
gen: proto model
	@echo "✓ 所有代码生成完成"
```

运行：
```bash
make proto    # 生成 API 代码
make model    # 生成数据库模型
make gen      # 生成所有代码
```

#### 方法三：使用脚本

创建 `scripts/generate_proto.sh`:

```bash
#!/bin/bash

echo "🚀 开始生成 Protobuf 代码..."

# 创建输出目录
mkdir -p api/generated

# 生成代码
python -m grpc_tools.protoc \
    -I./idl \
    --python_out=./api/generated \
    --grpc_python_out=./api/generated \
    --pyi_out=./api/generated \
    ./idl/crawler.proto

# 生成 __init__.py
cat > api/generated/__init__.py << 'EOF'
"""自动生成的 Protobuf 代码"""
from .crawler_pb2 import *
from .crawler_pb2_grpc import *

__all__ = [
    # 请求消息
    "FzuNoticeRequest",
    "StartFzuCrawlerRequest",
    "ZhihuTopicRequest",
    "StartZhihuCrawlerRequest",
    "OsppProjectRequest",
    "StartOsppCrawlerRequest",
    "ExportToCsvRequest",
    
    # 响应消息
    "FzuNoticeResponse",
    "ZhihuTopicResponse",
    "OsppProjectResponse",
    "ExportToCsvResponse",
    "CrawlerResult",
    
    # 实体消息
    "FzuNotice",
    "Attachment",
    "ZhihuQuestion",
    "ZhihuAnswer",
    "OsppProject",
    
    # 服务
    "CrawlerServiceServicer",
    "CrawlerServiceStub",
]
EOF

echo "✅ Protobuf 代码生成完成！"
echo "📁 输出目录: api/generated/"
```

运行：
```bash
chmod +x scripts/generate_proto.sh
./scripts/generate_proto.sh
```

### 3. 生成的文件说明

生成后会在 `api/generated/` 目录下得到：

```
api/generated/
├── __init__.py              # 模块初始化
├── crawler_pb2.py           # Protobuf 消息类
├── crawler_pb2.pyi          # 类型提示文件
└── crawler_pb2_grpc.py      # gRPC 服务类
```

### 4. 使用生成的代码

#### 方式一：作为数据模型使用（推荐用于 FastAPI）

```python
from api.generated import (
    FzuNoticeRequest,
    FzuNoticeResponse,
    StartFzuCrawlerRequest,
    CrawlerResult,
)

# 在 FastAPI 路由中使用（需要转换为 Pydantic）
from pydantic import BaseModel

class FzuNoticeRequestModel(BaseModel):
    page: int = 1
    page_size: int = 20
    keyword: str = None
    
    @staticmethod
    def to_proto():
        """转换为 Protobuf 消息"""
        pass
```

#### 方式二：作为 gRPC 服务使用

```python
from api.generated import CrawlerServiceServicer
import grpc
from concurrent import futures

class CrawlerServiceImpl(CrawlerServiceServicer):
    """实现 gRPC 服务"""
    
    async def StartFzuCrawler(self, request, context):
        # 实现逻辑
        pass
    
    async def GetFzuNotices(self, request, context):
        # 实现逻辑
        pass

# 启动 gRPC 服务器
server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
crawler_pb2_grpc.add_CrawlerServiceServicer_to_server(
    CrawlerServiceImpl(), server
)
server.add_insecure_port('[::]:50051')
await server.start()
```

### 5. Protobuf 转 Pydantic（用于 FastAPI）

可以使用 `protobuf-to-pydantic` 库：

```bash
pip install protobuf-to-pydantic
```

或手动转换：

```python
from pydantic import BaseModel
from typing import Optional, List

# 手动定义 Pydantic 模型（与 Protobuf 对应）
class FzuNoticeRequest(BaseModel):
    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None

class Attachment(BaseModel):
    name: str
    download_count: int
    url: str

class FzuNotice(BaseModel):
    id: str
    publisher: str
    title: str
    date: str
    detail_url: str
    html_content: str
    attachments: List[Attachment] = []

class FzuNoticeResponse(BaseModel):
    notices: List[FzuNotice]
    total: int
    message: str
```

## Protocol Buffers 接口定义详解 (idl/crawler.proto)

```protobuf
syntax = "proto3";

package crawler;

// ==================== 福大教务通知 ====================

message FzuNoticeRequest {
  int32 page = 1;           // 页码
  int32 page_size = 2;      // 每页数量
  optional string keyword = 3;  // 搜索关键词
}

message FzuNotice {
  string id = 1;
  string publisher = 2;     // 通知人
  string title = 3;         // 标题
  string date = 4;          // 日期
  string detail_url = 5;    // 详情链接
  string html_content = 6;  // 详情 HTML
  repeated Attachment attachments = 7;  // 附件列表
}

message Attachment {
  string name = 1;          // 附件名
  int32 download_count = 2; // 下载次数
  string url = 3;           // 附件链接
}

message FzuNoticeResponse {
  repeated FzuNotice notices = 1;
  int32 total = 2;
  string message = 3;
}

message StartFzuCrawlerRequest {
  int32 target_count = 1;   // 目标爬取数量 (至少500)
}

message CrawlerResult {
  bool success = 1;
  string message = 2;
  int32 crawled_count = 3;
  int32 saved_count = 4;
}

// ==================== 知乎话题 ====================

message ZhihuTopicRequest {
  string topic_id = 1;      // 话题ID
  int32 question_limit = 2; // 问题数量限制
  int32 answer_limit = 3;   // 每个问题的回答数量限制
}

message ZhihuQuestion {
  string id = 1;
  string title = 2;         // 问题标题
  string content = 3;       // 问题详细内容
  repeated ZhihuAnswer answers = 4;
}

message ZhihuAnswer {
  string id = 1;
  string content = 2;       // 回答内容 (纯文本)
  int32 vote_count = 3;     // 赞同数
  string author = 4;        // 作者
}

message ZhihuTopicResponse {
  repeated ZhihuQuestion questions = 1;
  string message = 2;
}

message StartZhihuCrawlerRequest {
  string topic_url = 1;
  int32 question_count = 2;
  int32 answer_per_question = 3;
}

// ==================== 开源之夏 ====================

message OsppProjectRequest {
  optional string keyword = 1;      // 搜索关键词
  optional string difficulty = 2;   // 难度筛选
  optional string tech_tag = 3;     // 技术标签筛选
}

message OsppProject {
  string id = 1;
  string name = 2;          // 项目名
  string difficulty = 3;    // 难度
  repeated string tech_tags = 4;  // 技术标签
  string description = 5;   // 项目简述
  string requirements = 6;  // 产出要求
  optional string pdf_url = 7;    // 申请书PDF链接
}

message OsppProjectResponse {
  repeated OsppProject projects = 1;
  int32 total = 2;
  string message = 3;
}

message StartOsppCrawlerRequest {
  bool download_pdf = 1;    // 是否下载PDF
}

// ==================== 导出接口 ====================

message ExportToCsvRequest {
  string crawler_type = 1;  // "fzu" | "zhihu" | "ospp"
  optional string output_path = 2;
}

message ExportToCsvResponse {
  bool success = 1;
  string file_path = 2;
  string message = 3;
}

// ==================== 服务定义 ====================

service CrawlerService {
  // 福大教务通知
  rpc StartFzuCrawler(StartFzuCrawlerRequest) returns (CrawlerResult);
  rpc GetFzuNotices(FzuNoticeRequest) returns (FzuNoticeResponse);
  
  // 知乎话题
  rpc StartZhihuCrawler(StartZhihuCrawlerRequest) returns (CrawlerResult);
  rpc GetZhihuTopics(ZhihuTopicRequest) returns (ZhihuTopicResponse);
  
  // 开源之夏
  rpc StartOsppCrawler(StartOsppCrawlerRequest) returns (CrawlerResult);
  rpc GetOsppProjects(OsppProjectRequest) returns (OsppProjectResponse);
  
  // 通用导出
  rpc ExportToCsv(ExportToCsvRequest) returns (ExportToCsvResponse);
}
```

## 数据库模型设计

### 基础模型 (models/base.py)

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 福大通知模型 (models/fzu_notice.py)

```python
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class FzuNotice(BaseModel):
    __tablename__ = "fzu_notices"
    
    publisher = Column(String(100), nullable=False, comment="通知人")
    title = Column(String(500), nullable=False, comment="标题")
    publish_date = Column(String(20), nullable=False, comment="发布日期")
    detail_url = Column(String(500), nullable=False, unique=True, comment="详情链接")
    html_content = Column(Text, comment="详情HTML内容")
    
    # 关联附件
    attachments = relationship("FzuNoticeAttachment", back_populates="notice", 
                              cascade="all, delete-orphan")

class FzuNoticeAttachment(BaseModel):
    __tablename__ = "fzu_notice_attachments"
    
    notice_id = Column(Integer, ForeignKey("fzu_notices.id"), nullable=False)
    name = Column(String(500), nullable=False, comment="附件名")
    download_count = Column(Integer, default=0, comment="下载次数")
    url = Column(String(500), nullable=False, comment="附件链接码")
    local_path = Column(String(1000), comment="本地存储路径")
    
    # 关联通知
    notice = relationship("FzuNotice", back_populates="attachments")
```

### 知乎话题模型 (models/zhihu_topic.py)

```python
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class ZhihuQuestion(BaseModel):
    __tablename__ = "zhihu_questions"
    
    question_id = Column(String(50), unique=True, nullable=False, comment="问题ID")
    topic_id = Column(String(50), nullable=False, comment="话题ID")
    title = Column(String(500), nullable=False, comment="问题标题")
    content = Column(Text, comment="问题详细内容")
    
    # 关联回答
    answers = relationship("ZhihuAnswer", back_populates="question",
                          cascade="all, delete-orphan")

class ZhihuAnswer(BaseModel):
    __tablename__ = "zhihu_answers"
    
    question_id = Column(Integer, ForeignKey("zhihu_questions.id"), nullable=False)
    answer_id = Column(String(50), unique=True, nullable=False, comment="回答ID")
    author = Column(String(200), comment="作者")
    content = Column(Text, nullable=False, comment="回答内容(纯文本)")
    vote_count = Column(Integer, default=0, comment="赞同数")
    
    # 关联问题
    question = relationship("ZhihuQuestion", back_populates="answers")
```

### 开源之夏模型 (models/ospp_project.py)

```python
from sqlalchemy import Column, String, Text, ARRAY
from models.base import BaseModel

class OsppProject(BaseModel):
    __tablename__ = "ospp_projects"
    
    project_id = Column(String(50), unique=True, nullable=False, comment="项目ID")
    name = Column(String(500), nullable=False, comment="项目名")
    difficulty = Column(String(50), comment="难度")
    tech_tags = Column(ARRAY(String), comment="技术标签列表")
    description = Column(Text, comment="项目简述")
    requirements = Column(Text, comment="产出要求")
    pdf_url = Column(String(500), comment="申请书PDF链接")
    pdf_local_path = Column(String(1000), comment="PDF本地路径")
```

## API 接口实现示例

### FastAPI 路由 (api/v1/fzu_notice.py)

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from api.deps import get_db
from schemas.fzu_notice import FzuNoticeRequest, FzuNoticeResponse, StartFzuCrawlerRequest
from crawlers.fzu_notice import FzuNoticeCrawler
from tasks.crawler_tasks import start_fzu_crawler_task

router = APIRouter(prefix="/fzu", tags=["福大教务通知"])

@router.post("/start-crawler")
async def start_crawler(
    request: StartFzuCrawlerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """启动福大通知爬虫 (异步任务)"""
    # 使用 Celery 异步任务
    task = start_fzu_crawler_task.delay(request.target_count)
    return {
        "task_id": task.id,
        "message": "Crawler task started"
    }

@router.get("/notices", response_model=FzuNoticeResponse)
async def get_notices(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """查询福大通知列表"""
    # 实现分页查询逻辑
    pass

@router.get("/notices/{notice_id}")
async def get_notice_detail(
    notice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取通知详情"""
    pass

@router.post("/export-csv")
async def export_to_csv(
    output_path: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """导出为 CSV"""
    pass
```

## 具体爬虫实现示例

### 福大教务通知爬虫 (crawlers/fzu_notice.py)

```python
from typing import List, Dict, Any
from lxml import etree
from core.http_crawler import HttpCrawler
from models.fzu_notice import FzuNotice, FzuNoticeAttachment
from core.parser import Parser

class FzuNoticeCrawler(HttpCrawler):
    """福大教务通知爬虫"""
    
    BASE_URL = "https://jwch.fzu.edu.cn"
    LIST_URL = "https://jwch.fzu.edu.cn/jxtz.htm"
    
    async def fetch(self, target_count: int = 500, **kwargs) -> List[Dict[str, Any]]:
        """
        获取通知列表
        
        实现要点:
        1. 分析网页分页规律 (jxtz.htm, jxtz/list2.htm, ...)
        2. 循环请求每一页
        3. 使用 XPath 提取通知列表
        """
        notices = []
        page = 0
        
        while len(notices) < target_count:
            if page == 0:
                url = self.LIST_URL
            else:
                url = f"{self.BASE_URL}/jxtz/list{page + 1}.htm"
            
            response = await self.get(url)
            html = response.text
            
            # XPath 提取列表项
            tree = etree.HTML(html)
            items = tree.xpath('//ul[@class="news_list list-left"]/li')
            
            if not items:
                break
            
            for item in items:
                notice_data = {
                    'title': item.xpath('.//a/@title')[0] if item.xpath('.//a/@title') else '',
                    'detail_url': self.BASE_URL + item.xpath('.//a/@href')[0],
                    'date': item.xpath('.//span[@class="news_meta"]/text()')[0].strip(),
                    'publisher': self._extract_publisher(item.xpath('.//a/@title')[0])
                }
                notices.append(notice_data)
            
            page += 1
        
        return notices[:target_count]
    
    def _extract_publisher(self, title: str) -> str:
        """从标题中提取发布者 (质量办、计划科等)"""
        # 使用正则或字符串处理提取
        import re
        match = re.search(r'【(.+?)】', title)
        return match.group(1) if match else "未知"
    
    async def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单条通知详情
        
        实现要点:
        1. 请求详情页
        2. 提取正文HTML
        3. 提取附件信息 (名称、下载次数、链接)
        4. 清理文本
        """
        detail_url = raw_data['detail_url']
        response = await self.get(detail_url)
        html = response.text
        tree = etree.HTML(html)
        
        # 提取正文
        content = tree.xpath('//div[@class="wp_articlecontent"]')[0]
        html_content = etree.tostring(content, encoding='unicode')
        
        # 提取附件
        attachments = []
        attachment_items = tree.xpath('//div[@class="wp_article_attach_list"]//li')
        for item in attachment_items:
            att = {
                'name': Parser.clean_text(item.xpath('.//a/text()')[0]),
                'url': item.xpath('.//a/@href')[0],
                'download_count': self._extract_download_count(item)
            }
            attachments.append(att)
        
        return {
            **raw_data,
            'html_content': html_content,
            'attachments': attachments
        }
    
    def _extract_download_count(self, item) -> int:
        """提取下载次数"""
        # 从页面中提取下载次数逻辑
        pass
    
    async def save(self, data: Dict[str, Any]) -> None:
        """保存到数据库"""
        notice = FzuNotice(
            publisher=data['publisher'],
            title=Parser.clean_text(data['title']),
            publish_date=data['date'],
            detail_url=data['detail_url'],
            html_content=data['html_content']
        )
        
        self.db_session.add(notice)
        await self.db_session.flush()  # 获取 notice.id
        
        # 保存附件
        for att_data in data['attachments']:
            attachment = FzuNoticeAttachment(
                notice_id=notice.id,
                name=att_data['name'],
                download_count=att_data['download_count'],
                url=att_data['url']
            )
            self.db_session.add(attachment)
```

### 知乎话题爬虫 (crawlers/zhihu_topic.py)

```python
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from core.selenium_crawler import SeleniumCrawler
from models.zhihu_topic import ZhihuQuestion, ZhihuAnswer
import time

class ZhihuTopicCrawler(SeleniumCrawler):
    """知乎话题爬虫"""
    
    async def fetch(self, topic_url: str, question_count: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """
        获取话题下的问题列表
        
        实现要点:
        1. 使用 Selenium 模拟浏览器
        2. 处理登录 (Cookie 或扫码)
        3. 滚动加载更多内容
        4. 提取问题链接
        """
        self.driver.get(topic_url)
        time.sleep(3)  # 等待页面加载
        
        # TODO: 处理登录 (可以提前保存 Cookie)
        
        questions = []
        scroll_count = 0
        max_scrolls = 10
        
        while len(questions) < question_count and scroll_count < max_scrolls:
            # 提取当前页面的问题
            question_elements = self.driver.find_elements(By.CSS_SELECTOR, '.List-item')
            
            for elem in question_elements:
                if len(questions) >= question_count:
                    break
                
                try:
                    question_data = {
                        'title': elem.find_element(By.CSS_SELECTOR, 'h2').text,
                        'url': elem.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
                    }
                    if question_data not in questions:
                        questions.append(question_data)
                except:
                    continue
            
            # 滚动加载更多
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            scroll_count += 1
        
        return questions[:question_count]
    
    async def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析问题详情和回答
        
        实现要点:
        1. 访问问题页面
        2. 提取问题详细内容
        3. 提取回答列表 (限制数量)
        4. 提取回答的纯文本内容
        """
        question_url = raw_data['url']
        self.driver.get(question_url)
        time.sleep(2)
        
        # 提取问题内容
        try:
            content_elem = self.driver.find_element(By.CSS_SELECTOR, '.QuestionRichText')
            content = content_elem.text
        except:
            content = ""
        
        # 提取回答
        answers = []
        answer_elements = self.driver.find_elements(By.CSS_SELECTOR, '.List-item')[:10]
        
        for elem in answer_elements:
            try:
                answer_data = {
                    'author': elem.find_element(By.CSS_SELECTOR, '.AuthorInfo-name').text,
                    'content': elem.find_element(By.CSS_SELECTOR, '.RichContent-inner').text,
                    'vote_count': self._extract_vote_count(elem)
                }
                answers.append(answer_data)
            except:
                continue
        
        return {
            'title': raw_data['title'],
            'content': content,
            'answers': answers,
            'question_id': self._extract_question_id(question_url)
        }
    
    def _extract_vote_count(self, element) -> int:
        """提取赞同数"""
        try:
            vote_text = element.find_element(By.CSS_SELECTOR, '.VoteButton--up').text
            return int(vote_text) if vote_text.isdigit() else 0
        except:
            return 0
    
    def _extract_question_id(self, url: str) -> str:
        """从URL提取问题ID"""
        import re
        match = re.search(r'/question/(\d+)', url)
        return match.group(1) if match else ""
    
    async def save(self, data: Dict[str, Any]) -> None:
        """保存到数据库"""
        question = ZhihuQuestion(
            question_id=data['question_id'],
            topic_id=data.get('topic_id', ''),
            title=data['title'],
            content=data['content']
        )
        
        self.db_session.add(question)
        await self.db_session.flush()
        
        # 保存回答
        for ans_data in data['answers']:
            answer = ZhihuAnswer(
                question_id=question.id,
                answer_id=ans_data.get('answer_id', ''),
                author=ans_data['author'],
                content=ans_data['content'],
                vote_count=ans_data['vote_count']
            )
            self.db_session.add(answer)
```

### 开源之夏爬虫 (crawlers/ospp_project.py)

```python
from typing import List, Dict, Any
import json
from core.http_crawler import HttpCrawler
from models.ospp_project import OsppProject

class OsppProjectCrawler(HttpCrawler):
    """开源之夏项目爬虫"""
    
    API_URL = "https://summer-ospp.ac.cn/api/projects"  # 假设的API地址
    
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        通过抓包找到的API获取项目列表
        
        实现要点:
        1. 使用浏览器开发者工具找到API接口
        2. 分析请求参数 (分页、筛选等)
        3. 模拟请求获取JSON数据
        """
        all_projects = []
        page = 1
        page_size = 50
        
        while True:
            params = {
                'page': page,
                'pageSize': page_size,
                'year': 2025
            }
            
            response = await self.get(self.API_URL, params=params)
            data = response.json()
            
            projects = data.get('data', {}).get('list', [])
            if not projects:
                break
            
            all_projects.extend(projects)
            
            # 检查是否还有下一页
            if len(projects) < page_size:
                break
            
            page += 1
        
        return all_projects
    
    async def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析项目详情
        
        实现要点:
        1. 提取项目基本信息
        2. 如果需要更详细信息,请求项目详情API
        3. 提取PDF链接 (进阶)
        """
        project_id = raw_data.get('id')
        
        # 请求详情API (如果有)
        detail_url = f"{self.API_URL}/{project_id}"
        response = await self.get(detail_url)
        detail_data = response.json().get('data', {})
        
        return {
            'project_id': str(project_id),
            'name': detail_data.get('name', ''),
            'difficulty': detail_data.get('difficulty', ''),
            'tech_tags': detail_data.get('techTags', []),
            'description': detail_data.get('description', ''),
            'requirements': detail_data.get('requirements', ''),
            'pdf_url': detail_data.get('pdfUrl', '')
        }
    
    async def save(self, data: Dict[str, Any]) -> None:
        """保存到数据库"""
        project = OsppProject(
            project_id=data['project_id'],
            name=data['name'],
            difficulty=data['difficulty'],
            tech_tags=data['tech_tags'],
            description=data['description'],
            requirements=data['requirements'],
            pdf_url=data['pdf_url']
        )
        
        self.db_session.add(project)
```

## 配置文件

### 应用配置 (config/settings.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Crawler Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/crawler"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 爬虫配置
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    DOWNLOAD_DIR: str = "./downloads"
    
    # Selenium 配置
    SELENIUM_HEADLESS: bool = True
    CHROME_DRIVER_PATH: str = "/usr/local/bin/chromedriver"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 数据库配置 (config/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.settings import get_settings

settings = get_settings()

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 创建异步会话工厂
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncSession:
    """依赖注入: 获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Celery 任务配置 (tasks/celery_app.py)

```python
from celery import Celery
from config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "crawler_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    task_soft_time_limit=3300,  # 55分钟软超时
)
```

## 开发流程

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装项目依赖
pip install -r requirements.txt

# 安装 sql-gen 工具依赖
pip install -r pkg/sql-gen/requirements.txt

# 安装 Protobuf 工具
pip install grpcio-tools

# 安装 PostgreSQL (使用 Homebrew)
brew install postgresql@14
brew services start postgresql@14

# 创建数据库
createdb crawler

# 创建数据库用户
createuser -s go-mcp-demo
psql -c "ALTER USER \"go-mcp-demo\" WITH PASSWORD 'go-mcp-demo';"
```

### 2. 配置文件设置

编辑 `config/config.yaml`:

```yaml
pgsql:
  host: "127.0.0.1"
  port: 5432
  database: "crawler"
  user: "go-mcp-demo"
  password: "go-mcp-demo"

ai_provider:  # 可选，用于 AI 功能
  model: "qwen3-vl-flash"
  remote:
    provider: "aliyun"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key: "your-api-key"
```

### 3. 代码生成工作流

#### 步骤 1: 生成 Protobuf API 代码

```bash
# 使用 Makefile
make proto

# 或手动执行
python -m grpc_tools.protoc \
    -I./idl \
    --python_out=./api/generated \
    --grpc_python_out=./api/generated \
    --pyi_out=./api/generated \
    ./idl/crawler.proto
```

#### 步骤 2: 设计数据库表结构

在 PostgreSQL 中创建表：

```sql
-- 福大教务通知表
CREATE TABLE fzu_notices (
    id SERIAL PRIMARY KEY,
    publisher VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    publish_date VARCHAR(20) NOT NULL,
    detail_url VARCHAR(500) UNIQUE NOT NULL,
    html_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 附件表
CREATE TABLE fzu_notice_attachments (
    id SERIAL PRIMARY KEY,
    notice_id INTEGER REFERENCES fzu_notices(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    download_count INTEGER DEFAULT 0,
    url VARCHAR(500) NOT NULL,
    local_path VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 知乎问题表
CREATE TABLE zhihu_questions (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(50) UNIQUE NOT NULL,
    topic_id VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 知乎回答表
CREATE TABLE zhihu_answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES zhihu_questions(id) ON DELETE CASCADE,
    answer_id VARCHAR(50) UNIQUE NOT NULL,
    author VARCHAR(200),
    content TEXT NOT NULL,
    vote_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 开源之夏项目表
CREATE TABLE ospp_projects (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    difficulty VARCHAR(50),
    tech_tags TEXT[],  -- PostgreSQL 数组类型
    description TEXT,
    requirements TEXT,
    pdf_url VARCHAR(500),
    pdf_local_path VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

#### 步骤 3: 生成数据库模型

```bash
# 使用 Makefile
make model

# 或手动执行
python pkg/sql-gen/main.py --config pkg/sql-gen/config.yaml

# 生成指定表的模型
python pkg/sql-gen/main.py -t fzu_notices fzu_notice_attachments

# 列出所有表
python pkg/sql-gen/main.py --list-tables
```

生成的模型会在 `pkg/sql-gen/generated_models/` 目录，需要手动复制到 `models/` 目录：

```bash
# 复制生成的模型
cp pkg/sql-gen/generated_models/*.py models/
```

#### 步骤 4: 一键生成所有代码

```bash
make gen  # 生成 API + 模型
```

### 4. 开发业务逻辑

#### 创建爬虫实现

在 `internal/infra/external/` 创建具体的爬虫实现：

```python
# internal/infra/external/fzu_crawler.py
from pkg.crawler.http_crawler import HttpCrawler

class FzuNoticeCrawler(HttpCrawler):
    async def fetch(self, **kwargs):
        # 实现爬取逻辑
        pass
    
    async def parse(self, raw_data):
        # 实现解析逻辑
        pass
```

#### 创建仓储实现

在 `internal/infra/persistence/` 实现数据持久化：

```python
# internal/infra/persistence/fzu_repo_impl.py
from internal.domain.repository.fzu_repository import FzuRepository
from models.fzu_notices import FzuNotices

class FzuRepositoryImpl(FzuRepository):
    def __init__(self, db_session):
        self.db = db_session
    
    async def save(self, notice_data):
        # 保存到数据库
        pass
    
    async def find_all(self, page, page_size):
        # 查询数据
        pass
```

#### 创建应用服务

在 `internal/application/` 编排业务流程：

```python
# internal/application/fzu_service.py
class FzuNoticeService:
    def __init__(self, repository, crawler):
        self.repository = repository
        self.crawler = crawler
    
    async def start_crawl(self, target_count):
        # 1. 调用爬虫获取数据
        data = await self.crawler.run(target_count=target_count)
        
        # 2. 保存到数据库
        for item in data:
            await self.repository.save(item)
        
        return {"success": True, "count": len(data)}
    
    async def get_notices(self, page, page_size):
        return await self.repository.find_all(page, page_size)
```

### 5. 测试运行

```bash
# 测试爬虫
python scripts/run_crawler.py --crawler fzu --count 500

# 测试数据库连接
python -c "from models import Base; print('Models loaded successfully')"

# 测试 Protobuf
python -c "from api.generated import FzuNoticeRequest; print('Protobuf loaded')"
```

## 依赖清单

### 主项目依赖 (requirements.txt)

```txt
# 数据库
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# 爬虫相关
httpx==0.25.2
lxml==4.9.3
selenium==4.15.2

# 配置
pyyaml==6.0.1

# Protobuf
protobuf==4.25.1
grpcio==1.60.0
grpcio-tools==1.60.0

# Web 框架 (可选)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# 测试 (可选)
pytest==7.4.3
pytest-asyncio==0.21.1
```

### sql-gen 工具依赖 (pkg/sql-gen/requirements.txt)

```txt
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
pyyaml==6.0.1
typing-extensions==4.9.0
```

## 开发建议

### 1. 代码组织
- 保持爬虫逻辑独立,便于复用
- 使用依赖注入管理数据库连接
- 遵循单一职责原则

### 2. 错误处理
- 网络请求添加重试机制
- 解析失败时记录日志但不中断流程
- 使用 try-except 包裹关键代码

### 3. 性能优化
- 使用异步 I/O (async/await)
- 合理使用连接池
- 避免在循环中进行数据库操作

### 4. 数据清洗
- 统一的文本清洗函数
- 去除 HTML 标签
- 处理特殊字符

### 5. 反爬应对
- 设置合理的请求间隔
- 使用代理池 (如需要)
- 轮换 User-Agent
- 处理 Cookie 和 Session

### 6. 日志记录
- 使用 loguru 记录详细日志
- 区分不同级别 (DEBUG, INFO, ERROR)
- 记录关键操作和异常

## CSV 导出示例 (utils/csv_writer.py)

```python
import csv
from typing import List, Dict, Any
from pathlib import Path

class CsvWriter:
    """CSV 导出工具"""
    
    @staticmethod
    async def write_fzu_notices(notices: List[Dict[str, Any]], output_path: str):
        """导出福大通知到 CSV"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['ID', '通知人', '标题', '日期', '详情链接', '附件数量']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for notice in notices:
                writer.writerow({
                    'ID': notice['id'],
                    '通知人': notice['publisher'],
                    '标题': notice['title'],
                    '日期': notice['publish_date'],
                    '详情链接': notice['detail_url'],
                    '附件数量': len(notice.get('attachments', []))
                })
    
    @staticmethod
    async def write_zhihu_topics(questions: List[Dict[str, Any]], output_path: str):
        """导出知乎话题到 CSV"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['问题ID', '问题标题', '问题内容', '回答数', '回答内容']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for question in questions:
                for answer in question.get('answers', []):
                    writer.writerow({
                        '问题ID': question['question_id'],
                        '问题标题': question['title'],
                        '问题内容': question['content'],
                        '回答数': len(question.get('answers', [])),
                        '回答内容': answer['content']
                    })
```

## 快速开始清单

### 新项目初始化

```bash
# 1. 克隆项目
git clone <your-repo>
cd crawler

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
pip install -r pkg/sql-gen/requirements.txt

# 4. 配置数据库
createdb crawler
# 编辑 config/config.yaml

# 5. 创建数据库表
psql -d crawler -f schema.sql

# 6. 生成代码
make gen  # 生成 API + 模型

# 7. 开始开发
# - 在 internal/infra/external/ 实现爬虫
# - 在 internal/infra/persistence/ 实现仓储
# - 在 internal/application/ 实现应用服务
```

### 常用命令

```bash
# 代码生成
make proto          # 生成 Protobuf API
make model          # 生成数据库模型
make gen            # 生成所有代码

# 查看数据库表
make model --list-tables

# 运行测试
pytest tests/

# 代码格式化
black .
isort .
```

## 架构优势

### 1. **清晰的分层结构**
- API 层：接口定义
- 应用层：业务编排
- 领域层：核心业务
- 基础设施层：技术实现

### 2. **高度可测试**
- 每层独立测试
- 接口依赖注入
- Mock 友好

### 3. **易于维护**
- 关注点分离
- 低耦合高内聚
- 业务逻辑与技术实现解耦

### 4. **扩展性强**
- 新增爬虫：继承 `BaseCrawler`
- 新增数据源：实现 `Repository` 接口
- 新增业务：在应用层编排

### 5. **代码生成**
- IDL → API 代码（Protobuf）
- 数据库 → 模型代码（sql-gen）
- 减少重复劳动

## 常见问题

### Q1: 为什么要分这么多层？
**A**: 遵循 Clean Architecture 原则，保证：
- 业务逻辑不依赖框架
- 易于测试
- 技术栈可替换

### Q2: 爬虫为什么不直接保存数据？
**A**: 遵循单一职责原则：
- 爬虫只负责数据获取和解析
- 仓储负责数据持久化
- 便于单元测试和复用

### Q3: 为什么使用 Protobuf？
**A**: 
- 强类型约束
- 跨语言支持
- 接口即文档
- 便于前后端协作

### Q4: sql-gen 生成的模型如何使用？
**A**: 
```bash
# 生成模型
make model

# 复制到项目
cp pkg/sql-gen/generated_models/*.py models/

# 在代码中使用
from models.fzu_notices import FzuNotices
```

## 进阶扩展

### 1. 添加缓存层
在 `internal/infra/` 添加 Redis 缓存实现

### 2. 添加消息队列
使用 Celery 处理异步爬虫任务

### 3. 添加监控
- Prometheus + Grafana
- 爬虫任务监控
- 性能指标收集

### 4. 容器化部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 参考资料

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Protocol Buffers](https://protobuf.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 总结

这个项目架构具有以下特点：

1. **DDD + Clean Architecture**：清晰的分层和职责划分
2. **代码生成驱动**：IDL → API，数据库 → 模型
3. **高度模块化**：爬虫引擎、模型生成器独立可复用
4. **易于扩展**：新增功能只需实现接口
5. **生产就绪**：完整的错误处理、日志、测试支持

## 下一步

1. ✅ 完成环境搭建和配置
2. ✅ 生成 API 和模型代码
3. 🔲 实现福大教务通知爬虫
4. 🔲 实现知乎话题爬虫
5. 🔲 实现开源之夏爬虫
6. 🔲 编写单元测试
7. 🔲 添加 FastAPI HTTP 服务（可选）
8. 🔲 容器化部署（可选）

有问题随时提问！🚀

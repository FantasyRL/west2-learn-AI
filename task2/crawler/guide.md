# 爬虫项目开发指南

## 项目概述

本项目是一个基于 Python 的通用爬虫平台,支持多种爬虫任务的统一管理和调度。采用前后端分离架构,通过 HTTP API 提供服务,数据持久化到 PostgreSQL 数据库。

### 核心特性

- **可复用的爬虫核心引擎**:抽象出通用的爬虫组件,支持快速扩展新的爬虫任务
- **统一的 API 接口**:通过 Protocol Buffers 定义接口规范
- **数据持久化**:使用 PostgreSQL + SQLAlchemy ORM
- **任务调度**:支持异步任务和定时任务
- **灵活配置**:支持多种爬虫策略(requests、Selenium、API 调用)

## 技术选型

### 1. Web 框架
**FastAPI** - 现代化的 Python Web 框架

**选型理由**:
- 原生支持 async/await,性能优异
- 自动生成 OpenAPI 文档
- 类型提示支持,开发体验好
- 与 Pydantic 深度集成

### 2. ORM 框架
**SQLAlchemy 2.0 + Alembic**

**选型理由**:
- SQLAlchemy 是 Python 生态最成熟的 ORM
- 2.0 版本支持类型提示,类似 GORM 的链式调用
- Alembic 提供数据库迁移功能
- 支持异步操作 (sqlalchemy.ext.asyncio)

**代码生成工具**: sqlacodegen (类似 gorm-gen)
```bash
sqlacodegen postgresql://user:pass@localhost/dbname --outfile models.py
```

### 3. IDL 定义
**Protocol Buffers (protobuf)** + **grpcio-tools**

**选型理由**:
- 跨语言支持
- 强类型约束
- 自动生成代码
- FastAPI 可以通过 protobuf-to-pydantic 转换为 Pydantic 模型

### 4. 爬虫相关库
- **requests**: HTTP 请求
- **selenium**: 浏览器自动化
- **lxml**: XPath 解析
- **BeautifulSoup4**: HTML 解析 (备选)
- **httpx**: 异步 HTTP 客户端

### 5. 任务调度
**Celery** + **Redis**

**选型理由**:
- 成熟的分布式任务队列
- 支持定时任务
- 支持任务重试和失败处理

## 项目结构

```
crawler/
├── __init__.py
├── guide.md                    # 本文档
├── requirements.txt            # 依赖包
├── config/                     # 配置文件
│   ├── __init__.py
│   ├── settings.py            # 应用配置
│   └── database.py            # 数据库配置
├── proto/                      # Protocol Buffers 定义
│   ├── crawler.proto          # 爬虫服务接口定义
│   └── generated/             # 自动生成的 Python 代码
│       ├── __init__.py
│       └── crawler_pb2.py
├── models/                     # 数据库模型
│   ├── __init__.py
│   ├── base.py                # 基础模型类
│   ├── fzu_notice.py          # 福大通知模型
│   ├── zhihu_topic.py         # 知乎话题模型
│   └── ospp_project.py        # 开源之夏项目模型
├── schemas/                    # Pydantic 数据模型
│   ├── __init__.py
│   ├── fzu_notice.py
│   ├── zhihu_topic.py
│   └── ospp_project.py
├── core/                       # 核心爬虫引擎
│   ├── __init__.py
│   ├── base_crawler.py        # 抽象基类
│   ├── http_crawler.py        # HTTP 爬虫基类
│   ├── selenium_crawler.py    # Selenium 爬虫基类
│   ├── parser.py              # 数据解析器
│   ├── downloader.py          # 文件下载器
│   └── middleware.py          # 中间件 (请求重试、日志等)
├── crawlers/                   # 具体爬虫实现
│   ├── __init__.py
│   ├── fzu_notice.py          # 作业1: 福大教务通知
│   ├── zhihu_topic.py         # 作业2: 知乎话题
│   └── ospp_project.py        # 作业3: 开源之夏
├── api/                        # API 接口
│   ├── __init__.py
│   ├── deps.py                # 依赖注入
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── fzu_notice.py      # 福大通知接口
│   │   ├── zhihu_topic.py     # 知乎话题接口
│   │   └── ospp_project.py    # 开源之夏接口
│   └── router.py              # 路由汇总
├── tasks/                      # Celery 任务
│   ├── __init__.py
│   ├── celery_app.py          # Celery 配置
│   └── crawler_tasks.py       # 爬虫异步任务
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── logger.py              # 日志配置
│   ├── csv_writer.py          # CSV 导出
│   └── validators.py          # 数据验证
├── migrations/                 # 数据库迁移
│   └── versions/
├── tests/                      # 测试
│   ├── __init__.py
│   ├── test_crawlers/
│   └── test_api/
├── main.py                     # FastAPI 应用入口
├── alembic.ini                # Alembic 配置
└── README.md                   # 项目说明
```

## 核心设计

### 1. 爬虫基类设计 (core/base_crawler.py)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class BaseCrawler(ABC):
    """爬虫抽象基类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = get_logger(self.__class__.__name__)
    
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
    
    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> None:
        """
        保存数据到数据库
        """
        pass
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        执行完整的爬虫流程
        返回: 执行结果统计
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
            
            # 3. 保存数据
            success_count = 0
            for data in parsed_data_list:
                try:
                    await self.save(data)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Save error: {e}")
                    continue
            
            await self.db_session.commit()
            
            return {
                "total": len(raw_data_list),
                "parsed": len(parsed_data_list),
                "saved": success_count
            }
        except Exception as e:
            await self.db_session.rollback()
            self.logger.error(f"Crawler run error: {e}")
            raise
```

### 2. HTTP 爬虫基类 (core/http_crawler.py)

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

## Protocol Buffers 接口定义 (proto/crawler.proto)

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

# 安装依赖
pip install -r requirements.txt

# 安装 PostgreSQL (使用 Homebrew)
brew install postgresql@14
brew services start postgresql@14

# 创建数据库
createdb crawler

# 安装 Redis
brew install redis
brew services start redis
```

### 2. 初始化数据库

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 3. 生成 Protobuf 代码

```bash
# 安装工具
pip install grpcio-tools protobuf-to-pydantic

# 生成 Python 代码
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    ./proto/crawler.proto

# 转换为 Pydantic 模型 (用于 FastAPI)
# 手动或使用工具转换
```

### 4. 启动服务

```bash
# 启动 FastAPI 应用
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker
celery -A tasks.celery_app worker --loglevel=info

# 启动 Celery Beat (定时任务)
celery -A tasks.celery_app beat --loglevel=info
```

### 5. 测试爬虫

```bash
# 使用 curl 或 httpie 测试
curl -X POST http://localhost:8000/api/v1/fzu/start-crawler \
  -H "Content-Type: application/json" \
  -d '{"target_count": 500}'

# 查询结果
curl http://localhost:8000/api/v1/fzu/notices?page=1&page_size=20
```

## 依赖清单 (requirements.txt)

```txt
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# 数据库
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.0
psycopg2-binary==2.9.9

# ORM 工具
sqlacodegen==3.0.0rc5

# 爬虫相关
requests==2.31.0
httpx==0.25.2
lxml==4.9.3
beautifulsoup4==4.12.2
selenium==4.15.2
webdriver-manager==4.0.1

# 任务队列
celery==5.3.4
redis==5.0.1

# Protobuf
protobuf==4.25.1
grpcio==1.60.0
grpcio-tools==1.60.0

# 工具库
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# 测试
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# 日志
loguru==0.7.2
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

## 总结

这个项目架构具有以下特点:

1. **高度模块化**: 核心爬虫引擎与具体实现分离
2. **可扩展性强**: 新增爬虫只需继承基类并实现三个方法
3. **技术栈现代**: 使用 FastAPI + SQLAlchemy 2.0 + async/await
4. **接口规范**: 通过 Protobuf 定义清晰的接口契约
5. **生产就绪**: 包含异步任务、数据库迁移、错误处理等完整功能

## 下一步

1. 完善配置文件 (.env)
2. 实现具体的爬虫逻辑
3. 编写单元测试
4. 添加 API 文档 (FastAPI 自动生成)
5. 部署上线 (Docker + Nginx)

有问题随时提问! 🚀

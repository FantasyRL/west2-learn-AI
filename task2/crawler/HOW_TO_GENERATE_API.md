# 如何通过 IDL 生成 API 代码

## 快速开始

### 方法一：使用 Makefile（推荐）

```bash
make proto
```

### 方法二：使用命令行

```bash
python -m grpc_tools.protoc \
    -I./idl \
    --python_out=./api/generated \
    --grpc_python_out=./api/generated \
    --pyi_out=./api/generated \
    ./idl/crawler.proto
```

### 方法三：使用脚本

```bash
chmod +x scripts/generate_proto.sh
./scripts/generate_proto.sh
```

## 前置条件

### 1. 安装依赖

```bash
pip install grpcio-tools
```

### 2. 确保目录结构

```
crawler/
├── idl/
│   └── crawler.proto    # IDL 定义文件
└── api/
    └── generated/       # 生成代码输出目录
```

## 生成的文件

运行后会在 `api/generated/` 目录生成：

```
api/generated/
├── __init__.py              # 模块初始化
├── crawler_pb2.py           # Protobuf 消息定义
├── crawler_pb2.pyi          # Python 类型提示
└── crawler_pb2_grpc.py      # gRPC 服务定义
```

## 使用生成的代码

### 1. 导入消息类型

```python
from api.generated.crawler_pb2 import (
    FzuNoticeRequest,
    FzuNoticeResponse,
    FzuNotice,
    Attachment,
    CrawlerResult,
)

# 创建请求
request = FzuNoticeRequest(
    page=1,
    page_size=20,
    keyword="通知"
)

# 创建响应
response = FzuNoticeResponse(
    notices=[],
    total=0,
    message="成功"
)
```

### 2. 使用 gRPC 服务（如果需要）

```python
from api.generated.crawler_pb2_grpc import (
    CrawlerServiceServicer,
    add_CrawlerServiceServicer_to_server,
)

class MyCrawlerService(CrawlerServiceServicer):
    async def StartFzuCrawler(self, request, context):
        # 实现服务逻辑
        return CrawlerResult(
            success=True,
            message="爬虫启动成功",
            crawled_count=0
        )
```

### 3. 转换为 Pydantic（用于 FastAPI）

```python
from pydantic import BaseModel
from typing import Optional

class FzuNoticeRequest(BaseModel):
    """对应 Protobuf 的 FzuNoticeRequest"""
    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None
```

## 添加到 Makefile

在项目根目录的 `Makefile` 中添加：

```makefile
# 生成 Protobuf API 代码
.PHONY: proto
proto:
	@echo "🚀 生成 Protobuf API 代码..."
	@mkdir -p api/generated
	python -m grpc_tools.protoc \
		-I./idl \
		--python_out=./api/generated \
		--grpc_python_out=./api/generated \
		--pyi_out=./api/generated \
		./idl/crawler.proto
	@echo "✅ Protobuf 代码生成完成！"

# 生成数据库模型
.PHONY: model
model:
	@echo "🚀 生成数据库模型..."
	python pkg/sql-gen/main.py --config pkg/sql-gen/config.yaml
	@echo "✅ 数据库模型生成完成！"

# 生成所有代码
.PHONY: gen
gen: proto model
	@echo "✅ 所有代码生成完成！"

# 清理生成的代码
.PHONY: clean-gen
clean-gen:
	rm -rf api/generated/*
	rm -rf pkg/sql-gen/generated_models/*
	@echo "✅ 清理完成！"
```

## 完整工作流

```bash
# 1. 编辑 IDL 文件
vim idl/crawler.proto

# 2. 生成 API 代码
make proto

# 3. 查看生成的代码
ls -la api/generated/

# 4. 在代码中使用
# 编辑 internal/application/fzu_service.py
# from api.generated import FzuNoticeRequest, FzuNoticeResponse

# 5. 重新生成（如果修改了 IDL）
make clean-gen
make proto
```

## 常见问题

### Q: 为什么需要 --pyi_out？
**A**: 生成 Python 类型提示文件（.pyi），提供更好的 IDE 智能提示。

### Q: 生成的代码可以修改吗？
**A**: 不建议。应该修改 IDL 文件后重新生成。

### Q: 如何在 FastAPI 中使用？
**A**: 需要手动转换为 Pydantic 模型，或使用 `protobuf-to-pydantic` 库。

### Q: gRPC 和 HTTP API 有什么区别？
**A**: 
- gRPC：高性能的 RPC 框架，适合微服务间通信
- HTTP API：通用的 REST API，适合前后端通信

本项目主要使用 Protobuf 定义接口契约，可以根据需要选择实现方式。

## 参考链接

- [Protocol Buffers 官方文档](https://protobuf.dev/)
- [gRPC Python 教程](https://grpc.io/docs/languages/python/)
- [grpcio-tools 文档](https://grpc.io/docs/languages/python/quickstart/)

DIR=$(shell pwd)
GEN_CONFIG_PATH=$(DIR)/pkg/sql-gen/config.yaml

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
	@echo "📁 输出目录: api/generated/"

# 生成数据库模型
.PHONY: model
model:
	@echo "🚀 生成数据库模型..."
	python pkg/sql-gen/main.py --config $(GEN_CONFIG_PATH)
	@echo "📁 输出目录: pkg/sql-gen/generated_models/"
	@echo "💡 提示: 请手动复制模型到 models/ 目录"

# 列出所有数据库表
.PHONY: list-tables
list-tables:
	@echo "📊 数据库表列表:"
	python pkg/sql-gen/main.py --config $(GEN_CONFIG_PATH) --list-tables

# 生成指定表的模型
# 使用方式: make model-table TABLES="table1 table2"
.PHONY: model-table
model-table:
	@echo "🚀 生成指定表的模型..."
	python pkg/sql-gen/main.py --config $(GEN_CONFIG_PATH) -t $(TABLES)

# 生成所有代码（API + 模型）
.PHONY: gen
gen: proto model
	@echo ""
	@echo "✅ 所有代码生成完成！"
	@echo ""
	@echo "下一步操作:"
	@echo "  1. 查看生成的 API 代码: ls api/generated/"
	@echo "  2. 查看生成的模型: ls pkg/sql-gen/generated_models/"
	@echo "  3. 复制模型到项目: cp pkg/sql-gen/generated_models/*.py models/"

# 清理生成的代码
.PHONY: clean-gen
clean-gen:
	@echo "🧹 清理生成的代码..."
	rm -rf api/generated/*
	rm -rf pkg/sql-gen/generated_models/*
	@echo "✅ 清理完成！"

# 帮助信息
.PHONY: help
help:
	@echo "可用命令:"
	@echo "  make proto          - 生成 Protobuf API 代码"
	@echo "  make model          - 生成所有数据库模型"
	@echo "  make list-tables    - 列出所有数据库表"
	@echo "  make model-table    - 生成指定表的模型 (TABLES='table1 table2')"
	@echo "  make gen            - 生成所有代码 (API + 模型)"
	@echo "  make clean-gen      - 清理生成的代码"
	@echo "  make help           - 显示此帮助信息"
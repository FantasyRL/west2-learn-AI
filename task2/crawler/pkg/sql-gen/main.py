"""SQL 模型生成器主程序"""
import sys
import argparse
from pathlib import Path
from config_loader import load_config
from db_inspector import DatabaseInspector
from model_generator import ModelGenerator


def print_banner():
    """打印欢迎信息"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        SQLAlchemy Model Generator (GORM-Gen Style)        ║
║                                                           ║
║        从 PostgreSQL 数据库生成 SQLAlchemy 模型           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从数据库生成 SQLAlchemy 模型')
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    parser.add_argument(
        '-o', '--output',
        default='models',
        help='输出目录 (默认: models)'
    )
    parser.add_argument(
        '-t', '--tables',
        nargs='+',
        help='指定要生成的表名 (不指定则生成所有表)'
    )
    parser.add_argument(
        '--list-tables',
        action='store_true',
        help='仅列出所有表名'
    )
    
    args = parser.parse_args()
    
    try:
        # 打印欢迎信息
        print_banner()
        
        # 加载配置
        print(f"📖 加载配置文件: {args.config}")
        config = load_config(args.config)
        
        print(f"🔌 连接数据库: {config.pgsql.host}:{config.pgsql.port}/{config.pgsql.database}")
        
        # 创建数据库检查器
        inspector = DatabaseInspector(config.pgsql)
        
        # 获取所有表
        all_tables = inspector.get_all_tables()
        
        if not all_tables:
            print("⚠️  数据库中没有找到任何表")
            return
        
        print(f"📊 找到 {len(all_tables)} 个表")
        
        # 如果只是列出表名
        if args.list_tables:
            print("\n数据库中的表:")
            print("=" * 60)
            for i, table in enumerate(all_tables, 1):
                print(f"  {i}. {table}")
            print("=" * 60)
            return
        
        # 确定要生成的表
        if args.tables:
            tables_to_generate = [t for t in args.tables if t in all_tables]
            not_found = [t for t in args.tables if t not in all_tables]
            
            if not_found:
                print(f"⚠️  以下表不存在: {', '.join(not_found)}")
            
            if not tables_to_generate:
                print("❌ 没有找到要生成的表")
                return
        else:
            tables_to_generate = all_tables
        
        print(f"🎯 将生成 {len(tables_to_generate)} 个表的模型:")
        for table in tables_to_generate:
            print(f"   • {table}")
        
        # 获取表信息
        print("\n🔍 分析表结构...")
        tables_info = []
        for table in tables_to_generate:
            try:
                info = inspector.get_table_info(table)
                tables_info.append(info)
                print(f"   ✓ {table} ({len(info['columns'])} 列)")
            except Exception as e:
                print(f"   ✗ {table} - 失败: {e}")
        
        # 生成模型
        generator = ModelGenerator(output_dir=args.output)
        generator.generate_all_models(tables_info)
        
        # 关闭数据库连接
        inspector.close()
        
        print("✅ 所有模型生成完成!")
        print(f"\n📁 模型文件位置: {Path(args.output).absolute()}")
        print("\n💡 使用方法:")
        print(f"   from {args.output} import Base, YourModelName")
        
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class BaseCrawler(ABC):
    def __init__(self):
        # logger
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()  # 控制台输出日志
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        pass

    """
    async是并发（go func()）
    抽象方法是定义在抽象类中的方法，意味着这个方法在基类中没有具体实现，
    子类需要实现它。抽象类是不能实例化的，只能作为其他类的基类
    kwargs 代表函数或方法接受任意数量的关键字参数kv(name="Alice", age=30...)
    Dict 字典 [k,v]
    """
    @abstractmethod
    async def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        抓取数据的主方法
        :param kwargs: 可选参数
        :return: 抓取到的数据列表
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
        运行爬虫的主流程
        :param kwargs: 可选参数
        :return: 结果字典，包含成功和失败的数量
        """
        try:
            """
            await 挂起自身，等待异步操作完成后继续执行(在线程内切换)
            f"Fetched {len(raw_data_list)} " f允许在字符串中嵌入表达式
            try-except 捕获异常
            """
            # 获取数据
            raw_data_list = await self.fetch(**kwargs)
            self.logger.info(f"Fetched {len(raw_data_list)} items")

            # 解析数据
            parsed_data_list = []
            for raw_data in raw_data_list:
                try:
                    parsed_data = await self.parse(raw_data)
                    parsed_data_list.append(parsed_data)
                except Exception as e:
                    self.logger.error(f"Error parsing data: {e}")
                    continue

            return parsed_data_list

        except Exception as e:
            self.logger.error(f"Error in run: {e}")
            raise



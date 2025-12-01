from abc import abstractmethod
from typing import Optional, Dict, List, Any
import httpx
from crawler.pkg.crawler.base_crawler import BaseCrawler

class HttpCrawler(BaseCrawler):
    """
    Optional[X] 等价于 Union[X, None]，表示该值可以是类型 X 或者 None
    """
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        超类（Superclass），也称为父类（Parent Class）或基类（Base Class），是被其他类继承的类
        HttpCrawler 需要实现 BaseCrawler 中定义的所有抽象方法
        """
        super().__init__()
        # hdr
        if headers is None:
            self._default_headers()
        self.headers = headers
        # timeout
        self.timeout = timeout
        # cli
        self.client=None

    # 默认头
    def _default_headers(self) -> None:
        self.headers["User-Agent"]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

    """
    __aenter__ 和 __aexit__ 是 Python 中 异步上下文管理器 的一部分。它们用于定义 异步 with 语句 的行为
    HttpCrawler 类被用作异步上下文管理器时，__aenter__ 会负责创建并返回 HttpCrawler
    __aexit__ 方法会在 async with 块结束时执行。它负责清理工作
    """
    async def __aenter__(self):
        self.client=(httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True,
        ))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
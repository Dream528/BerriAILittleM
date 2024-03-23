import httpx, asyncio
from typing import Optional


class AsyncHTTPHandler:
    def __init__(self, concurrent_limit=1000):
        # Create a client with a connection pool
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=concurrent_limit,
                max_keepalive_connections=concurrent_limit,
            )
        )

    async def close(self):
        # Close the client when you're done with it
        await self.client.aclose()

    async def get(
        self, url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ):
        response = await self.client.get(url, params=params, headers=headers)
        return response

    async def post(
        self,
        url: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ):
        response = await self.client.post(
            url, data=data, params=params, headers=headers
        )
        return response

    def __del__(self) -> None:
        try:
            asyncio.get_running_loop().create_task(self.close())
        except Exception:
            pass

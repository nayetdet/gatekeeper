from asyncio import Event
from contextlib import asynccontextmanager, suppress
from typing import Dict, Any, AsyncGenerator, Self
from playwright.async_api import Page, Response

class SessionEvents:
    def __init__(self) -> None:
        self.__login_success: Event = Event()
        self.__csrf_refresh: Event = Event()

    @property
    def login_success(self) -> Event:
        return self.__login_success

    @property
    def csrf_refresh(self) -> Event:
        return self.__csrf_refresh

    @asynccontextmanager
    async def listen(self, page: Page) -> AsyncGenerator[Self, None]:
        self.reset()
        page.on(event="response", f=self.on_response)
        try: yield self
        finally:
            page.remove_listener(event="response", f=self.on_response)

    async def on_response(self, response: Response) -> None:
        if response.request.method != "POST" or "talon" in response.url:
            return

        with suppress(Exception):
            result: Dict[str, Any] = await response.json()
            if "/id/api/analytics" in response.url and result.get("accountId"):
                self.__login_success.set()
            elif "/account/v2/refresh-csrf" in response.url and result.get("success") is True:
                self.__csrf_refresh.set()

    def reset(self) -> None:
        self.__login_success.clear()
        self.__csrf_refresh.clear()

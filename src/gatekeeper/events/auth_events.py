from asyncio import Event
from contextlib import suppress
from typing import Self, Dict, Any
from playwright.async_api import Page, Response

class AuthEvents:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page
        self.__login_success: Event = Event()
        self.__csrf_refresh: Event = Event()

    async def __aenter__(self) -> Self:
        self.__page.on(event="response", f=self.__on_response)
        return self

    async def __aexit__(self, *_) -> None:
        with suppress(Exception):
            self.__page.remove_listener(event="response", f=self.__on_response)

    @property
    def login_success(self) -> Event:
        return self.__login_success

    @property
    def csrf_refresh(self) -> Event:
        return self.__csrf_refresh

    async def __on_response(self, response: Response) -> None:
        if response.request.method != "POST" or "talon" in response.url:
            return

        with suppress(Exception):
            result: Dict[str, Any] = await response.json()
            if "/id/api/analytics" in response.url and result.get("accountId"):
                self.__login_success.set()
            elif "/account/v2/refresh-csrf" in response.url and result.get("success") is True:
                self.__csrf_refresh.set()

from asyncio import Event
from contextlib import suppress
from typing import Self
from playwright.async_api import Page, Response

class ClaimEvents:
    def __init__(self, page: Page) -> None:
        self.__page: Page = page
        self.__purchase_success: Event = Event()

    async def __aenter__(self) -> Self:
        self.__page.on("response", self.__on_response)
        return self

    async def __aexit__(self, *_) -> None:
        with suppress(Exception):
            self.__page.remove_listener("response", self.__on_response)

    @property
    def purchase_success(self) -> Event:
        return self.__purchase_success

    async def __on_response(self, response: Response) -> None:
        if response.request.method != "POST" or "talon" in response.url:
            return

        with suppress(Exception):
            if "/v2/purchase/confirm-order" in response.url and response.ok:
                self.__purchase_success.set()

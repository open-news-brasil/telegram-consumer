from typing import Any, Callable, Coroutine, TypeVar
from uuid import uuid4
from random import shuffle

from pyrogram import Client, utils
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, BadRequest
from aws_lambda_powertools import Logger

from function.settings import TELEGRAM_API_HASH, TELEGRAM_API_ID
from function.utils import get_peer_type_fixed
from function.telegram.message import TelegramMessage


T = TypeVar("T")

# Fixes PEER_ID_INVALID for channels
# https://github.com/pyrogram/pyrogram/issues/1314#issuecomment-2187830732
utils.get_peer_type = get_peer_type_fixed


class TelegramSender:
    def client_options(self, token: str):
        return {
            "name": str(uuid4()),
            "api_id": TELEGRAM_API_ID,
            "api_hash": TELEGRAM_API_HASH,
            "in_memory": True,
            "bot_token": token,
        }

    def __init__(self, tokens: list[str], logger: Logger):
        self.logger = logger
        self.tokens = tokens
        shuffle(self.tokens)

    async def _get_client(self, token: str) -> Client:
        client = Client(**self.client_options(token))
        await client.start()
        return client

    async def _token_rotation(
        self, method: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs
    ) -> T:
        for index, token in enumerate(self.tokens):
            try:
                telegram = await self._get_client(token)
                return await method(telegram, *args, **kwargs)  # type: ignore

            except FloodWait as exc:
                self.logger.error(str(exc))
                if (index + 1) < len(self.tokens):
                    continue
                raise exc

        raise EnvironmentError("Was not possible to send Telegram message!")

    async def _send_message(
        self, client: Client, message: TelegramMessage, reply_to: int | None = None
    ):
        await client.send_message(
            chat_id=message.chat_id,
            text=message.content,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_to_message_id=reply_to,  # type: ignore
            reply_markup=message.buttons,
        )

    async def _send_image(self, client: Client, message: TelegramMessage):
        try:
            await client.send_photo(
                chat_id=message.chat_id,
                photo=message.image,  # type: ignore
                caption=message.content,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=message.buttons,
            )

        except FloodWait as exc:
            raise exc

        except BadRequest as exc:
            self.logger.warning(str(exc))
            await self._send_message(client, message)

    async def _send_album(self, client: Client, message: TelegramMessage) -> int:
        sent_messages = await client.send_media_group(
            chat_id=message.chat_id,
            media=message.album,  # type: ignore
            disable_notification=True,
        )
        return sent_messages[0].id

    async def send(self, message: TelegramMessage):
        reply_to = None

        try:
            if message.album:
                reply_to = await self._token_rotation(self._send_album, message=message)

            if message.image:
                await self._token_rotation(self._send_image, message=message)

            else:
                await self._token_rotation(
                    self._send_message, message=message, reply_to=reply_to
                )

        except FloodWait as exc:
            raise exc

        except Exception as exc:
            self.logger.critical(str(exc), exc_info=True)
            raise exc

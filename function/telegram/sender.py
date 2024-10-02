from uuid import uuid4
from random import shuffle

from pyrogram import Client, utils
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, BadRequest
from aws_lambda_powertools import Logger

from function.settings import TELEGRAM_API_HASH, TELEGRAM_API_ID
from function.utils import get_peer_type_fixed
from function.telegram.message import TelegramMessage


# Fixes PEER_ID_INVALID for channels
# https://github.com/pyrogram/pyrogram/issues/1314#issuecomment-2187830732
utils.get_peer_type = get_peer_type_fixed


class TelegramSender:
    message_options = {
        "parse_mode": ParseMode.MARKDOWN,
    }

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

    async def client(self, token: str) -> Client:
        client = Client(**self.client_options(token))
        await client.start()
        return client

    async def _send_message(self, message: TelegramMessage):
        for index, token in enumerate(self.tokens):
            try:
                client = await self.client(token)
                return await client.send_message(
                    chat_id=message.chat_id,
                    text=message.content,
                    reply_markup=message.buttons,
                    disable_web_page_preview=True,
                    **self.message_options,  # type: ignore
                )
            except FloodWait as exc:
                self.logger.warning(str(exc))
                if (index + 1) < len(self.tokens):
                    continue
                raise exc

    async def _send_image(self, message: TelegramMessage):
        for index, token in enumerate(self.tokens):
            client = await self.client(token)

            try:
                return await client.send_photo(
                    chat_id=message.chat_id,
                    photo=message.image,  # type: ignore
                    caption=message.content,
                    reply_markup=message.buttons,
                    **self.message_options,  # type: ignore
                )

            except FloodWait as exc:
                self.logger.warning(str(exc))
                if (index + 1) < len(self.tokens):
                    continue
                raise exc

            except BadRequest:
                await self._send_message(message)

    async def _send_album(self, message: TelegramMessage):
        for index, token in enumerate(self.tokens):
            try:
                client = await self.client(token)
                return await client.send_media_group(
                    chat_id=message.chat_id,
                    media=message.album,  # type: ignore
                    disable_notification=True,
                )
            except FloodWait as exc:
                self.logger.warning(str(exc))
                if (index + 1) < len(self.tokens):
                    continue
                raise exc

    async def send(self, message: TelegramMessage):
        try:
            if message.album:
                await self._send_album(message)
            if message.image:
                return await self._send_image(message)
            else:
                return await self._send_message(message)

        except FloodWait as exc:
            raise exc

        except Exception as exc:
            self.logger.critical(str(exc), exc_info=True)
            raise exc

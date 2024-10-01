from emoji import emojize
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from src.settings import (
    TELEGRAM_MAX_ALBUM_QUANTITY,
    TELEGRAM_MAX_CONTENT_SIZE,
    WHATSAPP_LINK_FOR_CHANNEL,
)
from src.app import Message
from src.utils import get_domain, join_lines


class TelegramMessage:
    def __init__(self, message: Message):
        self.message = message

    @property
    def _album_images(self) -> list[str]:
        return self.message.images[1 : TELEGRAM_MAX_ALBUM_QUANTITY + 1 : -1]
    
    @property
    def _emoji(self) -> str:
        if self.message.youtube:
            return emojize(":video_camera:")
        if self.message.instagram:
            return emojize(":camera_with_flash:")
        return emojize(":page_facing_up:")

    @property
    def _domain(self) -> str:
        return get_domain(self.message.link)

    @property
    def _link(self) -> str:
        return f"__[{self._domain}]({self.message.link})__"

    @property
    def _title(self) -> str:
        return f"{self._emoji} **{self.message.title}**"

    @property
    def _body(self) -> str:
        text = " ".join(self.message.content)
        if len(text) > TELEGRAM_MAX_CONTENT_SIZE:
            return text[:TELEGRAM_MAX_CONTENT_SIZE] + " **[...]**"
        return text

    @property
    def _whatsapp_link(self) -> str:
        return join_lines(
            self._title.replace("**", "*"),
            f"*Fonte:* {self._link}",
            self._body.replace("**", "*"),
            f'{emojize(":mobile_phone:")} Entre agora no canal {WHATSAPP_LINK_FOR_CHANNEL} '
            'e receba notícias como esta em primeira mão no seu Telegram!',
        )

    def _button(self, text: str, link: str) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton(text=text, url=link)]

    @property
    def chat_id(self) -> str:
        return self.message.destiny

    @property
    def album(self) -> list[InputMediaPhoto]:
        return [InputMediaPhoto(img) for img in self._album_images]

    @property
    def image(self) -> str | None:
        if self.message.images:
            return self.message.images[0]
        return None

    @property
    def content(self) -> str:
        return join_lines(self._link, self._title, self._body)

    @property
    def buttons(self) -> InlineKeyboardMarkup:
        keyboard = [
            self._button("Acessar publicação", self.message.link),
            self._button("Compartilhar no Whatsapp", self._whatsapp_link),
        ]
        if self.message.youtube:
            keyboard.insert(
                0, self._button("Assistir no YouTube", self.message.youtube[0])
            )
        if self.message.instagram:
            keyboard.insert(
                0, self._button("Ver no Instagram", self.message.instagram[0])
            )
        return InlineKeyboardMarkup(keyboard)

from urllib.parse import quote_plus
from functools import cached_property

from emoji import emojize
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from pyrogram.enums import ParseMode

from function.settings import (
    TELEGRAM_MAX_ALBUM_QUANTITY,
    TELEGRAM_MAX_CONTENT_SIZE,
    WHATSAPP_LINK_FOR_CHANNEL,
    WHATSAPP_LINK_TEMPLATE,
)
from function.app import Message
from function.utils import get_domain, join_lines


class TelegramMessage:
    def __init__(self, message: Message):
        self.message = message

    @cached_property
    def video(self) -> str | None:
        if self.message.videos:
            return self.message.videos[0]
        return None

    @cached_property
    def image(self) -> str | None:
        if self.message.images and not self.video:
            return self.message.images[0]
        return None

    @cached_property
    def _album_images(self) -> list[str]:
        if self.image:
            return self.message.images[1 : TELEGRAM_MAX_ALBUM_QUANTITY + 1]
        return self.message.images[:TELEGRAM_MAX_ALBUM_QUANTITY]

    @cached_property
    def _album_caption(self) -> str:
        return emojize(f":framed_picture: **{self.message.title}**")

    @cached_property
    def _emoji(self) -> str:
        if self.message.youtube:
            return emojize(":play_button:")
        if self.message.instagram:
            return emojize(":camera_with_flash:")
        return emojize(":page_facing_up:")

    @cached_property
    def _domain(self) -> str:
        return get_domain(self.message.link)

    @cached_property
    def _link(self) -> str:
        return f"__[{self._domain}]({self.message.link})__"

    @cached_property
    def _title(self) -> str:
        return f"{self._emoji} **{self.message.title}**"

    @cached_property
    def _body(self) -> str:
        text = " ".join(self.message.content)

        if len(text) > TELEGRAM_MAX_CONTENT_SIZE:
            return text[:TELEGRAM_MAX_CONTENT_SIZE] + " **[...]**"

        elif not text.strip():
            if self.message.external_videos:
                return "Assista o vídeo clicando no botão abaixo."
            elif self.message.videos:
                return "Assista o vídeo no YouTube clicando no botão abaixo."
            elif self.message.instagram:
                return "Veja a publicação no Instagram clicando no botão abaixo."

        return text

    @cached_property
    def _whatsapp_link_text(self) -> str:
        return join_lines(
            self._title.replace("**", "*"),
            f"*Fonte:* {self.message.link}",
            self._body.replace("**", "*"),
            f'{emojize(":mobile_phone:")} Entre agora no canal {WHATSAPP_LINK_FOR_CHANNEL} '
            'e receba notícias como esta em primeira mão no seu Telegram!',
        )

    @property
    def _whatsapp_link(self) -> str:
        return WHATSAPP_LINK_TEMPLATE.format(text=quote_plus(self._whatsapp_link_text))

    def _button(self, text: str, link: str) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton(text=text, url=link)]

    @cached_property
    def chat_id(self) -> str:
        return self.message.destiny

    @cached_property
    def album(self) -> list[InputMediaPhoto]:
        return [
            InputMediaPhoto(
                img, caption=self._album_caption, parse_mode=ParseMode.MARKDOWN
            )
            for img in self._album_images
        ]

    @cached_property
    def content(self) -> str:
        return join_lines(self._link, self._title, self._body)

    @cached_property
    def buttons(self) -> InlineKeyboardMarkup:
        keyboard = [
            self._button(
                emojize(":page_facing_up: Acessar publicação"),
                self.message.link,
            ),
            self._button(
                emojize(":speech_balloon: Compartilhar no Whatsapp"),
                self._whatsapp_link,
            ),
        ]
        if self.message.external_videos:
            keyboard.insert(
                0,
                self._button(
                    emojize(":play_button: Assistir vídeo"),
                    self.message.external_videos[0],
                ),
            )
        if self.message.youtube:
            keyboard.insert(
                0,
                self._button(
                    emojize(":play_button: Assistir no YouTube"),
                    self.message.youtube[0],
                ),
            )
        if self.message.instagram:
            keyboard.insert(
                0,
                self._button(
                    emojize(":camera_with_flash: Ver no Instagram"),
                    self.message.instagram[0],
                ),
            )
        return InlineKeyboardMarkup(keyboard)

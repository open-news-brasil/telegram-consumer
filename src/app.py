from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

from src.schemas import Message
from src.settings import TELEGRAM_BOT_TOKENS
from src.telegram.message import TelegramMessage
from src.telegram.sender import TelegramSender


logger = Logger(app='telegram-lambda')


@event_parser(model=Message)
def handler(event: Message, context: LambdaContext):
    message = TelegramMessage(event)
    sender = TelegramSender(TELEGRAM_BOT_TOKENS, logger)

    try:
        sender.send(message)
        ...

    except Exception:
        ...
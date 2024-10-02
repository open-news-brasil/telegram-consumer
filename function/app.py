import asyncio

from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

from function.schemas import Message
from function.settings import TELEGRAM_BOT_TOKENS
from function.telegram.message import TelegramMessage
from function.telegram.sender import TelegramSender


logger = Logger(app="telegram-lambda")
loop = asyncio.get_event_loop()


@event_parser(model=Message)
def handler(event: Message, context: LambdaContext):
    message = TelegramMessage(event)
    sender = TelegramSender(TELEGRAM_BOT_TOKENS, logger)

    try:
        loop.run_until_complete(sender.send(message))

    except Exception as exc:
        logger.error(str(exc), exc_info=True)

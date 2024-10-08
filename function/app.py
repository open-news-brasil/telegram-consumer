import asyncio

from pyrogram.errors import FloodWait
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

from function.schemas import Message
from function.settings import TELEGRAM_BOT_TOKENS
from function.telegram.message import TelegramMessage
from function.telegram.sender import TelegramSender


loop = asyncio.get_event_loop()
logger = Logger(app="telegram-lambda")
sender = TelegramSender(TELEGRAM_BOT_TOKENS, logger)


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context: LambdaContext):
    for record in event.records:
        message = Message.model_validate_json(record.body)
        message_adapter = TelegramMessage(message)

        logger.info("Sending message...", extra={"received": message.model_dump()})

        try:
            loop.run_until_complete(sender.send(message_adapter))

        except FloodWait as exc:
            raise exc

        except Exception as exc:
            logger.error(str(exc), exc_info=True)

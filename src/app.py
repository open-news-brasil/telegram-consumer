from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.schemas import Message


@event_parser(model=Message)
def handler(event: Message, context: LambdaContext):
    ...

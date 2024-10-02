from aws_lambda_powertools.utilities.parser import BaseModel


class Message(BaseModel):
    destiny: str
    title: str
    link: str
    content: list[str] = []
    images: list[str] = []
    videos: list[str] = []
    youtube: list[str] = []
    instagram: list[str] = []

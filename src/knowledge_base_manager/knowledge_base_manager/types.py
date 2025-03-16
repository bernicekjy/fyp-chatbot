from pydantic import BaseModel

class Category(BaseModel):
    title: str
    description: str
    example_question: str
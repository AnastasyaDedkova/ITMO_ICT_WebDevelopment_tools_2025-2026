from pydantic import BaseModel


class Profile(BaseModel):
    id: int
    username: str
    city: str
# from pydantic import BaseModel

# class MembershipCreate(BaseModel):

#     gym_name: str
#     valid_till: str
#     days_left: int

from pydantic import BaseModel

class MembershipCreate(BaseModel):
    gym_name: str
    valid_till: str
    days_left: int

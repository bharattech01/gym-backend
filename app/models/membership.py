# # app/models/membership.py
# from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

# class Membership(Base):
#     __tablename__ = "memberships"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     user_id = Column(
#         Integer,
#         ForeignKey("users.id")
#     )

#     gym_name = Column(String)

#     valid_till = Column(String)

#     days_left = Column(Integer)

from sqlalchemy import Column, Integer, String, ForeignKey

class Membership(Base):

    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    gym_name = Column(String)

    valid_till = Column(String)

    days_left = Column(Integer)

    qr_code = Column(String, unique=True, nullable=False)



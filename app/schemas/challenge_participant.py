from pydantic import BaseModel


class ChallengeJoin(BaseModel):

    challenge_id: int

    user_id: int
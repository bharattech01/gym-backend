from pydantic import BaseModel

class SendOTPRequest(BaseModel):
    mobile: str


class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str

class ProfileSetupRequest(BaseModel):

    name: str

    fitness_goal: str

    fitness_level: str
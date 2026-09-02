from pydantic import BaseModel
from datetime import date, time


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class FacilityCreate(BaseModel):
    name: str
    location: str
    capacity: int


class FacilityResponse(BaseModel):
    id: int
    name: str
    location: str
    capacity: int


class BookingCreate(BaseModel):
    user_id: int
    facility_id: int
    date: date
    start_time: time
    end_time: time
    purpose: str


class BookingResponse(BaseModel):
    id: int
    user_id: int
    facility_id: int
    date: date
    start_time: time
    end_time: time
    purpose: str
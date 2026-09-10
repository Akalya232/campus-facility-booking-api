from pydantic import BaseModel
from datetime import date as Date, time as Time


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
    
class FacilityUpdate(BaseModel):

    name: str | None = None

    location: str | None = None

    capacity: int | None = None


class FacilityResponse(BaseModel):
    id: int
    name: str
    location: str
    capacity: int


class BookingCreate(BaseModel):
    user_id: int
    facility_id: int
    date: Date
    start_time: Time
    end_time: Time
    purpose: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    
class BookingUpdate(BaseModel):
    date: Date | None = None
    start_time: Time | None = None
    end_time: Time | None = None
    purpose: str | None = None
    
class BookingResponse(BaseModel): 
    id: int 
    user_id: int 
    facility_id: int 
    date: Date 
    start_time: Time 
    end_time: Time 
    purpose: str
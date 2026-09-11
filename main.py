from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from database import SessionLocal
from models import User, Facility, Booking
from schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    FacilityCreate,
    FacilityResponse,
    FacilityUpdate,
    BookingCreate,
    BookingResponse,
    BookingUpdate
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)
app = FastAPI()

# Database session
async def get_db():
    async with SessionLocal() as session:
        yield session
        
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    current_user = result.scalar_one_or_none()

    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return current_user

@app.get("/users/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    try:
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hash_password(user.password)
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

@app.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )

    user = result.scalar_one_or_none()

    if (
        user is None
        or user.password_hash is None
        or not verify_password(
            login_data.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    
@app.get("/users", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
    )

    users = result.scalars().all()

    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    update_data = user.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_user.name = update_data["name"]

    if "email" in update_data:
        existing_user.email = update_data["email"]

    try:
        await db.commit()
        await db.refresh(existing_user)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return existing_user

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await db.delete(user)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete user because they have existing bookings"
        )
        
@app.post("/facilities", response_model=FacilityResponse, status_code=201)
async def create_facility(
    facility: FacilityCreate,
    db: AsyncSession = Depends(get_db)
):
    new_facility = Facility(
        name=facility.name,
        location=facility.location,
        capacity=facility.capacity
    )

    db.add(new_facility)

    await db.commit()
    await db.refresh(new_facility)

    return new_facility

@app.get("/facilities", response_model=list[FacilityResponse])
async def get_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Facility)
        .order_by(Facility.id)
        .offset(skip)
        .limit(limit)
    )

    facilities = result.scalars().all()

    return facilities

@app.get("/facilities/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    facility_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        raise HTTPException(
            status_code=404,
            detail="Facility not found"
        )

    return facility

@app.patch("/facilities/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    facility_id: int,
    facility: FacilityUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    existing_facility = result.scalar_one_or_none()

    if existing_facility is None:
        raise HTTPException(
            status_code=404,
            detail="Facility not found"
        )

    update_data = facility.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_facility.name = update_data["name"]

    if "location" in update_data:
        existing_facility.location = update_data["location"]

    if "capacity" in update_data:
        existing_facility.capacity = update_data["capacity"]

    await db.commit()
    await db.refresh(existing_facility)

    return existing_facility

@app.delete("/facilities/{facility_id}", status_code=204)
async def delete_facility(
    facility_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )

    facility = result.scalar_one_or_none()

    if facility is None:
        raise HTTPException(
            status_code=404,
            detail="Facility not found"
        )

    await db.delete(facility)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete facility because it has existing bookings"
        )
        
@app.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether user exists
    user_result = await db.execute(
        select(User).where(User.id == booking.user_id)
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether facility exists
    facility_result = await db.execute(
        select(Facility).where(Facility.id == booking.facility_id)
    )

    facility = facility_result.scalar_one_or_none()

    if facility is None:
        raise HTTPException(
            status_code=404,
            detail="Facility not found"
        )

    # Validate time range
    if booking.start_time >= booking.end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )
        
    # Check for booking conflict
    conflict_result = await db.execute(
        select(Booking).where(
            Booking.facility_id == booking.facility_id,
            Booking.date == booking.date,
            Booking.start_time < booking.end_time,
            Booking.end_time > booking.start_time
        )
    )

    conflicting_booking = conflict_result.scalar_one_or_none()

    if conflicting_booking is not None:
        raise HTTPException(
            status_code=409,
            detail="Facility is already booked for this time"
        )

    # Create booking
    new_booking = Booking(
        user_id=booking.user_id,
        facility_id=booking.facility_id,
        date=booking.date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        purpose=booking.purpose
    )

    db.add(new_booking)

    await db.commit()
    await db.refresh(new_booking)

    return new_booking

@app.get("/bookings", response_model=list[BookingResponse])
async def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking)
        .order_by(Booking.id)
        .offset(skip)
        .limit(limit)
    )

    bookings = result.scalars().all()

    return bookings

@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking

@app.patch("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Find existing booking
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )

    existing_booking = result.scalar_one_or_none()

    if existing_booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Get updated values
    update_data = booking.model_dump(exclude_unset=True)

    new_date = update_data.get("date", existing_booking.date)
    new_start_time = update_data.get(
        "start_time",
        existing_booking.start_time
    )
    new_end_time = update_data.get(
        "end_time",
        existing_booking.end_time
    )

    # Validate time range
    if new_start_time >= new_end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )

    # Check for booking conflict
    conflict_result = await db.execute(
        select(Booking).where(
            Booking.id != booking_id,
            Booking.facility_id == existing_booking.facility_id,
            Booking.date == new_date,
            Booking.start_time < new_end_time,
            Booking.end_time > new_start_time
        )
    )

    conflicting_booking = conflict_result.scalar_one_or_none()

    if conflicting_booking is not None:
        raise HTTPException(
            status_code=409,
            detail="Facility is already booked for this time"
        )

    # Apply updates
    if "date" in update_data:
        existing_booking.date = update_data["date"]

    if "start_time" in update_data:
        existing_booking.start_time = update_data["start_time"]

    if "end_time" in update_data:
        existing_booking.end_time = update_data["end_time"]

    if "purpose" in update_data:
        existing_booking.purpose = update_data["purpose"]

    await db.commit()
    await db.refresh(existing_booking)

    return existing_booking

@app.delete("/bookings/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Find the booking
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Delete the booking
    await db.delete(booking)

    await db.commit()
    

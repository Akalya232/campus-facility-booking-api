from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from database import SessionLocal
from models import User
from schemas import UserCreate, UserResponse

app = FastAPI()

# Database session
async def get_db():
    async with SessionLocal() as session:
        yield session


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return new_user

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
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib
import uuid

from models import User, UserCreate, UserLogin, UserUpdate, UserResponse, Token, TokenData
from main import get_database

router = APIRouter()
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncIOMotorDatabase = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return User(**user)

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    user_dict.pop("password")
    
    user_dict["_id"] = str(uuid.uuid4())
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    
    return UserResponse(**created_user)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    update_data = user_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    if "preferences" in update_data:
        # Merge with existing preferences
        existing_prefs = current_user.preferences.dict()
        new_prefs = {**existing_prefs, **update_data["preferences"]}
        update_data["preferences"] = new_prefs
    
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"_id": current_user.id})
    return UserResponse(**updated_user)

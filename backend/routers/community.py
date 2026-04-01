from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional
import uuid
import os
import aiofiles

from models import (
    CommunityPost, CommunityPostCreate, CommunityPostUpdate, CommunityPostResponse,
    Comment, CommentCreate, CommentUpdate, ReactionCreate, User
)
from main import get_database
from routers.auth import get_current_user

router = APIRouter()

# Media upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return file path"""
    file_extension = upload_file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return file_path

@router.post("/posts", response_model=CommunityPostResponse)
async def create_post(
    post: CommunityPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    post_dict = post.dict()
    post_dict["user_id"] = current_user.id
    post_dict["username"] = current_user.username
    post_dict["_id"] = str(uuid.uuid4())
    post_dict["timestamp"] = datetime.utcnow()
    post_dict["reactions"] = {}
    post_dict["comments"] = []
    post_dict["is_edited"] = False
    post_dict["is_moderated"] = False
    
    result = await db.community_posts.insert_one(post_dict)
    created_post = await db.community_posts.find_one({"_id": result.inserted_id})
    
    return CommunityPostResponse(**created_post)

@router.post("/posts/{post_id}/media")
async def upload_post_media(
    post_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Check if post exists and belongs to user
    post = await db.community_posts.find_one({
        "_id": post_id,
        "user_id": current_user.id
    })
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Save uploaded files
    media_files = []
    for file in files:
        file_path = await save_upload_file(file)
        media_files.append(file_path)
    
    # Update post with media files
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$push": {"media_files": {"$each": media_files}}}
    )
    
    return {"message": f"Uploaded {len(media_files)} files successfully", "files": media_files}

@router.get("/posts", response_model=List[CommunityPostResponse])
async def get_posts(
    limit: int = 20,
    offset: int = 0,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    query = {"is_moderated": False}
    
    if tag:
        query["tags"] = tag
    
    posts = await db.community_posts.find(query).sort("timestamp", -1).skip(offset).limit(limit).to_list(length=limit)
    
    return [CommunityPostResponse(**post) for post in posts]

@router.get("/posts/{post_id}", response_model=CommunityPostResponse)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    post = await db.community_posts.find_one({"_id": post_id, "is_moderated": False})
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return CommunityPostResponse(**post)

@router.put("/posts/{post_id}", response_model=CommunityPostResponse)
async def update_post(
    post_id: str,
    post_update: CommunityPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Check if post exists and belongs to user
    existing_post = await db.community_posts.find_one({
        "_id": post_id,
        "user_id": current_user.id
    })
    
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    update_data = post_update.dict(exclude_unset=True)
    update_data["is_edited"] = True
    update_data["edited_at"] = datetime.utcnow()
    
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$set": update_data}
    )
    
    updated_post = await db.community_posts.find_one({"_id": post_id})
    return CommunityPostResponse(**updated_post)

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    result = await db.community_posts.delete_one({
        "_id": post_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return {"message": "Post deleted successfully"}

@router.post("/posts/{post_id}/reactions")
async def add_reaction(
    post_id: str,
    reaction: ReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Check if post exists
    post = await db.community_posts.find_one({"_id": post_id, "is_moderated": False})
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Add or update reaction
    reaction_field = f"reactions.{reaction.reaction_type.value}"
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$inc": {reaction_field: 1}}
    )
    
    return {"message": "Reaction added successfully"}

@router.post("/posts/{post_id}/comments", response_model=Comment)
async def add_comment(
    post_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Check if post exists
    post = await db.community_posts.find_one({"_id": post_id, "is_moderated": False})
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comment_dict = comment.dict()
    comment_dict["id"] = str(uuid.uuid4())
    comment_dict["user_id"] = current_user.id
    comment_dict["username"] = current_user.username
    comment_dict["timestamp"] = datetime.utcnow()
    comment_dict["reactions"] = {}
    comment_dict["is_edited"] = False
    
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$push": {"comments": comment_dict}}
    )
    
    return Comment(**comment_dict)

@router.put("/posts/{post_id}/comments/{comment_id}", response_model=Comment)
async def update_comment(
    post_id: str,
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Find the comment
    post = await db.community_posts.find_one({"_id": post_id, "is_moderated": False})
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Find and update the comment
    comment_found = False
    for comment in post["comments"]:
        if comment["id"] == comment_id and comment["user_id"] == current_user.id:
            comment["text"] = comment_update.text
            comment["is_edited"] = True
            comment["edited_at"] = datetime.utcnow()
            comment_found = True
            break
    
    if not comment_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or unauthorized"
        )
    
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$set": {"comments": post["comments"]}}
    )
    
    # Return the updated comment
    for comment in post["comments"]:
        if comment["id"] == comment_id:
            return Comment(**comment)

@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(
    post_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Find the post
    post = await db.community_posts.find_one({"_id": post_id, "is_moderated": False})
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Remove the comment if it belongs to the user
    original_length = len(post["comments"])
    post["comments"] = [
        comment for comment in post["comments"]
        if not (comment["id"] == comment_id and comment["user_id"] == current_user.id)
    ]
    
    if len(post["comments"]) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or unauthorized"
        )
    
    await db.community_posts.update_one(
        {"_id": post_id},
        {"$set": {"comments": post["comments"]}}
    )
    
    return {"message": "Comment deleted successfully"}

import io
import uuid
from fastapi import (
    HTTPException,
    Depends,
    Response,
    UploadFile,
    File,
    APIRouter,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel

from app.models import Channel, Post, Comment, Media
from app.db import get_db
from app.keycloak_api import keycloak_admin
from app.minio import get_minio_client, MINIO_BUCKET
from app.auth import get_current_user

router = APIRouter(prefix="/api/channels")


class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    client_email: str
    behaviorist_id: str


class ChannelUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class ChannelOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    client_id: str
    behaviorist_id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: str


class PostOut(BaseModel):
    id: str
    title: str
    content: str
    channel_id: str
    created_at: Optional[str]
    updated_at: Optional[str]
    author_id: str

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    content: str
    author_id: str


class CommentOut(BaseModel):
    id: str
    content: str
    post_id: str
    author_id: str
    created_at: Optional[str]

    class Config:
        orm_mode = True


class MediaOut(BaseModel):
    id: str
    post_id: str
    file_path: str
    created_at: Optional[str]

    class Config:
        orm_mode = True


# ----------------------------
# Channels endpoints
# ----------------------------


@router.post("/channels", response_model=ChannelOut)
async def create_channel(
    channel_in: ChannelCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    client = keycloak_admin.get_users({"email": channel_in.client_email})
    if len(client) > 0:
        client_id = client[0].get("id")
    else:
        # Jeśli klient nie istnieje – symulujemy wysłanie linku zaproszenia
        invitation_link = f"http://example.com/invite?email={channel_in.client_email}"
        print(f"Invitation link sent to {channel_in.client_email}: {invitation_link}")
        # Możesz tutaj wywołać np. funkcję wysyłającą email
        # Zapisujemy marker, aby odróżnić klientów, którzy nie ukończyli rejestracji
        client_id = f"INVITED:{channel_in.client_email}"

    new_channel = Channel(
        name=channel_in.name,
        description=channel_in.description,
        client_id=client_id,
        behaviorist_id=user["sub"],
    )
    db.add(new_channel)
    await db.commit()
    await db.refresh(new_channel)
    return new_channel


@router.get("/channels", response_model=List[ChannelOut])
async def list_channels(
    user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Channel).where(
            or_(Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"])
        )
    )
    channels = result.scalars().all()
    return channels


@router.get("/channels/{channel_id}", response_model=ChannelOut)
async def get_channel(
    channel_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            or_(
                Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"]
            ),
        )
    )
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@router.put("/channels/{channel_id}", response_model=ChannelOut)
async def update_channel(
    channel_id: str,
    channel_data: ChannelUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            or_(
                Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"]
            ),
        )
    )
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if channel_data.name is not None:
        channel.name = channel_data.name
    if channel_data.description is not None:
        channel.description = channel_data.description
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            or_(
                Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"]
            ),
        )
    )
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db.delete(channel)
    await db.commit()
    return


# ----------------------------
# Posts endpoints
# ----------------------------


@router.post("/channels/{channel_id}/posts", response_model=PostOut)
async def create_post(
    channel_id: str,
    post_in: PostCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            or_(
                Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"]
            ),
        )
    )
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    new_post = Post(
        title=post_in.title,
        content=post_in.content,
        channel_id=channel_id,
        author_id=post_in.author_id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("/channels/{channel_id}/posts", response_model=List[PostOut])
async def list_posts(
    channel_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    channel_cond = Channel.id == channel_id
    channel_user_cond = or_(
        Channel.behaviorist_id == user["sub"], Channel.client_id == user["sub"]
    )
    query = select(Channel).where(
        channel_cond,
        channel_user_cond,
    )
    result = await db.execute(query)
    channel = result.scalars().first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    result = await db.execute(select(Post).where(Post.channel_id == channel_id))
    posts = result.scalars().all()
    return posts


# ----------------------------
# Comment endpoints
# ----------------------------


@router.post("/posts/{post_id}/comments", response_model=CommentOut)
async def create_comment(
    post_id: str,
    comment_in: CommentCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment = Comment(
        content=comment_in.content, post_id=post_id, author_id=user.get("sub")
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def list_comments(post_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.post_id == post_id))
    comments = result.scalars().all()
    return comments


@router.post("/posts/{post_id}/media", response_model=MediaOut)
async def upload_media(
    post_id: str,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    minio_client = get_minio_client()
    file_content = await file.read()
    file_name = f"{uuid.uuid4()}_{file.filename}"
    try:
        minio_client.put_object(
            MINIO_BUCKET,
            file_name,
            data=io.BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Media upload failed")

    new_media = Media(post_id=post_id, file_path=file_name, created_by=user["sub"])
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)
    return new_media


@router.delete(
    "/posts/{post_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_media(
    post_id: str,
    media_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Media).where(
            Media.id == media_id,
            Media.post_id == post_id,
            Media.created_by == user["sub"],
        )
    )
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    minio_client = get_minio_client()
    try:
        minio_client.remove_object(MINIO_BUCKET, media.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Media deletion failed in MinIO: {e}"
        )

    await db.delete(media)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

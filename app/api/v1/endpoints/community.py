
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.gym import Gym
from app.models.gym_member import GymMember
from app.models.community_post import CommunityPost
from app.models.community_like import CommunityLike
from app.models.community_comment import CommunityComment
from app.models.community_message import CommunityMessage

from app.schemas.community import (
    CommunityPostCreate,
    CommunityCommentCreate,
    CommunityMessageCreate,
)

router = APIRouter()


def get_user_gym(db: Session, user_id: int):
    """Return the user's most recently created active gym membership."""
    membership = (
        db.query(GymMember)
        .filter(
            GymMember.user_id == user_id,
            func.lower(GymMember.status) == "active",
        )
        .order_by(GymMember.id.desc())
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="An active gym membership is required for Community",
        )

    return membership.gym_id


def require_post_in_gym(
    db: Session,
    post_id: int,
    gym_id: int,
):
    post = (
        db.query(CommunityPost)
        .filter(
            CommunityPost.id == post_id,
            CommunityPost.gym_id == gym_id,
        )
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


def serialize_post(db: Session, post: CommunityPost, user_id: int):
    author = db.query(User).filter(User.id == post.user_id).first()

    like_count = (
        db.query(func.count(CommunityLike.id))
        .filter(CommunityLike.post_id == post.id)
        .scalar()
    ) or 0

    comment_count = (
        db.query(func.count(CommunityComment.id))
        .filter(CommunityComment.post_id == post.id)
        .scalar()
    ) or 0

    liked = (
        db.query(CommunityLike.id)
        .filter(
            CommunityLike.post_id == post.id,
            CommunityLike.user_id == user_id,
        )
        .first()
    ) is not None

    gym = db.query(Gym).filter(Gym.id == post.gym_id).first()

    return {
        "id": post.id,
        "user_id": post.user_id,
        "author_name": author.name if author else None,
        "author_image": author.profile_photo if author else None,
        "gym_id": post.gym_id,
        "gym_name": gym.name if gym else None,
        "content": post.content,
        "category": post.category,
        "image_url": post.image_url,
        "like_count": like_count,
        "comment_count": comment_count,
        "liked_by_me": liked,
        "created_at": post.created_at,
    }


@router.get("/feed")
def get_community_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)

    posts = (
        db.query(CommunityPost)
        .filter(CommunityPost.gym_id == gym_id)
        .order_by(CommunityPost.created_at.desc(), CommunityPost.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "gym_id": gym_id,
        "posts": [
            serialize_post(db, post, user_id)
            for post in posts
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/posts", status_code=201)
def create_community_post(
    data: CommunityPostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)

    content = data.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Post content is required")

    post = CommunityPost(
        user_id=user_id,
        gym_id=gym_id,
        content=content,
        category=data.category.strip() or "General",
        image_url=data.image_url,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return serialize_post(db, post, user_id)


@router.post("/posts/{post_id}/like")
def toggle_post_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)
    post = require_post_in_gym(db, post_id, gym_id)

    existing_like = (
        db.query(CommunityLike)
        .filter(
            CommunityLike.post_id == post.id,
            CommunityLike.user_id == user_id,
        )
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        liked = False
    else:
        db.add(CommunityLike(post_id=post.id, user_id=user_id))
        liked = True

    db.commit()

    like_count = (
        db.query(func.count(CommunityLike.id))
        .filter(CommunityLike.post_id == post.id)
        .scalar()
    ) or 0

    return {
        "post_id": post.id,
        "liked_by_me": liked,
        "like_count": like_count,
    }


@router.get("/posts/{post_id}/comments")
def get_post_comments(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)
    post = require_post_in_gym(db, post_id, gym_id)

    comments = (
        db.query(CommunityComment)
        .filter(CommunityComment.post_id == post.id)
        .order_by(CommunityComment.created_at.asc())
        .all()
    )

    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.user_id).first()
        result.append({
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "author_name": author.name if author else None,
            "author_image": author.profile_photo if author else None,
            "content": comment.content,
            "created_at": comment.created_at,
        })

    return {"post_id": post.id, "comments": result}


@router.post("/posts/{post_id}/comments", status_code=201)
def add_post_comment(
    post_id: int,
    data: CommunityCommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)
    post = require_post_in_gym(db, post_id, gym_id)

    content = data.content.strip()
    if not content:
        raise HTTPException(
            status_code=422,
            detail="Comment content is required",
        )

    comment = CommunityComment(
        post_id=post.id,
        user_id=user_id,
        content=content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    author = db.query(User).filter(User.id == user_id).first()

    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": user_id,
        "author_name": author.name if author else None,
        "author_image": author.profile_photo if author else None,
        "content": comment.content,
        "created_at": comment.created_at,
    }


@router.get("/group-chat/messages")
def get_group_chat_messages(
    limit: int = Query(default=50, ge=1, le=100),
    before_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)

    query = db.query(CommunityMessage).filter(
        CommunityMessage.gym_id == gym_id
    )

    if before_id is not None:
        query = query.filter(CommunityMessage.id < before_id)

    messages = (
        query.order_by(CommunityMessage.id.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()

    result = []
    for message in messages:
        author = db.query(User).filter(User.id == message.user_id).first()
        result.append({
            "id": message.id,
            "gym_id": message.gym_id,
            "user_id": message.user_id,
            "author_name": author.name if author else None,
            "author_image": author.profile_photo if author else None,
            "message": message.message,
            "created_at": message.created_at,
        })

    return {"gym_id": gym_id, "messages": result}


@router.post("/group-chat/messages", status_code=201)
def send_group_chat_message(
    data: CommunityMessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]
    gym_id = get_user_gym(db, user_id)

    content = data.message.strip()
    if not content:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty",
        )

    message = CommunityMessage(
        gym_id=gym_id,
        user_id=user_id,
        message=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    author = db.query(User).filter(User.id == user_id).first()

    return {
        "id": message.id,
        "gym_id": gym_id,
        "user_id": user_id,
        "author_name": author.name if author else None,
        "author_image": author.profile_photo if author else None,
        "message": message.message,
        "created_at": message.created_at,
    }

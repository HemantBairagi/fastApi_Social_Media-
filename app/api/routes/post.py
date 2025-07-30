from typing import List
from fastapi import Depends , APIRouter
from sqlalchemy.orm import Session
from app.models.models import Posts as Post, Comment
from app.db.database import get_db
from app.schema.schema import CommentBase, PostCreate, PostOut, CommentCreate , CommentOut  # ✅ Use Pydantic models here
from fastapi import Depends
from sqlalchemy.orm import Session


router = APIRouter()


# get all posts in database
@router.get("/posts" , response_model=List[PostOut])
async def allPosts(db: Session = Depends(get_db)):
    db_posts = db.query(Post)
    return db_posts.all()


# create a new posts
@router.post("/posts" , response_model=PostOut)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(
        user_id=post.user_id,
        post_type=post.post_type,
        post_text=post.post_text
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# get a post by id<< Particular Post>>
@router.get("/posts/{post_id}", response_model=PostOut)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        return {"error": "Post not found"}
    return db_post

# get User posts by user id << User's Posts >>
@router.get("/user/{user_id}/posts", response_model=List[PostOut])
async def read_user_posts(user_id: int, db: Session = Depends(get_db)): 
    db_posts = db.query(Post).filter(Post.user_id == user_id).all()
    if not db_posts:
        return {"error": "No posts found for this user"}
    return db_posts


#get a post by user id and post id << Particular Post of User>>
@router.get("/users/{user_id}/posts/{post_id}", response_model=PostOut)
async def read_user_post(user_id: int, post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(
        Post.user_id == user_id, Post.id == post_id
    ).first()
    if db_post is None:
        return {"error": "Post not found for this user"}
    return db_post

# capture a comment on a post
@router.post("/users/{user_id}/posts/{post_id}/comments", response_model=CommentOut)
async def create_post_comment(user_id: int, post_id: int, comment: CommentBase, db: Session = Depends(get_db)):
    db_comment = Comment(
        user_id=user_id,
        post_id=post_id,
        comment_type=comment.comment_type,
        comment=comment.comment
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/users/{user_id}/posts/{post_id}/comments", response_model=List[CommentOut])
async def read_post_comments(user_id: int, post_id: int, db: Session = Depends(get_db)):
    db_comments = db.query(Comment).filter(
        Comment.user_id == user_id, Comment.post_id == post_id
    ).all()
    if not db_comments:
        return {"error": "No comments found for this post"}
    return db_comments



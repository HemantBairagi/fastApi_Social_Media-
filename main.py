from fastapi import FastAPI
from app.api.routes import follower, user , post , chat
import app.models.models as models
from app.db.database import engine , get_db



app = FastAPI(allow_methods=["*"], allow_headers=["*"] , allow_origins=["*"])
app.include_router(user.router)
app.include_router(post.router) 
app.include_router(chat.router)
app.include_router(follower.router)

models.Base.metadata.create_all(bind=engine)

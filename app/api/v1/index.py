# app/api/v1/index.py
from fastapi import APIRouter, Response, Request
import uuid

router = APIRouter()

# @router.get("/", include_in_schema=False)
# async def root(request: Request, response: Response):
#     session_token = request.cookies.get("session_token")
#     if not session_token:
#         session_token = str(uuid.uuid4())
#         response.set_cookie(
#             key="session_token",
#             value=session_token,
#             httponly=True,
#             samesite="lax",
#             path="/"
#         )
#     return {"message": "Привет! Ваша сессия: " + session_token}

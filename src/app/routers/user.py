from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix='/user',
    tags=['user']
)


@router.get("/")
async def read_root():
    return {"Hello": "World"}

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/hello", summary="Say hello")
def say_hello(name: str = Query("world", description="Name to greet")) -> dict:
    greeting = f"Hello, {name}!"
    return {"status": "ok", "data": {"greeting": greeting}}

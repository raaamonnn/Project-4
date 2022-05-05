from fastapi import FastAPI, HTTPException
from utils import start_connection
from validation_service import check_word
import random
import redis 
import json
from pprint import pprint

redis_host = "localhost"
redis_port = 6379
redis_password = ""

r = redis.Redis(host=redis_host, port=redis_port)

app = FastAPI()

@app.post("/startgame")
async def start_game(userId: str, gameId: str):
    if r.llen(userId) != 0:
        raise HTTPException(status_code=400, detail="Duplicate GameId error.")

    r.rpush(userId, 5, gameId)
    return {"result": "Succesfully Started Game"}

@app.post("/updatestate")
async def update_state(word: str, isCorrect: bool, userId: str):
    guessLeft = json.loads(r.lpop(userId))
    guessLeft -= 1
    
    r.rpush(userId, word)
    if isCorrect or guessLeft == 0:
        r.delete(userId)
        return {"result": "Game Over"}

    # Pushes it from head as first element again
    r.lpush(userId, guessLeft)
    return {"result": "Game State Updated"}
    
@app.post("/restorestate")
async def restore_state(userId: str):
    guessLeft = json.loads(r.lpop(userId))
    r.lpush(userId, guessLeft)
    
    print(guessLeft)
    words = []
    for x in range(0, 5 - guessLeft):
        words.append(r.rpop(userId))
        print(words)
    
    words.reverse()

    for word in words:
        r.rpush(userId, word)

    return {"result": words}
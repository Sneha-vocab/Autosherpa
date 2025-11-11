from pydantic import BaseModel
from typing import Optional
import time 
from router import graph, RouterState
from fastapi import FastAPI
app = FastAPI()



class UserMessage(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def WhatsApp_message(user_message: UserMessage):
    message = user_message.message
    user_id = user_message.user_id 
    
    start_time = time.time()
    response = graph.run({"input": message})
    end_time = time.time()  
    latency = end_time - start_time


    return {
        "response": response["output"],
        "latency_seconds": latency
    }
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool

@app.get("/devices")
def get_devices():
    return list(devices.find({},{"_id": 0}))

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id" : 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device

@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    return new_device

@app.put("/devices/{name}")
def put_device(name: str, device: Device):
    updated_device = device.model_dump()
    result = devices.update_one({"name" : name}, {"$set" : updated_device})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=("device called " + name + " does not exist"))
    return updated_device

@app.delete("/devices/{name}")
def delete_device(name : str):
    result = devices.delete_one({"name" : name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=("device called " + name + " does not exist"))
    return {"message" : name + " deleted successfully"}



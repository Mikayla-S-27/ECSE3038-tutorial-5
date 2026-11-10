import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
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
    if devices.find_one({"name": device.name}) is not None:
        raise HTTPException(status_code=409, detail="Device " + device.name + " already exists")
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    return new_device

@app.put("/devices/{name}")
def put_device(name: str, device: Device, response: Response):
    if device.name != name:
        raise HTTPException(status_code=400, detail="Body name must match URL name")
    new_device = device.model_dump()
    result = devices.replace_one({"name": name}, new_device, upsert=True)
    if result.upserted_id is not None:
        response.status_code = 201
    return new_device

@app.delete("/devices/{name}", status_code = 204)
def delete_device(name : str):
    result = devices.delete_one({"name" : name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=("device called " + name + " does not exist"))
    return Response(status_code=204)



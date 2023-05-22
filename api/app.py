from fastapi import FastAPI,HTTPException,Request
from bson import ObjectId
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
import uvicorn
import json
import requests
import re


app = FastAPI()

load_dotenv() 
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('Mongostuff'))
db = client.statedb
db2 = client.Pstatedb

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

origins = ["https://simple-smart-hub-client.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#to update the database with new information about the current state of everything babz
@app.post("/api/state",status_code=201) 
async def set_state(request:Request):
    
    Poketype = await request.json()
    Poketype["datetime"]=(datetime.now()+timedelta(hours=-5)).strftime('%Y-%m-%dT%H:%M:%S')
    #Hours-5 for timezone gmt-5


    newtype = await db["states"].insert_one(Poketype)
    modchange = await db["states"].find_one({"_id": newtype.inserted_id }) 
    if newtype.acknowledged == True:
        return modchange
    raise HTTPException(status_code=400,detail="Issue")



@app.get("/api/state")
async def getstate():
    currentstate = await db["states"].find().sort("datetime",-1).to_list(1)
  

    nowsettings = await db["settings"].find().to_list(1)

    presence = currentstate[0]["presence"]
    ctime=datetime.strptime(datetime.strftime(datetime.now()+timedelta(hours=-5),'%H:%M:%S'),'%H:%M:%S')
    lightuse=datetime.strptime(nowsettings[0]["user_light"],'%H:%M:%S')
    lightoff=datetime.strptime(nowsettings[0]["light_time_off"],'%H:%M:%S')

    fanstate = ((float(currentstate[0]["temperature"])>float(nowsettings[0]["user_temp"])) and presence)  
    lightstate = (ctime>lightuse) and (presence) and (ctime<lightoff)
    
    
    print(datetime.strftime(datetime.now()+timedelta(hours=-5),'%H:%M:%S'))
    print(nowsettings[0]["user_light"])
    print(nowsettings[0]["light_time_off"])
    print(presence)

    totalstate ={"fan":fanstate, "light":lightstate}
    return totalstate

def sunsettime():

    response= requests.get("https://api.sunrise-sunset.org/json?lat=q7.7936&lng=-76.7936")
    sunsetdata= response.json()

    sunsetstate= sunsetdata["results"]["sunset"]
    sunset_time= datetime.datetime.strptime(sunsetstate, "%I:%M:%S %p")
    return sunset_time



@app.get("/graph")
async def get_parameter(request: Request):
    n = int(request.query_params.get('size', 10))
    sensinput= await db["data_input"].find().to_list(n)
    
    tempp=[param["temperature"] for param in sensinput]
    datetimes= [param["datetime"] for param in sensinput]
    movementpresense= [param["presence"] for param in sensinput]
  

    output=[]
    if tempp and movementpresense and datetimes:
        output.append({
            "temperature": tempp,
            "presence": movementpresense,
            "datetime": datetimes
            })
        
    while len(output) < n:
        output.append({
            "temperature": 1.0,
            "presence": False,
            "datetime": datetime.now().time()
        })

    return output


@app.put("/settings")
async def setting(request:Request):
    
    Pstate = await request.json()
    elements = await db["settings"].find().to_list(1)
    mod_setting = {}
    mod_setting["user_temp"]=Pstate["user_temp"]
    if Pstate["user_light"]== "sunsettime":
        mod_setting["user_light"]=sunsettime()
    else:
        mod_setting["user_light"] = Pstate["user_light"]
    
    mod_setting["light_time_off"]= (datetime.strptime(mod_setting["user_light"],'%H:%M:%S')+parse_time(Pstate["light_duration"])).strftime("%H:%M:%S") #Convert to string ?
    

    if len(elements)==0:
         new_setting = await db["Pstate"].insert_one(mod_setting)
         patched_setting = await db["Pstate"].find_one({"_id": new_setting.inserted_id })
         return patched_setting
    else:
        id=elements[0]["_id"]
        updated_setting= await db["Pstate"].update_one({"_id":id},{"$set": mod_setting})
        patched_setting = await db["Pstste"].find_one({"_id": id})
        if updated_setting.modified_count>=1: 
            return patched_setting
    raise HTTPException(status_code=400,detail="Issue")

regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

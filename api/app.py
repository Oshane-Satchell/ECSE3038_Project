import re
import pytz
import requests
import datetime
import pydantic
from bson import ObjectId
import motor.motor_asyncio
from fastapi import FastAPI, Request
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://simple-smart-hub-client.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://oshanesatchell:fhTKIXZJz9YToJKN@cluster0.lrgcwoj.mongodb.net/?retryWrites=true&w=majority")
db = client.iotproject
stored_data = db['stored_data']
esp_data = db['esp_data']

# Initialize Nominatim API
geo_locator = Nominatim(user_agent="MyApp")

location = geo_locator.geocode("Hyderabad")


def get_sunset():
    latitude_location =  location.latitude
    longitude_location = location.longitude

    sunset_url = f'https://api.sunrise-sunset.org/json?lat={latitude_location}&lng={longitude_location}'

    sunset_response = requests.get(sunset_url)
    sunset_data = sunset_response.json()

    time_of_sunset = datetime.strptime(sunset_data['results']['sunset'], '%I:%M:%S %p').time()
    
    return datetime.strptime(str(time_of_sunset),"%H:%M:%S")


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

@app.get("/")
async def home():
    return {"message": "ECSE3038 - Project"}

@app.get('/graph')
async def graph(request: Request):
    size = int(request.query_params.get('size'))
    read_values = await esp_data.find().sort('_id', -1).limit(size).to_list(size)
    reading_data = []
    for things in read_values:
        temperature = things.get("temperature")
        presence = things.get("presence")
        current_time = things.get("current_time")

        reading_data.append({
            "temperature": temperature,
            "presence": presence,
            "datetime": current_time
        })

    return reading_data

@app.put('/settings')
async def get_stored_data(request: Request):
    condition = await request.json()
    
    input_temp = condition["user_temp"]
    input_light = condition["user_light"]
    light_time_off = condition["light_duration"]
    

    if input_light == "sunset":
        light_buffer = get_sunset()
    else:
        light_buffer = datetime.strptime(input_light, "%H:%M:%S")
    
    new_user_light = light_buffer + parse_time(light_time_off)

    final_output = {
        "user_temp": input_temp,
        "user_light": str(light_buffer.time()),
        "light_time_off": str(new_user_light.time())
        }
   
    object = await stored_data.find().sort('_id', -1).limit(1).to_list(1)

    if object:
        await stored_data.update_one({"_id": object[0]["_id"]}, {"$set": final_output})
        object_new = await stored_data.find_one({"_id": object[0]["_id"]})
    else:
        new = await stored_data.insert_one(final_output)
        object_new = await stored_data.find_one({"_id": new.inserted_id})
    return object_new


@app.post("/temp_presence")

async def update(request: Request): 
    condition = await request.json()

    variable = await stored_data.find().sort('_id', -1).limit(1).to_list(1)
    if variable:
        temperature = variable[0]["user_temp"]   
        input_light = datetime.strptime(variable[0]["user_light"], "%H:%M:%S")
        off_time = datetime.strptime(variable[0]["light_time_off"], "%H:%M:%S")
    else:
        temperature = 28
        input_light = datetime.strptime("18:00:00", "%H:%M:%S")
        off_time = datetime.strptime("20:00:00", "%H:%M:%S")

    now_time = datetime.now(pytz.timezone('Jamaica')).time()
    current_time = datetime.strptime(str(now_time),"%H:%M:%S.%f")


    condition["light"] = ((current_time < input_light) and (current_time < off_time ) & (condition["presence"] == 1))
    condition["fan"] = ((float(condition["temperature"]) >= temperature) & (condition["presence"]== 1))
    condition["current_time"]= str(datetime.now())

    new_settings = await esp_data.insert_one(condition)
    new_obj = await esp_data.find_one({"_id":new_settings.inserted_id}) 
    return new_obj


@app.get("/condition")
async def get_state():
    entry_final = await esp_data.find().sort('_id', -1).limit(1).to_list(1)

    if not entry_final:
        return {
            
            "fan": False,
            "light": False,
            "presence": False,
            "current_time": datetime.now()
        }

    return entry_final

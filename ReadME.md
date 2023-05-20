# Simple Smart Hub
## by Oshane Satchell

## Introduction

IoT stands for Internet of Things, and it refers to the network of physical objects or "things" that are connected to the internet and can communicate with each other to perform certain tasks.

An IoT platform is a software solution that enables the management, deployment, and integration of IoT devices and data. It allows users to control and monitor their IoT devices from a centralized location, and it provides the necessary tools for collecting and analyzing data generated by these devices.

The goal of this project is to build an IoT platform that controls simple appliances that are typically controlled by the clip of a switch, e.g. lighting appliances like lamps or in-wall lighting fixtures, and cooling/heating appliances such as fans and air conditioning units.

The platform should also allow users to interact with the IoT devices through the use of a webpage.

## Requirements

The platform will require:

1. An Espressif ESP32 development module, which will serve as the central sensor unit for the IoT platform. 
2. A lamp and a fan, which will be connected to the ESP32 module and controlled through the platform.
3. A RESTful API written using the FastAPI Python framework to be used as a “middle-man”. Your API should allow for effective communication among all components of the platform. 
4. Software and libraries that will enable the ESP32 module to control the connected appliances and to communicate connected sensors and with the web API.
5. A webpage that will allow users to interact with the devices and control them remotely. This will be provided to you. The requirement in this case is to implement your API such that is compatible with the requests that are sent by the webpage. Documentation will be provided.

## Implementation

### Time-based control

IoT platform should include a feature that allows users to specify a time after which the lights should turn on. The IoT platform can then compare the current time to the user-specified time and only turn on the lights if the current time is later.

In case the user sets the desired time for the lights to turn on at sunset, the IoT platform should also be able to determine the actual time of sunset for that day. This feature can be implemented by integrating a sunset API that provides accurate sunset times based on the user's location. By incorporating this feature, the platform can ensure that the lights are turned on at the appropriate time, regardless of whether the user has manually set the time or chosen the sunset option. This can enhance the user experience by ensuring that the lights are always turned on at the right time and can also help conserve energy by avoiding unnecessary use of lights during daylight hours.

### Temperature-based control

The IoT platform should include a feature that allows users to specify a temperature after which the fan should turn on. This can be accomplished using a temperature sensor, such as a digital temperature sensor, connected to the ESP32, which can read the current temperature of the room. The IoT platform can then compare the current temperature to the user-specified temperature and only turn on the fan if the current temperature is higher.

### Presence detection

The IoT platform should also include a sensor that can detect whether a person is present in the room. This can be accomplished using a passive infrared (PIR) sensor, for example, which detects changes in infrared radiation that occur when a person moves within its field of view. The IoT platform can then use this information to determine whether to turn on the lights.

### Combined logic

The IoT platform should combine the temperature-based control, time-base control and presence detection features so that the controlled appliances only turns on if each set relevant conditions is met. 

This can be accomplished using programming logic that checks:

- both the current temperature and the presence sensor data before deciding whether to turn on the fan.
- both the current time and the presence sensor data before deciding whether to turn on the lights.

To provide users with greater control over the IoT platform, they should be able to customize various settings. For example, the user should be able to specify the temperature at which the fan should turn on. Similarly, the user should be able to customize the time after which the lights should turn on and the duration for which they should stay on. These customizable settings can be accessed via a web interface that allows the user to input their preferred values. By providing these customization options, the IoT platform can be tailored to the specific needs of the user, making it more effective and user-friendly.

By implementing these features, the IoT platform can ensure that the lights only turn on when they are needed. This can save energy and reduce unnecessary light pollution. Additionally, the fan only turns on when the room temperature exceeds the user-specified temperature and a person is present. This can help save energy and create a more comfortable living environment.

To enhance the user experience and provide users with more information about the environmental conditions in the room, students should include a request method that returns the n most recent sensor readings from the IoT platform to the webpage. See [fig 2.1](https://www.notion.so/Simple-Smart-Hub-e7ebc70d3b23473bb20ca6e60eda9cbe) for example. (Hint: look up query parameters in FastAPI)

This data can then be used to plot graphs on the webpage, showing how the temperature has changed over time as well as how much time is spent in the room. 

By having access to this historical data, users can gain insights into how the temperature varies in the room, which can help them make more informed decisions about when to turn on the fan or adjust the thermostat. Moreover, the ability to visualize the temperature data in a graphical form can help users better understand the relationship between the temperature and the fan's performance, which can lead to improved energy efficiency and a more comfortable living environment.

Use this webapp to test your API:

```
https://simple-smart-hub-client.netlify.app/
```

### IMPORTANT

In order to ensure a smooth and efficient operation of the IoT platform, it is recommended that all processing and decision-making be done by the API, rather than by the microcontroller. The microcontroller should only be responsible for carrying out the instructions it receives from the server-app in response to user input and/or sensor data. 

This approach enables the API to handle complex decision-making processes, such as determining whether the temperature is too high to turn on the fan or if a person is present in the room to turn on the lights. This way, the microcontroller does not get overloaded with complex computations and is free to focus on executing the instructions received from the server-app, thereby ensuring the system's reliability and smooth operation. 

## Requests that will be made by the Webpage

*fig. 1.1*: User settings with specific definition of user temperature and time

```jsx
// Request
PUT /settings HTTP/1.1
Host: [server-node_ip-address:port]
Content-Type: "application/json"
Content-Length: 69

{ "user_temp": 30,	"user_light": "18:30:00", "light_duration": "4h" }

// Expected response
{ 
	"_id": {database defined _id}
	"user_temp": 30, 
	"user_light": "18:30:00", 
	"light_time_off": "22:30:00"
}
```

*fig 1.2*: User settings with specific definition of user temperature but time is to be determined

```jsx
// Request
PUT /settings HTTP/1.1
Host: {server-node_ip-address:port}
Content-Type: "application/json"
Content-Length: 67

{ "user_temp": 30, "user_light": "sunset", "light_duration": "4h" }

// Expected response
{ 
	"_id": {database defined _id}
	"user_temp": 30, 
	"user_light": "17:43:21", 
	"light_time_off": "21:43:21" 
}
```

*fig. 2.1*: Data to be used to plot graph

```jsx
// Request
GET /graph?size={n} HTTP/1.1
Host: {server-node_ip-address:port}

// Expected response
// total number of objects in array should be equal to n
[
	{
		"temperature": 29.3,
		"presence": true,
		"datetime": "2023-02-23T18:22:28"
	}
	...
]
```

## Some suggested parts

*fig 3.1:* Suggested list of parts for the hardware component of the platform

| microcontroller | switch | sensor | actuator | power converter | power supply |
| --- | --- | --- | --- | --- | --- |
| ESP32 | DC Relay | Digital temperature sensor | 12v PC Fan | 5v Voltage Regulator | 12v DC |
|  | MOSFET | On-board BLE | 12v Light | Buck Converter |  |
|  |  | PIR sensor | LED |  |  |

*fig 4.1:* This function can be used to parse the `light_duration` field in the client request shown in [*fig 1.1*](https://www.notion.so/Simple-Smart-Hub-e7ebc70d3b23473bb20ca6e60eda9cbe) and [*fig 1.2*](https://www.notion.so/d33e53fd5e654c0b907afc6114cd1aae)

```python
import re
from datetime import timedelta

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
```

## Submission

Your GitHub repository should be organised as follows:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/4dacc356-15cc-4f3d-96a2-c6ef4f829215/Untitled.png)

Due date is May 19, 2023.

The repo name must be "ECSE3038_Project".

You're only required to provide a link to your GitHub repository. 

Any commits made to the repo after the due date will not be considered.
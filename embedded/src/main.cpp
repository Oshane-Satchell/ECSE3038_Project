#include "env.h" 
#include <Wifi.h>
#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define endpoint "lab6-api.onrender.com"

#define fan_pin 22
#define light_pin 23
#define present_pin 24

float getTemp(){

  return random(21.1,33.1);
}
  int getPresence(){

  return random(0,1);
}

void setup() {

  Serial.begin(9600);

	pinMode(fan_pin,OUTPUT);
  pinMode(light_pin,OUTPUT);
  pinMode(present_pin,OUTPUT);

	// WiFi_SSID and WIFI_PASS should be stored in the env.h
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.println("");
	// Connect to wifi
  Serial.println("Connecting to WiFi...");
  while(WiFi.status() != WL_CONNECTED) {
    delay(600);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi and the IP Address is: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  //Check WiFi connection status
  if(WiFi.status()== WL_CONNECTED){
    Serial.println("");
    Serial.println("");
    HTTPClient http;
  
    // Establish a connection to the server
    String url = "https://" + String(endpoint) + "/api/state";
    http.begin(url);
    http.addHeader("Content-length", "23");
    http.addHeader("Content-type", "application/json");
   

    StaticJsonDocument<1024> docput;
    String httpRequestData;

    // Serialise JSON object into a string to be sent to the API
    docput["temperature"] = getTemp();


    // convert JSON document, doc, to string and copies it into httpRequestData
    serializeJson(docput, httpRequestData);

    // Send HTTP PUT request
    int httpResponseCode = http.PUT(httpRequestData);
    String http_response;

    // check reuslt of PUT request. negative response code means server wasn't reached
    if (httpResponseCode>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      Serial.print("HTTP Response from server: ");
      http_response = http.getString();
      Serial.println(http_response);
    }
    else {
      Serial.print("Code of Error: ");
      Serial.println(httpResponseCode);
    }

    http.end();    
    http.begin(url);
    httpResponseCode = http.GET();

    Serial.println("");
    Serial.println("");

    if (httpResponseCode>0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);

        Serial.print("Response from server: ");
        http_response = http.getString();
        Serial.println(http_response);
      }
      else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
    }
 
    StaticJsonDocument<1024> docget;

    DeserializationError error = deserializeJson(docget, http_response);

    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }
    
    bool temp = docget["fan"]; 
    bool light= docget["light"]; 
    bool presence = docget["presence"];

    digitalWrite(fan_pin,temp);
    digitalWrite(light_pin,temp);
    digitalWrite(presence_pin,temp);

    http.end();
  }
  else {
    Serial.println("Disconnected WiFi");
  }
}
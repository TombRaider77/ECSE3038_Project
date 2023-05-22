#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "env.h"

#define light 21
#define fan 19
#define distancesens 3
#define tempsens 2

OneWire oneWire(tempsens);	
DallasTemperature sensors(&oneWire);

const char * endpoint = "https://davidoforthawin.onrender.com/";
//who knows if this generated a link works atp

void setup() {


  pinMode(light, OUTPUT);
  pinMode(fan, OUTPUT);
  pinMode(distancesens, INPUT);
  pinMode(tempsens,INPUT);

  Serial.begin(9600);
  WiFi.begin(WIFI_SSID,WIFI_PASS);

  Serial.println("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  if (WiFi.status() == WL_CONNECTED){
  
    HTTPClient http;
  
    http.begin(endpoint);

    

    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<150> doc;
    String httpRequestData;

    sensors.requestTemperatures(); 

    Serial.print("Temperature: ");
    Serial.println(sensors.getTempCByIndex(0));

    Serial.print("Distance: ");
    Serial.println(digitalRead(distancesens));


    doc["presence"] = digitalRead(distancesens);
    doc["temperature"] = sensors.getTempCByIndex(0);

    serializeJson(doc, httpRequestData);

    int httpResponseCode = http.PUT(httpRequestData);
    String http_response;
     
   
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http_response = http.getString();
    Serial.println(http_response);
    
      http.end();

      delay(2000);

    HTTPClient http;

    String http_response;

    http.begin(endpoint);

    int httpResponseCode = http.GET();

    if(httpResponseCode>0){
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      Serial.print("Response from server: ");
      http_response = http.getString();
      

    }
    else {
      Serial.print("Error Code: ");
      Serial.println(httpResponseCode);
    }

    http.end();

    StaticJsonDocument<192> doc;

    DeserializationError error = deserializeJson(doc, http_response);

    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    bool light_switch = doc["light_switch_1"];
    bool fan_switch = doc["light_switch_2"]; 

    Serial.println("");

    Serial.print("light_switch: ");
    Serial.println(light_switch);
    

    Serial.print("fan_switch: ");
    Serial.println(fan_switch);

    Serial.println("");

    
    digitalWrite(light,light_switch);


    digitalWrite(fan,fan_switch);

  }

  else {
 return;
 }
}

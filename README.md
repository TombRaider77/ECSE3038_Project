# ECSE3038_Project

API CODE
Installed pytz, api,motor the @app.post("/api/state) updates the database with new information about on the current state 
It defines an HTTP POST route at /api/state extracting the JSON payload from the request using await request.json(), and assigns it to the variable Poketype.
It adds a new key-value pair to the Poketype dictionary. 
The new key is "datetime", and its value is the current date and time adjusted by 5 hours in the GMT-5 timezone.



the @app.get("/api/state) gets the nformation for the fanstate and state and returns the current for them
the sunsettie() funstion get a response from the inputted api link saves the data as seunsetstate and sunset_time and return senset_time


@app.get("/graph") is used get the information to draw the graph @app.put("/settings",status_code=200) 
is used to change the settings because the user can change what seetings they want, the put function is used to make adjustments to it status code ok used when completed

regex takes the string and ensures the time is in normal format parse_time takes in a string ensure
it matches pattern stated for regex and creates an object timedelta


Embedded code declared the light and fan as output and the distance sensor and temperature sensor as input 
Void loop() does the following:
Checks if the WiFi connection is active. Creates an HTTPClient object.
Makes a PUT request to an endpoint with JSON payload containing the temperature and presence data. 
Prints the HTTP response code and the response received from the server. Closes the HTTP connection and waits for 2 seconds. 
Creates a new HTTPClient object. Makes a GET request to the same endpoint. Prints the HTTP response code and the response received from the server.
Closes the HTTP connection. Deserializes the JSON response into a JSON document using the ArduinoJson library. 
Extracts the values of light_switch_1 and light_switch_2 from the JSON document. Prints the values of light_switch and fan_switch.
Sets the state of the light and fan based on the extracted values.


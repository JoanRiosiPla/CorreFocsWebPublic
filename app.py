import os
import random
from flask import Flask, render_template, request, json, url_for, redirect

app = Flask(__name__)
toDetonate = 0
toBeep = 0

@app.route("/")
def hello_world():
    return render_template("test.html")

@app.route("/detonate", methods=["POST"])
def detonate():
    global toDetonate
    #Get id from form
    id = request.form.get("formId")
        
    toDetonate = id
    return redirect(url_for('hello_world'))

@app.route("/beep", methods=["POST"])
def beep():
    global toBeep
    #Get id from form
    id = request.form.get("formId")
        
    toBeep = id
    return redirect(url_for('hello_world'))

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    global toDetonate
    global toBeep
    # Get data from the post request.
    # Values: "id", "latitude", "longitude", "temperature", "humidity", "CO2", "status
    if request.method == 'POST':
        print('Webhook Received')
        request_json = request.get_json()

        # print the received notification
        print('Payload: ')
        print(request_json)

        # check auth
        if request_json["api_key"] != "tPmAT5Ab3j7F9":
            return 'Unauthorised', 401
    
        # Update the ball with the appropiate ID in  static/balls.json 
        # with the new data
        id = request_json["id"]
        latitude = request_json["latitude"]
        longitude = request_json["longitude"]
        temperature = request_json["temperature"]
        humidity = request_json["humidity"]
        CO2 = request_json["CO2"]
        status = request_json["status"]
        # open the file to write
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "static", "balls.json")
        data = json.load(open(json_url))

        found = False
        for ball in data:
            if ball["id"] == id:
                ball["lat"] = latitude
                ball["long"] = longitude
                ball["temperature"] = temperature
                ball["humidity"] = humidity
                ball["CO2"] = CO2
                ball["status"] = status
                found = True
                break
        # if the ball was not found, add it to the list
        if not found:
            data.append({
                "id": id,
                "lat": latitude,
                "long": longitude,
                "temperature": temperature,
                "humidity": humidity,
                "CO2": CO2,
                "status": status,
            })
        
        # write the updated data to the file
        with open('static/balls.json', 'w') as json_file:
            json.dump(data, json_file)

        if toBeep != 0:
            toBeep = 0
            return 'Webhook notification received', 105
        # if the ball is to be detonated, return 104
        if toDetonate != 0:
            toDetonate = 0
            return 'Webhook notification received', 104
        return 'Webhook notification received', 202
    

# Start the application on port 3111
if __name__ == "__main__":
    app.run(host='bolacortafuegos.local', port=3111, debug=True)
    
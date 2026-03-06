from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import math

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route("/")
def home():
    city="Kuala Lumpur"
    
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()
    
    temperature = data["main"]["temp"]
    feel = data["main"]["feels_like"]
    humidity= data["main"]["humidity"]
    pressure= data["main"]["pressure"]
    weather = data["weather"][0]["description"]
    visibility = data["visibility"]
    wind = data["wind"]["speed"]

    a = 17.27
    b = 237.7

    alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100)
    dew_point = round((b * alpha) / (a - alpha),1)

    timestamp = data["dt"]
    offset = data["timezone"]
    local_time = datetime.fromtimestamp(timestamp, timezone.utc) + timedelta(seconds=offset)
    time_str = local_time.strftime("%H:%M")
    return render_template(
        "main_page.html",
        city=city,
        temperature=temperature,
        feel=feel,
        visibility=visibility,
        weather=weather,
        wind=wind,
        humidity=humidity,
        pressure=pressure,
        time=time_str,
        dew_point=dew_point
    )

# @app.route("/forecast")
# def forecast():
#     city="Kuala Lumpur"

#     url=f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

#     response = requests.get(url)
#     data = response.json()


if __name__ == "__main__":
    app.run(debug=True)

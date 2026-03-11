from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import math
from openai import OpenAI
from flask_cors import CORS
load_dotenv()

#Local memory for data
customer = {
    "name":"Chan",
    "email":"chan@gmail.com"


}

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
CORS(app)
conversation = [
    {
    "role": "system", 
    "content": "You are an AI assistant that helps farmer to provide agricultural advices."
    }
]

@app.route("/")
def home():
    city="Kuching, Sarawak"
    
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()
    
    temperature = round(data["main"]["temp"],1)
    feel = round(data["main"]["feels_like"],1)
    humidity= data["main"]["humidity"]
    pressure= data["main"]["pressure"]
    weather = data["weather"][0]["description"]
    visibility = data["visibility"]
    wind = data["wind"]["speed"]
    customer["weather"] = {
        "city": city,
        "temperature": temperature,
        "humidity": humidity,
        "weather": weather,
        "wind": wind
    }
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

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    question = request.args.get("question")
    answer = None
    
    if question:
        answer = get_chatbot_response(question)

    return render_template("InteractGreg.html", question=question, answer=answer)

def get_chatbot_response(question):
    weather_info = customer.get("weather", {})

    weather_context = f"""
    Current weather in {weather_info.get("city","unknown")}:
    Temperature: {weather_info.get("temperature","unknown")}°C
    Humidity: {weather_info.get("humidity","unknown")}%
    Condition: {weather_info.get("weather","unknown")}
    Wind Speed: {weather_info.get("wind","unknown")} m/s
    """
    conversation.append(
        {"role" : "user", 
         "content": f"""
        Weather data:
        {weather_context}

        Farmer question:
        {question}

        Use the weather information when giving agricultural advice.
        """
        }
    )
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=conversation
    )
    answer = response.choices[0].message.content
    conversation.append(
        {"role" : "assistant", 
         "content": answer
        }
    )

    return answer

@app.route("/chatbot-conversations", methods = ["POST"])
def ask_ai():

    data = request.get_json()
    question = data["question"]

    answer = get_chatbot_response(question)

    return jsonify({"reply": answer})

@app.route("/pre_setup", methods = ["GET", "POST"])
def pre_setup():
    
    if request.method == "POST":
        customer["location"] = request.form.get("location")
        customer["length"]  = request.form.get("length")
        customer["width"]  = request.form.get("width")
        customer["crops"]  = request.form.getlist("crops")
        customer["currency"]  = request.form.get("currency")
        customer["price"]  = request.form.getlist("price")

        return redirect(url_for("profile"))
    
    return render_template("pre_setup.html")



@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

def get_crop_plan(customer):

    area = int(customer["length"]) * int(customer["width"])
    crops = customer["crops"]
    prices = customer["price"]
    prompt = f"""
        A farmer has {area} square meters of land in {customer["location"]}.

        Available crops and market price per kg:
        {crops}
        {prices}

        Distribute the land among these crops to balance between yield and profit

        Rules:
        - Use ONLY the crops listed.
        - The total area must equal {area}.
        - Allocate integer square meters.

        Return ONLY valid JSON. Do not include markdown or ```json blocks and keys in all lowercase.

        Example format:

        {{
        "corn": 20,
        "potato": 30,
        "tomato": 10
        }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an agricultural profit optimization assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

@app.route("/profile", methods = ["GET"])  
def profile():
    suggestion = get_crop_plan(customer)
    print(suggestion)
    combined = zip(customer["crops"], customer["price"])
    print(combined)
    return render_template("profile.html",customer=customer,suggestion=suggestion,combined=combined)

if __name__ == "__main__":
    app.run(debug=True)

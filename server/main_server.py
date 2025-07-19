# main.py
from flask import Flask, request, jsonify
from datetime import datetime
import swisseph as swe
import pytz
from flask_cors import CORS
from combined import get_chart_details
# from langchain_pipeline import run_astrology_graph

app = Flask(__name__)
CORS(app)  

@app.route("/charts", methods=["POST"])
def charts():
    try:
        data = request.json
        dob = data.get("dob")       # e.g. "2003-09-20"
        tob = data.get("tob") 
        timezone_str = data.get("timezone", "Asia/Kolkata")      # e.g. "03:37"
        if not dob or not tob:
            return jsonify({"error": "Missing 'dob' or 'tob'"}), 400

        dt_str = f"{dob} {tob}"
        dt_local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(timezone_str)
        dt_localized = local_tz.localize(dt_local)
        birth_utc = dt_localized.astimezone(pytz.utc)
        # birth_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

        lat, lon = data["lat"], data["lon"]
        result = get_chart_details(birth_utc, lat, lon)
        return jsonify(result)

    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from chat import analyze_user_question, analyze_user_question_stream

@app.route("/chat", methods=["POST"])
def astrology_chat():
    try:
        data = request.json
        dob = data["dob"]
        tob = data["tob"]
        timezone = data.get("timezone", "Asia/Kolkata")
        lat = data["lat"]
        lon = data["lon"]
        question = data["question"]

        result = analyze_user_question(dob, tob, timezone, lat, lon, question)
        return jsonify({"response": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat/stream", methods=["POST"])
def astrology_chat_stream():
    try:
        data = request.json
        dob = data["dob"]
        tob = data["tob"]
        timezone = data.get("timezone", "Asia/Kolkata")
        lat = data["lat"]
        lon = data["lon"]
        question = data["question"]

        def generate():
            for chunk in analyze_user_question_stream(dob, tob, timezone, lat, lon, question):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return app.response_class(generate(), mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500   

if __name__ == "__main__":
    app.run(debug=True)

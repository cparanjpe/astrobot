import google.generativeai as genai
from combined import get_chart_details
from dotenv import load_dotenv
import os
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # OR load from os.environ

model = genai.GenerativeModel("gemini-2.5-flash")

# Determine which divisional charts are needed
def determine_required_charts(user_question: str):
    question = user_question.lower()
    charts = ['D1']  # Always include D1

    # D7 - Saptamsa Chart - Children
    d7_keywords = [
        # Correct terms
        "children", "child", "offspring", "progeny", "kids", "parenting", "parenthood",
        "birth", "pregnancy", "fertility", "procreation", "family", "lineage", "descendants",
        "son", "daughter", "childbirth", "nurturing", "raising children", "parental",
        # Misspellings  
        "childen", "offsprings", "progeny", "kid", "paranting", "parenthod", "fertillity",
        "procreatoin", "familly", "lineagee", "descendents", "sonn", "daugter", "childbrith",
        "nurturingg", "raisingg children", "parental"
        # Indian usage
        "saptamsa", "saptamsha", "putra", "putri", "santaan", "santan", "santati", "santati chart",
        "putra karaka", "putra bhava", "saptamsa chart","d7"

    ]

    # D9 - Marriage, Relationships
    d9_keywords = [
        # Correct terms
        "marriage", "partner", "relationship", "spouse", "husband", "wife", "love", "romantic",
        "wedding", "marital", "conjugal", "matchmaking", "compatibility",
        "boyfriend", "girlfriend", "affair", "commitment", "dating",
        # Misspellings
        "marraige", "mariage", "relashionship", "relatnship", "spouce", "husbund", "wief", 
        "romence", "romatic", "compability", "compatiblity", "mathcmaking",
        "boyfreind", "girfreind", "gurlfriend", "bf", "gf", "dateing",
        # Indian usage
        "shaadi", "vivah", "rishta", "kundli match", "kundli milan", "lagan", "mangal dosha","d9"
    ]

    # D20 - Spiritual Growth
    d20_keywords = [
        # Correct terms
        "spiritual", "moksha", "liberation", "enlightenment", "soul", "atma", "inner peace",
        "spirituality", "transcendence", "sadhana", "meditation", "karma", "bhakti", "jnana",
        "dhyana", "ascetic", "monk", "yogi", "yogini", "kundalini", "awakening", "samadhi",
        "inner self", "soul path", "purpose of life", "inner journey", "detachment",
        # Misspellings and typos
        "spritiual", "spritiul", "moksh", "liberasion", "liberration", "entlightenment",
        "medatation", "mediation", "mediatation", "spiritulity", "transendance", "sadhna",
        "karma yoga", "dian", "samadi", "enlightnment", "soull", "bhakthi", "gnana",
        # Slang or common modern phrasing
        "soul searching", "finding myself", "purpose", "life path", "destiny", "divine","d20"
    ]

    # Check for keywords in the question
    if any(keyword in question for keyword in d7_keywords):
        charts.append('D7')
    if any(keyword in question for keyword in d9_keywords):
        charts.append('D9')
    if any(keyword in question for keyword in d20_keywords):
        charts.append('D20')

    print(f"seelected charts: {charts}")

    return charts


# Format the chart data for Gemini input
def format_chart_for_llm(chart_data: dict, charts_needed: list):
    def format_chart(chart_name: str, chart: dict):
        lines = [f"**{chart_name} Chart**"]
        asc = chart.get("ascendant", "Unknown")
        lines.append(f"Ascendant: {asc}")
        lines.append("House Positions:")
        for house, planets in chart.get("chart", {}).items():
            planet_list = ', '.join(planets) if planets else 'None'
            lines.append(f"  House {house}: {planet_list}")
        lines.append("House Lords:")
        for house, details in chart.get("lords", {}).items():
            lines.append(
                f"  House {house}: Lord is {details['lord']} placed in House {details['lord_house']} ({details['sign']})"
            )
        return "\n".join(lines)

    def format_planetary_data(planets: dict):
        lines = ["**Planetary Positions (D1)**"]
        for planet, info in planets.items():
            lines.append(
                f"  {planet}: {info['sign']} {round(info['degree'], 2)}°, "
                f"Nakshatra: {info['nakshatra']} Pada {info['pada']}"
            )
        return "\n".join(lines)

    sections = []

    # Always add planetary data from D1
    if 'planets' in chart_data:
        sections.append(format_planetary_data(chart_data["planets"]))

    for chart_key in charts_needed:
        chart_upper = chart_key.upper()
        if chart_key.lower() in chart_data:
            chart = chart_data[chart_key.lower()]
            sections.append(format_chart(chart_upper, chart))

    return "\n\n".join(sections)

# Main logic
def analyze_user_question(dob, tob, timezone, lat, lon, question):
    # Step 1: Get UTC datetime
    from datetime import datetime
    import pytz

    dt_local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    local_tz = pytz.timezone(timezone)
    dt_localized = local_tz.localize(dt_local)
    birth_utc = dt_localized.astimezone(pytz.utc)

    # Step 2: Get chart data
    full_chart_data = get_chart_details(birth_utc, lat, lon)

    # Step 3: Determine which charts to use
    charts_needed = determine_required_charts(question)

    # Step 4: Format chart data
    chart_text = format_chart_for_llm(full_chart_data, charts_needed)

    # Step 5: Generate prompt
    prompt = f"""You are a learned Vedic astrologer. A user has provided their birth chart data.
Use the data below to answer their question.

User Question:
"{question}"

Date of Birth: {dob}
Time of Birth: {tob}
Location: lat={lat}, lon={lon}, Timezone={timezone}

Chart Data:
{chart_text}

Please answer clearly and concisely in astrological terms. contemplate and answer.
"""

    # Step 6: Call Gemini with streaming
    # print("prompt to gemini-->",prompt)
    response = model.generate_content(prompt, stream=True)
    
    # Collect all chunks and return the complete response
    full_response = ""
    for chunk in response:
        if chunk.text:
            full_response += chunk.text
    
    return full_response

# Streaming version of the analyze function
def analyze_user_question_stream(dob, tob, timezone, lat, lon, question):
    # Step 1: Get UTC datetime
    from datetime import datetime
    import pytz

    dt_local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    local_tz = pytz.timezone(timezone)
    dt_localized = local_tz.localize(dt_local)
    birth_utc = dt_localized.astimezone(pytz.utc)

    # Step 2: Get chart data
    full_chart_data = get_chart_details(birth_utc, lat, lon)

    # Step 3: Determine which charts to use
    charts_needed = determine_required_charts(question)

    # Step 4: Format chart data
    chart_text = format_chart_for_llm(full_chart_data, charts_needed)

    # Step 5: Generate prompt
    prompt = f"""You are a learned Vedic astrologer. A user has provided their birth chart data.
Use the data below to answer their question.

User Question:
"{question}"

Date of Birth: {dob}
Time of Birth: {tob}
Location: lat={lat}, lon={lon}, Timezone={timezone}

Chart Data:
{chart_text}

Please answer clearly and concisely in astrological terms. contemplate and answer.
"""

    # Step 6: Call Gemini with streaming
    response = model.generate_content(prompt, stream=True)
    
    # Yield each chunk as it arrives
    for chunk in response:
        if chunk.text:
            yield chunk.text

def generate_next_questions(current_question):
    """
    Calls the LLM to generate the next set of relevant questions.
    """
    try:
        # Simulate LLM call using Google Generative AI
        prompt = f"Based on the question given to a vedic astrology chatbot suggest additional questions(user could ask so they dont have to type it out).Additional questions can be followups,etc. Question: '{current_question}'. Suggest 4 questions and one from different category so user has a little variety.RESPONSE SHOULD BE A STRING WITH QUESTIONS SEPARATED BY NEWLINE(\n)"
        response = model.generate_content(prompt)
        print(response.text)
        # Parse the response to extract questions (assuming response is a string with questions separated by newlines)
        questions = response.text.split("\n")
        return [q.strip() for q in questions if q.strip()]

    except Exception as e:
        print(f"Error generating next questions: {e}")
        return []

from datetime import datetime
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain_google_genai import ChatGoogleGenerativeAI
import pytz
from dotenv import load_dotenv
import os
from combined import get_chart_details
load_dotenv()


# ---------------- State ----------------

class GraphState(TypedDict):
    question: str
    charts: List[str]
    chart_data: dict
    final_prompt: str
    llm_response: str


# ---------------- Chart Classifier ----------------

def classify_charts(state: GraphState) -> GraphState:
    question = state["question"].lower()
    charts = ["d1"]
    if any(k in question for k in ["spiritual", "moksha", "meditation", "liberation"]):
        charts.append("d20")
    if any(k in question for k in ["marriage", "partner", "love", "relationship"]):
        charts.append("d9")
    return {**state, "charts": charts}


# ---------------- Fetch Chart Data ----------------

def fetch_chart_data(state: GraphState) -> GraphState:
    # REPLACE THIS WITH REAL /charts API CALL
    
    dob= "1968-12-31"
    tob= "08:42"
    timezone_str = "Asia/Kolkata"
    dt_str = f"{dob} {tob}"
    dt_local = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    local_tz = pytz.timezone(timezone_str)
    dt_localized = local_tz.localize(dt_local)
    birth_utc = dt_localized.astimezone(pytz.utc)
    lat= 18.9690
    lon= 72.8205


    chart_data = get_chart_details(birth_utc, lat, lon)
    print(chart_data)
    # charts = [chart_data.d1,chart_data.d9, chart_data.d20]
    return {**state, "chart_data": chart_data}


# ---------------- Format Prompt ----------------

def format_prompt(state: GraphState) -> GraphState:
    chart_data = state["chart_data"]
    charts = state["charts"]
    output = ["I'll tell you my placements house wise:\n"]

    for chart_key in charts:
        chart = chart_data.get(chart_key)
        if not chart:
            continue

        output.append(f"\nFrom chart {chart_key.upper()}:\n")

        chart_houses = chart.get("chart", {})
        for house, planets in chart_houses.items():
            if planets:
                planets_str = ", ".join(planets)
                output.append(f"House {house}: {planets_str}")

        output.append("\nHouse lords:")
        for house, data in chart.get("lords", {}).items():
            output.append(
                f"House {house} is ruled by {data['lord']} (in house {data['lord_house']}, sign {data['sign']})."
            )

    full_prompt = "\n".join(output)
    full_prompt += f"\n\nNow based on the above placements, please answer this question:\n{state['question']}"
    return {**state, "final_prompt": full_prompt}


# ---------------- Call Gemini LLM ----------------

def call_gemini(state: GraphState) -> GraphState:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5
    )
    print(state)
    result = llm.predict(state["final_prompt"])
    return {**state, "llm_response": result}


# ---------------- Graph Builder ----------------

def build_astrology_graph():
    print("building")
    graph = StateGraph(GraphState)

    graph.add_node("ClassifyCharts", classify_charts)
    graph.add_node("FetchChartData", fetch_chart_data)
    graph.add_node("GeneratePrompt", format_prompt)
    graph.add_node("CallGeminiLLM", call_gemini)

    graph.set_entry_point("ClassifyCharts")
    graph.add_edge("ClassifyCharts", "FetchChartData")
    graph.add_edge("FetchChartData", "GeneratePrompt")
    graph.add_edge("GeneratePrompt", "CallGeminiLLM")
    graph.add_edge("CallGeminiLLM", END)

    return graph.compile()

graph = build_astrology_graph()
result = graph.invoke({"question": "How will my marriage be? "})

print(result["llm_response"])

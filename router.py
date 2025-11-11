import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from flows import (
    run_browse_flow,
    run_validation_flow,
    run_contact_flow,
    run_about_flow,
    run_normal_flow,
)
from system_message import system_prompt

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key
)

from typing import TypedDict, Optional, List

class RouterState(TypedDict, total=False):
    input: str
    output: str
    route_history: List[str]


def llm_router_node(state: RouterState):
    user_message = state.get("input", "")
    if not user_message:
        print("⚠️ Missing 'input' in state, defaulting to normal flow.")
        return {"input": "", "output": "normal", "route_history": ["router→normal"]}

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    llm_response = llm.invoke(messages)
    detected_flow = llm_response.content.strip().lower()

    # --- Log routing decision ---
    print(f"🔀 LLM Routed to → {detected_flow}")

    # --- Update route history ---
    route_history = state.get("route_history", [])
    route_history.append(f"router→{detected_flow}")

    return {"input": user_message, "output": detected_flow, "route_history": route_history}




graph = StateGraph(RouterState)

graph.add_node("router", llm_router_node)
graph.add_node("browse_used_cars", run_browse_flow)
graph.add_node("get_car_validation", run_validation_flow)
graph.add_node("contact_us", run_contact_flow)
graph.add_node("about_us", run_about_flow)
graph.add_node("normal", run_normal_flow)

graph.add_edge(START, "router")

graph.add_conditional_edges(
    "router",
    lambda state: state["output"],  
    {
        "browse_used_cars": "browse_used_cars",
        "get_car_validation": "get_car_validation",
        "contact_us": "contact_us",
        "about_us": "about_us",
        "normal": "normal"
    },
)

graph.add_edge("browse_used_cars", END)
graph.add_edge("get_car_validation", END)
graph.add_edge("contact_us", END)
graph.add_edge("about_us", END)
graph.add_edge("normal", END)

graph_dynamic = graph.compile()


# ===========================================================
# Helper: Pretty Print Flow Route
# ===========================================================
def print_route_summary(state: RouterState):
    print("\n🧭 Routing Path Trace:")
    for step in state.get("route_history", []):
        print(f"   → {step}")
    print("✅ Flow execution completed successfully.\n")


if __name__ == "__main__":
    query = "show me all type all brand cars ?"
    print(f"\n💬 User Query: {query}")
    print("===========================================")

    result = graph_dynamic.invoke({"input": query})

    print_route_summary(result)
    print("=== 🏁 Final Output ===")
    print(result["output"])

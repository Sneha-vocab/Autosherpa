# flow_nodes.py (temporary version for testing router)

from system_message import (
    browse_used_cars_start,
    get_car_validation_start,
    contact_us_start,
    about_us_start,
    normal_start
)

# --- Dummy Flow Class ---
class DummyFlow:
    def invoke(self, state):
        query = state.get("input", "")
        return {"output": f"[Simulated Response] Flow processed input: '{query}'"}

# --- Dummy flow instances ---
browse_used_cars_flow = DummyFlow()
car_validation_flow = DummyFlow()
contact_us_flow = DummyFlow()
about_us_flow = DummyFlow()

# === Flow Runners ===
def run_browse_flow(state):
    query = state["input"]
    print("🚗 Running Browse Used Cars flow...")
    result = browse_used_cars_flow.invoke({"input": query})
    return {"output": f"{browse_used_cars_start}\n\n{result['output']}"}

def run_validation_flow(state):
    query = state["input"]
    print("📊 Running Car Validation flow...")
    result = car_validation_flow.invoke({"input": query})
    return {"output": f"{get_car_validation_start}\n\n{result['output']}"}

def run_contact_flow(state):
    query = state["input"]
    print("📞 Running Contact Us flow...")
    result = contact_us_flow.invoke({"input": query})
    return {"output": f"{contact_us_start}\n\n{result['output']}"}

def run_about_flow(state):
    query = state["input"]
    print("ℹ️ Running About Us flow...")
    result = about_us_flow.invoke({"input": query})
    return {"output": f"{about_us_start}\n\n{result['output']}"}

def run_normal_flow(state):
    print("💬 Running Normal flow...")
    return {"output": normal_start}

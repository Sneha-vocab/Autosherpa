from jinja2 import Template
from .config import settings
# optionally use an LLM to polish, else return templated string

# Example template library (extend per intent)
TEMPLATES = {
    "buy_car_list": "Here are some cars you might like:\n{% for car in cars %}- {{car.name}} (₹{{car.price}})\n{% endfor %}Would you like to filter by fuel type or budget?",
    "testdrive_request": "I can book a test drive for {{car}}. When would you like to come (date & time)?",
    "testdrive_confirm": "Your test drive for {{car}} is confirmed for {{slot}}. See you then!",
    "finance_emi": "Estimated EMI for {{car}} at price ₹{{price}} for {{tenure}} months is approximately ₹{{emi}}/month.",
    "fallback": "Sorry, I didn't understand that. I can help with: Buy, Test Drive, Compare, Finance, Valuation, or Service. Which would you like?"
}

def format_template(key: str, **ctx):
    tpl = TEMPLATES.get(key, "{{message}}")
    return Template(tpl).render(**ctx)

# optional LLM polish function (pseudo)
def polish_with_llm(text: str, context: dict | None = None) -> str:
    # If you have an LLM configured, call it to rephrase to brand tone.
    # For demo return text as-is.
    return text

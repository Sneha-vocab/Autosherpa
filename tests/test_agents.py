# tests/test_agents.py
import pytest
from app import testdrive_handle, finance_handle
from app.services.car_service import CARS

# Use the test client or call agents directly

def test_testdrive_agent_needs_model():
    # when no model is specified, should ask for model
    reply = testdrive_handle("919000000000", "I want to book a test drive", {})
    assert "model" in reply.lower() or "which model" in reply.lower() or "which" in reply.lower()

def test_testdrive_agent_with_model_books_slot():
    # specify a known model (using our stub tokens e.g., 'nexon')
    reply = testdrive_handle("919000000000", "Book a test drive for Nexon", {})
    assert "confirmed" in reply.lower() or "book" in reply.lower() or "scheduled" in reply.lower()

def test_finance_agent_requires_price_or_model():
    reply = finance_handle("919000000000", "Calculate EMI", {})
    assert "please share" in reply.lower() or "share the car model" in reply.lower() or "price" in reply.lower()

def test_finance_agent_with_model_calculates():
    # get a model from stub CARS list to ensure price exists
    model = CARS[0]["id"]
    # form text asking EMI for model
    reply = finance_handle("919000000000", f"EMI for {model}", {})
    assert "emi" in reply.lower() or "estimated" in reply.lower() or "₹" in reply or "rupee" in reply.lower()

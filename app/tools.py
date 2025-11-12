"""
LangChain tools for AutoSherpa agents.
These tools wrap the service functions for use with LangChain agents.
"""
from typing import Optional, List, Dict
from langchain_core.tools import tool
from .services import (
    car_service,
    testdrive_service,
    finance_service,
    valuation_service,
    service_center,
)
from .faqs import search_faq


@tool
def search_cars(brand: Optional[str] = None, budget_lt: Optional[int] = None) -> List[Dict]:
    """Search for cars by brand and/or maximum budget.
    
    Args:
        brand: Car brand name (e.g., 'hyundai', 'tata', 'kia')
        budget_lt: Maximum budget in INR (e.g., 1500000 for 15 lakh)
    
    Returns:
        List of car dictionaries with id, name, price, and fuel type
    """
    return car_service.search_cars(brand=brand, budget_lt=budget_lt)


@tool
def get_car_by_id(car_id: str) -> Optional[Dict]:
    """Get detailed information about a specific car by its ID.
    
    Args:
        car_id: Car model ID (e.g., 'nexon', 'creta', 'seltos')
    
    Returns:
        Car dictionary with id, name, price, and fuel type, or None if not found
    """
    return car_service.get_car_by_id(car_id)


@tool
def book_testdrive(user_phone: str, car_model: str, slot: str) -> Dict:
    """Book a test drive appointment.
    
    Args:
        user_phone: User's phone number
        car_model: Car model ID (e.g., 'nexon', 'creta')
        slot: Time slot in format 'YYYY-MM-DD HH:MM'
    
    Returns:
        Booking confirmation dictionary
    """
    booking = testdrive_service.book_testdrive(user_phone=user_phone, car_model=car_model, slot=slot)
    return {
        "id": getattr(booking, "id", None),
        "user_phone": user_phone,
        "car_model": car_model,
        "slot": slot,
    }


@tool
def get_available_testdrive_slots(location: Optional[str] = None, date: Optional[str] = None) -> List[str]:
    """Get available test drive time slots.
    
    Args:
        location: Optional location filter
        date: Optional date filter in format 'YYYY-MM-DD'
    
    Returns:
        List of available slots in format 'YYYY-MM-DD HH:MM'
    """
    return testdrive_service.available_slots(location=location, date=date)


@tool
def calculate_emi(principal: int, annual_rate_percent: float = 8.5, months: int = 60) -> float:
    """Calculate EMI (Equated Monthly Installment) for a car loan.
    
    Args:
        principal: Loan amount in INR
        annual_rate_percent: Annual interest rate percentage (default 8.5)
        months: Loan tenure in months (default 60)
    
    Returns:
        Monthly EMI amount in INR
    """
    return finance_service.calculate_emi(principal=principal, annual_rate_percent=annual_rate_percent, months=months)


@tool
def estimate_car_value(model: str, year: int, kms: int = 0, condition: str = "good") -> int:
    """Estimate the resale value of a car.
    
    Args:
        model: Car model ID (e.g., 'nexon', 'creta')
        year: Registration year (e.g., 2018, 2020)
        kms: Total kilometers driven (default 0)
        condition: Car condition - 'excellent', 'good', 'fair', or 'poor' (default 'good')
    
    Returns:
        Estimated resale value in INR
    """
    return valuation_service.estimate_value(model=model, year=year, kms=kms, condition=condition)


@tool
def list_service_packages() -> List[Dict]:
    """Get list of available service packages.
    
    Returns:
        List of service package dictionaries with id, name, price, and description
    """
    return service_center.list_packages()


@tool
def get_available_service_slots(location: Optional[str] = None, date: Optional[str] = None) -> List[str]:
    """Get available service appointment time slots.
    
    Args:
        location: Optional location filter
        date: Optional date filter in format 'YYYY-MM-DD'
    
    Returns:
        List of available slots in format 'YYYY-MM-DD HH:MM'
    """
    return service_center.available_slots(location=location, date=date)


@tool
def book_service_appointment(user_phone: str, car_model: str, slot: str, package_id: Optional[str] = None) -> Dict:
    """Book a service appointment.
    
    Args:
        user_phone: User's phone number
        car_model: Car model ID (e.g., 'nexon', 'creta')
        slot: Time slot in format 'YYYY-MM-DD HH:MM'
        package_id: Optional service package ID (e.g., 'basic', 'comprehensive')
    
    Returns:
        Booking confirmation dictionary
    """
    booking = service_center.book_service(user_phone=user_phone, car_model=car_model, slot=slot, package_id=package_id)
    return {
        "id": getattr(booking, "id", None),
        "user_phone": user_phone,
        "car_model": car_model,
        "slot": slot,
        "package_id": package_id,
    }


@tool
def faq_lookup(question: str) -> str:
    """Look up answers from the Sherpa Hyundai FAQ knowledge base."""
    return search_faq(question)


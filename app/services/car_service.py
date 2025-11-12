# simple stub data, replace with real DB/API queries
CARS = [
    {"id": "nexon", "name": "Tata Nexon", "price": 999900, "fuel": "petrol"},
    {"id": "creta", "name": "Hyundai Creta", "price": 1399000, "fuel": "petrol"},
    {"id": "seltos", "name": "Kia Seltos", "price": 1299000, "fuel": "petrol"},
]

def search_cars(brand: str|None=None, budget_lt: int|None=None):
    results = CARS
    if brand:
        results = [c for c in results if brand.lower() in c["name"].lower()]
    if budget_lt:
        results = [c for c in results if c["price"] <= budget_lt]
    return results

def get_car_by_id(car_id: str):
    for c in CARS:
        if c["id"] == car_id:
            return c
    return None

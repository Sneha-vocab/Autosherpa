def calculate_emi(principal: int, annual_rate_percent: float, months: int):
    r = annual_rate_percent / 12 / 100
    if r == 0:
        emi = principal / months
    else:
        emi = principal * r * (1 + r)**months / ((1 + r)**months - 1)
    return round(emi)

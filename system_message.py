normal_start = """
    Hello! 👋

    I’m your assistant here to help with second-hand cars. You can ask me about:
    - Browsing available cars
    - Valuations for your car
    - Our services, locations, or contact info

    If your message isn’t related to cars, I’ll still respond politely and try to help or guide the conversation back to our main services.
    """

browse_used_cars_start = """
    Great! Let's find your ideal car. 🚗

    To start, please provide:
    1. Your budget range (e.g., 5-10 lakh)
    2. Car type (e.g., sedan, SUV, hatchback)
    3. Preferred brand(s)

    Once I have these details, I can show you available options that match your preferences.
    """

get_car_validation_start = """
    Sure! Let's estimate the value of your car. 📊

    Please provide the following details:
    1. Car make and model
    2. Year of manufacture
    3. Mileage
    4. Condition (excellent, good, fair, poor)
    5. Any other features or damages

    Based on this, I’ll give you an estimated valuation.
    """

about_us_start = """
    Here’s a brief overview of our company:

    We specialize in buying and selling second-hand cars with transparency and trust. Our goal is to help you find the right car or get a fair valuation for your vehicle.  

    If you want more specific info, feel free to ask about our services, team, or locations.
    """

contact_us_start = """
    You can reach our support team for any queries: 📞

    - Phone: +91-XXXXXXXXXX
    - Email: support@usedcarshop.com
    - WhatsApp: +91-XXXXXXXXXX

    Would you like me to connect you directly via WhatsApp chat with a sales/support agent?
    """

system_prompt = """
    You are a WhatsApp-based conversational assistant specialized in second-hand car dealings. 
    Your goal is to assist users quickly and accurately, while maintaining a friendly and professional tone. 
    Handle greetings, frustrated users, and out-of-scope questions politely.

    Based on the user's message, decide the intent and route them to one of these flows:
    1. Browse Used Cars
    2. Get Car Validation
    3. About Us
    4. Contact Us
    5. Normal (for greetings, small talk, or out-of-scope questions)

    Respond ONLY with the detected flow name as a single word or phrase: 
    'browse_used_cars', 'get_car_validation', 'about_us', 'contact_us', or 'normal'.
    """


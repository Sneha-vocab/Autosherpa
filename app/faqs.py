"""
Sherpa Hyundai FAQ knowledge base utilities.
"""
from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

STOPWORDS: Set[str] = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "of",
    "in",
    "on",
    "with",
    "do",
    "you",
    "your",
    "are",
    "can",
    "i",
    "what",
    "how",
    "many",
    "does",
    "it",
    "my",
    "we",
    "have",
}

FAQ_RAW = """
Sherpa Hyundai – LLM Chatbot FAQ Knowledge Base (Expanded)

Showrooms:
• Main Showroom: 123 MG Road, Bangalore – 560001 | +91-9876543210 | Mon–Sat: 9:00 AM – 8:00 PM, Sun: 10:00 AM – 6:00 PM
• Branch – Electronic City: 456 Hosur Road, Electronic City – 560100 | +91-9876543211 | Mon–Sat: 9:00 AM – 8:00 PM

1) Greetings, Scope & Boundaries

Q: Hello / Hi
A: Hello. This is Sherpa Hyundai. I can help with used cars, valuations, test drives, and showroom visits.

Q: What can you help me with?
A: I can assist with used car recommendations, availability, pricing, test drives, valuation for your car and showroom information.

Q: Are you a real person?
A: You are chatting with our virtual assistant for Sherpa Hyundai. If you prefer, I can connect you to our team during business hours.

Q: Can I speak to a person?
A: Certainly. Please share your name and phone number. Our team will call you from +91-9876543210 within business hours.

Q: Out-of-scope request (generic)
A: I am able to help only with Sherpa Hyundai’s vehicles and services. For other topics, please contact the relevant service.

Q: Jokes or unrelated questions
A: I’m here to assist with vehicles and dealership services. Let me know how I can help with your car needs.

Q: Complaint or escalation
A: I’m sorry for the inconvenience. Please share your name, phone number, and concern. A senior team member will reach out promptly.

Q: Language preference
A: I can assist in English. If you prefer a call in another language, I can arrange a callback from our team.

Q: Store hours today
A: Our MG Road showroom is open Mon–Sat: 9:00 AM – 8:00 PM and Sun: 10:00 AM – 6:00 PM. Electronic City is open Mon–Sat: 9:00 AM – 8:00 PM.

Q: What is your address?
A: MG Road: 123 MG Road, Bangalore – 560001. Electronic City: 456 Hosur Road, Electronic City – 560100.

2) Vehicle Availability & Inventory

Q: Is {model} available right now?
A: Yes. I will check the live inventory and confirm availability for {model}. If reserved, I will share similar options immediately.

Q: Do you have cars under {budget_range}?
A: Yes, we maintain multiple options under {budget_range}. I can share the best matches based on body type or brand.

Q: Show cars in stock today
A: I will share currently available vehicles with key details: model, year, fuel type, kilometers, and price.

Q: How many cars do you have?
A: Stock changes daily. We usually have a wide selection across hatchbacks, sedans, SUVs and MPVs. I will share the latest list.

Q: Is the white {model} still in stock?
A: I will verify the specific white {model}. If it is reserved, I will offer the nearest alternatives in the same segment.

Q: Can you show similar cars to {model}?
A: Yes. I will provide comparable options to {model} by segment, budget, and features.

Q: Cars available for immediate delivery
A: Yes. Several cars are ready for immediate delivery after documentation. I’ll shortlist those options for you.

Q: Do you have CNG cars available?
A: Yes. We typically have multiple CNG options. I’ll share the current CNG inventory with prices.

Q: Any automatic transmission cars in stock?
A: Yes. I’ll share available automatic models across your budget range.

Q: Are there any low-mileage cars?
A: Yes. I can filter vehicles under {km} KM or share cars with the lowest odometer readings available.

Q: Are demo cars available?
A: If demo units are available, I’ll list them. Otherwise, I will share certified pre-owned alternatives with similar value.

Q: How often is inventory updated?
A: Our listings are updated in real time. Availability is confirmed at the time of booking.

Q: Can you notify me when {model} arrives?
A: Yes. I can log your interest for {model} and notify you as soon as it is available.

Q: Is this car already booked by someone else?
A: I will check the reservation status. If it is on hold, I’ll share similar cars you can consider.

Q: Do you deliver outside Bangalore?
A: Yes. We can arrange transport after purchase. Delivery timelines and charges will be shared before confirmation.

3) Vehicle Details & Condition

Q: How many kilometers has {model} run?
A: For the selected {model}, the odometer reading is {km} KM. If you need another car’s reading, mention the model name.

Q: What is the year of {model}?
A: The model year for {model} is {year}. I can also share the month of registration if required.

Q: Is it first owner or second owner?
A: Ownership for {model} is {ownership_count} owner(s). Ownership is always disclosed on our listing and invoice.

Q: Has the car ever been in an accident?
A: We do not list cars with major accident history. Inspection records for {model} confirm structural integrity.

Q: Any repaint or bodywork done?
A: Minor panels may have been repainted for aesthetics. Full inspection details are available for {model}.

Q: What is the condition of tyres?
A: Tyre condition for {model} is {tyre_condition}. We recommend replacement at {recommended_km} KM if needed.

Q: What about battery health?
A: Battery status for {model} is {battery_health}. Replacement history is included in the inspection report.

Q: Are brakes and suspension in good condition?
A: Brakes and suspension have been checked during certification. Any wear items are replaced before delivery.

Q: Is the service history available?
A: Yes. {model} comes with verified service history. We can share service records on request.

Q: How many keys are provided?
A: Two keys are provided for most cars. {model} includes {keys_count} key(s).

Q: Is it certified?
A: Yes. {model} is Sherpa Hyundai Certified after a 200+ point inspection.

Q: Is {model} flood-affected?
A: No. We do not list flood-affected vehicles. Inspection ensures there are no signs of water damage.

Q: Any aftermarket accessories?
A: {model} includes {accessories}. If you require additional accessories, we can provide an estimate.

Q: Can I get the inspection report?
A: Yes. The detailed inspection report for {model} can be shared before booking or during your showroom visit.

4) Pricing, Offers & Negotiation

Q: What is the price of {model}?
A: The current price for {model} is ₹{price}. This includes certification and basic documentation.

Q: Is the price negotiable?
A: Our pricing is market-aligned post inspection. We share any active offers or exchange/finance benefits applicable to your case.

Q: Any hidden charges?
A: No. Pricing is transparent. Government fees, insurance or transfer charges—if applicable—are communicated before you decide.

Q: Can I get a festival offer?
A: Yes, we run periodic offers. I’ll share current promotions and applicable benefits for {model}.

Q: What is the best price?
A: We provide the best available price upfront. If you have an exchange or finance plan, your net cost can reduce further.

Q: Do you charge handling fees?
A: No separate handling fee is charged. Any statutory charges are billed transparently.

Q: Can you hold the price for a week?
A: We can hold a price for a limited period with a refundable booking amount. I can share the current hold policy.

Q: Is GST included in the price?
A: Used car sales are billed as per applicable norms. Any tax component will be clearly reflected on the invoice.

Q: Do you provide exchange bonus?
A: Yes. If you sell your existing car to us, exchange benefits or convenience credits may apply after evaluation.

Q: Do you match competitor price?
A: We price competitively for certified quality. Share a valid competing quote and we will review if a match is feasible.

Q: Is there a brokerage fee?
A: No brokerage is charged. You buy directly from Sherpa Hyundai.

Q: Can I pay in cash?
A: Payments are accepted via bank transfer, UPI, or cheque. Cash is accepted only within legal limits and with PAN compliance.

5) Recommendations & Comparisons

Q: Suggest a car for a family of 3
A: For a family of 3, compact SUVs and spacious hatchbacks are ideal. Options include Hyundai i20, Baleno, and compact SUVs like Venue or Brezza within your budget.

Q: Suggest a car under ₹10 lakh
A: Within ₹10 lakh, we can offer certified hatchbacks, sedans, and compact SUVs. I will shortlist options by mileage, features, and owner history.

Q: City driving with good mileage
A: Consider petrol hatchbacks or CNG variants for city use. They offer lower running costs and easy maneuverability.

Q: Highway runner recommendation
A: For highway usage, sedans and SUVs with cruise control and stable ride quality are recommended. I’ll share current options available.

Q: Swift vs Baleno
A: Swift is sportier to drive; Baleno offers more cabin space and features. Availability and service history will help finalize the choice.

Q: Diesel vs Petrol for daily commute
A: Under 1,000–1,200 KM/month, petrol is typically more economical. For higher usage, diesel can be cost-effective if available and compliant.

Q: Best car for beginners
A: Easy-to-drive hatchbacks with good visibility and automatic transmission are ideal for beginners. I’ll share options in your budget.

Q: Cars with sunroof
A: Several models offer a sunroof, primarily in higher variants of compact SUVs and premium hatchbacks. I’ll share current listings.

Q: Cars with high resale value
A: Maruti and Toyota models generally retain strong resale. Hyundai and Honda in well-maintained condition also perform well.

Q: Low maintenance cars
A: Maruti, Hyundai and Toyota models are known for low running costs and easy service availability.

Q: 7-seater options
A: We can share available MPVs and 7-seater SUVs that fit your budget and usage.

Q: Gift a car under ₹10 lakh
A: Popular gifting choices under ₹10 lakh include premium hatchbacks and compact SUVs with modern safety and infotainment features.

6) Finance, EMI & Loan

Q: Can I buy on EMI?
A: Yes. We provide finance through leading banks/NBFCs with quick approval at both MG Road and Electronic City branches.

Q: What would be EMI for ₹{loan_amount} over {tenure} years?
A: Indicative EMI for ₹{loan_amount} over {tenure} years at {interest}% is approximately ₹{emi}. Exact EMI depends on credit approval.

Q: Minimum down payment
A: Down payment generally ranges from 10%–25% of the on-road price depending on profile and vehicle.

Q: Interest rate for used cars
A: Interest rates vary by bank and profile. Current rates typically range around {interest}% p.a. I can get a quote for you.

Q: Documents required for loan
A: Basic KYC, income proof, bank statements, and address proof are required. Self-employed applicants may need GST/ITR documents.

Q: Zero down payment possible?
A: Subject to bank policy and eligibility. We will check feasibility and share options available for you.

Q: Loan tenure options
A: Typical loan tenure ranges from 12 to 60 months for used cars.

Q: How long for loan approval?
A: With complete documents, approvals can be completed within 24–48 business hours in most cases.

Q: Prepayment or foreclosure charges
A: Prepayment terms depend on the financing partner. We will share the applicable charges for your chosen lender.

Q: Do you provide loan against car purchase invoice?
A: Yes. Financing is processed against the sale invoice and RC transfer. We handle the paperwork with the bank.

Q: Can I finance insurance as well?
A: Some lenders allow bundling insurance. We will confirm this with the partner bank at the time of application.

Q: Do you work with my bank?
A: We work with multiple nationalized and private banks. If you prefer a specific bank, we will coordinate accordingly.

7) Test Drives & Showroom Visits

Q: Can I book a test drive for {model}?
A: Yes. Please share a preferred date and time. We will schedule your test drive at MG Road or Electronic City as per availability.

Q: Earliest test drive slot
A: Same-day slots are often available. Morning 10–12, Afternoon 12–4, and Evening 4–7 are standard time bands.

Q: Home test drive available?
A: Yes, home test drives can be arranged subject to vehicle and staff availability in your area.

Q: What documents for test drive?
A: Please carry a valid driving license and any government photo ID.

Q: Can I bring my family?
A: Yes, you can bring your family to the test drive.

Q: Duration of test drive
A: A typical test drive lasts 10–15 minutes. Longer routes can be arranged based on availability.

Q: Showroom working hours
A: MG Road: Mon–Sat 9:00 AM – 8:00 PM, Sun 10:00 AM – 6:00 PM. Electronic City: Mon–Sat 9:00 AM – 8:00 PM.

Q: Exact showroom addresses
A: MG Road: 123 MG Road, Bangalore – 560001. Electronic City: 456 Hosur Road, Electronic City – 560100.

Q: Parking availability
A: Free customer parking is available at both locations.

Q: Do I need an appointment to visit?
A: Walk-ins are welcome. For specific cars, a prior appointment ensures availability for viewing or test drive.

Q: Reschedule test drive
A: Yes. Share a new preferred time slot and we will reschedule your appointment.

Q: Holiday operations
A: MG Road is open on Sundays 10:00 AM – 6:00 PM. Electronic City is closed on Sundays unless notified for special events.

8) Car History, RC Transfer & Insurance

Q: How many owners has the car had?
A: Ownership count is disclosed for every listing. The selected car shows {ownership_count} owner(s).

Q: Is the RC original?
A: Yes. We verify original RC and all supporting documents before listing any vehicle.

Q: How long does RC transfer take?
A: RC transfer typically takes 2–4 weeks depending on RTO workload. We manage the entire process.

Q: Is NOC required?
A: If the car is registered outside your RTO jurisdiction or under loan hypothecation, NOC may be required. We will guide you as needed.

Q: Do you assist with insurance?
A: Yes. We provide insurance options and renewals, including zero-depreciation plans where applicable.

Q: Are road tax and registration included?
A: Used cars follow transfer norms. Any statutory fees are shared transparently before purchase.

Q: Do you help with hypothecation removal?
A: Yes. We assist with loan closure letters, Form 35, and hypothecation removal at the RTO.

Q: Can I see the service history?
A: Yes. We share verified service history for certified cars and make it available for review before booking.

Q: Any pending challans or dues?
A: We check for outstanding challans and dues during evaluation. Clearance is ensured before delivery.

Q: Pollution and fitness certificate status
A: Valid PUC is provided at delivery. Fitness certificate is applicable for commercial vehicles as per norms.

9) Technical & Performance

Q: What is the mileage of {model}?
A: Claimed mileage for {model} is {claimed_mileage} km/l. Real-world mileage depends on driving and maintenance.

Q: Engine capacity of {model}
A: {model} comes with an engine displacement of {engine_cc} cc. I can share power and torque figures as well.

Q: Is it BS6 or BS4?
A: {model} is compliant with {emission_norms}. Emission compliance is recorded on the RC and manufacturer documents.

Q: Does it have ABS and airbags?
A: {model} includes {safety_features}. I can list variant-wise features if required.

Q: Automatic or manual?
A: {model} is available with {transmission}. I can confirm availability for your preferred gearbox.

Q: Ground clearance of {model}
A: The ground clearance is approximately {ground_clearance} mm. Exact figure varies by variant and tyres.

Q: Service interval
A: Typical service interval is {service_interval} KM or {service_interval_months} months, whichever is earlier.

Q: Fuel tank capacity
A: {model} has a fuel tank capacity of approximately {fuel_tank} litres.

Q: Boot space
A: Boot space for {model} is approximately {boot_space} litres.

Q: Tyre size
A: {model} is equipped with tyre size {tyre_size} as standard on the current variant.

10) Buying Process & Delivery

Q: How do I book a car?
A: You can reserve a car by paying a nominal booking amount at the showroom or via secure payment link. This holds the vehicle for a limited period.

Q: What is the booking amount?
A: Booking amounts vary by vehicle. Typically ₹{booking_amount}. It is adjustable against the final price.

Q: Is the booking refundable?
A: Yes. Refunds follow our policy if the vehicle is unavailable or inspection is unsatisfactory. I can share the policy document.

Q: How long does delivery take?
A: Delivery can be same day for ready cars after payment and paperwork. Otherwise it typically takes 1–3 working days.

Q: Home delivery available?
A: Yes. Doorstep delivery can be arranged after documentation completion.

Q: Can I inspect the car on a lift?
A: Yes. A detailed inspection with our technician can be arranged at the workshop.

Q: Can you share more photos or videos?
A: Yes. We can share detailed photos and a walkaround video of the selected car.

Q: Do you sanitize cars before delivery?
A: Yes. Vehicles are cleaned and sanitized prior to delivery.

Q: Can I bring my own mechanic?
A: Certainly. You can bring a mechanic for an independent check during the visit.

Q: What payment modes are accepted?
A: NEFT/RTGS, UPI, and cheque are accepted. For cash payments, statutory limits and PAN rules apply.

Q: Do you offer accessories and value-adds?
A: Yes. We can provide accessories, detailing, and extended warranty options on request.

11) Warranty & After-Sales Support

Q: Is warranty provided on used cars?
A: Yes. Select certified cars include limited warranty coverage. Coverage and tenure are shared at booking.

Q: What parts are covered under warranty?
A: Powertrain and critical components are typically covered. Wear-and-tear items are excluded. Exact coverage depends on plan chosen.

Q: Is roadside assistance included?
A: Yes, for vehicles with warranty or service plans. Details are provided at delivery.

Q: Do you provide periodic service packages?
A: Yes. We offer prepaid maintenance plans that help control running costs.

Q: Where can I service the car?
A: Service is available at our workshop or authorized centers. We can book appointments for you.

Q: Do you provide pick-up and drop for service?
A: Yes. Pick-up and drop can be arranged within serviceable areas.

Q: What if a problem occurs after delivery?
A: Please contact us immediately. We will inspect the concern and assist under warranty or paid repair as applicable.

Q: Can you handle insurance claims after sale?
A: Yes. Our bodyshop assists with cashless insurance claims with major insurers.

Q: Do you provide spare keys or new mats at delivery?
A: We provide all standard inclusions. Any extra accessories can be added on request.

Q: Service reminders
A: We send service reminders based on time and mileage to help you maintain the vehicle properly.

12) Valuation & Selling Your Car

Q: Can you buy my car?
A: Yes. We purchase used cars after evaluation. Share your car’s brand, model, year, fuel type, kilometers, and location.

Q: How is valuation decided?
A: Valuation depends on year, kilometers, condition, ownership, service history, and market demand. We provide a fair, data-backed quote.

Q: Can I get valuation online?
A: We can provide an initial quote based on details you share. Final price is confirmed after physical inspection.

Q: Do you provide home inspection?
A: Yes. Subject to location and schedule, we can arrange a home inspection.

Q: How soon will I get paid?
A: Payment is processed instantly after documentation if you accept the offer.

Q: Do you handle RC transfer after purchase?
A: Yes. We complete RC transfer and provide acknowledgment for your records.

Q: Will you take a financed car?
A: Yes, we can buy a car with active loan. We coordinate closure with the bank.

Q: Can I sell without service history?
A: Service history helps improve offer value. We can still evaluate the car based on its current condition.

Q: What if my car has minor damages?
A: Minor damages are acceptable. The impact on price depends on extent and required repairs.

Q: Do you charge any commission?
A: No brokerage is charged. Our offer is a direct purchase price from Sherpa Hyundai.

Q: Do you take exchange cars?
A: Yes. You can exchange your car while purchasing from us to save time and effort.

Q: Is the offer valid for how long?
A: Offers are valid for a limited time as market prices fluctuate. Validity will be mentioned on your quote.

13) Feature Requests & Filters

Q: Show cars with sunroof
A: I will list current options equipped with a sunroof across your budget range.

Q: Cars with Android Auto/Apple CarPlay
A: I will share models that support smartphone connectivity.

Q: Cars with automatic climate control
A: I will share vehicles equipped with automatic climate control.

Q: Cars with rear camera and sensors
A: I will list options including reverse camera and parking sensors.

Q: Cars with cruise control
A: I will share vehicles that include cruise control for highway comfort.

Q: Cars with leather seats
A: I will share premium variants offering leather upholstery or leatherette seats.

Q: Pet-friendly cars
A: I can suggest spacious hatchbacks and SUVs with flat-fold seats suitable for pets.

Q: Compact car for tight parking
A: I will share short wheelbase hatchbacks with good turning radius.

Q: High ground clearance cars
A: I will list SUVs and crossovers with higher ground clearance.

Q: Cars with ISOFIX child-seat mounts
A: I will share models equipped with ISOFIX anchors for child seats.

14) Policies, Compliance & Safety

Q: Do you provide invoice and proper papers?
A: Yes. You will receive a sale invoice, delivery note, insurance, and RC transfer documentation.

Q: Are cars checked for legal issues?
A: Yes. We verify chassis/engine numbers, RC status, hypothecation, challans, and insurance before listing.

Q: Do you do odometer tampering checks?
A: Yes. Odometer readings are validated during inspection and through service history where available.

Q: Are flood-damaged cars listed?
A: No. We do not list flood-affected or structurally compromised cars.

Q: Do you provide emission certificate?
A: A valid PUC is provided at delivery.

Q: Is test drive insured?
A: Test drives are conducted under dealership coverage as per policy and local regulations.

Q: Data privacy of my documents
A: Customer documents are used only for loan and transfer processing and handled securely.
"""


def _tokenize(text: str) -> Set[str]:
    words = re.findall(r"\w+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def _build_entries() -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    current_question: str | None = None

    for line in FAQ_RAW.splitlines():
        stripped = line.strip()
        if stripped.startswith("Q:"):
            current_question = stripped[2:].strip()
        elif stripped.startswith("A:") and current_question:
            answer = stripped[2:].strip()
            keywords = _tokenize(current_question)
            if keywords:
                entries.append(
                    {
                        "question": current_question,
                        "answer": answer,
                        "keywords": keywords,
                    }
                )
            current_question = None
    return entries


FAQ_ENTRIES: List[Dict[str, str]] = _build_entries()


def search_faq(query: str, max_results: int = 5) -> str:
    """
    Return FAQ answers relevant to the query.
    """
    if not query:
        top_entries = FAQ_ENTRIES[:max_results]
        return "\n\n".join(
            f"Q: {entry['question']}\nA: {entry['answer']}"
            for entry in top_entries
        )

    query_words = _tokenize(query)
    scores: List[Tuple[int, Dict[str, str]]] = []

    for entry in FAQ_ENTRIES:
        score = len(entry["keywords"] & query_words)
        if score > 0:
            scores.append((score, entry))

    if not scores:
        scores = [(len(entry["keywords"] & query_words), entry) for entry in FAQ_ENTRIES[:max_results]]

    scores.sort(key=lambda x: x[0], reverse=True)
    top = [entry for _, entry in scores[:max_results]]

    return "\n\n".join(
        f"Q: {entry['question']}\nA: {entry['answer']}"
        for entry in top
    ) or "No FAQ entries found."


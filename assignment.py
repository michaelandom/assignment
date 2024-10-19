
def calculate_energy_usage():
    pass
def calculate_waste():
    pass

def calculate_business_travel():
    pass    
question_users = {
    "ENERGY_USAGE": {
        "ENERGY_USAGE_QUESTION_1": "What is your average monthly electricity bill in euros?",
        "ENERGY_USAGE_QUESTION_2": "What is your average monthly natural gas bill in euros?",
        "ENERGY_USAGE_QUESTION_3": "What is your average monthly fuel bill for transportation in euros?",
        # "ENERGY_USAGE_FORMULA": "((monthly_electricity_bill * 12) * (0.0005))+ ((monthly_natural_gas_bill * 12) * (0.0053)) + ((monthly_fuel_bill * 12) * (2.32))",
        "ENERGY_USAGE_FORMULA": "((ENERGY_USAGE_QUESTION_1 * 12) * (0.0005))+ ((ENERGY_USAGE_QUESTION_2 * 12) * (0.0053)) + ((ENERGY_USAGE_QUESTION_3 * 12) * (2.32))",
        # "ENERGY_USAGE_RESULT": calculate_energy_usage
        },
        "WASTE": {
        "WASTE_QUESTION_1": "How much waste do you generate per month in kilograms?",
        "WASTE_QUESTION_2": "How much of that waste is recycled or composted (in percentage)?",
        # "WASTE_FORMULA": "((total_waste_generated_per_month) * (12)) * (0.57 - recycling_or_composting_percentage)",
        "WASTE_FORMULA": "((WASTE_QUESTION_1) * (12)) * ((57 - WASTE_QUESTION_2)/100)",
        # "WASTE_RESULT": calculate_waste
        },
    "BUSINESS_TRAVEL": {
        "BUSINESS_TRAVEL_QUESTION_1": "How many kilometers do your employees travel per year for business purposes?",
        "BUSINESS_TRAVEL_QUESTION_2": "What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?",
        "BUSINESS_TRAVEL_FORMULA": "(BUSINESS_TRAVEL_QUESTION_1) * (1 / BUSINESS_TRAVEL_QUESTION_2) * (2.31)",
        # "BUSINESS_TRAVEL_FORMULA": "(total_kilometers_traveled_per_year_for_business_purposes) * (1 / average_fuel_efficiency_in_L_per_100km) * (2.31)",
        # "WASTE_RESULT": calculate_business_travel
        },
}; 

def main():
    pass



if __name__== "__main__":
    main()


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
}; 





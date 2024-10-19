
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
}; 





HEADER_COLOR = "\033[95m"  
DATA_COLOR = "\033[92m"
ERROR_COLOR = "\033[91m"     
RESET_COLOR = "\033[0m" 
question_users = {
    "ENERGY_USAGE": {
        "ENERGY_USAGE_QUESTION_1": "What is your average monthly electricity bill in euros?",
        "ENERGY_USAGE_QUESTION_2": "What is your average monthly natural gas bill in euros?",
        "ENERGY_USAGE_QUESTION_3": "What is your average monthly fuel bill for transportation in euros?",
        "ENERGY_USAGE_FORMULA": "((ENERGY_USAGE_QUESTION_1 * 12) * (0.0005))+ ((ENERGY_USAGE_QUESTION_2 * 12) * (0.0053)) + ((ENERGY_USAGE_QUESTION_3 * 12) * (2.32))",
        },
    "WASTE": {
        "WASTE_QUESTION_1": "How much waste do you generate per month in kilograms?",
        "WASTE_QUESTION_2": "How much of that waste is recycled or composted (in percentage)?",
        "WASTE_FORMULA": "((WASTE_QUESTION_1) * (12)) * ((57 - WASTE_QUESTION_2)/100)",
        },
    "BUSINESS_TRAVEL": {
        "BUSINESS_TRAVEL_QUESTION_1": "How many kilometers do your employees travel per year for business purposes?",
        "BUSINESS_TRAVEL_QUESTION_2": "What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?",
        "BUSINESS_TRAVEL_FORMULA": "(BUSINESS_TRAVEL_QUESTION_1) * (1 / BUSINESS_TRAVEL_QUESTION_2) * (2.31)",
        "BUSINESS_TRAVEL_QUESTION_2_VALIDATION": "BUSINESS_TRAVEL_QUESTION_2 != 0"
        },
}; 
def getQuestion(dictionary,search_key):
   new_dictionary= {}
   for key, value in dictionary.items():
        if search_key.upper() in key.upper() and not key.endswith("_VALIDATION"):
            new_dictionary[key] = value
   return new_dictionary 
    
def section_not_completed(dictionary):
    question_count =0
    formula_count = 0
    for key, _ in dictionary.items():
        if  key.endswith("_FORMULA"):
            formula_count+=1
        elif "_QUESTION_" in key.upper():
            question_count+=1
    
    return not(formula_count==1 and question_count>0)

def printTable(section_answers):
    print(f"{HEADER_COLOR}{'Category':<20} {'CO2 (kg)':<15} {'Time Frame':<15} {RESET_COLOR}")
    print("-" * 50)
    for key, value in section_answers.items():
        print(f"{DATA_COLOR}{key:<20} {value:<15} {'in year':<15}{RESET_COLOR}")
    print("-" * 50)
    print("\n\n")

def ask():
    section_answers = {}
    total = 0
    for section in question_users:
        if section_not_completed(question_users[section]):
            print(f'{section} section is not completed \n')
            continue
        print(f'{section} section \n')
        formula= question_users[section][f"{section}_FORMULA"]
        section_questions= getQuestion(question_users[section],"_QUESTION_")
        print(f'{section} section has {len(section_questions)} questions \n')
        for key, value in section_questions.items():
            while True:
                try:
                    response =int(input(f"{value} {HEADER_COLOR}"))
                    validation_key = (key + "_VALIDATION")
                    if validation_key in question_users[section]  and not eval((question_users[section][validation_key].replace(key, f"{response}"))):
                       print(f"{ERROR_COLOR}{response} is not a valid input {question_users[section][validation_key]} {RESET_COLOR}\n")
                       raise Exception(f"{value}")
                    formula = formula.replace(key, f"{response}")
                    print(f"{RESET_COLOR}\n")
                    break
                except ValueError:
                    print(f"{ERROR_COLOR}That's not a valid response. Please enter a number.{RESET_COLOR}\n")
                except:
                    pass
                    # print(f"{ERROR_COLOR}Average fuel efficiency in L / 100km cant not be zero.{RESET_COLOR}\n")

        try:
            result = round(eval(formula), 2)
            section_answers[section] = result
            total+=result;
            print(f"The result of the {section} is: {DATA_COLOR}{result} kgCO2 {RESET_COLOR}")
        except Exception as e:
            print(f"Error in evaluating the formula for {section}:", e)  
        print("\n\n")
    section_answers["TOTAL"] = round(total,2)
    printTable(section_answers)
    





if __name__== "__main__":
    ask()

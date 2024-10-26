import matplotlib.pyplot as pyplot
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
        "ENERGY_USAGE_RECOMMENDATIONS": """
Recommendations for Energy Usage Reducing CO2 Emissions:<br/>
1. Upgrade Efficiency: Improve insulation, use ENERGY STAR appliances, switch to LED lighting.<br/>
2. Smart Technology: Install smart thermostats, utilize energy monitoring systems.<br/>
3. Behavioral Changes: Unplug devices when not in use, turn off lights and appliances.<br/>
4. Renewable Energy: Install solar panels, explore small wind turbines.<br/>
5. Optimize Heating/Cooling: Maintain HVAC systems, implement zoning.<br/>
6. Water Heating: Insulate water heaters, set temperature to 120°F (49°C).<br/>
 """
        },
    "WASTE": {
        "WASTE_QUESTION_1": "How much waste do you generate per month in kilograms?",
        "WASTE_QUESTION_2": "How much of that waste is recycled or composted (in percentage)?",
        "WASTE_FORMULA": "((WASTE_QUESTION_1) * (12)) * ((57 - WASTE_QUESTION_2)/100)",
        "WASTE_RECOMMENDATIONS": """
Recommendations for Waste Reducing CO2 Emissions:<br/>
Reduce: Minimize single-use items (e.g., plastic bags, straws). Opt for durable products over disposable ones.<br/>
Reuse: Repurpose containers and materials instead of discarding them. Donate items you no longer need rather than throwing them away.<br/>
Recycle: Familiarize yourself with local recycling programs and guidelines. Ensure materials are clean and sorted properly before recycling.<br/>
Compost: Start a compost bin for organic waste (e.g., food scraps, yard waste). Use compost to enrich soil and reduce landfill waste.<br/>
Educate: Raise awareness about waste reduction in your community. Share tips and resources on sustainable practices.<br/>
Purchase Wisely: Buy in bulk to reduce packaging waste. Choose products with minimal or recyclable packaging.<br/>
Plan Meals: Create a meal plan to avoid food waste. Store food properly to extend its shelf life.<br/>
"""
        },
    "BUSINESS_TRAVEL": {
        "BUSINESS_TRAVEL_QUESTION_1": "How many kilometers do your employees travel per year for business purposes?",
        "BUSINESS_TRAVEL_QUESTION_2": "What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?",
        "BUSINESS_TRAVEL_FORMULA": "(BUSINESS_TRAVEL_QUESTION_1) * (1 / BUSINESS_TRAVEL_QUESTION_2) * (2.31)",
        "BUSINESS_TRAVEL_QUESTION_2_VALIDATION": "BUSINESS_TRAVEL_QUESTION_2 != 0",
        "BUSINESS_TRAVEL_RECOMMENDATIONS":"""
Recommendations for Business Travel Reducing CO2 Emissions:<br/>
Travel Less: Utilize video conferencing to reduce travel needs. Combine multiple meetings into one trip.<br/>
Sustainable Transportation: Opt for public transport over taxis. Use trains for shorter distances instead of flying.<br/>
Eco-Friendly Accommodations: Select hotels with sustainability certifications. Support energy-saving practices.<br/>
Reduce Single-Use Items: Bring reusable water bottles and utensils. Avoid plastic straws and bags.<br/>
Plan Efficiently: Schedule meetings close together to minimize travel time. Use direct flights to reduce fuel consumption.<br/>
Offset Carbon Footprint: Invest in carbon offset programs. Encourage the company to support sustainability initiatives.<br/>
Educate Employees: Provide training on sustainable travel practices. Share resources for eco-friendly travel options.<br/>
"""
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
    recommendation_count = 0
    for key, _ in dictionary.items():
        if  key.endswith("_FORMULA"):
            formula_count+=1
        elif "_QUESTION_" in key.upper():
            question_count+=1
        elif key.endswith("_RECOMMENDATIONS"):
            recommendation_count+=1
    
    return not(formula_count==1 and recommendation_count==1 and question_count>0)

def printTable(section_answers):
    print(f"{HEADER_COLOR}{'Category':<20} {'CO2 (kg)':<15} {'Time Frame':<15} {RESET_COLOR}")
    print("-" * 50)
    for key, value in section_answers.items():
        print(f"{DATA_COLOR}{key:<20} {value:<15} {'in year':<15}{RESET_COLOR}")
    print("-" * 50)
    print("\n\n")

def createPie(section_answers):
    categories = [key for key in section_answers.keys() if key != "TOTAL"] 
    co2_emissions = [value for key, value in section_answers.items() if key != "TOTAL"]
    time_frame = ['1 year'] * len(categories)
    max_key, _ = max(
    ((key, value) for key, value in section_answers.items() if key != "TOTAL"),
    key=lambda item: item[1]
    )
    recommendations_text = question_users[max_key][f'{max_key}_RECOMMENDATIONS']

    pyplot.figure(figsize=(10, 10))
    pyplot.pie(co2_emissions, labels=categories, autopct='%1.1f%%', startangle=90)
    pyplot.title('CO2 Emissions by Category (in kg) - Yearly',pad=20)
    pyplot.axis('equal') 
    table_data = list(zip(categories, co2_emissions,time_frame))
    column_labels = ['Category', 'CO2 Emissions (kg)', 'Time Frame']
    table = pyplot.table(cellText=table_data, colLabels=column_labels, loc='bottom', cellLoc='center', bbox=[0.1, -0.4, 0.8, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)
    pyplot.text(-25,3.5,recommendations_text)
    pyplot.subplots_adjust(bottom=0.35)
    pdf_filename = "co2_emissions_pie_chart.pdf"
    pyplot.savefig(pdf_filename, format='pdf')
    pyplot.close() 
    print(f"PDF '{pdf_filename}' created successfully.")

    pdf_filename = "recommendations.pdf"
    document = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    content = []
    title = Paragraph(f"Recommendations", style_heading)
    content.append(title)
    content.append(Spacer(1, 12))
    recommendations_paragraph = Paragraph(recommendations_text, style_normal)
    content.append(recommendations_paragraph)
    content.append(Spacer(1, 12))
    document.build(content)
    print(f"PDF '{pdf_filename}' created successfully.")

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
    createPie(section_answers)
    





if __name__== "__main__":
    ask()

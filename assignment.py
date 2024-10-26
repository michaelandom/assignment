import matplotlib.pyplot as pyplot
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json
import os
from datetime import datetime

HEADER_COLOR = "\033[95m"  
DATA_COLOR = "\033[92m"
ERROR_COLOR = "\033[91m"     
RESET_COLOR = "\033[0m" 
question_users = {}
organization_name = ""
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

def createFolder(file_name):
    parent_folder = organization_name.lower().replace(' ', '_')
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = f"{parent_folder}/output_{current_datetime}"
    os.makedirs(folder_path, exist_ok=True)
    pdf_filename = os.path.join(folder_path, file_name)
    return pdf_filename
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
    
    pdf_filename = createFolder('co2_emissions_pie_chart.pdf')
    pyplot.savefig(pdf_filename, format='pdf')
    pyplot.close() 
    print(f"PDF '{pdf_filename}' created successfully.")
    pdf_filename = createFolder('recommendations.pdf')
    pyplot.savefig(pdf_filename, format='pdf')
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
    

def setUp():
    global question_users, organization_name
    json_file_path = "question.json"
    with open(json_file_path, 'r') as file:
        data_dict = json.load(file)
    question_users = data_dict
    organization_name = input('Enter your organization name : ')
    print("\n\n")




if __name__== "__main__":
    setUp()
    ask()

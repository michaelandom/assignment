import matplotlib.pyplot as pyplot
import json
import os
from datetime import datetime
from pdf_creater import PDF
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

HEADER_COLOR = "\033[95m"  
DATA_COLOR = "\033[92m"
ERROR_COLOR = "\033[91m"     
RESET_COLOR = "\033[0m"
date_string = None
answer_dict = []
question_users = {}
organization_name = ""
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
    folder_path = f"{parent_folder}/output_{current_datetime}"
    os.makedirs(folder_path, exist_ok=True)
    pdf_filename = os.path.join(folder_path, file_name)
    return pdf_filename
def createPie(section_answers):
    categories = [key for key in section_answers.keys() if key != "TOTAL"] 
    co2_emissions = [value for key, value in section_answers.items() if key != "TOTAL"]
    pyplot.figure(figsize=(10, 10))
    createChart(categories, co2_emissions)
    pdf_filename = createFolder('co2_emissions_pie_chart.png')
    pyplot.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    pyplot.close()
    df = pd.DataFrame(answer_dict)
    latest_data = df.sort_values('date').groupby('organization_id').last().reset_index()
    ranked_data = latest_data.sort_values('TOTAL', ascending=False)
    
   
    plt.figure(1)
    createHistoryGraph(categories, df)

    # Show plot
    pdf_filename = createFolder('emissions_history.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    # other 
    plt.figure(1)
    create_emissions_chart(df)
    pdf_filename = createFolder('emissions_plot.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    pdf = PDF()
    pdf.add_page()
    # Add date
    pdf_filename = createFolder('co2_emissions_pie_chart.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    pdf_filename = createFolder('emissions_history.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.ln(5) 
    pdf_filename = createFolder('emissions_plot.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    # Add rankings table
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Company Rankings by Total Emissions', 0, 1)
    pdf.ln(5)


    # Table headers
    pdf.set_font('Arial', 'B', 10)

    # Get dynamic categories (excluding certain columns)
    excluded_columns = ['organization_id', 'date']
    categories = [col for col in ranked_data.columns if col not in excluded_columns]

    # Sort the data by TOTAL emissions in descending order
    ranked_data = ranked_data.sort_values('TOTAL', ascending=False).reset_index(drop=True)

    # Calculate dynamic column widths
    page_width = pdf.w - 20  # Total width minus margins
    rank_width = 15  # Fixed width for rank column
    company_width = 35  # Fixed width for company name
    remaining_width = page_width - (rank_width + company_width)
    category_width = remaining_width / (len(categories) - 1)  # -1 because company name is already accounted for

    # Create dynamic column widths list
    col_widths = [rank_width, company_width] + [category_width] * (len(categories) - 1)

    # Create headers list
    headers = ['Rank', 'Company'] + [col.replace('_', ' ').title() for col in categories if col not in ['organization_name']]

    # Print headers
    pdf.set_font('Arial', 'B', 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), 1)
    pdf.ln()

    # Print data
    pdf.set_font('Arial', '', 10)
    for idx, row in ranked_data.iterrows():
        # Calculate rank (idx + 1 since indexing starts at 0)
        rank = idx + 1
        
        # Print rank
        pdf.cell(col_widths[0], 10, str(rank), 1)
        
        # Print company name
        pdf.cell(col_widths[1], 10, str(row['organization_name']), 1)
        
        # Print all other categories dynamically
        for category in categories:
            if category not in ['organization_name']:
                value = row[category]
                # Format numeric values with 2 decimal places
                formatted_value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                pdf.cell(category_width, 10, formatted_value, 1)
        pdf.ln()

    # Optional: Add a note about sorting
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'Note: Companies are ranked by total emissions in descending order', 0, 1, 'L')
    # Add summary statistics
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Summary Statistics', 0, 1)
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    summary_stats = [
        f"Total Emissions Across All Companies: {ranked_data['TOTAL'].sum():,.2f}",
        f"Average Emissions per Company: {ranked_data['TOTAL'].mean():,.2f}",
        f"Company with Highest Emissions: {ranked_data.iloc[0]['organization_name']} ({ranked_data.iloc[0]['TOTAL']:,.2f})",
        f"Company with Lowest Emissions: {ranked_data.iloc[-1]['organization_name']} ({ranked_data.iloc[-1]['TOTAL']:,.2f})"
    ]
    for stat in summary_stats:
        pdf.cell(0, 10, stat, 0, 1)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    max_key, _ = max(
    ((key, value) for key, value in section_answers.items() if key != "TOTAL"),
    key=lambda item: item[1]
    )
    recommendations_text = question_users[max_key][f'{max_key}_RECOMMENDATIONS']
    pdf.multi_cell(0, 10, recommendations_text)
    pdf.ln(5)
    pdf_filename = createFolder('company_emissions_report.pdf')
    pdf.output(pdf_filename)
    pdf_filename = createFolder('emissions_plot.png')
    os.remove(pdf_filename)
    pdf_filename = createFolder('co2_emissions_pie_chart.png')
    os.remove(pdf_filename)
    pdf_filename = createFolder('emissions_history.png')
    os.remove(pdf_filename)

    print("PDF report has been generated as 'company_emissions_report.pdf'")
    print(f"PDF '{pdf_filename}' created successfully.")

def createHistoryGraph(categories, df):
    df['date'] = pd.to_datetime(df['date'])
    org_id = organization_name.lower().replace(' ', '_')
    org_data = df[df['organization_id'] == org_id]

    # Sort by date
    org_data = org_data.sort_values('date')
    # Plotting
    plt.figure(figsize=(10, 5))
    headers = [col for col in categories if col not in ['organization_id','organization_name','date']]
    for idx, col  in enumerate(headers):
        plt.plot(org_data['date'], org_data[col], marker='o', label=col.replace('_', ' ').title())
    # Adding titles and labels
    plt.title(f'Progress of {organization_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    return plt

# def createChart(categories, co2_emissions):
#     pyplot.pie(co2_emissions, labels=categories, autopct='%1.1f%%', startangle=90)
#     pyplot.title(f'CO2 Emissions by Category (in kg) - Yearly for {organization_name}',pad=20)
#     pyplot.axis('equal') 
#     pyplot.subplots_adjust(bottom=0.35)
#     return pyplot
def createChart(categories, co2_emissions):
    explode = [0.1 if value == max(co2_emissions) else 0 for value in co2_emissions]

    pyplot.figure(figsize=(10, 6))
    wedges, texts, autotexts = pyplot.pie(co2_emissions, 
                                           labels=categories, 
                                           autopct='%1.1f%%', 
                                           startangle=90, 
                                           explode=explode, 
                                           textprops={'fontsize': 10, 'color': 'black'})

    for text in texts:
        text.set_size(10)  
    for autotext in autotexts:
        autotext.set_color('white') 
        autotext.set_size(10)  

    pyplot.legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    pyplot.title(f'CO2 Emissions by Category (in kg) - Yearly for {organization_name}', pad=20)
    pyplot.axis('equal') 
    pyplot.subplots_adjust(bottom=0.35)    
    return pyplot

def create_emissions_chart(data, scale_type='dual'):
    """
    Create emissions chart with different scaling options
    scale_type: 'dual', 'log', or 'normalize'
    """
   
    latest_data = data.sort_values('date').groupby('organization_id').last().reset_index()
    
    
    ranked_data = latest_data.sort_values('TOTAL', ascending=False)
    
    
    excluded_columns = ['organization_id', 'organization_name', 'TOTAL', 'date']
    categories = [col for col in ranked_data.columns if col not in excluded_columns]
    
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
    
    
    value_ranges = {cat: ranked_data[cat].max() - ranked_data[cat].min() for cat in categories}
    max_values = {cat: ranked_data[cat].max() for cat in categories}
    
    
    large_categories = [k for k, v in max_values.items() if v > np.mean(list(max_values.values()))]
    small_categories = [k for k, v in max_values.items() if v <= np.mean(list(max_values.values()))]
    
    plt.figure(figsize=(12, 6))
    
    if scale_type == 'dual' and large_categories and small_categories:
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        width = 0.8 / len(categories)
        x = np.arange(len(ranked_data['organization_id']))
        
        for idx, category in enumerate(large_categories):
            ax1.bar(x + idx * width, 
                   ranked_data[category], 
                   width, 
                   label=f"{category.replace('_', ' ').title()} (Primary)",
                   color=colors[idx])
        
        for idx, category in enumerate(small_categories):
            ax2.bar(x + (idx + len(large_categories)) * width,
                   ranked_data[category],
                   width,
                   label=f"{category.replace('_', ' ').title()} (Secondary)",
                   color=colors[idx + len(large_categories)])
        
        ax1.set_xlabel('Companies')
        ax1.set_ylabel('Primary Scale Emissions')
        ax2.set_ylabel('Secondary Scale Emissions')
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1, 1))
        
    elif scale_type == 'log':
        width = 0.8 / len(categories)
        x = np.arange(len(ranked_data['organization_id']))
        
        for idx, category in enumerate(categories):
            if all(ranked_data[category] > 0): 
                plt.bar(x + idx * width,
                       ranked_data[category],
                       width,
                       label=category.replace('_', ' ').title(),
                       color=colors[idx])
        
        plt.yscale('log')
        plt.legend(bbox_to_anchor=(1, 1))
        
    else:  
        normalized_data = ranked_data.copy()
        for category in categories:
            max_val = ranked_data[category].max()
            if max_val > 0:  # Avoid division by zero
                normalized_data[category] = (ranked_data[category] / max_val) * 100
        
        width = 0.8 / len(categories)
        x = np.arange(len(normalized_data['organization_id']))
        
        for idx, category in enumerate(categories):
            plt.bar(x + idx * width,
                   normalized_data[category],
                   width,
                   label=category.replace('_', ' ').title(),
                   color=colors[idx])
        
        plt.ylabel('Percentage of Maximum (%)')
        plt.legend(bbox_to_anchor=(1, 1))
    
    plt.title('Company Emissions by Category')
    plt.xticks(x + width * (len(categories) - 1) / 2, ranked_data['organization_id'], rotation=45)
    plt.tight_layout()
    
    return plt

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
    saveAnswers(section_answers)
    createPie(section_answers)
    

def saveAnswers(section_answers):
    global organization_name , answer_dict , date_string
    organization_id = organization_name.lower().replace(' ', '_')
    answers = {
        "organization_id": organization_id,
        "organization_name": organization_name,
        "date": date_string,
        **section_answers
    }
    json_file_path = "answer.json"  
    try:
        with open(json_file_path, 'r') as file:
            answer_dict = json.load(file)
    except FileNotFoundError:
        answer_dict = []
    answer_dict = [entry for entry in answer_dict if not (entry.get("date") == date_string and entry.get("organization_id") == organization_id)]
    answer_dict.append(answers)
    with open(json_file_path, 'w') as file:
        json.dump(answer_dict, file, indent=4)


def setUp():
    try:
        global question_users, organization_name
        json_file_path = "question.json"
        with open(json_file_path, 'r') as file:
            data_dict = json.load(file)
        question_users = data_dict
        organization_name = input('Enter your organization name : ')
        print("\n\n")
        create_date()
    except:
        print (f"{ERROR_COLOR}System issue\n{RESET_COLOR}")
        pass
def create_date():
    global date_string
    
    while True:
        year = input('Enter the year of the data (YYYY, e.g., 2024): ')
        if len(year) == 4 and year.isdigit():
            year = int(year)
            break  
        else:
            print(f"{ERROR_COLOR}Invalid input: Year must be a four-digit number (YYYY). Please try again. {RESET_COLOR}")

    
    while True:
        month = input('Enter the month of the year (1-12): ')
        try:
            month = int(month)
            if 1 <= month <= 12:
                break  
            else:
                print(f"{ERROR_COLOR}Invalid input: Month must be between 1 and 12. Please try again.{RESET_COLOR}")
        except ValueError:
            print(f"{ERROR_COLOR}Invalid input: Month must be an integer. Please try again.{RESET_COLOR}")
    date_string = f"{year}-{month:02d}-01"





if __name__== "__main__":
    setUp()
    ask()

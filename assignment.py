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
DATE_STRING = None
answer_dict = []
question_users = {}
ORGANIZATION_NAME = ""
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_question(dictionary, search_key):
    """
    This function takes an input dictionary and a search key, 
    then retrieves and returns a list of questions from the dictionary 
    that match the specified criteria.
    """
    new_dictionary = {}
    for key, value in dictionary.items():
        if search_key.upper() in key.upper() and not key.endswith("_VALIDATION"):
            new_dictionary[key] = value
    return new_dictionary


def section_not_completed(dictionary):
    """
    This function takes an input dictionary and checks if the section 
    is completed and available for the user.
    """
    question_count = 0
    formula_count = 0
    recommendation_count = 0
    for key, _ in dictionary.items():
        if key.endswith("_FORMULA"):
            formula_count += 1
        elif "_QUESTION_" in key.upper():
            question_count += 1
        elif key.endswith("_RECOMMENDATIONS"):
            recommendation_count += 1

    return not (formula_count == 1 and recommendation_count == 1 and question_count > 0)


def print_table(section_answers):
    """
    This function takes user input and creates a formatted table 
    in the terminal with colored output.
    """
    print(f"{HEADER_COLOR}{'Category':<20} {
          'CO2 (kg)':<15} {'Time Frame':<15} {RESET_COLOR}")
    print("-" * 50)
    for key, value in section_answers.items():
        print(f"{DATA_COLOR}{key:<20} {value:<15} {
              'in year':<15}{RESET_COLOR}")
    print("-" * 50)
    print("\n\n")


def create_folder(file_name):
    """
    This function takes an input file name and creates a path in the 
    parent folder under ORGANIZATION_NAME, along with an output directory 
    that includes a timestamp.
    """
    parent_folder = ORGANIZATION_NAME.lower().replace(' ', '_')
    folder_path = f"{parent_folder}/output_{current_datetime}"
    os.makedirs(folder_path, exist_ok=True)
    pdf_filename = os.path.join(folder_path, file_name)
    return pdf_filename


def create_pdf(section_answers):
    """
    This function takes user answers and creates a PDF that includes a 
    chart, a table, a summary, and recommendations. It also cleans up 
    unwanted files, such as chart images.
    """
    categories = [key for key in section_answers.keys() if key != "TOTAL"]
    co2_emissions = [value for key,
                     value in section_answers.items() if key != "TOTAL"]
    plt.figure(1)
    create_chart(categories, co2_emissions)
    df = pd.DataFrame(answer_dict)
    latest_data = df.sort_values('date').groupby(
        'organization_id').last().reset_index()
    ranked_data = latest_data.sort_values('TOTAL', ascending=False)
    plt.figure(1)
    create_history_graph(categories, df)
    plt.figure(1)
    chart_type = get_chart_type()
    print(f"{HEADER_COLOR} Creating Report ... {RESET_COLOR}")
    plt.figure(1)
    create_emissions_chart(df, chart_type)
    pdf = add_chart_image_to_pdf_file()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Company Rankings by Total Emissions', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    excluded_columns = ['organization_id', 'date']
    categories_for_rank_table = [
        col for col in ranked_data.columns if col not in excluded_columns]
    ranked_data = ranked_data.sort_values(
        'TOTAL', ascending=False).reset_index(drop=True)
    rank_table(categories_for_rank_table, ranked_data, pdf)
    summery_statistics(ranked_data, pdf)
    recommendations(section_answers, pdf)
    pdf_filename = create_folder('company_emissions_report.pdf')
    pdf.output(pdf_filename)
    clean_up()
    print("PDF report has been generated as 'company_emissions_report.pdf'")
    print(f"PDF '{pdf_filename}' created successfully.")


def add_chart_image_to_pdf_file():
    """
    This function create a pdf and add the chart image to and return the pdf instabs
    """
    pdf = PDF()
    pdf.add_page()
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    pdf_filename = create_folder('emissions_history.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Report Generated: {
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
    pdf.ln(5)
    pdf_filename = create_folder('emissions_plot.png')
    pdf.image(pdf_filename, x=10, w=190)
    pdf.ln(10)
    return pdf


def get_chart_type():
    """
    this function ask user what time of cahrt do othe whant for better data vecleit 
    """
    options = ['dual', 'log', 'normalize']
    print("\nAvailable chart types:")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")

    while True:
        try:
            choice = input("\nSelect chart type (enter number): ").strip()

            if not choice:
                print(f"\n{DATA_COLOR}Using default chart type 'dual'{
                      RESET_COLOR}")
                return options[0]

            index = int(choice) - 1

            if 0 <= index < len(options):
                print(f"\n{DATA_COLOR}Using chart type {
                      options[index]}{RESET_COLOR}")
                return options[index]
            else:
                print(f"{ERROR_COLOR}Please enter a number between 1 and {
                      len(options)}{RESET_COLOR}")

        except ValueError:
            print(f"{ERROR_COLOR}Please enter a valid number{RESET_COLOR}")
        except KeyboardInterrupt:
            print(f"\n{ERROR_COLOR}Operation cancelled. Using default chart type 'dual'{
                  RESET_COLOR}")
            return options[0]


def clean_up():
    """
    this function clean up the chat image file becouse we alredy add it to pdf file
    """
    pdf_filename = create_folder('emissions_plot.png')
    os.remove(pdf_filename)
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    os.remove(pdf_filename)
    pdf_filename = create_folder('emissions_history.png')
    os.remove(pdf_filename)


def recommendations(section_answers, pdf):
    """
    this function take a input section_answers, pdf it will give recommendations base on thw user ansuwer  
    """
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    max_key, _ = max(
        ((key, value)
         for key, value in section_answers.items() if key != "TOTAL"),
        key=lambda item: item[1]
    )
    recommendations_text = question_users[max_key][f'{
        max_key}_RECOMMENDATIONS']
    pdf.multi_cell(0, 10, recommendations_text)
    pdf.ln(5)
    return pdf


def summery_statistics(ranked_data, pdf):
    """
    this function take  ranked_data, pdf and create as summer of the all orgnazation set and comber to the current orgnazation
    """
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Summary Statistics', 0, 1)
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    summary_stats = [
        f"Total Emissions Across All Companies: {
            ranked_data['TOTAL'].sum():,.2f}",
        f"Average Emissions per Company: {ranked_data['TOTAL'].mean():,.2f}",
        f"Company with Highest Emissions: {ranked_data.iloc[0]['ORGANIZATION_NAME']} ({
            ranked_data.iloc[0]['TOTAL']:,.2f})",
        f"Company with Lowest Emissions: {
            ranked_data.iloc[-1]['ORGANIZATION_NAME']} ({ranked_data.iloc[-1]['TOTAL']:,.2f})"
    ]
    for stat in summary_stats:
        pdf.cell(0, 10, stat, 0, 1)
    return pdf


def rank_table(categories, ranked_data, pdf):
    """
    This function takes input categories and ranked data to create a PDF table 
    showing the organization's rank with total emissions in descending order.
    """
    page_width = pdf.w - 20  # Total width minus margins
    rank_width = 15  # Fixed width for rank column
    company_width = 35  # Fixed width for company name
    remaining_width = page_width - (rank_width + company_width)
    # -1 because company name is already accounted for
    category_width = remaining_width / (len(categories) - 1)

    # Create dynamic column widths list
    col_widths = [rank_width, company_width] + \
        [category_width] * (len(categories) - 1)

    # Create headers list
    headers = ['Rank', 'Company'] + [col.replace('_', ' ').title()
                                     for col in categories if col not in ['ORGANIZATION_NAME']]

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
        pdf.cell(col_widths[1], 10, str(row['ORGANIZATION_NAME']), 1)

        # Print all other categories dynamically
        for category in categories:
            if category not in ['ORGANIZATION_NAME']:
                value = row[category]
                # Format numeric values with 2 decimal places
                formatted_value = f"{value:,.2f}" if isinstance(
                    value, (int, float)) else str(value)
                pdf.cell(category_width, 10, formatted_value, 1)
        pdf.ln()

    # Optional: Add a note about sorting
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(
        0, 10, 'Note: Companies are ranked by total emissions in descending order', 0, 1, 'L')
    return pdf


def create_history_graph(categories, df):
    """
    This function takes input categories and organization history to create 
    a chart displaying progress over the years.
    """
    df['date'] = pd.to_datetime(df['date'])
    org_id = ORGANIZATION_NAME.lower().replace(' ', '_')
    org_data = df[df['organization_id'] == org_id]
    org_data = org_data.sort_values('date')
    plt.figure(figsize=(10, 5))
    headers = [col for col in categories if col not in [
        'organization_id', 'organization_name', 'date']]
    for _, col in enumerate(headers):
        plt.plot(org_data['date'], org_data[col], marker='o',
                 label=col.replace('_', ' ').title())
    plt.title(f'Progress of {ORGANIZATION_NAME} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    pdf_filename = create_folder('emissions_history.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    return plt


def create_chart(categories, co2_emissions):
    """
    This function takes input categories and CO2 emissions, 
    and creates a chart that compares the different categories 
    for the organization.
    """
    # plt.figure(figsize=(10, 10))
    explode = [0.1 if value == max(
        co2_emissions) else 0 for value in co2_emissions]

    plt.figure(figsize=(10, 6))
    wedges, texts, auto_texts = plt.pie(co2_emissions,
                                        labels=categories,
                                        autopct='%1.1f%%',
                                        startangle=90,
                                        explode=explode,
                                        textprops={'fontsize': 10, 'color': 'black'})

    for text in texts:
        text.set_size(10)
    for auto_text in auto_texts:
        auto_text.set_color('white')
        auto_text.set_size(10)

    plt.legend(wedges, categories, title="Categories",
               loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.title(
        f'CO2 Emissions by Category (in kg) - Yearly for {ORGANIZATION_NAME}', pad=20)
    plt.axis('equal')
    plt.subplots_adjust(bottom=0.35)
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    return plt


def create_emissions_chart(data, scale_type='dual'):
    """
    Create emissions chart with different scaling options
    scale_type: 'dual', 'log', or 'normalize'
    """

    latest_data = data.sort_values('date').groupby(
        'organization_id').last().reset_index()

    ranked_data = latest_data.sort_values('TOTAL', ascending=False)

    excluded_columns = ['organization_id',
                        'ORGANIZATION_NAME', 'TOTAL', 'date']
    categories = [
        col for col in ranked_data.columns if col not in excluded_columns]

    colors = np.linspace(0, 1, len(categories))

    # value_ranges = {cat: ranked_data[cat].max(
    # ) - ranked_data[cat].min() for cat in categories}

    max_values = {cat: ranked_data[cat].max() for cat in categories}

    large_categories = [k for k, v in max_values.items(
    ) if v > np.mean(list(max_values.values()))]
    small_categories = [k for k, v in max_values.items(
    ) if v <= np.mean(list(max_values.values()))]

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
                normalized_data[category] = (
                    ranked_data[category] / max_val) * 100

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
    plt.xticks(x + width * (len(categories) - 1) / 2,
               ranked_data['organization_id'], rotation=45)
    plt.tight_layout()
    pdf_filename = create_folder('emissions_plot.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    return plt


def ask():
    """
    This function handle the folw of the program check section and asking quatioin creating chat and pdf
    """
    section_answers = {}
    total = 0
    for section in question_users:
        if section_not_completed(question_users[section]):
            print(f'{section} section is not completed \n')
            continue
        print(f'{section} section \n')
        formula = question_users[section][f"{section}_FORMULA"]
        section_questions = get_question(question_users[section], "_QUESTION_")
        print(f'{section} section has {len(section_questions)} questions \n')
        for key, value in section_questions.items():
            while True:
                try:
                    response = int(input(f"{value} {HEADER_COLOR}"))
                    validation_key = (key + "_VALIDATION")
                    if validation_key in question_users[section] and not eval((question_users[section][validation_key].replace(key, f"{response}"))):
                        print(f"{ERROR_COLOR}{response} is not a valid input {
                              question_users[section][validation_key]} {RESET_COLOR}\n")
                        raise ValueError(f"{value}")
                    formula = formula.replace(key, f"{response}")
                    print(f"{RESET_COLOR}\n")
                    break
                except ValueError:
                    print(f"{ERROR_COLOR}That's not a valid response. Please enter a number.{
                          RESET_COLOR}\n")
                    # print(f"{ERROR_COLOR}Average fuel efficiency in L / 100km cant not be zero.{RESET_COLOR}\n")

        try:
            result = round(eval(formula), 2)
            section_answers[section] = result
            total += result
            print(f"The result of the {section} is: {
                  DATA_COLOR}{result} kgCO2 {RESET_COLOR}")
        except:
            print(f"Error in evaluating the formula for {section}:", e)
        print("\n\n")
    section_answers["TOTAL"] = round(total, 2)
    print_table(section_answers)
    save_answers(section_answers)
    create_pdf(section_answers)


def save_answers(section_answers):
    """
    this function take the user answer and save ti in the gernal orhanzation dat set
    """
    global ORGANIZATION_NAME, answer_dict, DATE_STRING
    organization_id = ORGANIZATION_NAME.lower().replace(' ', '_')
    answers = {
        "organization_id": organization_id,
        "ORGANIZATION_NAME": ORGANIZATION_NAME,
        "date": DATE_STRING,
        **section_answers
    }
    json_file_path = "answer.json"
    try:
        with open(json_file_path, 'r') as file:
            answer_dict = json.load(file)
    except FileNotFoundError:
        answer_dict = []
    answer_dict = [entry for entry in answer_dict if not (entry.get(
        "date") == DATE_STRING and entry.get("organization_id") == organization_id)]
    answer_dict.append(answers)
    with open(json_file_path, 'w') as file:
        json.dump(answer_dict, file, indent=4)


def set_up():
    """ 
    Sets up the environment by loading questions from a JSON file and initializing
    global variables for organization and date.
    - Loads the 'question.json' file to initialize the 'question_users' variable.
    - Prompts the user to input the organization name and initializes the 'ORGANIZATION_NAME' variable.
    - Calls the 'create_date()' function to set a date string in the global 'DATE_STRING' variable.
    Raises:
        FileNotFoundError: If 'question.json' is not found.
        JSONDecodeError: If there is an error decoding the JSON data.
        Exception: For any other issues encountered during setup.    
    """
    try:
        global question_users, ORGANIZATION_NAME
        json_file_path = "question.json"
        with open(json_file_path, 'r') as file:
            data_dict = json.load(file)
        question_users = data_dict
        ORGANIZATION_NAME = input('Enter your organization name : ')
        print("\n\n")
        create_date()
    except FileNotFoundError:
        print(f"{ERROR_COLOR}Error: File '{
              json_file_path}' not found. Please ensure the file exists and try again.{RESET_COLOR}")
    except json.JSONDecodeError:
        print(f"{ERROR_COLOR}Error: Failed to parse JSON data from '{
              json_file_path}'. Please check the file format.{RESET_COLOR}")
    except Exception as e:
        print(f"{ERROR_COLOR}System issue: {e}{RESET_COLOR}")


def create_date():
    """
    Prompts the user for a year and month to create a 'YYYY-MM-DD' date string.

    - Validates a 4-digit year and sets the global 'DATE_STRING'.

    Global:
        DATE_STRING (str): e.g., '2024-01-01'.

    Exceptions:
        ValueError: For non-integer year input.
    """
    global DATE_STRING
    while True:
        year = input('Enter the year of the date (YYYY, e.g., 2024): ')
        if len(year) == 4 and year.isdigit():
            year = int(year)
            break
        else:
            print(
                f"{ERROR_COLOR}Invalid input: Year must be a four-digit number (YYYY). Please try again.{RESET_COLOR}")

    DATE_STRING = f"{year}-12-01"


if __name__ == "__main__":
    set_up()
    ask()

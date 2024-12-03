import json
import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pdf_creator import PDF
from secure_json import SecureJSON
from service_utility import ServiceUtility
HEADER_COLOR = "\033[95m"
DATA_COLOR = "\033[92m"
ERROR_COLOR = "\033[91m"
RESET_COLOR = "\033[0m"
DATE_STRING = None
question_users = {}
ORGANIZATION_NAME = ""
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
secure = SecureJSON()


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
    parent_folder = get_organization_id()
    folder_path = f"output/{parent_folder}/output_{current_datetime}"
    os.makedirs(folder_path, exist_ok=True)
    pdf_filename = os.path.join(folder_path, file_name)
    return pdf_filename


@ServiceUtility.timer
def create_pdf(section_answers, answer_dict):
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
    aggregate = {
        'organization_name': 'first',
        'date': 'last',
        'TOTAL': 'sum'
    }
    aggregate.update({category: 'sum' for category in categories})
    latest_data = df.sort_values('date').groupby(
        'organization_id').agg(aggregate).reset_index()
    ranked_data = latest_data.sort_values('TOTAL', ascending=False)
    categories_for_rank_table = [
        col for col in ranked_data.columns if col not in excluded_columns]
    ranked_data = ranked_data.reset_index(drop=True)
    rank_table(categories_for_rank_table, ranked_data, pdf)
    summery_statistics(ranked_data, df, pdf, categories)
    recommendations(section_answers, pdf)
    pdf_filename = create_folder('company_emissions_report.pdf')
    pdf.output(pdf_filename)
    clean_up()
    print("PDF report has been generated as 'company_emissions_report.pdf'")
    print(f"PDF '{pdf_filename}' created successfully.")


def add_chart_image_to_pdf_file():
    """
      Creates a PDF and adds a chart image to it.
    This function generates a PDF file and inserts the specified chart image, returning the PDF file path.
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
      Prompts the user to select a chart type for data visualization.
      This function helps users choose the most suitable chart type to effectively represent their data.
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
    Cleans up the chart image file after it has been added to the PDF.

    This function deletes the chart image file to free up resources, as it is no longer needed.
    """
    pdf_filename = create_folder('emissions_plot.png')
    os.remove(pdf_filename)
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    os.remove(pdf_filename)
    pdf_filename = create_folder('emissions_history.png')
    os.remove(pdf_filename)


def recommendations(section_answers, pdf):
    """
    Generates recommendations based on user responses.

    This function analyzes the provided section answers and the related PDF to offer tailored recommendations.

    Parameters:
    section_answers (list): User responses for different sections.
    pdf (str): Path or URL to a related PDF.
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


@ServiceUtility.memoize
def summery_statistics(ranked_data, df, pdf, categories):
    """
    Provides comprehensive summary statistics for organizations' emissions data.

    Parameters:
    ranked_data (pandas.DataFrame): Ranked emissions data for organizations
    pdf (FPDF object): PDF document to add statistics to

    Returns:
    pdf (FPDF object): Updated PDF with detailed statistics
    """
    # Convert input to DataFrame if not already
    if not isinstance(ranked_data, pd.DataFrame):
        ranked_data = pd.DataFrame(ranked_data)
    # Prepare PDF page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Comprehensive Emissions Summary Statistics', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)

    # Overall Summary Statistics
    overall_stats = [
        f"Total Emissions Across All Companies: {
            ranked_data['TOTAL'].sum():,.2f}",
        f"Average Emissions per Company: {ranked_data['TOTAL'].mean():,.2f}",
        f"Company with Highest Emissions: {ranked_data.iloc[0]['organization_name']} ({
            ranked_data.iloc[0]['TOTAL']:,.2f})",
        f"Company with Lowest Emissions: {
            ranked_data.iloc[-1]['organization_name']} ({ranked_data.iloc[-1]['TOTAL']:,.2f})"
    ]

    # Add overall statistics to PDF
    for stat in overall_stats:
        pdf.cell(0, 10, stat, 0, 1)

    pdf.ln(5)

    # Detailed Breakdown by Emission Category
    for category in categories:
        category_breakdown = [
            f"{ServiceUtility.update_text(category)
               } - Total: {ranked_data[category].sum():,.2f}",
            f"{ServiceUtility.update_text(category)
               } - Average: {ranked_data[category].mean():,.2f}",
            f"{ServiceUtility.update_text(category)} - Highest Contributor: {ranked_data.loc[ranked_data[category].idxmax(
            ), 'organization_name']} ({ranked_data[category].max():,.2f})",
            f"{ServiceUtility.update_text(category)} - Lowest Contributor: {ranked_data.loc[ranked_data[category].idxmin(
            ), 'organization_name']} ({ranked_data[category].min():,.2f})"
        ]

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'{ServiceUtility.update_text(
            category)} Detailed Analysis', 0, 1)
        pdf.set_font('Arial', '', 10)

        for stat in category_breakdown:
            pdf.cell(0, 10, stat, 0, 1)
        pdf.ln(5)
    pdf.add_page()
    current_org_id = get_organization_id()
    current_org_data = df[df['organization_id']
                          == current_org_id]
    # Sort current organization's data by date
    current_org_sorted = current_org_data.sort_values('date')

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Detailed Analysis for Organization: {
             ORGANIZATION_NAME}', 0, 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 10)
    # Skip if insufficient data
    if len(current_org_sorted) < 2:
        pdf.cell(
            0, 10, 'Insufficient historical data for comprehensive analysis', 0, 1)
        return pdf

    # Key Metrics
    total_emissions = current_org_sorted['TOTAL']
    dates = current_org_sorted['date']

    # Breakdown by Emission Categories
    category_breakdown = {}
    category_breakdown.update(
        {category: current_org_sorted[category] for category in categories})

    # Comparative Statistics
    comparative_stats = [
        f"Organization name: {ORGANIZATION_NAME}",
        f"Total Historical Data Points: {len(current_org_sorted)}",
        f"Date Range: {dates.min()} to {dates.max()}",
        f"Lowest Total Emissions: {total_emissions.min(
        ):,.2f} (on {dates.iloc[total_emissions.argmin()]})",
        f"Highest Total Emissions: {total_emissions.max(
        ):,.2f} (on {dates.iloc[total_emissions.argmax()]})"
    ]

    # Percentage Changes
    pct_changes = total_emissions.pct_change() * 100

    # Emission Category Analysis
    category_stats = []
    for category, values in category_breakdown.items():
        category_pct_changes = values.pct_change() * 100
        category_stats.extend([
            f"{category} - Lowest: {values.min():,.2f}",
            f"{category} - Highest: {values.max():,.2f}",
            f"{category} - Average: {values.mean():,.2f}",
            f"{category} - Change Volatility: {category_pct_changes.std():,.2f}%"
        ])

    # Performance Comparison
    overall_mean = ranked_data['TOTAL'].mean()
    org_mean = total_emissions.mean()
    performance_comparison = [
        f"Performance vs Sector Mean: {
            'Above' if org_mean > overall_mean else 'Below'} "
        f"(Difference: {abs(org_mean - overall_mean):,.2f}, "
        f"{abs(org_mean - overall_mean) / overall_mean * 100:,.2f}%)",
        f"Emissions Trend Volatility: {pct_changes.std():,.2f}%"
    ]

    # Additional Trend Analysis
    trend_analysis = [
        f"Most Recent Emissions Change: {pct_changes.iloc[-1]:,.2f}%",
        f"Average Emissions Change: {pct_changes.mean():,.2f}%"
    ]

    # Comparative Context
    percentile_rank = (total_emissions.rank(pct=True).iloc[-1]) * 100
    comparative_context = [
        f"Emissions Percentile Ranking: {percentile_rank:,.2f}%"
    ]

    # PDF Writing
    sections = [
        ("Organizational Overview", comparative_stats),
        ("Category-wise Breakdown", category_stats),
        ("Performance Comparison", performance_comparison),
        ("Trend Analysis", trend_analysis),
        ("Comparative Context", comparative_context)
    ]

    for section_title, section_stats in sections:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, section_title, 0, 1)
        pdf.set_font('Arial', '', 10)

        for stat in section_stats:
            pdf.cell(0, 10, stat, 0, 1)
        pdf.ln(3)
    return pdf


def get_organization_id():
    """ Get organization id from ORGANIZATION_NAME"""
    return ORGANIZATION_NAME.lower().replace(' ', '_')


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
                                     for col in categories if col not in ['organization_name']]

    pdf.set_font('Arial', 'B', 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, str(header), 1)
    pdf.ln()

    pdf.set_font('Arial', '', 10)
    for idx, row in ranked_data.iterrows():
        # Calculate rank (idx + 1 since indexing starts at 0)
        rank = idx + 1

        pdf.cell(col_widths[0], 10, str(rank), 1)

        pdf.cell(col_widths[1], 10, str(row['organization_name']), 1)

        # Print all other categories dynamically
        for category in categories:
            if category not in ['organization_name']:
                value = row[category]
                formatted_value = f"{value:,.2f}" if isinstance(
                    value, (int, float)) else str(value)
                pdf.cell(category_width, 10, formatted_value, 1)
        pdf.ln()
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
    org_id = get_organization_id()
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


def create_pie_chart(categories, co2_emissions, title):
    """
    Create a pie chart for the given categories and CO2 emissions.
    """
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

    plt.title(title, pad=20)
    plt.axis('equal')
    plt.subplots_adjust(bottom=0.35)
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    return plt


def create_bar_chart(categories, co2_emissions, title):
    """
    Create a bar chart for the given categories and CO2 emissions.
    """
    plt.figure(figsize=(10, 6))
    plt.bar(categories, co2_emissions, color='skyblue')
    plt.title(title, pad=20)
    plt.xlabel('Categories')
    plt.ylabel('CO2 Emissions (kg)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf_filename = create_folder('co2_emissions_pie_chart.png')
    plt.savefig(pdf_filename, dpi=300, bbox_inches='tight')
    plt.close()
    return plt


def create_chart(categories, co2_emissions):
    """
    Create a chart (pie or bar) for the given categories and CO2 emissions.
    """
    title = f'CO2 Emissions by Category (in kg) - Yearly for {
        ORGANIZATION_NAME}'
    if any(value < 0 for value in co2_emissions):
        print("Negative CO2 emissions detected. Creating a bar chart instead.")
        create_bar_chart(categories, co2_emissions, title)
    else:
        create_pie_chart(categories, co2_emissions, title)
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
                        'organization_name', 'TOTAL', 'date']
    categories = [
        col for col in ranked_data.columns if col not in excluded_columns]
    colors = plt.cm.tab20(np.linspace(0, 1, len(categories)))
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


def save_user_response(response_by_section):
    """
      This function takes the user's responses organized by section and saves them to a JSON file. 
    This serves as a backup before processing the responses, ensuring we can retain the original data 
    in case of any future changes to the format. It also assists with auditing and can be useful 
    if additional features or requirements are introduced later.
    """
    organization_id = get_organization_id()
    response = {
        "organization_id": organization_id,
        "organization_name": ORGANIZATION_NAME,
        "date": DATE_STRING,
        **response_by_section
    }
    json_file_path = "response.json"
    responses_dict_list = secure.decrypt(json_file_path)
    responses_dict_list = [entry for entry in responses_dict_list if not (entry.get(
        "date") == DATE_STRING and entry.get("organization_id") == organization_id)]
    responses_dict_list.append(response)
    secure.encrypt(responses_dict_list, json_file_path)


def ask():
    """
     Manages the program flow by checking sections and asking questions.
    This function orchestrates user interactions, generates charts, and creates PDFs based on responses.
    """
    section_answers = {}
    response_by_section = {}
    total = 0
    for section in question_users:
        if ServiceUtility.section_not_completed(question_users[section]):
            print(f'{section} section is not completed \n')
            continue
        print(f'{section} section \n')
        formula = question_users[section][f"{section}_FORMULA"]
        section_questions = ServiceUtility.get_question(
            question_users[section], "_QUESTION_")
        response_by_section[section] = {}
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
                    response_by_section[section][key] = response
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
        except (SyntaxError, NameError, TypeError) as e:
            print(f"Error in evaluating the formula for {section}: {e}")
    print("\n\n")
    section_answers["TOTAL"] = round(total, 2)
    print_table(section_answers)
    save_user_response(response_by_section)
    answer_dict = save_answers(section_answers)
    create_pdf(section_answers, answer_dict)


def save_answers(section_answers) -> list:
    """
    This function takes the user's answers and saves them in the general organization dataset.
    It ensures that user responses are recorded for future reference or analysis within the organization.
    """
    organization_id = get_organization_id()
    answers = {
        "organization_id": organization_id,
        "organization_name": ORGANIZATION_NAME,
        "date": DATE_STRING,
        **section_answers
    }
    json_file_path = "answer.json"
    answer_dict = secure.decrypt(json_file_path)
    answer_dict = [entry for entry in answer_dict if not (entry.get(
        "date") == DATE_STRING and entry.get("organization_id") == organization_id)]
    answer_dict.append(answers)
    secure.encrypt(answer_dict, json_file_path)
    return answer_dict


def set_up() -> dict:
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
    variable = {}
    try:
        json_file_path = "question.json"
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data_dict = json.load(file)
        questions = data_dict
        organization_name = input('Enter your organization name : ')
        print("\n\n")
        date_string = create_date()
        variable["question_users"] = questions
        variable["organization_name"] = organization_name
        variable["date_string"] = date_string
        return variable
    except FileNotFoundError:
        print(f"{ERROR_COLOR}Error: File '{
              json_file_path}' not found. Please ensure the file exists and try again.{RESET_COLOR}")
    except json.JSONDecodeError:
        print(f"{ERROR_COLOR}Error: Failed to parse JSON data from '{
              json_file_path}'. Please check the file format.{RESET_COLOR}")
    except (SyntaxError, NameError, TypeError) as e:
        print(f"{ERROR_COLOR}System issue: {e}{RESET_COLOR}")
    return variable


def create_date() -> str:
    """
    Prompts the user for a year to create a 'YYYY-MM-DD' date string.
    - Validates the year as a 4-digit number between 1800 and current year
    - Sets the date to December 1st of the specified year
    """
    while True:
        try:
            year = input(
                'Enter the year of the date (YYYY, e.g., 2024): ').strip().replace('-', '')
            if len(year) != 4 or not year.isdigit():
                print(
                    f"{ERROR_COLOR}Invalid input: Year must be a four-digit number (YYYY). Please try again.{
                        RESET_COLOR}"
                )
                continue
            year = int(year)
            current_year = datetime.now().year
            if year < 1800 or year > current_year:
                print(
                    f"{ERROR_COLOR}Invalid year: Year must be between 1800 and {
                        current_year}. Please try again.{RESET_COLOR}"
                )
                continue
            return f"{year}-12-01"
        except ValueError:
            print(
                f"{ERROR_COLOR}Invalid input. Please enter a valid four-digit year.{RESET_COLOR}"
            )


if __name__ == "__main__":
    try:
        system_variable = set_up()
        required_keys = ["question_users", "organization_name", "date_string"]
        for key in required_keys:
            if key not in system_variable:
                raise ValueError(f"Missing required variable: {key}")
        question_users = system_variable["question_users"]
        ORGANIZATION_NAME = system_variable["organization_name"]
        DATE_STRING = system_variable["date_string"]
        ask()
    except KeyboardInterrupt:
        print('\nProgram interrupted by user')
        exit(0)
    except EOFError:
        print('\nEOF detected - program ending')
        exit(0)
    except (SyntaxError, NameError, TypeError, ValueError) as e:
        print(f'Error: {e}')
        exit(1)

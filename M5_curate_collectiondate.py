# Description: This script reads a CSV file containing Biosample Collection Date and Genbank Collection Date columns, and
# curates the collection dates


import csv
from datetime import datetime


def format_date(date_str):
    try:
        # Define date formats for parsing and output
        formats = [
            ("%Y-%m", "%Y-%m"),  # 2023-12
            ("%m/%d/%y", "%Y-%m-%d"),  # 8/28/23
            ("%m/%d/%y", "%Y-%m-%d"),  # 11/22/22
            ("%d-%b-%y", "%Y-%m-%d"),  # 23-Mar-23
            ("%Y", "%Y"),  # 2018
            ("%Y-%m", "%Y-%m"),  # 2014-07
            ("%b-%y", "%Y-%m"),  # Dec-17
            ("%d-%b-%y", "%Y-%m-%d"),  # 27-Apr-16
            ("%m/%d/%y", "%Y-%m-%d"),  # 7/8/13
            ("%b-%y", "%Y-%m"),  # Mar-76
            ("%d-%b-%Y", "%Y-%m-%d"),  # 21-Oct-1952
            ("%b-%Y", "%Y-%m"),  # Mar-1945
            ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"),  # 2015-10-11T17:53:03Z
            ("%Y-%m-%dT%HZ", "%Y-%m-%d"),  # YYYY-MM-DDThhZ
            ("%Y-%m-%d", "%Y-%m-%d"),  # 1990-10-30
            ("%Y-%m-%dT%H:%MZ", "%Y-%m-%d")  # 1952-10-21T11:43Z
        ]

        # Try parsing with each format
        for fmt, output_fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime(output_fmt)
            except ValueError:
                pass

        # Return None if no format matches
        return None

    except Exception as e:
        print("Error in format_date:", e)
        return None


def check_collection_dates(biosample_date, genbank_date):
    try:
        # If both dates are available
        if biosample_date and genbank_date:
            if biosample_date == genbank_date:
                return biosample_date
            else:
                return "DateMismatch"
        # If only one date is available
        elif biosample_date or genbank_date:
            return biosample_date or genbank_date
        # If both dates are missing
        else:
            return "null"
    except Exception as e:
        print("Error in check_collection_dates:", e)
        return None


def read_csv(file_path):
    biosample_dates = []
    genbank_dates = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                biosample_dates.append(row['Biosample Collection Date'])
                genbank_dates.append(row['Genbank Collection Date'])
        return biosample_dates, genbank_dates
    except Exception as e:
        print("Error in read_csv:", e)
        return [], []


def extract_year(date_str):
    try:
        # Split the date string by '-' or '/' depending on the format
        if '-' in date_str:
            parts = date_str.split('-')
        elif '/' in date_str:
            parts = date_str.split('/')
        else:
            # If no separator is found, it means it's just a year
            return date_str

        # Get the last element which is the year
        year = parts[0]
        return year
    except Exception as e:
        print("Error in extract_year:", e)
        return None


def main():
    # File paths
    input_file_path = '/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/results_code2_Abril.csv'
    output_file_path = '/Users/rbhattac/Desktop/curated_collection_date2.csv'

    # Read CSV
    biosample_dates, genbank_dates = read_csv(input_file_path)

    # Prepare data for writing to CSV
    results = []
    for biosample_date, genbank_date in zip(biosample_dates, genbank_dates):
        # Format dates
        biosample_date_formatted = format_date(biosample_date)
        genbank_date_formatted = format_date(genbank_date)

        # Check if biosample date is present in genbank date
        if biosample_date_formatted and genbank_date_formatted and biosample_date_formatted in genbank_date_formatted:
            result = genbank_date_formatted
        else:
            result = check_collection_dates(biosample_date_formatted, genbank_date_formatted)

        # Extract year
        year = extract_year(result)

        # Append original and formatted dates along with result to results list
        results.append({
            'Original Biosample Collection Date': biosample_date,
            'Original Genbank Collection Date': genbank_date,
            'Formatted Biosample Collection Date': biosample_date_formatted,
            'Formatted Genbank Collection Date': genbank_date_formatted,
            'Curated Collection Date': result,
            'Curated Collection Year': year
        })

    # Write results to CSV
    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Original Biosample Collection Date', 'Original Genbank Collection Date',
                      'Formatted Biosample Collection Date', 'Formatted Genbank Collection Date',
                      'Curated Collection Date', 'Curated Collection Year']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    main()



import argparse
import csv
import re


# Read CSV file into a list of dictionaries
def read_csv(filename):
    with open(filename, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


# Search for keywords in the data
def search_keywords(data, keywords):
    for keyword in keywords:
        search_text = keyword['include'].strip()

        isOR = ' OR ' in search_text
        includes = search_text.split(' OR ' if isOR else ' AND ')

        pattern = ''
        for k in includes:
            k = k.strip()
            # Check if looking for exact match
            if k.startswith('"') and k.endswith('"'):
                part = r'^' + re.escape(k[1:-1]) + r'$'
            else:
                part = re.escape(k)

            pattern += f'{part}|' if isOR else r'(?=.*' + part + r')'

        # Remove trailing '|' for OR patterns
        if isOR:
            pattern = pattern.rstrip('|')

        # Handle exclusions if present
        if keyword['exclude']:
            exclude = keyword['exclude'].strip()
            excludes = exclude.split(' AND ')
            pattern += ''.join([r'(?!.*' + re.escape(k.strip()) + r')' for k in excludes])

        # Compile the regex pattern
        regex = re.compile(pattern, re.IGNORECASE)

        # Search for the pattern in the data
        # Return Y once there is a match and no need to check others
        if regex.search(data):
            return "Y"

    return "N"


def main():
    # parser = argparse.ArgumentParser(description='Process data based on arguments.')
    # parser.add_argument('--data', type=str, required=True, help='Input text to be checked')
    # parser.add_argument('--keywords', nargs='+', required=True, help='List of paths to keyword CSV files')
    #
    # args = parser.parse_args()

    data= "Tissue"
    #specify the path to the keyword files
    keywords= ["Keywords_LabHost_04JUNE2024.csv", "Keywords_IsolationSource_04JUNE2024.csv"]

    # Read keywords from all specified CSV files
    match_result = []
    for keyword_file in keywords:
        #print(keyword_file)
        keywords = read_csv(keyword_file)
        match = search_keywords(data, keywords)
        match_result.append(match)

    print(match_result)
    return match_result


if __name__ == "__main__":
    main()
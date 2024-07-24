#Description: This script reads a CSV file containing Biosample geographic location and Genbank geographic Location columns, and
# curates the geographic locations for BV-BRC
#By Abril



import csv


def clean_geo_loc(geo_loc):
    if ':' in geo_loc:
        parts = geo_loc.split(':')
        cleaned_parts = [part.strip() for part in parts]
        return ':'.join(cleaned_parts)
    else:
        return geo_loc.strip()


def check_geographic_location(biosample_geo_loc, genbank_geo_loc):
    biosample_geo_loc = clean_geo_loc(biosample_geo_loc)
    genbank_geo_loc = clean_geo_loc(genbank_geo_loc)

    if biosample_geo_loc and genbank_geo_loc:
        score = 2
        match = biosample_geo_loc == genbank_geo_loc
        present_loc = biosample_geo_loc if ':' in biosample_geo_loc else genbank_geo_loc
    elif biosample_geo_loc or genbank_geo_loc:
        score = 1
        match = False
        present_loc = genbank_geo_loc if genbank_geo_loc else biosample_geo_loc
    else:
        score = 0
        match = False
        present_loc = "null"
    return present_loc


def extract_country_and_group_from_location(present_loc, country_groups):
    present_loc_words = present_loc.split(":")[0]  # Extract the first word before colon
    for country in country_groups.keys():
        if present_loc_words.lower() in country.lower():
            return country, country_groups[country]
    return None, None


def check_geographic_location_from_csv(input_csv_filename, output_csv_filename):
    country_groups = load_country_geographic_groups('GeoLocation.csv')

    with open(input_csv_filename, 'r', newline='') as input_csvfile:
        reader = csv.DictReader(input_csvfile)

        # Define the fieldnames for the output CSV file
        fieldnames = ['Original Biosample Location', 'Original Genbank Location', 'Isolation Country', 'Country',
                      'Geographic Group']

        rows = []
        for row in reader:
            biosample_geo_loc = row['Biosample Geographic Location']
            genbank_geo_loc = row['Genbank Geographic Location']
            present_loc = check_geographic_location(biosample_geo_loc, genbank_geo_loc)
            country, group = extract_country_and_group_from_location(present_loc, country_groups)

            # Add the present location, country, and group to the row
            rows.append({
                'Original Biosample Location': biosample_geo_loc,
                'Original Genbank Location': genbank_geo_loc,
                'Isolation Country': present_loc,
                'Country': country,
                'Geographic Group': group
            })

    with open(output_csv_filename, 'w', newline='') as output_csvfile:
        writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_country_geographic_groups(csv_filename):
    country_groups = {}
    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            country = row[0].strip()
            group = row[1].strip()
            country_groups[country] = group
    return country_groups


# Example usage:
check_geographic_location_from_csv('/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/results_code2_Abril.csv', '/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/curated_geographic_location2.csv')
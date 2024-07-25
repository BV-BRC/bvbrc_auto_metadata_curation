#Obtain metadata from genbank and biosample records given an genbank accession number
# the input is the bv-brc genome group in csv format. The accessions are listed with column name "GenBank Accessions"

#developed by @AnnaCapria @RoshniBhattacharya @AbrilZuniga

#import statements
from Bio import Entrez, SeqIO
import csv
import pandas as pd
import xml.etree.ElementTree as ET
from urllib.error import HTTPError

# Provide your email to NCBI Entrez
Entrez.email = "abrilz2296@gmail.com"

# extract the accessions from the genome group csv file
def extract_accessions(file_path):
    df = pd.read_csv(file_path)
    accession_number = df["GenBank Accessions"].tolist()
    return accession_number

# extract the genbank record given an accession number
def fetch_genbank_record(accession_number):
    #Entrez.email = "bvbrcacapria@gmail.com"     #put your email
    try:
        handle = Entrez.efetch(db="nucleotide", id=accession_number, rettype="gb", retmode="text")
        record = SeqIO.read(handle, "genbank")
        handle.close()
        return record
    except Exception as e:
        print(f"Error fetching GenBank record {accession_number} : {e}")
        return None

#extract the host and labhost and isolation_source metadata from a genbank record
def extract_genbank_info(record):
    host_info = ""
    lab_host_info = ""
    isolation_source = ""
    country = ""
    collection_date = ""
    host_health = ''
    for feature in record.features:
        if feature.type == "source":
            qualifiers = feature.qualifiers
            if "host" in qualifiers:
                host_info = ', '.join(qualifiers["host"])
            if "lab_host" in qualifiers:
                lab_host_info = ', '.join(qualifiers["lab_host"])
            if "isolation_source" in qualifiers:
                isolation_source = ', '.join(qualifiers["isolation_source"])
            if "collection_date" in qualifiers:
                collection_date = ', '.join(qualifiers["collection_date"])
            if "host_health" in qualifiers:
                host_health = ', '.join(qualifiers["host_health"])
            if "country" in qualifiers:
                country = ', '.join(qualifiers["country"])
    return host_info, lab_host_info, isolation_source, country, collection_date, host_health
    #return host_info, lab_host_info, isolation_source

#extract the biosample accession number from a genbank record
def get_biosample_accession(genbank_accessions):
    biosample_accessions = []
    try:
        handle = Entrez.elink(dbfrom="nucleotide", db="biosample", id=genbank_accessions)
        record = Entrez.read(handle)
        #print(record)
        handle.close()
        if record[0]['LinkSetDb']:
            links = record[0]['LinkSetDb'][0]['Link']
            biosample_accessions = [link['Id'] for link in links]
    except HTTPError as e:
        print(f"HTTP Error occurred for GenBank accession {genbank_accessions}: {e}")
    except Exception as e:
        print(f"An error occurred for GenBank accession {genbank_accessions}: {e}")
    #print(biosample_accessions)
    return biosample_accessions

#extract the biosample record given a biosample accession number
def get_biosample_record(biosample_accession):
    try:
        handle = Entrez.efetch(db="biosample", id=biosample_accession, retmode="xml")
        xml_data = handle.read()
        handle.close()
        return xml_data
    except HTTPError as e:
        print(f"HTTP Error occurred for BioSample accession {biosample_accession}: {e}")
        return None

#extract the metadata from a biosample record
def extract_biosample_information(xml_data, genbank_accession):
    if xml_data is None:
        return None
    # Parse the XML data
    root = ET.fromstring(xml_data)
    #print(xml_data)

    # Find the relevant sample attributes
    biosample = root.find('BioSample')
    sample_attributes = root.findall(".//Attribute[@harmonized_name]")
    #print(sample_attributes1)

    # Extract information from the  attributes
    extracted_info = {"GenBank Accession": genbank_accession}  # Include GenBank accession number

    #get the biosample id
    bio_accession = biosample.attrib['accession']
    extracted_info = {"Biosample_Accession": bio_accession}  # Include biosample accession number

    #print(accession)


    for attr in sample_attributes:
        harmonized_name = attr.attrib.get('harmonized_name')
        #print(harmonized_name)
        # Only interested in the certain attribute names
        if 'host' in harmonized_name or 'isolation_source' in harmonized_name or 'lab_host' in harmonized_name or 'host_common_name' in harmonized_name or 'host_health_state' in harmonized_name or 'collection_date' in harmonized_name or 'geo_loc_name' in harmonized_name:
            # print(attribute_name)
            attribute_value = attr.text
            # print(attribute_value)
            extracted_info[harmonized_name] = attribute_value

    return extracted_info

#get bisample metadata
def get_biosample_metadata(extracted_info):
    biosample_host_info = ''  # Initialize host_info
    biosample_lab_host_info = ''  # Initialize lab_host_info
    biosample_isolation_source = ''
    biosample_scientific_names = []  # Initialize biosample_scientific_names
    bio_accession = ''  # Initialize biosample accession
    biosample_host_health = ''
    bio_geo_loc = ''
    bio_collection_date = ''

    if extracted_info:
        # Check if attribute is host common name, common name
        if 'host_common_name' in extracted_info:
            biosample_host_info = extracted_info['host_common_name']

        if 'isolation_source' in extracted_info:
            biosample_isolation_source = (extracted_info['isolation_source'])

        # Check if attribute is lab_host
        if 'lab_host' in extracted_info:
            biosample_lab_host_info = extracted_info['lab_host']

        # Check if attribute is host scientific name or scientific_name
        if 'host' in extracted_info:
            biosample_scientific_names.append(extracted_info['host'])
        if 'collection_date' in extracted_info:
            bio_collection_date = (extracted_info['collection_date'])
        if 'geo_loc_name' in extracted_info:
            bio_geo_loc = (extracted_info['geo_loc_name'])
        if 'host_health_state' in extracted_info:
            biosample_host_health = (extracted_info['host_health_state'])

        if 'Biosample_Accession' in extracted_info:
            bio_accession = extracted_info['Biosample_Accession']

    else:
        print(f"No information extracted for BioSample accession")

    return biosample_host_info, biosample_lab_host_info, biosample_scientific_names, biosample_isolation_source, bio_accession, bio_collection_date, bio_geo_loc, biosample_host_health


def main():

        file_path = "/Users/rbhattac/Desktop/Host_biosample_results.csv"  #path to your genome group csv file
        #extract the accession numbers
        accession_numbers = extract_accessions(file_path)
        #accession_numbers=['KT844544']

        #initialize lists to store the metadata
        #genbank_metadata = []
        #all_biosample_info = []
        # open the output file to write
        with open("/Users/rbhattac/Desktop/results_code_1.csv", "w", newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header
            csv_writer.writerow(
                ["Accession", "Genbank Host", "Genbank Lab Host", "Genbank Isolation Source", "Genbank Collection Date",
                 "Genbank Geographic Location", "Genbank Host Health", "Biosample_accession",
                 "Biosample Host Common Name", "Biosample Lab Host",
                 "Biosample Host Scientific Name", "Biosample Isolation Source", "Biosample Collection Date",
                 "Biosample Geographic Location", "Biosample Host Health"])

            for accession in accession_numbers:
                #print(accession)
                print(f"Processing genbank accession {accession}..")
                record = fetch_genbank_record(accession)
                if record.annotations["data_file_division"] == "VRL":
                    if record:
                        accession_id = accession
                        # Extract selected genbank metadata information
                        host_info, lab_host_info, isolation_source, country, collection_date, host_health = extract_genbank_info(record)
                        #genbank_metadata.append([accession_id, host_info, lab_host_info, isolation_source])

                    # Extract BioSample information
                    biosample_accession = get_biosample_accession(accession)

                    biosample_host_info = ''  # Initialize host_info
                    biosample_lab_host_info = ''  # Initialize lab_host_info
                    biosample_isolation_source = ''
                    biosample_scientific_names = []  # Initialize biosample_scientific_names
                    bio_accession ='' # Initialize biosample accession
                    biosample_host_health = ''
                    bio_geo_loc = ''
                    bio_collection_date = ''

                    for bioid in biosample_accession:
                        biosample_xml = get_biosample_record(bioid)

                        if biosample_xml:
                            extracted_info = extract_biosample_information(biosample_xml, accession)
                            #biosample_host_info, biosample_lab_host_info, biosample_scientific_names, biosample_isolation_source, bio_accession, bio_collection_date, bio_geo_loc, biosample_host_health = get_biosample_metadata(extracted_info)
                            # Assign the result to a single variable
                            biosample_metadata = get_biosample_metadata(extracted_info)

                            # Unpack the values to individual variables
                            biosample_host_info = biosample_metadata[0]
                            biosample_lab_host_info = biosample_metadata[1]
                            biosample_scientific_names = biosample_metadata[2]
                            biosample_isolation_source = biosample_metadata[3]
                            bio_accession = biosample_metadata[4]
                            bio_collection_date = biosample_metadata[5]
                            bio_geo_loc = biosample_metadata[6]
                            biosample_host_health = biosample_metadata[7]

                        else:
                            print(f"No record found for BioSample accession {biosample_accession}")
                    # Write data to CSV
                    #csv_writer.writerow([accession, host_info, lab_host_info,isolation_source,bio_accession, biosample_host_info, biosample_lab_host_info,
                                # ", ".join(biosample_scientific_names), biosample_isolation_source])
                    csv_writer.writerow(
                        [accession, host_info, lab_host_info, isolation_source, collection_date, country, host_health,
                         bio_accession, biosample_host_info, biosample_lab_host_info,
                         (", ".join(biosample_scientific_names)), biosample_isolation_source, bio_collection_date,
                         bio_geo_loc, biosample_host_health])





if __name__ == "__main__":
    main()
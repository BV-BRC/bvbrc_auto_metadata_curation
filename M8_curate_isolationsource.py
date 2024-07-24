import pandas as pd
import M2_keyword_match as keyword_match
import M3_host_annotation as Host_Annotation

def check_isolation(genbank_isolation, biosample_isolation):
    try:
        # If both are available
        #check if  isolation fields are blank or has NaN values
        if pd.isnull(genbank_isolation) and pd.isnull(biosample_isolation):
            return "null"

        #if one of the fields is blank or has NaN values and other is not, return the non-blank value
        elif pd.isnull(genbank_isolation):
            return biosample_isolation
        elif pd.isnull(biosample_isolation):
            return genbank_isolation
        #if both fields have values, check if they are the same. if yes return the value, if not return "Isolation_Mismatch"
        elif genbank_isolation and biosample_isolation:
            genbank_isolation_temp = genbank_isolation.replace(" ", "")
            biosample_isolation_temp = biosample_isolation.replace(" ", "")
            if genbank_isolation_temp.lower() == biosample_isolation_temp.lower():
                return genbank_isolation
            #check if the genbank isolation source is a substring of biosample isolation source
            elif genbank_isolation in biosample_isolation:
                return biosample_isolation
            #check if the biosample isolation source is a substring of genbank isolation source
            elif biosample_isolation in genbank_isolation:
                return genbank_isolation
            else:
                return "Isolation_Mismatch"


    except Exception as e:
        print("Error in check_isolation:", e)
        return None

def get_curated_isolation(isolation):
    match_result = []
    # specify the path to the keyword files
    keywords = ["Keywords_LabHost_04JUNE2024.csv",
                "Keywords_IsolationSource_04JUNE2024.csv"]

    for keyword_file in keywords:
        keywords = keyword_match.read_csv(keyword_file)
        match = keyword_match.search_keywords(isolation, keywords)
        match_result.append(match)
    if match_result == ['N', 'Y']:
        return isolation
    if match_result == ['Y', 'N'] or match_result == ['Y', 'Y']:
        return "FLAG: Unclear Isolation Source"
    if match_result == ['N', 'N']:
        responseJSON = Host_Annotation.annotateHostText(isolation)
        if responseJSON['data'] is not None:
            annotation_data = responseJSON['data']
            Score = annotation_data['score']
            if Score > 75:
                return "FLAG: probable host found"
            else:
                return "FlAG: Fail_isoSource"
        else:
            return "FlAG: Fail_isoSource"

def main():
    df = pd.read_csv("/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/results_code_Abril.csv")
    #print(df['Genbank Isolation Source'])
    Curated_isoSource = ""
    Flag= ""
    #write to a csv file
    with open("/Users/rbhattac/Desktop/curated_isolation.csv", "w") as file:
        file.write("Accession, Biosample Isolation Source, Genbank Isolation Source, Curated Isolation Source, FLAG\n")
        for row in df.iterrows():
            Accession = row[1]['Accession']
            biosample_isolation = row[1]['Biosample Isolation Source']
            print(f'Biosample Isolation Source: {biosample_isolation}')
            genbank_isolation = row[1]['Genbank Isolation Source']
            print(f'Genbank Isolation Source: {genbank_isolation}')
            isolation = check_isolation(genbank_isolation, biosample_isolation)
            print(isolation)

            if isolation == "null":
                Curated_isoSource = "null"
                Flag = "null"
            elif isolation == "Isolation_Mismatch":
                Curated_isoSource= ""
                Flag = "FLAG: Isolation Mismatch"
            else:
                print(f"Isolation: {isolation}")
                Curated_isoSource_temp = get_curated_isolation(isolation)
                if "FLAG" in Curated_isoSource_temp:
                    Curated_isoSource = ""
                    Flag = Curated_isoSource_temp
                else:
                    Curated_isoSource = Curated_isoSource_temp
                    Flag=""

            print(f"Curated_isoSource= {Curated_isoSource}")
            file.write(f"{Accession},{biosample_isolation},{genbank_isolation},{Curated_isoSource}, {Flag}\n")

if __name__ == "__main__":
    main()

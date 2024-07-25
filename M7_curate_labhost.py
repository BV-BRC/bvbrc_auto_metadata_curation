#Curate the labhost metadata field

import pandas as pd
import M2_keyword_match as keyword_match
import M3_host_annotation as Host_Annotation

#specify the path to the keyword files
keywords = ["Keywords_LabHost_04JUNE2024.csv", "Keywords_IsolationSource_04JUNE2024.csv"]

def check_labhost(genbank_labhost, biosample_labhost):
    try:
        # If both are available
        #check if  labhost fields are blank or has NaN values
        if pd.isnull(genbank_labhost) and pd.isnull(biosample_labhost):
            return "null"
        #if one of the fields is blank or has NaN values and other is not, return the non-blank value
        elif pd.isnull(genbank_labhost):
            return biosample_labhost
        elif pd.isnull(biosample_labhost):
            return genbank_labhost
        #if both fields have values, check if they are the same. if yes return the value, if not return "LabHost_Mismatch"
        elif genbank_labhost and biosample_labhost:
            genbank_labhost_temp = genbank_labhost.replace(" ", "")
            biosample_labhost_temp = biosample_labhost.replace(" ", "")
            if genbank_labhost_temp.lower() == biosample_labhost_temp.lower():
                return genbank_labhost
            elif genbank_labhost in biosample_labhost:
                return biosample_labhost
            elif biosample_labhost in genbank_labhost:
                return genbank_labhost
            else:
                return "LabHost_Mismatch"

    except Exception as e:
        print("Error in check_labhost:", e)
        return None

def get_curated_labhost(labhost):
    match_result = []
    # specify the path to the keyword files
    keywords = ["Keywords_LabHost_04JUNE2024.csv",
                "Keywords_IsolationSource_04JUNE2024.csv"]

    for keyword_file in keywords:
        keywords = keyword_match.read_csv(keyword_file)
        match = keyword_match.search_keywords(labhost, keywords)
        match_result.append(match)
    if match_result == ['Y', 'N']:
        return labhost
    if match_result == ['N', 'Y'] or match_result == ['Y', 'Y']:
        return "FLAG: Unclear LabHost"
    if match_result == ['N', 'N']:
        responseJSON = Host_Annotation.annotateHostText(labhost)
        if responseJSON['data'] is not None:
            annotation_data = responseJSON['data']
            Score = annotation_data['score']
            if Score > 75:
                return "FLAG: probable host found"
            else:
                return "FlAG: Fail_labhost"
        else:
            return "FLAG: Fail_labhost"

def main():
    df = pd.read_csv("/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/results_code_Abril.csv")
    Curated_labhost = ""
    Flag= ""
    #print(df['Biosample Lab Host'])
    #write in a csv file
    with open("/Users/rbhattac/Desktop/curated_labhost.csv", "w") as file:
        file.write("Accession,Biosample Lab Host,Genbank Lab Host,Curated Lab Host, FLAG\n")

        for row in df.iterrows():
            Accession = row[1]['Accession']
            biosample_labhost = row[1]['Biosample Lab Host']
            #print(f'Biosample Lab Host: {biosample_labhost}')
            genbank_labhost = row[1]['Genbank Lab Host']
            #print(f'Genbank Lab Host: {genbank_labhost}')
            labhost = check_labhost(genbank_labhost, biosample_labhost)
            #print(f"Value: {labhost}")

            if labhost == "null":
                Curated_labhost = "null"
                Flag = "null"
            elif labhost == "LabHost_Mismatch":
                Curated_labhost = ""
                Flag = "FLAG: LabHost Mismatch"
            else:
                #print(f"LabHost: {labhost}")
                Curated_labhost_temp = get_curated_labhost(labhost)
                if "FLAG" in Curated_labhost_temp:
                    Curated_labhost = ""
                    Flag = Curated_labhost_temp
                else:
                    Curated_labhost = Curated_labhost_temp
                    Flag= ""

            print(f"Curated_labhost= {Curated_labhost}")

            file.write(f"{Accession},{biosample_labhost},{genbank_labhost},{Curated_labhost}, {Flag}\n")




if __name__ == "__main__":
    main()

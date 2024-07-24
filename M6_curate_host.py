#curate the host metadata field

import pandas as pd
import requests
import numpy as np


class Settings:
    accessToken: str = "eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJwMmMiOjgxOTIsInAycyI6Im14WXJISk96QlZqSVp3NFEiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiemlwIjoiREVGIn0.SXUJ-5e5lc0YcSbLLSXAOr3MXxKcmkEpQTAGD8jJA-3184Q4lorJpA.Ug3mCshkWc4fYc-fvKJ7JQ.PpPQlPOha-VvZReIHHtKYffguLWjvY1tToB5C5HeMSAGddNkDDKfspZsEX0pGebrpQ71t0rUGV1VG9Mq5_mAG-ePMFowm6vvBBCS7wIahdNl-B0WsARnEml7kBvVEeCkeeoW6NXvcDRZnWa5L3zPlmu-uA4IQezhK-ZpIbvRO1ZDX1ODiRWt72Kof__sWypztcQY3cVvrwTU69NRnkpwiA.QjJHRBxOoJ0ElUuuLC8dVA"
    baseURL: str = "https://dev.ictv.global/HostAnnotation"

    @classmethod
    def get_headers(cls):
        headers = {"Authorization": cls.accessToken}
        return headers


def annotate_host_text(host_text: str):
    payload = {"hostText": host_text}
    response = requests.post(
        f"{Settings.baseURL}/annotateHostText",
        headers=Settings.get_headers(),
        data=payload
    )
    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    response_json = response.json()
    return response_json


def process_row(row):
    genbank_host = row["Genbank Host"]
    biosample_scientific_name = row["Biosample Host Scientific Name"]
    biosample_common_name = row["Biosample Host Common Name"]

    # Determine source of host information
    if pd.notna(genbank_host):
        host_text = genbank_host
        source = "Genbank Host"
    elif pd.notna(biosample_scientific_name):
        host_text = biosample_scientific_name
        source = "Biosample Host Scientific Name"
    elif pd.notna(biosample_common_name):
        host_text = biosample_common_name
        source = "Biosample Host Common Name"
    else:
        host_text = ""
        source = ""

    # Annotate host text if available
    if host_text:
        annotated_host = annotate_host_text(host_text)
        return annotated_host, host_text, source
    else:
        return None, "", ""


def populate_curated_columns(df):
    for index, row in df.iterrows():
        if pd.isna(row["less_than_75_or_no_annotation_found"]):
            if sum([1 for col in ["Genbank Host", "Biosample Host Scientific Name", "Biosample Host Common Name"] if
                    not pd.isna(row[col])]) == 1:
                df.at[index, "curated_host_scientific_name"] = row["greater_than_equal_75_scientific_name"]
                df.at[index, "curated_host_common_name"] = row["greater_than_equal_75_common_name"]
            else:
                if all(pd.isna(row[col]) for col in
                       ["Genbank Host", "Biosample Host Scientific Name", "Biosample Host Common Name"]):
                    df.at[index, "curated_host_scientific_name"] = ""
                    df.at[index, "curated_host_common_name"] = ""
                else:
                    if (row["greater_than_equal_75_scientific_name"] == row["Biosample Host Scientific Name"]) or \
                            (row["Genbank Host"] == row["Biosample Host Scientific Name"]):
                        df.at[index, "curated_host_scientific_name"] = row["greater_than_equal_75_scientific_name"]
                        df.at[index, "curated_host_common_name"] = row["greater_than_equal_75_common_name"]
                    elif (row["greater_than_equal_75_common_name"] == row["Biosample Host Common Name"]) or \
                            (row["Genbank Host"] == row["Biosample Host Common Name"]):
                        df.at[index, "curated_host_scientific_name"] = row["greater_than_equal_75_scientific_name"]
                        df.at[index, "curated_host_common_name"] = row["greater_than_equal_75_common_name"]
                    elif row["greater_than_equal_75_common_name"] == row["Biosample Host Scientific Name"]:
                        df.at[index, "curated_host_scientific_name"] = row["greater_than_equal_75_scientific_name"]
                        df.at[index, "curated_host_common_name"] = row["greater_than_equal_75_common_name"]
                    else:
                        df.at[index, "curated_host_scientific_name"] = "GB-Bio_Host_mismatch"
                        df.at[index, "curated_host_common_name"] = "GB-Bio_Host_mismatch"
        else:
            df.at[index, "curated_host_scientific_name"] = ""
            df.at[index, "curated_host_common_name"] = ""


def annotate_and_process(df):
    less_than_75_or_not_found = []
    greater_than_equal_75_scientific_name = []
    greater_than_equal_75_common_name = []
    host_information_source = []
    score = []
    flag = []

    for index, row in df.iterrows():
        annotated_host, host_text, source = process_row(row)

        if annotated_host and annotated_host['data']:
            annotation_data = annotated_host['data']
            score_value = annotation_data.get('score')
            score.append(score_value)
            if score_value is not None and score_value < 75:
                less_than_75_or_not_found.append(host_text)
                greater_than_equal_75_scientific_name.append("")
                greater_than_equal_75_common_name.append("")
                flag.append('low confidence host')
            else:
                less_than_75_or_not_found.append("")
                greater_than_equal_75_scientific_name.append(annotation_data['scientificName'])
                greater_than_equal_75_common_name.append(annotation_data['commonName'])
                flag.append('high confidence host')
        else:
            score.append(None)
            less_than_75_or_not_found.append(host_text)
            greater_than_equal_75_scientific_name.append("")
            greater_than_equal_75_common_name.append("")
            flag.append('host not found')

        host_information_source.append(source)

    df["less_than_75_or_no_annotation_found"] = less_than_75_or_not_found
    df["greater_than_equal_75_scientific_name"] = greater_than_equal_75_scientific_name
    df["greater_than_equal_75_common_name"] = greater_than_equal_75_common_name
    df["host_information_source"] = host_information_source
    df['curated_host_common_name'] = ''
    df['curated_host_scientific_name'] = ''
    df['Score'] = score
    df['Flag'] = flag


def main():
    df = pd.read_csv("/Users/rbhattac/Desktop/Curation/Pipeline/abril_Code/results_code_Abril.csv")
    annotate_and_process(df)

    df = df[["Accession", "Genbank Host", "Biosample Host Scientific Name", "Biosample Host Common Name",
             "less_than_75_or_no_annotation_found", "greater_than_equal_75_scientific_name",
             "greater_than_equal_75_common_name", "host_information_source", 'curated_host_scientific_name',
             'curated_host_common_name', 'Score', 'Flag']]
    df.to_csv("/Users/rbhattac/Desktop/curated_host_with_annotations.csv", index=False)

    df = pd.read_csv("/Users/rbhattac/Desktop/curated_host_with_annotations.csv")
    df_copy = df.replace(["NA", "not applicable", "not provided"], np.nan)
    populate_curated_columns(df_copy)
    df_copy.to_csv("/Users/rbhattac/Desktop/curated_host_with_annotations_1.csv", index=False)


if __name__ == "__main__":
    main()


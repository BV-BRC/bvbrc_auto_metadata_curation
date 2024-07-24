import pandas as pd
import requests
import time
import csv

class Settings:
    accessToken: str = "eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJwMmMiOjgxOTIsInAycyI6Im14WXJISk96QlZqSVp3NFEiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiemlwIjoiREVGIn0.SXUJ-5e5lc0YcSbLLSXAOr3MXxKcmkEpQTAGD8jJA-3184Q4lorJpA.Ug3mCshkWc4fYc-fvKJ7JQ.PpPQlPOha-VvZReIHHtKYffguLWjvY1tToB5C5HeMSAGddNkDDKfspZsEX0pGebrpQ71t0rUGV1VG9Mq5_mAG-ePMFowm6vvBBCS7wIahdNl-B0WsARnEml7kBvVEeCkeeoW6NXvcDRZnWa5L3zPlmu-uA4IQezhK-ZpIbvRO1ZDX1ODiRWt72Kof__sWypztcQY3cVvrwTU69NRnkpwiA.QjJHRBxOoJ0ElUuuLC8dVA"
    baseURL: str = "https://dev.ictv.global/HostAnnotation"

    @classmethod
    def get_headers(cls):
        headers = {"Authorization": cls.accessToken}
        return headers

def annotateHostText(hostText: str):
    payload = {"hostText": hostText}
    print('Annotating Host...')
    try:
        response = requests.post(
            f"{Settings.baseURL}/annotateHostText",
            headers=Settings.get_headers(),
            data=payload
        )
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        responseJSON = response.json()
        return responseJSON
    except Exception as e:
        print(f"Error fetching host annotation: {e}")
        return None

def main():
    #start_time = time.time()
    #read the host names to be curated from a csv file
    file_path="/Users/rbhattac/Desktop/test_don.csv"
    df = pd.read_csv(file_path)
    hosts = df["Genbank Host"].tolist() #choose the appropriate column name

    #decide the output format
    with open("/Users/rbhattac/Desktop/results_code_don.csv", "w", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(["Host", "Scientific Name", "Common Name", "Score"])

        #Annotate hosts
        for hostText in hosts:
            #hostText = "Human"
            start_time = time.time()
            responseJSON = annotateHostText(hostText)
            #print(responseJSON)
            if responseJSON['data'] is not None:
                annotation_data = responseJSON['data']
                Scientific= annotation_data['scientificName']
                Common = annotation_data['commonName']
                Score = annotation_data['score']
                # print(f"Scientific Name: {Scientific}")
                # print(f"Common Name: {Common}")
                # print(f"Score: {Score}")
                print(f"Execution time: {time.time() - start_time}")
                csv_writer.writerow([hostText, Scientific, Common, Score])

if __name__ == "__main__":
    main()
from dotenv import load_dotenv
import os
load_dotenv()
from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# If modifying these scopes, delete the file token.json.


# The ID spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SAMPLE_SPREADSHEET_ID")
API_KEY_TEQUILA = os.getenv("API_KEY_TEQUILA")
GOOGLE_SHEET_API_KEY= os.getenv("GOOGLE_SHEET_API_KEY")


service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="prices!A1:C11").execute()
values = result.get('values', [])
#print(values)

# iata=[]
# for i in range(0,9):
#     iata.append(["TESTING"])
# print(f"iata: {iata}")
#
# result = sheet.values().update(
#     spreadsheetId=SAMPLE_SPREADSHEET_ID, range='prices!B2:B10',
#     valueInputOption="USER_ENTERED", body={"values":iata}).execute()


sheet_data = values

prices = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="prices!C2:C11").execute()
#print("prices")

import requests
cities = []
iatas = []
for i in range(1, len(values)):
    cities.append(values[i][0])
#print(cities)

for city in cities:
    headers = {
        "apikey": API_KEY_TEQUILA ,
    }

    query = {
        "term": city,

    }
    #print(city)
    response = requests.get(url="https://tequila-api.kiwi.com/locations/query", headers=headers, params=query)
    results = response.json()
    #print(results)
    iatas.append(results["locations"][0]['code'])

#print(iatas)
iatas_list = []
for iata in iatas:
    iatas_list.append([iata])
#print(iatas_list)

result = sheet.values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range='prices!B2:B11',
    valueInputOption="USER_ENTERED", body={"values": iatas_list}).execute()
endpoint = "https://tequila-api.kiwi.com/v2/search"
import requests

headers = {
    "apikey": GOOGLE_SHEET_API_KEY,
}

superior_price = None
from datetime import datetime, timedelta
current_date=datetime.now()
next_six_months = current_date + timedelta(days=90)
next_six_months = next_six_months.strftime("%d/%m/%Y")
current_date = current_date.strftime("%d/%m/%Y")

for iata in iatas:
    #print(iata)
    if iata == "BER":
        pass
    else:
        query = {
            "fly_from": "BER",
            "fly_to": f"{iata}",
            "date_from": current_date,
            "date_to": next_six_months,
            "flight_type": "round",
            "max_stopovers": 3,
            "nights_in_dst_from": "7",
            "nights_in_dst_to": "28",

        }
        try:
            response = requests.get(url=f"{endpoint}", params=query, headers=headers)

            formated_message = f' with only {response.json()["data"][0]["price"]}euro ' \
                               f'from {response.json()["data"][0]["cityFrom"]} to ' \
                               f'{response.json()["data"][0]["cityTo"]}' \
                               f' {response.json()["data"][0]["flyFrom"]}-->{response.json()["data"][0]["flyTo"]}'
            prices = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="prices!C2:C9").execute()
            prices = prices["values"]

            print(prices)
            prices_list = []
            for list in prices:
                prices_list.append(int(list[0]))
            print(prices_list)
            for price in prices_list:
                if price > response.json()["data"][0]["price"]:
                    inferior_price = response.json()["data"][0]["price"]
                    superior_price = True
            if superior_price==True:
                print(formated_message)
                print("______________________________________________________")
                stops_data = response.json()["data"][0]["route"]
                stop_city = f"{stops_data[0]['cityTo']}-{stops_data[0]['flyTo']}"
                stop_city_name=stops_data[0]['cityTo']
                price = response.json()["data"][0]["price"]
                airport_from = response.json()["data"][0]["flyFrom"]
                airport_to = response.json()["data"][0]["flyTo"]
                city_from = response.json()["data"][0]["cityFrom"]
                city_to = response.json()["data"][0]["cityTo"]
                formated_message = f'{city_to}-{airport_to}' \
                                   f'with one stop at {stop_city}'
                if city_to != stop_city_name:
                    print(formated_message)
                print("______________________________________________________")
            else:
                pass
        except IndexError:
            print(f"there is no flight with the required parameters to {iata}")




































































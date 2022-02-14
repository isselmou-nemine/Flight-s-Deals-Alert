
from dotenv import load_dotenv
import os
load_dotenv()
SAMPLE_SPREADSHEET_ID = os.getenv("SAMPLE_SPREADSHEET_ID")
API_KEY_TEQUILA = os.getenv("API_KEY_TEQUILA")
GOOGLE_SHEET_API_KEY= os.getenv("GOOGLE_SHEET_API_KEY")

from googleapiclient.discovery import build
from google.oauth2 import service_account
SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="prices!A1:C11").execute()
values = result.get('values', [])

sheet_data = values
prices = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="prices!C2:C11").execute()
import requests
cities = []
iatas = []
for i in range(1, len(values)):
    cities.append(values[i][0])


#geeting IATA of each city in my google sheet (International Air Transport Association code)

for city in cities:
    headers = {
        "apikey": API_KEY_TEQUILA,
    }

    query = {
        "term": city,
    }

    response = requests.get(url="https://tequila-api.kiwi.com/locations/query", headers=headers, params=query)
    results = response.json()
    #print(results)
    iatas.append(results["locations"][0]['code'])
#print(iatas)

iatas_list = []
for iata in iatas:
    iatas_list.append([iata])
#print(iatas_list)

#writing in my google sheet IATAS that we get back from taquila API

result = sheet.values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID, range='prices!B2:B11',
    valueInputOption="USER_ENTERED", body={"values": iatas_list}).execute()
endpoint = "https://tequila-api.kiwi.com/v2/search"


#getting the date of today and next 6 months from today

from datetime import datetime, timedelta
current_date=datetime.now()
next_six_months = current_date + timedelta(days=90)
next_six_months = next_six_months.strftime("%d/%m/%Y")
current_date = current_date.strftime("%d/%m/%Y")

#making request to taquila api to get data in case the price is lower then the price that i have in google sheet.
#note that i'm intrested in just in all flights from berlin to the destination cities in google sheet.
#period between my deperature and return should be from 7 to 28 nights.

import requests
headers = {
    "apikey": GOOGLE_SHEET_API_KEY,
}
superior_price = None
for iata in iatas:
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

            #print(prices)
            prices_list = []
            for list in prices:
                prices_list.append(int(list[0]))
            #print(prices_list)
            for price in prices_list:
                if price > response.json()["data"][0]["price"]:
                    inferior_price = response.json()["data"][0]["price"]
                    superior_price = True
            if superior_price==True:
                print("___________________________####___________________________")
                print(formated_message)
                stops_data = response.json()["data"][0]["route"]
                stop_city = f"{stops_data[0]['cityTo']}-{stops_data[0]['flyTo']}"
                stop_city_name=stops_data[0]['cityTo']
                price = response.json()["data"][0]["price"]
                airport_from = response.json()["data"][0]["flyFrom"]
                airport_to = response.json()["data"][0]["flyTo"]
                city_from = response.json()["data"][0]["cityFrom"]
                city_to = response.json()["data"][0]["cityTo"]
                formated_message =  f' with only {price}euro! ' \
                                    f'from {city_from}-{airport_from} to ' \
                                    f'{city_to}-{airport_to}' \
                                    f'with one stop at {stop_city}.\n' \
                                    f'Wish you a nice trip!'

                if city_to != stop_city_name:
                    print(formated_message)
                print("_____________________@@@_________________________________")
                import smtplib
                my_email = "first.user799@gmail.com"
                password = "Azerty1234."
                #Now i will send an email alert to the costumer with the relevant data
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(user=my_email, password=password)
                    connection.sendmail(from_addr=my_email, to_addrs="first.user79@yahoo.com",
                                        msg=f"subject:Dear costumer\n\n {formated_message}")
                print("email sent")
            else:
                pass
        except IndexError:
            print(f"there is no flight with the required parameters to {iata}")


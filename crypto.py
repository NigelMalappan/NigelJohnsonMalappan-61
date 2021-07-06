'''
This program tracks BitCoin price every one hour.
We have used CoinMarketCap API for the price.
All the prices are pushed in the Google Sheets.
This data can be visualized further on a Dashboard.

If the change percentage of the price is above the threshold set by the admin :
    Then it will send the user an email and whatsapp alert.
    For sending email it parses the emails.txt file for the mails.

DEF send_mail():
    1:SMPT lib
    1:Parsing email ids from emails.txt

DEF get_bit():
    1:Data from CoinMarketCap API 
    1:Parsing the JSON Data
    1:Pushing the data to Google Sheets
    1:Thresholding percentage logic

    0:Sending the mail
        Title of the email

    0:Sending WhatsApp message
        Proper scripting of the message.
        Sending time issue (Causing due to abs trash library wriiten).


'''

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os
import pywhatkit
import time
from datetime import datetime
import requests
import smtplib
import yaml



def send_mail(percent_change):
    '''
    - It parses the emails of the users to send email.
    - It also creates server connection to send that email.

    Args:
        percent_change (int) : The percentage change within one hour.
        
        server (obj) :  Object of SMTP library to send an email.
        subject (str):  Subject of the email.
        body (str) :    Body of the email
        msg (str)  :    The combined string of subject and body.

        my_file (Str) : An object to parse the txt file.
        words (list)  : List of string containing email ids.

    '''

    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.environ.get('EMAIL_ID'),os.environ.get('EMAIL_ID_PASSWORD'))

        subject='Alert Bitcoin is '
        body='The price of Bitcoin is down by: ' + str(percent_change)
            
        msg=f"Subject: {subject}\n\n{body}"

        my_file = open(r'D:\Vcode\Crypto-Tracker\Experimentation\emails.txt')
        my_file.seek(0)
        words = my_file.read().split()

        for i in words:
            server.sendmail(os.environ.get('EMAIL_ID'),i,msg)
            print("Sent ! ")
        
        server.quit()
        
        
    except:
        print("Somethings wrong ! ")


def get_bit():
    '''
    - It parses the Google Sheets link from the yaml file.
    - Gets the json data from the API and parses it.
    - Sends the data to the Google Sheets.
    - Sends Email and Whatsapp message.

    Args:
        url_sheets (str) :  Google Sheets API link.
        response (str) :    Gets the data from the CoinMarketCap API.
        bitObj (json)  :    Converts the data into json format.
        
        bit_price (double):     INR value of the bitcoin.
        bit_per_1h (double):    The percentage change in one hour.  
        bit_per_24h(double):    The percentage change in 24 hour.  
        bit_per_7d(double):     The percentage change in 7 days.  
        bit_per_30d(double):    The percentage change in 30 days.

        message (str) : The string of message to be sent.
        param (dictionary) :    The dictionary of key and value pairs to be sent to update the Google Sheets.
        now (tuple) :   It contains time.
        current_hour (int) :    Time in hours.
        current_min  (int) :    Time in minutes.
        threshold_change (int): The variable to assign the change value.  

    '''
    #URL and header files to get the response from the API
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol':'BTC',
        'convert':'INR'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.environ.get('CRYPTO_API_KEY'),                          ????
    }

    session = Session()
    session.headers.update(headers)
    
    #The Google Sheets API link.
    with open(r"ans.yaml","r") as s:
        y = yaml.load(s)
    url_sheets = y["key"]

    try:
        response = session.get(url, params=parameters)
        parseData = json.dumps(response.json())
        bitObj = json.loads(parseData)
        bit_price = bitObj['data']['BTC']['quote']['INR']['price']
        bit_per_1h = bitObj['data']['BTC']['quote']['INR']['percent_change_1h']
        bit_per_24h = bitObj['data']['BTC']['quote']['INR']['percent_change_24h']
        bit_per_7d = bitObj['data']['BTC']['quote']['INR']['percent_change_7d']
        bit_per_30d = bitObj['data']['BTC']['quote']['INR']['percent_change_30d']

        print(bit_price)
        # print(bit_per_1h)
        # print(bit_per_24h)
        # print(bit_per_7d)
        # print(bit_per_30d)

        #The message to be send using WhatsApp.
        message = "The price moved by : "+str(bit_per_1h)+" %"

        #To send the data to Google Sheets.
        param = {"id":"Sheet1", "Price-INR": bit_price ,"Change1hr": bit_per_1h ,"Change24hr": bit_per_24h ,"Change7d": bit_per_7d ,"Change30d": bit_per_30d } 
        response = requests.get(url_sheets, params=param)
        print(response.content)
        
        #Time required to send the WhatsApp message
        now = datetime.now()
        current_hour = int(now.strftime("%H"))
        current_min = int(now.strftime("%M")) + 2

        #The percent change required to trigger the user.
        threshold_change = 0.1
        if abs(bit_per_1h) > threshold_change:
            send_mail(bit_per_1h)
            pywhatkit.sendwhatmsg(os.environ.get('PHONE_NUMBER'),message,current_hour,current_min)
            
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

get_bit()

# while(True):
#     get_bit()
#     time.sleep(60*60)
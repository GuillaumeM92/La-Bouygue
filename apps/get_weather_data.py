import requests
import openpyxl
from datetime import datetime
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
url = 'https://www.google.fr/search?q=meteo+parthenay+79200'

xls_file_name = 'parthenay_weather_data.xlsx'

month_names = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre' , 'novembre', 'décembre']

def get_weather_data():
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    # get required data with beautiful soup selector
    data = {
        'location': soup.select('#wob_loc')[0].getText().strip(),
        'time': soup.select('#wob_dts')[0].getText().strip(),
        'info': soup.select('#wob_dc')[0].getText().strip(),
        'temp': soup.select('#wob_tm')[0].getText().strip(),
    }
    return data

def write_to_xls(data):
    # open existing excel file and existing sheet
    xls_file = openpyxl.load_workbook(xls_file_name)
    sheet = xls_file.active
    count = sheet['F2'].value
    # format time data
    weekday, hour = data['time'].split(' ')
    day, month, year = datetime.now().day, datetime.now().month, datetime.now().year
    month_name = get_month_name(month)
    # insert weather data on new line
    sheet[f'A{count}'] = data['location']
    sheet[f'B{count}'] = f'{weekday} {day} {month_name} {year} - {hour}'
    sheet[f'C{count}'] = data['info']
    sheet[f'D{count}'] = int(data['temp'])
    # increment counter by 1
    sheet['F2'] = count + 1
    xls_file.save(xls_file_name)

def get_month_name(month):
    return month_names[month]

def run():
    data = get_weather_data()
    write_to_xls(data)

run()

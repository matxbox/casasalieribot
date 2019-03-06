from bs4 import BeautifulSoup
from requests import get as gethttp
import re
import csv
from time import time


start = time()

def room_url_parser(sede):
    table_url = 'https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do'
    url_keys = {
        'csic': sede,
        'categoria': 'tutte',
        'tipologia': 'tutte',
        'giorno_day': 3,
        'giorno_month': 3,
        'giorno_year': 2019,
        'jaf_giorno_date_format': r'dd%2FMM%2Fyyyy',
        'evn_visualizza': 'Visualizza+occupazioni'
    }
    webpage = gethttp(table_url, params=url_keys)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    rooms = soup.find_all(name='td', attrs={
                                            'class': 'dove',
                                            'rowspan': True})
    rooms_url='https://www7.ceda.polimi.it/spazi/spazi/controller/'
    rooms_link = [rooms_url + x.a.attrs['href'] for x in rooms]
    return rooms_link

def room_details_parser(url):
    room_web = gethttp(url)
    souproom = BeautifulSoup(room_web.content, 'html.parser')
    allestimenti_table = souproom.find(name = 'table', id = 'aula_proprietaPubblicabili_auleColl')
    allestimenti_list = [x for x in allestimenti_table.tbody.stripped_strings]
    try:
        allestimenti_list.index('Postazioni dotate di presa elettrica')
    except ValueError:
        prese = False
    else:
        prese = True
    try:
        allestimenti_list.index('Postazioni dotate di presa di rete')
    except ValueError:
        ethernet = False
    else:
        ethernet = True
    details_div = souproom.find(name = 'div', id = re.compile('tab[0-9]{5}-0'))
    details_list = [x for x in details_div.stripped_strings]
    edificio_full = details_list[details_list.index('Edificio')+1]
    edificio = edificio_full.split(' - ')[0][9:]
    room_details = {
                    'nome': details_list[details_list.index('Sigla')+1],
                    'categoria': details_list[details_list.index('Categoria')+1],
                    'tipologia': details_list[details_list.index('Tipologia')+1],
                    'edificio': edificio,
                    'prese' : prese,
                    'ethernet' : ethernet
                    }
    return room_details

sedi = ['MIB', 'MIA', 'COE', 'CRG', 'LCF', 'MNI', 'PCL']
fields = ['edificio', 'nome', 'prese', 'tipologia', 'ethernet', 'categoria']
csv.excel.delimiter = ';'
with open('rooms.csv', 'w', newline = '') as csvrooms:
    csvwriter = csv.DictWriter(csvrooms, fieldnames = fields,)
    csvwriter.writeheader()
    for sede_code in sedi:
        for room_url in room_url_parser(sede_code):
            csvwriter.writerow(room_details_parser(room_url))
             
elapsed = str((start - time())//60) + ':' + str((start-time()) % 60)
print(elapsed)
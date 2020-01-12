import requests
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://goverla.ua'

page = requests.get(BASE_URL)

soup = BeautifulSoup(page.text, 'html.parser') 


result_bid = []
result_ask = []

titles = [div['title'] for div in soup.find_all('img', title=True)]
print('\n')
num = 0
for bid, ask in zip(soup.find_all(class_ = "gvrl-table-cell bid"), soup.find_all(class_ = "gvrl-table-cell ask")):
	bid = str(bid)
	ask = str(ask)

	bid = re.findall(r'[0-9]', bid)
	if bid != []:
		print(titles[num])
		bid = int(''.join(bid))/100
		print('bid: ', bid)

	ask = re.findall(r'[0-9]', ask)
	if ask != []:
		ask = int(''.join(ask))/100
		print('ask: ', ask)
		print('\n')

	num += 1
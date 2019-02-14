import bs4
with open('occupazioni.html', mode='r') as htmlfile:
    filter_scrollcontent = bs4.SoupStrainer(class_='scrollContent', name='tbody')
    page = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=filter_scrollcontent)
normalrows_list = page.find_all(name='tr', class_='normalRow')




with open('solorighe.html', mode='w+') as destfile:
    destfile.write(str(page))
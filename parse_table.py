import bs4

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

first, second, third = rows[0], rows[1], rows[2]
for row in (first,):
	row.td.decompose()  # Delete date cell
	room = row.td.extract().a.string[1:-2]  #[1:-2] strips white spaces
	print(room)
	# The row obj now contains only relevant information
	eight_o_clock = 480 # 480=60*8 minutes after midnight
	for tag in row.children:
		minuti, attività = None, None
		if tag.attrs['class'] ==['slot']:
			minuti = int(tag.attrs['colspan'])*15
			attività = tag.string
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):
			minuti = 15
			attività = '[vuoto]'
		else:
			print(str(tag))
		print('Slot di {} minuti per {}'.format(minuti, attività))

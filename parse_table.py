import bs4

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

def occupation_of_room(row): # Returns single key dict: {room:[changes_of_activity]}
	events_duration = []
	def add_15m_free(): # List with (time, ending event name) tuples
		nonlocal events_duration
		if len(events_duration) == 0:
			events_duration.append((15, None))
			return
		lastduration, lastevent = events_duration[-1]
		if lastevent==None:
			events_duration[-1] = (lastduration + 15, lastevent)
		else:
			events_duration.append((15, None))

	for tag in row.children:
		if tag.attrs['class'] == ['slot']:
			length = int(tag.attrs['colspan']) * 15
			activity = tag.string
			events_duration.append((length, activity))
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):
			add_15m_free()
		elif tag.attrs['class'] in (['data'], ['dove']):
			continue
		else:
			raise Error('Tag imprevisto!')
			print(str(tag))
#		print('Slot di {} minuti per {}'.format(minutes, activity))
	return events_duration


rows = rows[:2]
rooms = {}
while len(rows) != 0:
	row = rows.pop(0)
	if row.find(name='td', class_='dove') is not None:
		room = row.find(name='td', class_='dove').a.string[1:-2]
	occupation = occupation_of_room(row)
	if room in rooms.keys():
		for i in range(1, 10):
			if '_'.join([room, str(i)]) in rooms.keys():
				continue
			else:
				rooms['_'.join([room, str(i)])] = occupation
				break
	else:
		rooms[room] = occupation

exit()

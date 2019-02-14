import bs4

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

def occupation_of_room(row): # Returns single key dict: {room:[changes_of_activity]}
	events_ending_times = [(480, None)]
	def add_15m_free(): # List with (time, ending event name) tuples
		nonlocal events_ending_times
		lasttime, lastevent = events_ending_times[-1]
		if lastevent==None:
			events_ending_times[-1] = (lasttime+15, lastevent)
		else:
			events_ending_times.append((lasttime+15, None))
	def add_long_event(length, activity):
		nonlocal events_ending_times
		lasttime, lastevent = events_ending_times[-1]
		events_ending_times.append((lasttime+length, activity))
	for tag in row.children:
		if tag.attrs['class'] == ['slot']:
			minutes = int(tag.attrs['colspan'])*15
			activity = tag.string
			add_long_event(minutes, activity)
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):
			minutes = 15
			activity = '[vuoto]'
			add_15m_free()
		elif tag.attrs['class'] in (['data'], ['dove']):
			continue
		else:
			raise Error('Tag imprevisto!')
			print(str(tag))
#		print('Slot di {} minuti per {}'.format(minutes, activity))
	return events_ending_times


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

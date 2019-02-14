import bs4

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

def occupation_of_room(row): # Returns single key dict: {room:[changes_of_activity]}
	row.td.decompose()  # Delete date cell
	try:
		room = row.td.extract().a.string[1:-2]  #[1:-2] strips white spaces
	except AttributeError:
		return 'Duplicate row', None
#	print(room)
	# The row obj now contains only relevant information
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
		else:
			print(str(tag))
#		print('Slot di {} minuti per {}'.format(minutes, activity))
	return room, events_ending_times


rows = rows
rooms = {}
for row in rows:
	room, occupation = occupation_of_room(row)
	rooms[room]=occupation
if 'Duplicate row' in rooms.keys():
	del rooms['Duplicate row']
print('Exit')

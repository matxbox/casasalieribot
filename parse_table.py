import datetime
import bs4

# Here is html --> data per row
def parse_row_get_occupation(row):
	"""Actually does the parsing, converting a refined row to a list of tuples"""
	events_duration = []
	def add_15m_free(): # List with (time, ending event name) tuples
		nonlocal events_duration
		if len(events_duration) == 0:
			events_duration.append((15, 'Vuota'))
			return
		lastduration, lastevent = events_duration[-1]
		if lastevent == 'Vuota':
			events_duration[-1] = (lastduration + 15, lastevent)
		else:
			events_duration.append((15, 'Vuota'))

	for tag in row.children:
		if tag.attrs['class'] == ['slot']:  # That's an event!
			length = int(tag.attrs['colspan']) * 15
			activity = tag.string
			if activity[-8:] == '(ESAME) ':
				activity = 'Esame'
			events_duration.append((length, activity))
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):  # That's a free spot!
			add_15m_free()
		elif tag.attrs['class'] in (['data'], ['dove']):  # First cells, useless
			continue
		else:
			print(str(tag))
			raise Error('Tag imprevisto!')
	return events_duration

# Here is data --> readable text per room
def return_list_of_readable_lines(name, roomdata):
	output_list = []
	output_list.append(name + '\n')
	currenttime = datetime.datetime(1, 1, 1, hour=8, minute=00)
	for duration, event in roomdata:
		output_list.append(currenttime.time().isoformat(timespec='minutes') + ' ' + event + '\n')
		currenttime = currenttime + datetime.timedelta(minutes=duration)
	output_list.append('\n')
	return output_list


with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

# Here is done parsing for every row, handling multiple rows per room
rooms = {}
while len(rows) != 0:
	row = rows.pop(0)
	if row.find(name='td', class_='dove') is not None:  # Se la riga contiene l'indicazione dell'aula...
		room = row.find(name='td', class_='dove').a.string[
		       1:-2]  # ...considera quello come il nome dell'attuale aula...
	occupation = parse_row_get_occupation(row)  # ...e interpreta la riga. Ora abbiamo nome e dati, vanno salvati
	if room in rooms.keys():  # Se la riga non ha il nome dell'aula usa il nome precedente
		for i in range(1, 10):  # e salvalo nel dizionario aggiungendo _1, _2 eccetera
			if '_'.join([room, str(i)]) in rooms.keys():
				continue
			else:
				rooms['_'.join([room, str(i)])] = occupation
				break
	else:
		rooms[room] = occupation  # Se invece va tutto bene, salva semplicemente

# Here text is generated for every row and saved
text_list = []
for room, roomdata in rooms.items():
	text_list.extend(return_list_of_readable_lines(room, roomdata))
with open('messaggio.txt', 'w+') as outputfile:
	outputfile.writelines(text_list)
exit()

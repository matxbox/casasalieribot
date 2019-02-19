import datetime

import bs4

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]


def parse_row_get_occupation(row):
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
		if tag.attrs['class'] == ['slot']:
			length = int(tag.attrs['colspan']) * 15
			activity = tag.string
			if activity[-8:] == '(ESAME) ':
				activity = 'Esame'
			events_duration.append((length, activity))
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):
			add_15m_free()
		elif tag.attrs['class'] in (['data'], ['dove']):
			continue
		else:
			raise Error('Tag imprevisto!')
			print(str(tag))
	# 		print('Slot di {} minuti per {}'.format(minutes, activity))
	return events_duration


def print_string_of_occupation(name, roomdata):
	output_list = []
	output_list.append(name + '\n')
	currenttime = datetime.datetime(1, 1, 1, hour=8, minute=00)
	for duration, event in roomdata:
		output_list.append(currenttime.time().isoformat(timespec='minutes') + ' ' + event + '\n')
		currenttime = currenttime + datetime.timedelta(minutes=duration)
	output_list.append('\n')
	return output_list


# Itera su tutte le righe per generare il dizionario 'rooms'
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
# Qui tutti i dati sono stati interpretati e salvati in 'rooms', un dizionario {nomeaula: listaoccupazioni}

# Genera il testo a partire dal dizionario 'rooms' e al posto di inviarlo per messaggio lo salva in un file
text_list = []
for room, roomdata in rooms.items():
	text_list.extend(print_string_of_occupation(room, roomdata))
with open('messaggio.txt', 'w+') as outputfile:
	outputfile.writelines(text_list)
exit()

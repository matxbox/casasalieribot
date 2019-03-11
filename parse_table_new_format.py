import datetime
import bs4

class Event:
	def __init__(self, name, starttime, duration):
		self.name = name
		self.starttime = starttime
		self.duration = duration
	def __str__(self):
		return self.name +', '+ str(self.starttime)

	@property
	def endtime(self):
		return self.starttime + self.duration

class Occupation:
	def __init__(self):
		self.eventlist = []
		self.occupation = []
	
	def _delete_events_before(self, starttime): # Pass a datetime.time or datetime.datetime, no problems
		new_eventlist = self.eventlist.copy()
		if isinstance(starttime, datetime.datetime): starttime = starttime.time()
		for i in self.eventlist:
			if i.endtime.time() <= starttime: new_eventlist.remove(i)
			else: break
		
		minutes_from_8oclock = 60*(starttime.hour-8) + starttime.minute
		slots_tbd = minutes_from_8oclock//15
		new_occupation = self.occupation[slots_tbd:]
		return new_eventlist, new_occupation
				
	def evaluate(self, starttime=datetime.time(hour=8)):
		current_slot_number = (60*(starttime.hour-8) + starttime.minute)//15
		current_event = self.occupation[current_slot_number]
		if current_event.name == 'Vuota':
			return current_event.endtime.time() - starttime

# Here is html --> data per row
def parse_row_get_occupation(row):
	occ = Occupation()
	interval = datetime.timedelta(minutes=15)
	y, m, d = datetime.date.today().year, datetime.date.today().month, datetime.date.today().day
	currenttime = datetime.datetime(year=y, month=m, day=d, hour=8)
	for tag in row.children:
		if tag.attrs['class'] == ['slot']:  # That's an event!
			length = int(tag.attrs['colspan'])
			duration = interval*length
			activity = tag.string
			if activity[-8:] == '(ESAME) ':
				activity = 'Esame'
			event = Event(activity, currenttime, duration)
			occ.eventlist.append(event)
			for i in range(length):
				occ.occupation.append(event)
			currenttime += duration
		elif tag.attrs['class'] in (['empty'], ['empty_prima']):  # That's a free spot!
			try:
				last_event=occ.occupation[-1]
				if last_event.name == 'Vuota':
					last_event.duration += interval
					occ.occupation.append(last_event)
				else:
					newevent = Event('Vuota', currenttime, interval)
					occ.occupation.append(newevent)
					occ.eventlist.append(newevent)
			except IndexError:
					newevent = Event('Vuota', currenttime, interval)
					occ.occupation.append(newevent)
					occ.eventlist.append(newevent)
			currenttime += interval
		elif tag.attrs['class'] in (['data'], ['dove']):  # First cells, useless
			continue
	return occ

with open('occupazioni.html', 'r') as htmlfile:
	parsed = bs4.BeautifulSoup(htmlfile, 'html.parser', parse_only=bs4.SoupStrainer(class_='scrollContent', name='tbody'))
rows = parsed.find_all(class_='normalRow')[1:]

# Here is done parsing for every row, handling multiple rows per room
rooms = {}
rows = rows[:3]
while len(rows) != 0:
	row = rows.pop(0)
	if row.find(name='td', class_='dove') is not None:  # Se la riga contiene l'indicazione dell'aula...
		room = row.find(name='td', class_='dove').a.string[1:-2]  # ...considera quello come il nome dell'attuale aula...
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
occ=Occupation()
occ.eventlist = rooms['N.0.1']
'''exit()'''
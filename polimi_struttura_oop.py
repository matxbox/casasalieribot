import datetime
from geopy import distance as geodist
import csv


all_rooms={}

class Aula:
	'Crea una nuova aula con le sue proprietà. Richiede un oggetto Edificio in input'
	weights = {
				'occupation': 10/60,  # Per minute of availability
				'distance': 10,
				'prese': 10,
				'disegno': 10,
				'ethernet': 10,
				'informatizzata': 10,
				}
	def __init__(
				self, 
				nome: str, 
				edificio, 
				disegno: bool, 
				prese: bool, 
				ethernet: bool, 
				informatizzata: bool, 
				campus: str):
		all_rooms[nome] = self
		self.userlocation = None
		self.nome = nome
		self.edificio = edificio
		self.disegno = disegno
		self.prese = prese
		self.ethernet = ethernet
		self.informatizzata = informatizzata
		self.campus = campus
		self._occupation = None

	def is_free(self, time=datetime.datetime.now().time()): #TODO: support for out-of-range time
		slot_number = (time.hour-8)*4 + time.minute//15
		return self._occupation.occupation[slot_number].name == 'Vuota'

	def evaluate(self, posizione, orario):
		'Returns evaluation of the room based on user location and datetime.datetime object'
		def value_distance(posizione):
			return min((50/(geodist.distance(posizione, self.edificio.posizione).m),1))
		disegno =  self.weights['disegno'] * int(self.disegno)
		prese = self.weights['prese'] * int(self.prese)
		ethernet = self.weights['ethernet'] * int(self.ethernet)
		informatizzata = self.weights['informatizzata'] * int(self.informatizzata)
		distanza = self.weights['distance'] * value_distance(posizione)
		if self._occupation is not None:
			occupazione = self.weights['occupation'] * self._occupation.evaluate(orario)
			if occupazione < 0: return 0
			else: return disegno + prese + ethernet + informatizzata + distanza + occupazione
		else: return disegno + prese + ethernet + informatizzata
			
	def __cmp_prese(self, other):
		if self.prese:
			if other.prese:
				return 0
			else:
				return 1
		else:
			if other.prese: return -1
		return 0

	def __cmp_disegno(self, other):
		if self.disegno:
			if other.disegno:
				return 0
			else:
				return 1
		else:
			if other.disegno: return -1
		return 0

	def __cmp_ethernet(self, other):
		if self.ethernet:
			if other.ethernet:
				return 0
			else:
				return 1
		else:
			if other.ethernet: return -1
		return 0

	def __cmp_informatizzata(self, other):
		# criterio inverso, se NON informatizzata è meglio
		if self.informatizzata:
			if other.informatizzata:
				return 0
			else:
				return -1
		else:
			if other.informatizzata: return 1
		return 0

	def __cmp(self, other):
		disegno =  self.weights['disegno'] * self.__cmp_disegno(other)
		prese = self.weights['prese'] * self.__cmp_prese(other)
		ethernet = self.weights['ethernet'] * self.__cmp_ethernet(other)
		informatizzata = self.weights['informatizzata'] * self.__cmp_informatizzata(other)
		# Occupazione
		total = prese + disegno + ethernet + informatizzata
		return total

	def __str__(self):
		return self.nome

	def __eq__(self, other):
		return self.__cmp(other) == 0

	def __lt__(self, other):
		return self.__cmp(other) < 0

	def __le__(self, other):
		return self.__cmp(other) <= 0

	def __gt__(self, other):
		return self.__cmp(other) > 0

	def __ge__(self, other):
		return self.__cmp(other) >= 0

	def __ne__(self, other):
		return self.__cmp(other) != 0

	@property
	def occupation(self):
		return self._occupation

	@occupation.setter
	def occupation(self, value):
		self._occupation = value
		#self.edificio.aule.sort(reverse=True)
		#print('Edificio ' + str(self.edificio) + ' riordinato')

all_buildings = {}
class Edificio:
	'Crea un nuovo edificio dati un nome e una tupla (lat, long)'

	def __init__(self, nome: str, latitudine: float, longitudine: float, campus: str, aule=[]):
		all_buildings[nome] = self
		self.campus = campus
		self.nome = nome  # Stringa
		self.posizione = (latitudine, longitudine)  # Tupla lat-lon
		self.aule = []  # Lista di oggetti Aula. Automaticamente riordinata quando ne viene aggiunta una

	def aggiungi_aula(self, nome, disegno, prese, ethernet, informatizzata, campus):
		nuova_aula = Aula(nome, self, disegno, prese, ethernet, informatizzata, campus)
		self.aule.append(nuova_aula)
		self.aule.sort(reverse=True)
	
	def distance_from(self, location):
		return geodist.distance(location, self.posizione)

	def __str__(self):
		return self.nome

def sorted_buildings(location, buildings=all_buildings):
	"""Returns list of Edificio objects, closest first.
	Parameters: location, list/dict of Edificio objects (optional)"""
	def distance(location, edificio):
		pos_edificio = edificio.posizione
		return geodist.distance(location, pos_edificio)
	if isinstance(buildings, dict): buildings = buildings.values() # Allow passing a list of buildings as parameter
	list_with_distances = [(building, distance(location, building)) for building in buildings]
	list_with_distances.sort(key=lambda x: x[1])
	return [pair[0] for pair in list_with_distances]  #Returns a sorted list of Edificio objects

def best_rooms(location, dtime, rooms=all_rooms.values(), limit=-1):
	list_with_evaluation = [(room, room.evaluate(location, dtime)) for room in rooms]
	list_with_evaluation.sort(key=lambda x: x[1], reverse=True)
	return [pair[0] for pair in list_with_evaluation[:limit]]  #Returns a sorted list of Edificio objects

#%% Loads buildings' data
with open('parsers\\buildings.csv', 'r') as csvfile:
	for line in csv.reader(csvfile):
		campus, name, lat, lon = line
		lat = float(lat.replace(',', '.'))
		lon = float(lon.replace(',', '.'))
		all_buildings[name] = Edificio(name, lat, lon, campus)
del csvfile, line, name, lat, lon, campus

#%% Loads rooms' data
with open('parsers\\rooms.csv', 'r') as csvfile:
	for row in csv.DictReader(csvfile):
		campus, edificio, nome, prese, tipologia, ethernet, categoria = row.values()
		prese = bool(prese)
		ethernet = bool(ethernet)
		if tipologia == 'DISEGNO':
			disegno = True
			informatizzata = False
		elif tipologia == 'INFORMATIZZATA':
			disegno = False
			informatizzata = True
		else:
			disegno = False
			informatizzata = False
		all_buildings[edificio].aggiungi_aula(nome, disegno, prese, ethernet, informatizzata, campus)
del csvfile, row, campus, edificio, nome, prese, tipologia, ethernet, categoria, disegno, informatizzata

if __name__ == "__main__":  # Avoid execution if imported
	__piazza = (45.4780440, 9.2256319)
	__lambrate = (45.4850472, 9.2372908)
	from parsers.parse_table_new_format import parse_file
	with open('occupazioni.html', 'r') as htmlfile:
		results = parse_file(htmlfile)
		for nomeaula, occupation in results.items():
			try: all_rooms[nomeaula].occupation = occupation
			except KeyError: continue

	#%% Test area
	time = datetime.datetime(2019, 3, 18, hour=15, minute = 15)
	for i in best_rooms(__piazza, time, limit=10):
		if i.occupation is None: break
		time_free = i.occupation.evaluate(time)
		print(i, f'{time_free//60} h {time_free%60} min')
	''
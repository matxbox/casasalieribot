from geopy import distance as geodist
import csv


all_rooms={}

class Aula:
	'Crea una nuova aula con le sue proprietà. Richiede un oggetto Edificio in input'

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
		self._occupation = []
		self.weights = {
						'occupation': 10,
						'distance': 10,
						'prese': 10,
						'disegno': 10,
						'ethernet': 10,
						'informatizzata': 10,
						}


	def __cmp_distance(self, other):
		if self.userlocation is None:
			return 0
		else:
			selfdist = geodist.distance(self.edificio.posizione, self.userlocation).km
			otherdist = geodist.distance(other.edificio.posizione, self.userlocation).km
			if selfdist < otherdist:
				return 1
			elif selfdist > otherdist:
				return -1
			else: return 0

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
		distanza = self.weights['distance'] * self.__cmp_distance(other)
		ethernet = self.weights['ethernet'] * self.__cmp_ethernet(other)
		informatizzata = self.weights['informatizzata'] * self.__cmp_informatizzata(other)
		# Occupazione
		total = prese + disegno + distanza + ethernet + informatizzata
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
		self.edificio.aule.sort(reverse=True)
		print('Edificio ' + str(self.edificio) + ' riordinato')

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

def best_rooms(location):  #TODO: change criteria, this is useless
	"""Returns buildingname:[room, ] dict based on location.
	"""
	edifici_migliori = sorted_buildings(location)[:2]
	best_rooms={}
	for edificio in edifici_migliori:
		best_rooms[edificio] = edificio.aule[:6]
	return best_rooms

#%% Loads buildings' data
with open('buildings.csv', 'r') as csvfile:
	for line in csv.reader(csvfile):
		campus, name, lat, lon = line
		lat = float(lat.replace(',', '.'))
		lon = float(lon.replace(',', '.'))
		all_buildings[name] = Edificio(name, lat, lon, campus)
del csvfile, line, name, lat, lon, campus

#%% Loads rooms' data
with open('rooms.csv', 'r') as csvfile:
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

''' OLD AULE CSV
with open('aule.csv', 'r') as csvfile:
	for line in csv.reader(csvfile):
		building, name, draw, plug = line
		draw = bool(draw)
		plug = bool(plug)
		all_buildings[building].aggiungi_aula(name, draw, plug)
del csvfile, line, building, name, plug, draw

for aula in aule.keys():
	all_rooms[aula] = occupation[aula]
# Considero 'occupation' come un dizionario con chiavi i nomi delle aule e valori le liste di eventi
'''

if __name__ == "__main__":  # Avoid execution if imported
	__piazza = (45.4780440, 9.2256319)
	__lambrate = (45.4850472, 9.2372908)
	#%% Check buildings sorting
	print('Dalla __piazza: ')
	print([str(i) for i in sorted_buildings(__piazza)])
	print('Dalla stazione: ')
	print([str(i) for i in sorted_buildings(__lambrate)])
	#%% Check combined buildings+rooms sorting
	print([[str(j) for j in i.aule] for i in best_rooms(__piazza)])
	print([[str(j) for j in i.aule] for i in best_rooms(__lambrate)])
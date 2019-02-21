from geopy import distance as geodist
import csv

all_rooms = {}
class Aula:
	'Crea una nuova aula con le sue proprietà. Richiede un oggetto Edificio in input'

	def __init__(self, nome, edificio, disegno, prese):
		all_rooms[nome] = self
		self.nome = nome
		self.edificio = edificio
		self.disegno = disegno
		self.prese = prese
		self._occupation = []

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

	def __cmp(self, other):
		disegno = self.__cmp_disegno(other)
		prese = self.__cmp_prese(other)
		total = 1 * prese + 1.5 * disegno
		return total

	def __str__(self):
		return self.nome

	def __eq__(self, other):
		return self.__cmp_prese(other) == 0

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
	
	def aggiungi_aula(self, nome, disegno, prese):
		nuova_aula = Aula(nome, self, disegno, prese)
		self.aule.append(nuova_aula)
		self.aule.sort(reverse=True)

	def __init__(self, nome, posizione, aule=[]):
		all_buildings[nome] = self
		self.nome = nome  # Stringa
		self.posizione = posizione  # Tupla lat-lon
		self.aule = []  # Lista di oggetti Aula. Automaticamente riordinata quando ne viene aggiunta una

	def __str__(self):
		return self.nome

def get_sorted_buildings(location, buildings=all_buildings):
	def distance(location, edificio):
		pos_edificio = edificio.posizione
		return geodist.distance(location, pos_edificio)
	if isinstance(buildings, dict): buildings = buildings.values() # Allow passing a list instead of a dict
	list_with_distances = [(building, distance(location, building)) for building in buildings]
	list_with_distances.sort(key=lambda x: x[1])
	return [pair[0] for pair in list_with_distances]

def print_best_rooms(location):
	edifici_migliori = get_sorted_buildings(location)[:2]
	for edificio in edifici_migliori:
		print(edificio, [str(aula) for aula in edificio.aule[:6]], sep=': ')

#%% Loads buildings' data
with open('edifici.csv', 'r') as csvfile:
	for line in csv.reader(csvfile, delimiter=';'):
		name, lat, lon = line
		lat = float(lat.replace(',', '.'))
		lon = float(lon.replace(',', '.'))
		all_buildings[name] = Edificio(name, (lat, lon))
del csvfile, line, name, lat, lon

#%% Load rooms' data
with open('aule.csv', 'r') as csvfile:
	for line in csv.reader(csvfile, delimiter=';'):
		building, name, draw, plug = line
		draw = bool(draw)
		plug = bool(plug)
		all_buildings[building].aggiungi_aula(name, draw, plug)
del csvfile, line, building, name, plug, draw

#%%
"""
for aula in aule.keys():
	all_rooms[aula] = occupation[aula]
# Considero 'occupation' come un dizionario con chiavi i nomi delle aule e valori le liste di eventi
"""

piazza = (45.4780440, 9.2256319)
lambrate = (45.4850472, 9.2372908)
#%% Check buildings sorting
print('Dalla piazza: ')
print([str(i) for i in get_sorted_buildings(piazza)])
print('Dalla stazione: ')
print([str(i) for i in get_sorted_buildings(lambrate)])
#%% Check combined buildings+rooms sorting
print_best_rooms(piazza)
print_best_rooms(lambrate)
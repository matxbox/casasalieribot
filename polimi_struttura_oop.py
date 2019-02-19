from geopy import distance as geodist


class Aule:
	tutte = {}

	def __init__(self, nome, edificio, disegno, prese):
		self.tutte[nome] = self
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


class Edificio:
	tutti = []

	def aggiungi_aula(self, nome, disegno, prese):
		nuova_aula = Aule(nome, self, disegno, prese)
		self.aule.append(nuova_aula)
		self.aule.sort(reverse=True)

	def __init__(self, nome, posizione, aule=[]):
		self.tutti.append(self)
		self.nome = nome  # Stringa
		self.posizione = posizione  # Tupla lat-lon
		self.aule = []  # Lista di oggetti Aula. Automaticamente riordinata quando ne viene aggiunta una

	def __str__(self):
		return self.nome


def get_sorted_buildings(posizione, edifici=Edificio.tutti):
	def distance(posizione, edificio):
		pos_edificio = edificio.posizione
		return geodist.distance(posizione, pos_edificio)

	list_with_distances = [(edificio, distance(posizione, edificio)) for edificio in edifici]
	list_with_distances.sort(key=lambda x: x[1])
	return [coppia[0] for coppia in list_with_distances]


Nave = Edificio('Nave', (45.4799597, 9.2299996))
Nord = Edificio('Nord', (45.4787942, 9.22750011))
Sud = Edificio('Sud', (45.4773985, 9.2275527))
L26 = Edificio('L26', (45.4759806, 9.2349167))

Nave.aggiungi_aula('B.2.1', False, False)
Nave.aggiungi_aula('B.2.2', True, False)
Nave.aggiungi_aula('B.2.3', True, False)
Nave.aggiungi_aula('B.2.4', False, False)
Nave.aggiungi_aula('B.4.1', True, False)
Nave.aggiungi_aula('B.4.2', False, False)
Nave.aggiungi_aula('B.4.3', True, True)
Nave.aggiungi_aula('B.4.4', True, False)

Nord.aggiungi_aula('N.2.1', True, False)
Nord.aggiungi_aula('N.2.2', True, False)
Nord.aggiungi_aula('N.2.3', True, False)
Nord.aggiungi_aula('N.2.4', True, True)
Nord.aggiungi_aula('N.1.6', False, False)

Sud.aggiungi_aula('S.1.1', True, False)
Sud.aggiungi_aula('S.1.2', False, True)
Sud.aggiungi_aula('S.1.3', False, True)
Sud.aggiungi_aula('S.1.4', False, True)
Sud.aggiungi_aula('S.1.5', False, True)
Sud.aggiungi_aula('S.1.6', False, True)
Sud.aggiungi_aula('S.1.7', True, True)
Sud.aggiungi_aula('S.1.8', True, True)
Sud.aggiungi_aula('S.1.9', True, True)

L26.aggiungi_aula('L26.01', False, False)
L26.aggiungi_aula('L26.02', False, False)
L26.aggiungi_aula('L26.03', False, False)
L26.aggiungi_aula('L26.04', False, True)
L26.aggiungi_aula('L26.11', False, False)
L26.aggiungi_aula('L26.12', False, False)
L26.aggiungi_aula('L26.13', True, True)
L26.aggiungi_aula('L26.14', True, True)
L26.aggiungi_aula('L26.15', False, False)
L26.aggiungi_aula('L26.16', False, False)

"""
for aula in Aule.tutte.keys():
	Aule.tutte[aula] = occupation[aula]
# Considero 'occupation' come un dizionario con chiavi i nomi delle aule e valori le liste di eventi
"""

# Aule.tutte['N.2.4'].occupation = ['ciao', 'mamma']         Esempio di assegnazione dell'occupazione
piazza = (45.4780440, 9.2256319)
lambrate = (45.4850472, 9.2372908)

print('Dalla piazza: ')
print([str(i) for i in get_sorted_buildings(piazza)])
print('Dalla stazione: ')
print([str(i) for i in get_sorted_buildings(lambrate)])


def print_best_rooms(location):
	edifici_migliori = get_sorted_buildings(location)[:2]
	for edificio in edifici_migliori:
		print(edificio, [str(aula) for aula in edificio.aule[:6]], sep=': ')


print_best_rooms(piazza)
print_best_rooms(lambrate)

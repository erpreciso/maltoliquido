# -*- coding: utf-8 -*-
from google.appengine.ext import ndb

class Caratteristica(ndb.Model):
	nome = ndb.StringProperty()
	ascii = ndb.StringProperty()
	data = ndb.StringProperty()
	autore = ndb.StringProperty()
	# stato (da rivedere, approfondire, correggere)

class Immagine(ndb.Model):
	blob = ndb.BlobKeyProperty()
	descrizione = ndb.StringProperty()
	data = ndb.StringProperty()
	autore = ndb.StringProperty()
	# tipo immagine


class Birra(ndb.Model):
	data_inserimento = ndb.StringProperty()
	autore_inserimento = ndb.StringProperty()

class Nome(Caratteristica):
	pass
class Produttore(Caratteristica):
	pass
class Stile(Caratteristica):
	pass
class Sottostile(Caratteristica):
	pass
class Nazione(Caratteristica):
	pass
class GradoAlcolico(Caratteristica):
	pass
class Marchio(Caratteristica):
	pass
class Colore(Caratteristica):
	pass
class Fermentazione(Caratteristica):
	pass
class TemperaturaDiServizio(Caratteristica):
	pass
class Schiuma(Caratteristica):
	pass
class Gusto(Caratteristica):
	pass
class FormatoDiVendita(Caratteristica):
	pass
class Bicchiere(Caratteristica):
	pass
class Fonte(Caratteristica):
	pass
class Link(Caratteristica):
	pass
class Status(Caratteristica):
	pass

class ImmagineBirra(Immagine):
	pass


class Commento(ndb.Model):
	testo = ndb.TextProperty()
	data = ndb.StringProperty()

class Dove(Caratteristica):
	pass
class Quando(Caratteristica):
	pass

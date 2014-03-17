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
    
class ImmagineBirra(Immagine):
	pass
class Fonte(Caratteristica):
    pass
class Nome(Caratteristica):
    pass
class Produttore(Caratteristica):
    pass
class GradoAlcolico(Caratteristica):
    pass
class Nazione(Caratteristica):
    pass
class Tipo(Caratteristica):
    pass
class Birra(ndb.Model):
	data_inserimento = ndb.StringProperty()
	autore_inserimento = ndb.StringProperty()

class Commento(ndb.Model):
	testo = ndb.TextProperty()
	data = ndb.StringProperty()

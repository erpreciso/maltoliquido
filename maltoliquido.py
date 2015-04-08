# coding: utf-8
# copyright Stefano Merlo
# [maltoliquido] website

import jinja2, webapp2
import json, os, csv, StringIO, time, logging, cgi
from google.appengine.ext import ndb, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images, memcache

from oggetti import *
from mie_funzioni import *

TOPS = 10

# funzioni

def dati_json():
	dati_json = memcache.get("dati_json")
	if dati_json == None:
		dati_json = json.loads(open("liste/liste.json").read())
		memcache.add("dati_json", dati_json)
	return dati_json

def url_immagine(blob, dimensione=None):
	"""restituisce url dell'immagine della dimensione specificata, numero o 'max'"""
	if dimensione == 'max':
		dimensione_pixel = 1600
	else:
		dimensione_pixel = dimensione
	if blob:
		return images.get_serving_url(blob, size=dimensione_pixel)
	return None

def estrai_commenti():
	commenti = memcache.get("lista_commenti")
	if commenti is not None:
		return commenti
	else:
		q = Commento.query().order(-Commento.data)
		if q.get():
			commenti = []
			for c in q:
				commenti.append(c)
			if not memcache.add("lista_commenti", commenti):
				raise Exception("Memcache set failure.")
			return commenti
		memcache.add("lista_commenti", "no comments")
		return None

def aggiungi_commento_al_datastore(commento):
	inser = Commento()
	inser.testo = commento
	inser.data = questo_istante()
	if inser.testo != "":
		inser.put()
		memcache.delete("lista_commenti")

def estrai_acquisti(nome_birra):
	json_data = dati_json()
	birre = memcache.get("birre_nome_%s" % nome_birra)
	if birre == None:
		q = Nome.query(Nome.ascii == valore)
		birre = [Nome.query(Nome.ascii == valore).get().key.parent().get()]
		memcache.add("birre_nome_%s" % valore, birre)
	res = []
	if birre == None:
		return None
	for birra in birre:
		voce = {}
		for attributo in json_data["attributi_acquisto"]:
			if attributo["famiglia"] == "Caratteristica":
				t = estrai_valori_da_classe(attributo["classe"], birra)
				if t != None and t != "":
					voce[attributo["ascii"]] = t
		if voce:
			res.append(voce)
	return res

def estrai_valori_da_classe(classe, genitore):
	mkey = classe + str(genitore.key.urlsafe())
	res = memcache.get(mkey)
	if res is not None:
		return res
	else:
		res = []
		q = globals()[classe].query(ancestor = genitore.key).order(-(globals()[classe].data))
		if q.get():
			for p in q:
				res.append([p.nome, p.ascii])
			memcache.add(mkey, res)
			return res
		else:
			memcache.add(mkey, "")
			return None

def estrai_valore_da_classe(classe, genitore, criterio, valore = None):
	"""dato il genitore, estraggo l'ultimo valore della classe specificata"""
	if valore:
		mkey = classe + criterio + valore + str(genitore.key.urlsafe())
	else:
		mkey = classe + criterio + str(genitore.key.urlsafe())
	res = memcache.get(mkey)
	if res is not None:
		return res
	else:
		if criterio == "ultimo":
			q = globals()[classe].query(ancestor = genitore.key).order(-(globals()[classe].data))
		elif criterio == "data":
			q = globals()[classe].query(ancestor = genitore.key).filter(globals()[classe].data == valore)
		else:
			raise Exception("criterio ricerca valore non definito")
		if q.get():
			res = [q.get().nome, q.get().ascii]
			memcache.add(mkey, res)
			return res
		else:
			memcache.add(mkey, "")
			return None
				
def estrai_birre(
			criterio = None,
			valore = "",
		):
	def estrai_lista_birre(criterio, valore, json_data):
		birre = None
		if criterio == "ultime" or criterio == None:
			birre = memcache.get("birre_ultime_%s" % str(TOPS))
			if birre == None:
				birre = Birra.query().order(-Birra.data_inserimento).fetch(TOPS)
				memcache.add("birre_ultime_%s" % str(TOPS), birre)
		elif criterio == "tutte":
			birre = memcache.get("birre_tutte")
			if birre == None:
				q = Birra.query().order(-Birra.data_inserimento)
				birre = [t for t in q]
				memcache.add("birre_tutte", birre)
		elif criterio == "nome" or criterio == "cronologia":
			birre = memcache.get("birre_nome_%s" % valore)
			if birre == None:
				q = Nome.query(Nome.ascii == valore)
				birre = [Nome.query(Nome.ascii == valore).get().key.parent().get()]
				memcache.add("birre_nome_%s" % valore, birre)
		elif criterio == "autore":
			birre = Birra.query(Birra.autore_inserimento == valore).fetch(TOPS)
		else:
			birre = memcache.get("birre_%s_%s_%s" % (criterio, valore, str(TOPS)))
			if birre == None:
				oggetto = None
				for attributo in json_data["attributi_birra"]:
					if criterio == attributo["ascii"]:
						oggetto = globals()[attributo["classe"]]
				if oggetto:
					q = oggetto.query(oggetto.ascii == valore)
					if q.get():
						birre = []
						for birra in q:
							n = birra.key.parent().get()
							if n not in birre:
								birre.append(n)
					memcache.add("birre_%s_%s_%s" % (criterio, valore, str(TOPS)), birre)
		return birre
	def estrai_blob_immagine_birra(genitore, criterio, valore = None):
		mkey = "immagine_" + criterio + str(genitore)
		res = memcache.get(mkey)
		if res is not None:
			return res
		else:
			if criterio == "ultimo":
				q = ImmagineBirra.query(ancestor = genitore).order(-ImmagineBirra.data)
			elif criterio == "data":
				q = ImmagineBirra.query(ancestor = genitore).filter(ImmagineBirra.data == valore)
			else:
				raise Exception("criterio ricerca immagine non definito")
			img = q.get()
			if img:
				memcache.add(mkey, img.blob)
				return img.blob
			else:
				memcache.add(mkey, "")
				return None
	def estrai_figli_da_birra(birra):
		"""ritorna lista figli --> oggetti Nome con ancestor birra"""
		if birra == None:
			return None
		figli = memcache.get("figli_birra_" + birra.key.urlsafe())
		if figli is not None:
			return figli
		figli = Nome.query(ancestor = birra.key)
		if figli.get():
			res = [figlio for figlio in figli]
		else:
			res = []
		memcache.add("figli_birra_" + birra.key.urlsafe(), res)
		return res
	
	json_data = dati_json()
	birre = estrai_lista_birre(criterio, valore, json_data)
	res = []
	if birre == None:
		return None
	for birra in birre:
		if criterio == "cronologia":
			figli = estrai_figli_da_birra(birra)
			if figli:
				for figlio in figli:
					img = estrai_blob_immagine_birra(birra.key, "data", figlio.data)
					if img and img != "":
						immaginebirra = url_immagine(img, 100)
					else:
						immaginebirra = None
					voce = {}
					voce["key"] = birra.key.urlsafe()
					voce["immaginebirra"] = immaginebirra
					for attributo in json_data["attributi_birra"]:
						if attributo["famiglia"] == "Caratteristica":
							t = estrai_valore_da_classe(attributo["classe"], birra, "data", figlio.data)
							if t != None and t != "":
								voce[attributo["ascii"]] = t
					res.append(voce)
		else:
			img = estrai_blob_immagine_birra(birra.key, "ultimo")
			if img and img != "":
				immaginebirra = url_immagine(img, 100)
			else:
				immaginebirra = None
			voce = {}
			voce["key"] = birra.key.urlsafe()
			voce["immaginebirra"] = immaginebirra
			voce["autore"] = birra.autore_inserimento
			for attributo in json_data["attributi_birra"]:
				if attributo["famiglia"] == "Caratteristica":
					t = estrai_valore_da_classe(attributo["classe"], birra, "ultimo")
					if t != None and t != "":
						voce[attributo["ascii"]] = t
			if voce:
				res.append(voce)
	return res

class GestoreHTML(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), 'pagine')
	jinja_env = jinja2.Environment(
		loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True,
		trim_blocks = True,
		)
	def scrivi(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def leggi(self,param):
		return self.request.get(param)
		
	def render_str(self, template, **params):
		return self.jinja_env.get_template(template).render(params)
		
	def render(self, template, **kw):
		self.scrivi(self.render_str(template, **kw))
	
	def servi_pagina(self, template, **kw):
		self.scrivi(self.render_str(template,**kw))

class PaginaContenuti(GestoreHTML):
	def post(self, criterio, valore):
		dove = self.request.get("pos")
		self.scrivi(dove)
		
	def get(self, criterio, valore):
		if criterio == "nome" and valore != "":
			contenuto = estrai_birre(
								criterio = criterio,
								valore = valore,
								)
			assert(len(contenuto) == 1)
			acquisti = estrai_acquisti(valore)
			self.scrivi_birra(contenuto[0], acquisti)
		elif criterio == "nome" and valore == "":
			self.scrivi_birra()
		else:
			self.scrivi_tops(criterio, valore)

	def scrivi_tops(self, criterio, valore = None):
		birre = estrai_birre(
					criterio = criterio,
					valore = valore,
					)
		json_data = dati_json()
		self.servi_pagina("tops.html",
						links = [
							{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/struttura.css"},
							{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/tops.css"},
							],
						metas = [
							{"name": "description", "content": "maltoliquido", "httpequiv": ""},
							{"name": "", "content": "text/html; charset=utf-8", "httpequiv": "Content-Type"},
							],
						scripts = [
							{"src": "/statici/funzioni_js/jquery-1.10.1.min.js"},
							{"src": "/statici/funzioni_js/struttura.js"},
							],
						birre = birre,
						json_data = json_data,
						criterio = criterio,
						stats = memcache.get_stats(),
						)
	
	def scrivi_birra(self, birra = None, acquisti = None):
		json_data = dati_json()
		self.servi_pagina("birra.html",
						links = [
							{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/struttura.css"},
							{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/birra.css"},
							],
						metas = [
							{"name": "description", "content": "maltoliquido", "httpequiv": ""},
							{"name": "", "content": "text/html; charset=utf-8", "httpequiv": "Content-Type"},
							],
						scripts = [
							{"src": "/statici/funzioni_js/jquery-1.10.1.min.js"},
							{"src": "/statici/funzioni_js/birra.js"},
							{"src": "/statici/funzioni_js/struttura.js"},
							],
						birra = birra,
						acquisti = acquisti,
						json_data = json_data,
						upload_url = blobstore.create_upload_url('/upload'),
						stats = memcache.get_stats(),
						)

class PaginaChiSiamo(GestoreHTML):
	def get(self):
		in_costruzione = '<h1><a href="/" style="color:red;font-family:monospace;">Pagina in costruzione</a></h1>'
		self.scrivi(in_costruzione)

def cancella_memcache_dopo_caricamento():
	#json_data = dati_json()
	#memcache.delete("birre_ultime_" + str(TOPS))
	#memcache.delete("birre_tutte")
	#for attributo in json_data["attributi_birra"]:
		#memcache.delete("birre_" + attributo["classe"] + "_" + str(TOPS))
	memcache.flush_all()

def cancella_memcache_singola_birra(birra):
	#json_data = dati_json()
	#for attributo in json_data["attributi_birra"]:
		#mkey = attributo["classe"] + str(birra.urlsafe())
		#memcache.delete(mkey)
	#for attributo in json_data["attributi_acquisto"]:
		#mkey = attributo["classe"] + str(birra.urlsafe())
		#memcache.delete(mkey)
	#memcache.delete("immagine_ultimo" + str(birra))
	#memcache.delete("immagine_data" + str(birra))
	memcache.flush_all()

def carica_inserimento(valori, attributi):
	json_data = dati_json()
	cancella_memcache_dopo_caricamento()
	adesso = valori["adesso"]
	autore = valori["autore"]
	if "key" in valori.keys():
		birra = ndb.Key(urlsafe = valori["key"])
		cancella_memcache_singola_birra(birra)
	else:
		birra = Birra(
			data_inserimento = adesso,
			autore_inserimento = autore,
			).put()
	for chiave in valori.keys():
		stringa = valori[chiave]
		if stringa:
			oggetto, immagine = None, None
			for attributo in json_data[attributi]:
				if chiave == "immaginebirra":
					immagine = ImmagineBirra(parent = birra)
				elif chiave == attributo["ascii"]:
					oggetto = globals()[attributo["classe"]](parent = birra)
			if oggetto:
				oggetto.nome = stringa
				oggetto.ascii = converti_unicode_in_ascii(stringa)
				oggetto.data = adesso
				oggetto.autore = autore
				oggetto.put()
			if immagine:
				immagine.blob = stringa
				immagine.data = adesso
				immagine.autore = autore
				immagine.put()

class CaricaInserimento(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		adesso = questo_istante()
		autore = self.request.get("autore")
		form = self.request.get("nome_form")
		argomenti = self.request.arguments()
		valori = {"adesso": adesso, "autore": autore}
		for argomento in argomenti:
			valori[argomento] = self.request.get(argomento)
		if form == "form_birra":
			valori["immaginebirra"] = self.get_uploads("immaginebirra")[0].key()
			carica_inserimento(valori, "attributi_birra")
		elif form == "form_acquisto":
			carica_inserimento(valori, "attributi_acquisto")
		time.sleep(1)
		self.redirect("/ultime")	

class PaginaCommenti(GestoreHTML):
	def get(self):
		self.scrivi_commenti()

	def post(self):
		commento = self.request.get("commento")
		aggiungi_commento_al_datastore(commento)
		time.sleep(1)
		self.redirect("/commenti")
			
	def scrivi_commenti(self):
		commenti = estrai_commenti()
		if commenti == "no comments":
			commenti = None
		self.servi_pagina("commenti.html",
				links = [
					{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/struttura.css"},
					{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/commenti.css"},
					],
				metas = [
					{"name": "description", "content": "maltoliquido", "httpequiv": ""},
					{"name": "", "content": "text/html; charset=utf-8", "httpequiv": "Content-Type"},
					],
				scripts = [
					{"src": "/statici/funzioni_js/jquery-1.10.1.min.js"},
					{"src": "/statici/funzioni_js/struttura.js"},
					],
				commenti = commenti,
				stats = memcache.get_stats(),
				)

class PaginaMappa(GestoreHTML):
	def scrivi_mappa(self):
		self.servi_pagina("mappa.html",
					links = [
						{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/struttura.css"},
						{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/mappa.css"},
						],
					metas = [
						{"name": "description", "content": "maltoliquido", "httpequiv": ""},
						{"name": "viewport", "content": "initial-scale=1.0, user-scalable=no", "httpequiv": ""},
						],
					scripts = [
						{"src": "/statici/funzioni_js/jquery-1.10.1.min.js"},
						{"src": "https://maps.googleapis.com/maps/api/js?sensor=false"},
						{"src": "/statici/funzioni_js/mappa.js"},
						{"src": "/statici/funzioni_js/struttura.js"},
						],
					)
						
	def get(self):
		self.scrivi_mappa()
		
class SingolaImmagine(GestoreHTML):
	def scrivi_singola_immagine(self,immagine,chiave):
		self.render("singola_immagine.html",
					immagine = immagine,
					chiave = chiave,
					blob = url_immagine(immagine, 500),
					)
		
	def get(self,chiave):
		immagine = revision = ndb.Key(urlsafe=chiave).get()
		self.scrivi_singola_immagine(immagine,chiave)
		
			
	def post(self,chiave):
		db.delete(chiave)
		time.sleep(1)
		self.redirect("/")

class PaginaImportaCSV(GestoreHTML):
	def scrivi_importacsv(self):
		self.servi_pagina("importacsv.html",
					links = [
						{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/struttura.css"},
						{"type": "text/css", "rel": "stylesheet", "href": "/statici/stili/importacsv.css"},
						],
					metas = [
						{"name": "description", "content": "maltoliquido", "httpequiv": ""},
						],
					scripts = [
						{"src": "/statici/funzioni_js/jquery-1.10.1.min.js"},
						{"src": "/statici/funzioni_js/struttura.js"},
						],
					upload_url = blobstore.create_upload_url('/upload_csv'),
					)
	
	def get(self):
		self.scrivi_importacsv()

class PaginaCaricaCSV(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		cancella_memcache_dopo_caricamento()
		upload_files = self.get_uploads("csv_birre")
		blob_info = upload_files[0]
		blob_reader = blobstore.BlobReader(blob_info.key())
		csv_data = importa_csv(StringIO.StringIO(blob_reader.read()))
		for elemento in csv_data:
			autore = elemento["autore"]
			adesso = questo_istante()
			json_data = dati_json()
			birra = Birra(
				data_inserimento = adesso,
				autore_inserimento = autore,
				).put()
			for argomento in elemento.keys():
				oggetto = None
				for attributo in json_data["attributi_birra"]:
					if argomento == attributo["ascii"] and elemento[argomento]:
						oggetto = globals()[attributo["classe"]](parent = birra)
						oggetto.nome = elemento[argomento]
						oggetto.ascii = converti_unicode_in_ascii(elemento[argomento])
						oggetto.data = adesso
						oggetto.autore = autore
						oggetto.put()
			time.sleep(1)
		self.redirect("/")

class PaginaEsportaCSV(GestoreHTML):
	def get(self):
		self.scrivi([attributo["ascii"] for attributo in dati_json()["attributi_birra"]])
	

def importa_csv(file_type_object):
	class UnicodeCsvReader(object):
	    def __init__(self, f, encoding="utf-8", **kwargs):
	        self.csv_reader = csv.reader(f, **kwargs)
	        self.encoding = encoding
	    def __iter__(self):
	        return self
	    def next(self):
	        # read and split the csv row into fields
	        row = self.csv_reader.next() 
	        # now decode
	        return [unicode(cell, self.encoding) for cell in row]
	    @property
	    def line_num(self):
	        return self.csv_reader.line_num
	class UnicodeDictReader(csv.DictReader):
	    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
	        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
	        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)
	# questa riga sotto usa il modulo esterno unicodecsv
	# da riportare anche negli import
	#csv_dict = unicodecsv.DictReader(file_type_object)
	
	# questa qui sotto invece le classi qui sopra
	csv_dict = UnicodeDictReader(file_type_object)
	
	res = []
	for row in csv_dict:
		res.append(row)
	return res
		
class CancellaDatastore(GestoreHTML):
	def get(self):
		json_data = dati_json()
		for attributo in json_data["attributi_birra"]:
			oggetto = globals()[attributo["classe"]]()
			q = oggetto.query()
			if q.get():
				for t in q:
					t.key.delete()
		q = Birra.query()
		for t in q:
			t.key.delete()
		self.redirect("/")
        
app = webapp2.WSGIApplication([
								("/visualizza/' + r'((?:[a-zA-Z0-9_-]+)*)", SingolaImmagine),
								("/chisiamo", PaginaChiSiamo),
								("/importacsv", PaginaImportaCSV),
								("/esportacsv", PaginaEsportaCSV),
								("/mappa", PaginaMappa),
								("/commenti", PaginaCommenti),
								("/cancella", CancellaDatastore),
								("/upload_csv", PaginaCaricaCSV),
								("/upload", CaricaInserimento),
								(r"/([a-z]+)*/*([0-9a-zA-Z+#]*)", PaginaContenuti),
								], debug= True)


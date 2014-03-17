# coding: utf-8
# copyright Stefano Merlo
# [maltoliquido] website

import webapp2
import jinja2
import random
import string
import json
import os
import unicodedata
from google.appengine.ext import ndb, blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from time import localtime, strftime, sleep
from oggetti import *

# funzioni

def generatore_id_casuale(
			size = 6,
			chars = string.ascii_uppercase + string.digits
			):
	return ''.join(random.choice(chars) for x in range(size))

def converti_unicode_in_ascii(testo):
	res = ''
	nkfd_form = unicodedata.normalize('NFKD', unicode(testo))
	q = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
	res = ''.join(e for e in q if e.isalnum())
	return res

def questo_istante():
	"""restituisce data e ora in questo istante, formato 'yyyy-mm-dd HH-MM-SS'"""
	return strftime("%Y-%m-%d %H:%M:%S", localtime())

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
	q = Commento.query().order(-Commento.data)
	if q.get():
		res = []
		for c in q:
			res.append(c)
		return res
	return None

def estrai_cronologia(ascii_birra):
	json_data = json.loads(open("liste/liste.json").read())
	birra = Nome.query(Nome.ascii == ascii_birra).get().key.parent().get()
	figli = Nome.query(ancestor = birra.key)
	if figli.get():
		res = []
		for figlio in figli:
			data = figlio.data
			img = ImmagineBirra.query(ancestor = birra.key).filter(ImmagineBirra.data == data).get()
			if img:
				immagineprincipale = url_immagine(ImmagineBirra.query(ancestor = birra.key).filter(ImmagineBirra.data == data).get().blob, 100)
			else:
				immagineprincipale = None
			voce = {}
			voce["key"] = birra.key.urlsafe()
			voce["immagineprincipale"] = immagineprincipale
			for attributo in json_data["attributi_birra"]:
				if attributo["famiglia"] == "caratteristica":
					q = globals()[attributo["classe"]].query(ancestor = birra.key).filter(globals()[attributo["classe"]].data == data).get()
					voce[attributo["ascii"]] = [q.nome, q.ascii]
			res.append(voce)
		return res
	return None
		

	
	

def estrai_birre(
			quanti = 1,
			criterio = None,
			valore = "",
		):
	birre = None
	json_data = json.loads(open("liste/liste.json").read())
	if criterio == "ultime" or criterio == None:
		birre = Birra.query().order(-Birra.data_inserimento).fetch(quanti)
	if criterio == "tutte":
		q = Birra.query().order(-Birra.data_inserimento)
		birre = [t for t in q]
	elif criterio == "nome":
		assert quanti == 1
		birre = [Nome.query(Nome.ascii == valore).get().key.parent().get()]
	elif criterio == "autore":
		birre = Birra.query().order(-Birra.autore_inserimento).fetch(quanti)
	else:
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
	res = []
	if birre == None:
		return None
	for birra in birre:
		img = ImmagineBirra.query(ancestor = birra.key).get()
		if img:
			immagineprincipale = url_immagine(ImmagineBirra.query(ancestor = birra.key).order(-ImmagineBirra.data).get().blob, 100)
		else:
			immagineprincipale = None
		voce = {}
		voce["key"] = birra.key.urlsafe()
		voce["immagineprincipale"] = immagineprincipale
		for attributo in json_data["attributi_birra"]:
			if attributo["famiglia"] == "caratteristica":
				q = globals()[attributo["classe"]].query(ancestor = birra.key).order(-(globals()[attributo["classe"]].data)).get()
				voce[attributo["ascii"]] = [q.nome, q.ascii]
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
	def get(self, criterio, valore):
		if criterio == "nome" and valore != "":
			contenuto = estrai_birre(
								criterio = criterio,
								quanti = 1,
								valore = valore,
								)
			assert(len(contenuto) == 1)
			self.scrivi_birra(contenuto[0])
		elif criterio == "nome" and valore == "":
			self.scrivi_birra()
		else:
			self.scrivi_tops(criterio, valore)

	def post(self, criterio, valore):
		argomenti = self.request.arguments()
		if "commento" in argomenti:
			commento = Commento()
			commento.testo = self.request.get("commento")
			commento.data = questo_istante()
			if commento.testo != "":
				commento.put()
			sleep(1)
			self.redirect("/commenti")

	def scrivi_tops(self, criterio, valore = None):
		if criterio == "cronologia":
			birre = estrai_cronologia(valore)
		else:
			birre = estrai_birre(
						criterio = criterio,
						quanti = 10,
						valore = valore,
						)
		json_data = json.loads(open("liste/liste.json").read())
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
							{"src": "/statici/funzioni_js/tops.js"},
							{"src": "/statici/funzioni_js/struttura.js"},
							],
						birre = birre,
						json_data = json_data,
						criterio = criterio,
						)
	
	def scrivi_birra(self, birra = None):
		json_data = json.loads(open("liste/liste.json").read())
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
						json_data = json_data,
						upload_url = blobstore.create_upload_url('/upload'),
						)

#class PaginaJsonPubblicazione(GestoreHTML):
	#def get(self, nome_pubblicazione):
		#pubb = estrai_pubblicazione(nome_pubblicazione)
		#outp = crea_json(pubb)
		#self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
		#self.scrivi(json.dumps(outp))

class PaginaChiSiamo(GestoreHTML):
	def get(self):
		in_costruzione = '<h1><a href="/" style="color:red;font-family:monospace;">Pagina in costruzione</a></h1>'
		self.scrivi(in_costruzione)

class CaricaInserimento(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		adesso = questo_istante()
		autore = self.request.get("autore")
		json_data = json.loads(open("liste/liste.json").read())
		argomenti = self.request.arguments()
		if autore == "carica":
			for k in range(len(json_data["birre_test"])):
				birra = Birra(data_inserimento = adesso, autore_inserimento = autore).put()
				for argomento in json_data["birre_test"][k]:
					oggetto, immagine = None, None
					for attributo in json_data["attributi_birra"]:
						if argomento == attributo["ascii"]:
							oggetto = globals()[attributo["classe"]](parent = birra)
					if oggetto:
						oggetto.nome = json_data["birre_test"][k][argomento]
						oggetto.ascii = converti_unicode_in_ascii(json_data["birre_test"][k][argomento])
						oggetto.data = adesso
						oggetto.autore = autore
						oggetto.put()
			self.redirect("/ultime")
			return
		argomenti = self.request.arguments()
		if "key" in argomenti:
			birra = ndb.Key(urlsafe=self.request.get("key"))
		else:
			birra = Birra(data_inserimento = adesso, autore_inserimento = autore).put()
		for argomento in argomenti:
			oggetto, immagine = None, None
			for attributo in json_data["attributi_birra"]:
				if argomento == "immagineprincipale":
					immagine = ImmagineBirra(parent = birra)
				elif argomento == attributo["ascii"]:
					oggetto = globals()[attributo["classe"]](parent = birra)
			if oggetto:
				oggetto.nome = self.request.get(argomento)
				oggetto.ascii = converti_unicode_in_ascii(self.request.get(argomento))
				oggetto.data = adesso
				oggetto.autore = autore
				oggetto.put()
			if immagine:
				immagine.blob = self.get_uploads(argomento)[0].key()
				immagine.data = adesso
				immagine.autore = autore
				immagine.put()
		sleep(1)
		self.redirect("/ultime")	

class PaginaCommenti(GestoreHTML):
	def get(self):
		self.scrivi_commenti()
		
	def scrivi_commenti(self):
		commenti = estrai_commenti()
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
		sleep(1)
		self.redirect("/")

app = webapp2.WSGIApplication([
								("/visualizza/' + r'((?:[a-zA-Z0-9_-]+)*)", SingolaImmagine),
								("/chisiamo", PaginaChiSiamo),
								("/mappa", PaginaMappa),
								("/commenti", PaginaCommenti),
								("/upload", CaricaInserimento),
								(r"/([a-z]+)*/*([0-9a-zA-Z+#]*)", PaginaContenuti),
								], debug= True)


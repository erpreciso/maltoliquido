# la mia libreria funzioni

import random, string, unicodedata, time

def hit(cosa = "hit"):
	raise Exception(cosa)
	
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
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

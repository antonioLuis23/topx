from django.apps import AppConfig
#import nltk
#import time
#import timeit
#etiq = None
class TopxConfig(AppConfig):
	name = 'topx'
	# def ready(self):
	# 	global etiq
	# 	inicio = timeit.default_timer()
	# 	etiqPadrao = nltk.DefaultTagger('N')  # Usando etiquetas default para os tokens nao reconhecidos
	# 	sentencas_treinadoras = nltk.corpus.mac_morpho.tagged_sents()[::]
	# 	print('entrou aki')
	# 	etiq = nltk.UnigramTagger(sentencas_treinadoras, backoff=etiqPadrao)
	# 	fim = timeit.default_timer()
	# 	print ('duracao: %f' % (fim - inicio))


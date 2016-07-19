from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import time
import timeit
from .models import Comentario, Produto, Tipo
from topx.forms import importanciaForm
from urllib.request import urlopen
from .topx import TopX
from .topxFuzzy import TopxFuzzy
import nltk
from topx.apps import etiq
#from topxcrawler.spiders import topx_spider
#etiq = Nones
# Create your views here.

def try_open_url(url):
	tries = 5
	while tries >= 0:
		try:
			return urlopen(url)
			
		except:
			if tries == 0:
				raise
			else:
				print(">>>>>>>>>>>>>>>erro ao abrir tentando de novo")
                    # Wait a few seconds before retrying and hope the problem goes away
				time.sleep(3) 
				tries -= 1
				continue

def descobreTipo(soup):
	
	details = soup.select(".product-details li")
	tipo = ""
	for detail in details:
		feat = detail.select('span.name')
			
		if(feat[0].get_text() == "Tipo"):
			tipo = detail.select('span.value')[0].get_text().lower()
			break
	t = Tipo.objects.filter(nome = tipo)	
	if len(t)>0:
		t = t[0]

	if not t:
		features = soup.select(".product-details li span.name")
		
		featuresString  = ''
		for feature in features:
			featuresString  +=feature.get_text().lower()+';'
		features = soup.select(".product-details h2.title")
		for feature in features:
			if feature.get_text() != 'Informações Básicas':
				featuresString  +=feature.get_text().lower()+';'
		t = Tipo(nome = tipo, caracteristicas = featuresString)
		t.save()
		return t
	else:
		return t


def index(request):
	global etiq
	if request.method == 'GET':
		inicio = timeit.default_timer()
		if not etiq:
			global etiq
			etiqPadrao = nltk.DefaultTagger('N')  # Usando etiquetas default para os tokens nao reconhecidos
			sentencas_treinadoras = nltk.corpus.mac_morpho.tagged_sents()[::]
			etiq = nltk.UnigramTagger(sentencas_treinadoras, backoff=etiqPadrao)
		fim = timeit.default_timer()
		print ('duracao: %f' % (fim - inicio))
		return render(request, 'topx/index.html')
	else:
		inicio = timeit.default_timer()
		url =  request.POST.get('url-comment')
		topx = int(request.POST.get('topx'))

		r = try_open_url(url)
		soup = BeautifulSoup(r, "lxml")
		tipoProd = descobreTipo(soup)	

		indexFinal = url.index('#')
		nomeProduto = url[26:indexFinal]
		nomeProd = nomeProduto.replace("-", " ")


		p = Produto.objects.filter(nome = nomeProduto)
		if len(p)>0:
			p =p[0]
		print('p:',p)
		if not p:
		
			p = tipoProd.produto_set.create(nome = nomeProduto)
			p.save()
			urlParcial = "http://www.buscape.com.br/avaliacoes/" + nomeProduto + "/?pagina="
			numeros = soup.select("ul.pages-list > li > a.item")
			maior = 0
			for numStr in numeros:
				try:
					num = int(numStr.get_text())
					if(num>maior):
						maior = num
				except ValueError:
					continue

			for i in range(1, maior+1):
				
				urlFinal = urlParcial + str(i)
				print('url:', urlFinal)
				r = try_open_url(urlFinal)
				soup = BeautifulSoup(r, "lxml")
				comentarios = soup.select(".review-content p")
				autores = soup.select(".review-meta__author") 
				#notas = soup.select(".rating-stars span:first-child")
				recomendacoes = soup.select(".review-meta__recommend")
				votos_positivos = soup.select(".pros.ico-label")
				votos_negativos = soup.select(".contras.ico-label")
				for index, coment in enumerate(comentarios):
					p.comentario_set.create(comentario = comentarios[index].get_text(), autor = autores[index].get_text(), 
						voto_positivo = votos_positivos[index].get_text(), voto_negativo = votos_negativos[index].get_text(), recomenda=recomendacoes[index].get_text())
			p.save()

			top = TopX()
			top.main(p.id, tipoProd.id, etiq)

		fim = timeit.default_timer()
		print ('duracao: %f' % (fim - inicio))
		p.save()
		print('p.pol_caracteristica:', p.pol_caracteristica)
		topComment = p.comentario_set.all().order_by('-importancia')[:topx]
		return render(request, 'topx/index.html',{'topComment':topComment,'nomeProduto':nomeProd,'url':url,'topx':topx})			
	#print(soup.select(".review-content p")[0].get_text())



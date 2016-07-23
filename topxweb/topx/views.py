from django.shortcuts import render
from bs4 import BeautifulSoup
import time
import timeit
from .models import Produto, Tipo
from urllib.request import urlopen
from .topx import TopX
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.common.by import By
import threading
from multiprocessing import Queue
#from topx.apps import etiq
#etiq = None
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
    t = Tipo.objects.filter(nome=tipo)
    if len(t) > 0:
        t = t[0]

    if not t:
        features = soup.select(".product-details li span.name")
        featuresString = ''
        for feature in features:
            featuresString += feature.get_text().lower()+';'
        features = soup.select(".product-details h2.title")
        for feature in features:
            if feature.get_text() != 'Informações Básicas':
                featuresString += feature.get_text().lower()+';'
        t = Tipo(nome=tipo, caracteristicas=featuresString)
        t.save()
        return t
    else:
        return t


def read_url(url, p, queue):
    print('url:', url)
    r = try_open_url(url)
    soup = BeautifulSoup(r, "lxml")
    comentarios = soup.select(".review-content p")
    autores = soup.select(".review-meta__author")
    #notas = soup.select(".rating-stars span:first-child")
    recomendacoes = soup.select(".review-meta__recommend")
    votos_positivos = soup.select(".pros.ico-label")
    votos_negativos = soup.select(".contras.ico-label")
    for index, coment in enumerate(comentarios):
        coment = p.comentario_set.all().filter(comentario=comentarios[index].get_text())
        if not coment:
            p.comentario_set.create(comentario=comentarios[index].get_text(), autor=autores[index].get_text(),
                voto_positivo=votos_positivos[index].get_text(), voto_negativo=votos_negativos[index].get_text(), recomenda=recomendacoes[index].get_text())


def getComentarios(url, topx, nomeProduto):

    r = try_open_url(url)
    soup = BeautifulSoup(r, "lxml")
    tipoProd = descobreTipo(soup)

    p = Produto.objects.filter(nome=nomeProduto)
    if len(p) > 0:
        p = p[0]
    print('p:', p)
    if not p:
        p = tipoProd.produto_set.create(nome=nomeProduto)
        p.save()
        urlParcial = "http://www.buscape.com.br/avaliacoes/" + nomeProduto + "/?pagina="
        numeros = soup.select("ul.pages-list > li > a.item")
        maior = 0
        for numStr in numeros:
            try:
                num = int(numStr.get_text())
                if(num > maior):
                    maior = num
            except ValueError:
                continue

        inicio = timeit.default_timer()
        urls_to_load = []
        for i in range(1, maior+1):
            urlFinal = urlParcial + str(i)
            urls_to_load.append(urlFinal)
        print('entrou?')
        result = Queue()

        threads = [threading.Thread(target=read_url, args=(url, p, result)) for url in urls_to_load]
        for t in threads:

            t.start()
        for t in threads:
            t.join()

        p.save()
        fim = timeit.default_timer()
        print ('duracao obtendo comentários: %f' % (fim - inicio))
        top = TopX()
        top.main(p.id, tipoProd.id)

    return p.comentario_set.all().order_by('-importancia')[:topx]


def descobreMarca(soup):
    details = soup.select(".product-details li")
    marca = ""
    for detail in details:
        feat = detail.select('span.name')
        if(feat[0].get_text() == "Marca"):
            marca = detail.select('span.value')[0].get_text().lower()
            break
    return marca


def procuraMarca(marca):
    #driver = webdriver.PhantomJS(executable_path='/Users/Antonio/node_modules/phantomjs/lib/phantom/bin/phantomjs')
    driver = webdriver.Firefox()
    marcaInfo = {}
    driver.get("http://www.reclameaqui.com.br/busca/?q="+marca)

    try:
        # we have to wait for the page to refresh, the last thing that seems to be updated is the title
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.business-name .ng-binding')))

        # You should see "cheese! - Google Search"
        # print(driver.page_source)
        soupBusca = BeautifulSoup(driver.page_source, "lxml")
        empresaUrl = soupBusca.select('.business-name .ng-binding')[0]['href']
        empresaUrlComp = 'http://www.reclameaqui.com.br'+empresaUrl
        marcaInfo['urlReclameAqui'] = empresaUrlComp
        driver.get(empresaUrlComp)

        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#n3-pie-arcs')))
            soupEmpresa = BeautifulSoup(driver.page_source, "lxml")

            reclamacoes = soupEmpresa.select('.all-complaints p')[0].get_text()
            marcaInfo['numReclamacoes'] = reclamacoes

            atendidas = soupEmpresa.select('.complaints-answered p')[0].get_text()
            marcaInfo['atendidas'] = atendidas

            naoAtendidas = soupEmpresa.select('.complaints-unanswered p')[0].get_text()
            marcaInfo['naoAtendidas'] = naoAtendidas

            nomeEmpresa = soupEmpresa.select('.business-name-site h1')[0].get_text()
            marcaInfo['nomeEmpresa'] = nomeEmpresa

            classificacaoEmpresa = soupEmpresa.select('.business-seal p')[0].get_text()
            marcaInfo['classificacaoEmpresa'] = classificacaoEmpresa

            siteEmpresa = 'http://'+soupEmpresa.select('.business-contact-info a')[0].get_text()
            marcaInfo['siteEmpresa'] = siteEmpresa

            tempoDeResposta = soupEmpresa.select('.reply-time .ng-binding')[0].get_text()
            marcaInfo['tempoDeResposta'] = tempoDeResposta

            notaConsumidor = soupEmpresa.select('.user-rating .ng-binding')[0].get_text()
            marcaInfo['notaConsumidor'] = notaConsumidor

            numAvaliacoes = soupEmpresa.select('.all-ratings .ng-binding')[0].get_text()
            marcaInfo['numAvaliacoes'] = numAvaliacoes

            porcentagens = soupEmpresa.select('.legend-value')

            marcaInfo['pctAtendidas'] = porcentagens[0].get_text()
            marcaInfo['voltaNegocio'] = porcentagens[1].get_text()
            marcaInfo['indiceSolucao'] = porcentagens[2].get_text()

            print('marcaInfo:', marcaInfo)
            return marcaInfo

        finally:
            driver.quit()

    finally:
        driver.quit()


def getInfoMarca(url):
    inicio = timeit.default_timer()
    r = try_open_url(url)
    soup = BeautifulSoup(r, "lxml")
    marca = descobreMarca(soup)
    print('marca:', marca)
    marcaInfo = procuraMarca(marca)
    fim = timeit.default_timer()
    print ('duracao obtendo informação da marca: %f' % (fim - inicio))
    return marcaInfo


def index(request):
#   global etiq
    if request.method == 'GET':
        # inicio = timeit.default_timer()
        # if not etiq:
        #   global etiq
        #   etiqPadrao = nltk.DefaultTagger('N')  # Usando etiquetas default para os tokens nao reconhecidos
        #   sentencas_treinadoras = nltk.corpus.mac_morpho.tagged_sents()[::]
        #   etiq = nltk.UnigramTagger(sentencas_treinadoras, backoff=etiqPadrao)
        # fim = timeit.default_timer()
        # print ('duracao: %f' % (fim - inicio))
        return render(request, 'topx/index.html')
    else:
        url = request.POST.get('url-comment')
        topx = int(request.POST.get('topx'))
        indexFinal = url.index('#')
        nomeProduto = url[26:indexFinal]
        nomeSemTraco = nomeProduto.replace("-", " ")
        inicio = timeit.default_timer()
        topComment = getComentarios(url, topx, nomeProduto)
        fim = timeit.default_timer()
        print ('duracao obtendo e classificando comentários: %f' % (fim - inicio))
        marcaInfo = getInfoMarca(url)
        print('marcaInfo', marcaInfo)
        return render(request, 'topx/index.html', {'topComment': topComment, 'nomeProduto': nomeSemTraco, 'url': url, 'topx': topx, 'marcaInfo':marcaInfo})

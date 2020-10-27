from django.shortcuts import render
from bs4 import BeautifulSoup
import time
import timeit
from .models import Produto, Tipo, Marca
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
        numComments = 0
        perfil = autores[index]
        if autores[index].has_attr('href'):
            urlPerfil = autores[index]['href']
            comecoNome = urlPerfil.find('-')
            fimNome = urlPerfil.rfind('.')
            nomeUser = urlPerfil[comecoNome+1:fimNome]
            comecoUid = urlPerfil.find('=')
            uid = urlPerfil[comecoUid+1:]
            urlCommentProd = 'http://www.buscape.com.br/opinioes-de-'+nomeUser+'-produtos?UsuarioID='+uid+'&tpopn=prd'
            htmlPerfil = try_open_url(urlCommentProd)
            soupPerfil = BeautifulSoup(htmlPerfil, "lxml")
            numComments = len(soupPerfil.select(".line h3"))
            print('type(numComments):', type(numComments), 'numComments:', numComments)
        coment = p.comentario_set.all().filter(comentario=comentarios[index].get_text())
        if not coment:
            if numComments == 0:
                numComments = 1
            p.comentario_set.create(comentario=comentarios[index].get_text(), autor=autores[index].get_text(),
                voto_positivo=votos_positivos[index].get_text(), voto_negativo=votos_negativos[index].get_text(), recomenda=recomendacoes[index].get_text(), reputacaoAutor=numComments)


def getComentarios(url, topx, nomeProduto):

    r = try_open_url(url)
    soup = BeautifulSoup(r, "lxml")
    tipoProd = descobreTipo(soup)

    p = Produto.objects.filter(nome=nomeProduto)
    if len(p) > 0:
        p = p[0]
    print('p:', p)
    if not p:
        precoProd = soup.select(".price .price__value")[0].get_text()
        print('precoProd:', precoProd, 'len(precoProd):',len(precoProd))
        url_image_prod = soup.select(".load-gallery img")[0]['src']

        r = try_open_url('https://www.youtube.com/results?hl=pt&search_query='+nomeProduto.replace('-','+')+'&gl=BR')
        soupYoutube = BeautifulSoup(r, "lxml")

        href_youtube = soupYoutube.select('.yt-lockup-title a')[0]['href']
        position = href_youtube.find('=')

        url_yt = 'https://www.youtube.com/embed/'+href_youtube[position+1:]
        print('url_youtube:', url_yt)

        p = tipoProd.produto_set.create(nome=nomeProduto, preco=precoProd, url_imagem=url_image_prod, url_youtube=url_yt)
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

    return p


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
    driver = webdriver.PhantomJS(executable_path='/Users/anton/AppData/Roaming/npm/node_modules/phantomjs-prebuilt/lib/phantom/bin/phantomjs')
    #driver = webdriver.Firefox()
    driver.get("http://www.reclameaqui.com.br/busca/?q="+marca)

    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.business-name .ng-binding')))

        soupBusca = BeautifulSoup(driver.page_source, "lxml")
        empresaUrl = soupBusca.select('.business-name .ng-binding')[0]['href']
        empresaUrlComp = 'http://www.reclameaqui.com.br'+empresaUrl
        marca = Marca()
        marca.url_reclame_aqui = empresaUrlComp
        driver.get(empresaUrlComp)

        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#n3-pie-arcs')))
            soupEmpresa = BeautifulSoup(driver.page_source, "lxml")

            reclamacoes = soupEmpresa.select('.all-complaints p')[0].get_text()
            marca.num_reclamacoes = int(reclamacoes)

            atendidas = soupEmpresa.select('.complaints-answered p')[0].get_text()
            marca.num_atendidas = int(atendidas)

            naoAtendidas = soupEmpresa.select('.complaints-unanswered p')[0].get_text()
            marca.num_nao_atendidas = int(naoAtendidas)

            nomeEmpresa = soupEmpresa.select('.business-name-site h1')[0].get_text()
            marca.nome = nomeEmpresa

            classificacaoEmpresa = soupEmpresa.select('.business-seal p')[0].get_text()
            marca.recomendacao = classificacaoEmpresa

            siteEmpresa = "" if not soupEmpresa.select('.business-contact-info a') else 'http://'+soupEmpresa.select('.business-contact-info a')[0].get_text()
            marca.url_marca = siteEmpresa

            tempoDeResposta = soupEmpresa.select('.reply-time .ng-binding')[0].get_text()
            marca.tempo_resposta = tempoDeResposta

            notaConsumidor = soupEmpresa.select('.user-rating .ng-binding')[0].get_text()
            marca.nota_consumidor = float(notaConsumidor)

            numAvaliacoes = soupEmpresa.select('.all-ratings .ng-binding')[0].get_text()
            marca.num_avaliacoes = int(numAvaliacoes)

            porcentagens = soupEmpresa.select('.legend-value')

            marca.pct_atendidas = float(porcentagens[0].get_text()[:-1])
            marca.volta_negocio = float(porcentagens[1].get_text()[:-1])
            marca.indice_solucao = float(porcentagens[2].get_text()[:-1])
            marca.save()
            return marca

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
    marcaInfo = Marca.objects.filter(nome__icontains=marca)
    if len(marcaInfo) > 0:
        marcaInfo = marcaInfo[0]
    if not marcaInfo:
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
        if '#' in url:
            indexFinal = url.index('#')
            nomeProduto = url[26:indexFinal]
        else:
            nomeProduto = url[26:]
        nomeSemTraco = nomeProduto.replace("-", " ")
        inicio = timeit.default_timer()
        p = getComentarios(url, topx, nomeProduto)
        topComment = p.comentario_set.all().order_by('-importancia')[:topx]
        fim = timeit.default_timer()
        print ('duracao obtendo e classificando comentários: %f' % (fim - inicio))
        marcaInfo = getInfoMarca(url)

        return render(request, 'topx/index.html', {'topComment': topComment, 'nomeProduto': nomeSemTraco, 'url': url, 'topx': topx, 'marcaInfo': marcaInfo, 'prod':p})

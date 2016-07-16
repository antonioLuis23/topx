import pymysql.cursors
import nltk
import time
import timeit
import re
from .topxFuzzy import TopxFuzzy
import json

class TopX(object):
    def __init__(self):
        self.padroes = {}
        self.autores = {}
        self.contAutores = {}
        self.comentarios = {}
        self.importancia = {}
        self.padraoIgual = 0

    def sent_adverbio(self, adv, lista_adverbios):
        for dicAdverbio in lista_adverbios:
            adverbio = dicAdverbio['adverb']
            if adv in adverbio:
                return dicAdverbio['pol']
        return 0


    def sent_classificador(self, palavra, sentilex):
        for dicSentilex in sentilex:
            palavra_lex = dicSentilex['palavra']
            split_words = palavra_lex.split(',')
            for word in split_words:
                if palavra == word:
                    pol = dicSentilex['pol']
                    if '-1' in pol:
                        return -1
                    else: 
                        return 1
        return 0
    def sentimentoDaTupla(self, tags, lista_adverbios, sentilex):
        total_modificadores = 0
        total_qualificadores = 0
        inversor = 1
        #procurando inversor
        for palavra in tags:
            if palavra[0] in 'não' or palavra[0] in 'nao' or palavra[0] in 'jamais':
                inversor = -1
        #procurando adverbios
        for palavra in tags:
            if 'ADV' in palavra[1] and palavra[0] != 'nao' and palavra[0] != 'não' and palavra[0] != 'jamais':
                pol = self.sent_adverbio(palavra[0], lista_adverbios)
                total_modificadores = total_modificadores + pol
            if 'ADJ' in palavra[1] or 'V' in palavra[1]:
                pol = self.sent_classificador(palavra[0], sentilex)
                total_qualificadores = total_qualificadores + pol
        if total_modificadores > 0:
            if total_qualificadores > 0:
                return total_qualificadores + (inversor * total_modificadores)
            else:
                return total_qualificadores - (inversor * total_modificadores)
        else:
            return inversor*total_qualificadores
        return 0

    def obtemPadroes(self, result, cursor, id_produto, id_tipo, etiq):

        caracteristicas = []
        acerto_positivo = 0
        acerto_negativo = 0
        acerto_neutro = 0
        num_positivo = 0
        num_negativo = 0
        num_neutro = 0


        sql = "SELECT `*` FROM `adverblist`"
        cursor.execute(sql)
        lista_adverbios = cursor.fetchall()

        sql = "SELECT `*` FROM `sentilex_flex_pt02`"
        cursor.execute(sql)
        sentilex = cursor.fetchall()

        sql = "SELECT `caracteristicas` FROM `topx_tipo` where id = %s"
        cursor.execute(sql, (id_tipo))
        features = cursor.fetchall()
        caracteristicas = features[0]['caracteristicas'][:-1].split(';')
        print('caracteristicas:', caracteristicas, 'type:', type(caracteristicas))
        #with open('C:/djangoScrapy/topxweb/topx/caracteristicas.txt', 'r', encoding="utf-8") as dict:
        #    for palavra in dict:
        #        caracteristicas.append(palavra.replace("\n", ""))
        
        #etiqPadrao = nltk.DefaultTagger('N')  # Usando etiquetas default para os tokens nao reconhecidos
        #sentencas_treinadoras = nltk.corpus.mac_morpho.tagged_sents()[::]
        #etiq = nltk.UnigramTagger(sentencas_treinadoras, backoff=etiqPadrao)
        for dicComentario in result:
            comentario = dicComentario['comentario']
           # pos = dicComentario['POS']
           # neg = dicComentario['NEG']
            id = dicComentario['id']

            tokens = nltk.word_tokenize(comentario.lower())
            print('comentario:',comentario)
            tokens=nltk.word_tokenize(comentario.lower())
            tags = etiq.tag(tokens)
            
            ag = nltk.chunk.RegexpParser(r"""
            PADRAO0: {(<N> | <N> <PREP> <N>) <ADV>? <V> <ADV>? <ADJ>}
            """)
            av = ag.parse(tags)

            x0 = self.ExtractPhrases(av, "PADRAO0")
          
            analiseGramatical = nltk.chunk.RegexpParser(r"""
            PADRAO1: {<N>(<PREP>?<N>)*(<ADJ>)<ADV><ADV>?}
            PADRAO2: {<N>(<PREP>?<N>)*<ADV>?<ADJ>+}
            PADRAO3: {<ADJ><N>(<PREP>?<N>)*}
            PADRAO4: {<ADV><ADV>?<ADJ>(<N>(<PREP>?<N>)*)?}
            PADRAO5: {<ADV><V>}
            PADRAO6: {<V><ADV>}
            """)
            tags2 = []
            for index, classe in enumerate(tags):
                if 'ART' in classe[1] or 'PROPESS' in classe[1] or 'KC' in classe[1] or 'NUM' in classe[1]:
                    continue
                else:
                    tags2.append(classe)
            tags = tags2
            #print('tags:', tags)
            arvore = analiseGramatical.parse(tags)

            x1 = self.ExtractPhrases(arvore, "PADRAO1")
            x2 = self.ExtractPhrases(arvore, "PADRAO2")
            x3 = self.ExtractPhrases(arvore, "PADRAO3")
            x4 = self.ExtractPhrases(arvore, "PADRAO4")
            x5 = self.ExtractPhrases(arvore, "PADRAO5")
            x6 = self.ExtractPhrases(arvore, "PADRAO6")
            print('suj+ver+predSuj:', x0)
            print('x1:', x1)
            print('x2:', x2)
            print('x3:', x3)
            print('x4:', x4)
            print('x5:', x5)
            print('x6:', x6)
            padroes = [x0, x1, x2, x3, x4, x5, x6]
            quantPadroes = 0;
            sentComment = 0
            for x in padroes:
                for frase in x:
                    tokens=nltk.word_tokenize(frase.lower())
                    tags = etiq.tag(tokens)
                    sentPad = self.sentimentoDaTupla(tags, lista_adverbios, sentilex)
                    sentComment = sentComment + sentPad;
                    #print('frase', frase)   
                    for feature in caracteristicas:
                        if feature in frase:      
                            print('frase:',frase)  
                            print('caracteristica:', feature)
                            quantPadroes = quantPadroes + 1
            #cursor.execute("UPDATE meusresultados SET PATT = %s WHERE ID = %s", (quantPadroes, id))  
            if quantPadroes > 5:
                quantPadroes = 5
            self.padroes[id]=quantPadroes

         #  print('quantPadroes:', quantPadroes)
        #   name = input("Espere!")
        #   polaridade do comentario               
            print('sentComment',sentComment)
            if sentComment>0:
                cursor.execute("UPDATE topx_comentario SET polaridade = %s WHERE id = %s", ('positivo', id))
                #num_positivo = num_positivo+1
            else:
                if sentComment < 0:
                    cursor.execute("UPDATE topx_comentario SET polaridade = %s WHERE id = %s", ('negativo', id))
                    num_negativo = num_negativo + 1
                else:
                    cursor.execute("UPDATE topx_comentario SET polaridade = %s WHERE id = %s", ('neutro', id))
                    num_neutro = num_neutro + 1

        #    if pos == 1 and neg == 0 and sentComment >0:
        #        acerto_positivo = acerto_positivo + 1
        #    if pos == 0 and neg == 1 and sentComment <0:
        #        acerto_negativo = acerto_negativo + 1 
        #    if pos == 1 and neg == 1 and sentComment == 0:
        #        acerto_neutro = acerto_neutro + 1 

        #print('acerto_positivo:', acerto_positivo)
        #print('acerto_negativo:', acerto_negativo)
        #print(' acerto_neutro:', acerto_neutro)
        #print('num_positivo:', num_positivo)
        #print('num_negativo:',num_negativo)
        #print('num_neutro:', num_neutro)




    def ExtractPhrases(self, myTree, phrase):
        myPhrases = []
        if (myTree.label() == phrase):
            treeTmp = myTree.copy(True)
            word=""
            for w in treeTmp.leaves():
                if (len(word)==0):
                    word = w[0]
                else:
                    word = word+" "+w[0]
            myPhrases.append(word)
        for child in myTree:
            if (type(child) is nltk.Tree):
                list_of_phrases = self.ExtractPhrases(child, phrase)
                if (len(list_of_phrases) > 0):
                    myPhrases.extend(list_of_phrases)
        return myPhrases



    def contaAutor(self, result, cursor):
        for dicAutor in result:
            autor = dicAutor['autor']

            #print(dicAutor['autor'])
            if autor in self.autores.keys():
                if autor == 'e-bit' or autor == '' or autor == 'Consumidor e-bit':
                    self.autores[autor] = 1
                else:
                    self.autores[autor] =  self.autores[autor]+1
            else:
                 self.autores[autor] = 1;
        #print(autores)

        for dicAutor in result:
            autor = dicAutor['autor']
            id = dicAutor['id']
            if self.autores[autor]>4:
                self.contAutores[id] = 4
            else:
                self.contAutores[id] = self.autores[autor]
            self.contAutores[id] = self.autores[autor]
            #cursor.execute("UPDATE meusresultados SET REPAUTOR = %s WHERE ID = %s", (self.autores[autor], id))


    def corretudeComentario(self,result, cursor):
        dicionario = []
        with open('C:/djangoScrapy/topxweb/topx/palavras.ispell', 'r', encoding="utf-8") as dict:
            for palavra in dict:
                dicionario.append(palavra.replace("\n", ""))


        for dicComentario in result:
            comentario = dicComentario['comentario']
            id = dicComentario['id']
            tokens = nltk.word_tokenize(comentario)
            words = [w.lower() for w in tokens if w.isalnum()]
            countCorreta = 0
            countWord = 0
            for word in words:
                if(word in dicionario):
                    countCorreta = countCorreta+1
                countWord=countWord+1
            if countWord == 0 or countCorreta == 0:
                pct = 0
            else:
                pct = countCorreta/countWord*100
            print("Comentario:", comentario)
            print("Porcentagem palavras corretas:", pct ,"%")
            self.comentarios[id]=pct
            #cursor.execute("UPDATE meusresultados SET CORR = %s WHERE ID = %s", (pct, id))
       

    def main(self, id_produto, id_tipo, etiq):
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='Mysql!)@9',
                                    db='comentariostopx',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                connection.autocommit(True)
                # Read a single record
                sql = "SELECT `*` FROM `topx_comentario` WHERE produto_id = %s"
                cursor.execute(sql, (id_produto))
                #result_comments = cursor.fetchall()
                result_comments = cursor.fetchmany(size=100)

                inicio = timeit.default_timer()
                fuzzy = TopxFuzzy
                self.obtemPadroes(result_comments, cursor, id_produto, id_tipo, etiq )
                self.corretudeComentario(result_comments,cursor)
                self.contaAutor(result_comments, cursor)
                # with open('C:/relautor.txt', 'w') as outfile:
                #     json.dump(self.contAutores, outfile)
                # with open('C:/padroes.txt', 'w') as outfile:
                #     json.dump(self.padroes, outfile)
                # with open('C:/corretude.txt', 'w') as outfile:
                #     json.dump(self.comentarios, outfile)

                #fuzzy.calculaFuzzy(4,3,88)
                for key in self.padroes:
                    k = fuzzy.calculaFuzzy(self.contAutores[key], self.padroes[key], self.comentarios[key])
                    self.importancia[key] = k
                    cursor.execute("UPDATE topx_comentario SET importancia = %s WHERE id = %s", (k.item(), key))
                fim = timeit.default_timer()
                print('self.importancia', self.importancia)
                print ('duracao: %f' % (fim - inicio))


        finally:
            connection.close()


from django.db import models


class Tipo(models.Model):
    nome = models.CharField(max_length=50, blank=True, null=True)
    caracteristicas = models.CharField(max_length=3500, blank=True, null=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=1000, blank=True, null=True)
    preco = models.CharField(max_length=1000, blank=True, null=True)
    url_imagem = models.CharField(max_length=1000, blank=True, null=True)
    pol_caracteristica = models.CharField(max_length=3500, blank=True, null=True)
    url_youtube = models.CharField(max_length=1000, blank=True, null=True)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.nome


class Marca(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True)
    recomendacao = models.CharField(max_length=255, blank=True, null=True)
    num_reclamacoes = models.IntegerField(blank=True, null=True)
    num_atendidas = models.IntegerField(blank=True, null=True)
    num_nao_atendidas = models.IntegerField(blank=True, null=True)
    tempo_resposta = models.CharField(max_length=50, blank=True, null=True)
    nota_consumidor = models.FloatField(blank=True, null=True)
    num_avaliacoes = models.IntegerField(blank=True, null=True)
    pct_atendidas = models.FloatField(blank=True, null=True)
    volta_negocio = models.FloatField(blank=True, null=True)
    indice_solucao = models.FloatField(blank=True, null=True)
    url_marca = models.CharField(max_length=255, blank=True, null=True)
    url_reclame_aqui = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome


class Comentario(models.Model):
    comentario = models.CharField(max_length=3500, blank=True, null=True)
    autor = models.CharField(max_length=255, blank=True, null=True)
    voto_positivo = models.IntegerField(blank=True, null=True)
    voto_negativo = models.IntegerField(blank=True, null=True)
    reputacaoAutor = models.IntegerField(blank=True, null=True)
    nota = models.PositiveSmallIntegerField(blank=True, null=True)
    recomenda = models.CharField(max_length=100, blank=True, null=True)
    importancia = models.FloatField(blank=True, null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    polaridade = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.comentario

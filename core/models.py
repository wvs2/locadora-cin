from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField
from core.choices import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Genero(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)

    class Meta:
        ordering = ['nome',]
        verbose_name = 'Gênero'
        verbose_name_plural = 'Gêneros'

    def __str__(self):
        return "%s" % self.nome 

    def get_absolute_url(self):
        return reverse('core:genero-detalhe', kwargs={'pk': self.pk})

class Artista(models.Model):
    nome = models.CharField('Nome', max_length=150, unique=True)
    tipo = MultiSelectField('Atividade', choices=tipo_pessoa_filme)

    class Meta:
        ordering = ['nome',]
        verbose_name = 'Artista'
        verbose_name_plural = 'Artistas'

    def __str__(self):
        return "%s" % self.nome 

    def get_absolute_url(self):
        return reverse('core:artista-detalhe', kwargs={'pk': self.pk})

class Estado(models.Model):
    nome = models.CharField('Nome', max_length=60, unique=True)
    sigla = models.CharField('Sigla', max_length=30, unique=True)

    class Meta:
        ordering = ['nome',]
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return "%s" % self.nome

    def get_absolute_url(self):
        return reverse('core:estado-detalhe', kwargs={'pk': self.pk})
    
    def clean(self):
        self.sigla = self.sigla.upper()

class Cidade(models.Model):
    nome = models.CharField('Nome', max_length=60)
    capital = models.BooleanField('Capital ?', default=False)
    estado = models.ForeignKey(Estado, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['nome', 'estado',]
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

    def __str__(self):
        return "%s/%s" % (self.nome, self.estado.sigla)

    def get_absolute_url(self):
        return reverse('core:cidade-detalhe', kwargs={'pk': self.pk})

class Endereco(models.Model):
    logradouro = models.CharField('Logradouro', max_length=100)
    numero = models.PositiveIntegerField('Número')
    complemento = models.CharField('Complemento', max_length=60, null=True, blank=True)
    bairro = models.CharField('Bairro', max_length=50)
    cep = models.CharField('CEP', max_length=10)
    cidade = models.ForeignKey(Cidade, on_delete=models.DO_NOTHING)
    estado = models.ForeignKey(Estado, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ordering = ['logradouro', 'numero', 'cidade',]
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return "%s, nº %d - %s - %s - CEP %s" % (self.logradouro, self.numero, self.bairro, self.cidade, self.cep)

    def get_absolute_url(self):
        return reverse('core:endereco-detalhe', kwargs={'pk': self.pk})

class Telefone(models.Model):
    prefixo = models.CharField('Prefixo', max_length=10)
    numero = models.CharField('Número', max_length=20)
    tipo = models.CharField('Tipo de Telefone', max_length=15, choices=tipo_classificacao)

    class Meta:
        ordering = ['prefixo', 'tipo',]
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

    def __str__(self):
        return "(%s) %s - %s" % (self.prefixo, self.numero, self.tipo)

    def get_absolute_url(self):
        return reverse('core:cidade-detalhe', kwargs={'pk': self.pk})

class Distribuidora(models.Model):
    razao_social = models.CharField('Razão Social', max_length=150)
    cnpj = models.CharField('CNPJ', max_length=20)
    contato = models.CharField('Pessoa de Contato', max_length=150)
    telefone = models.CharField('Telefone', max_length=30)
    endereco = models.OneToOneField(Endereco, on_delete=models.CASCADE)

    class Meta:
        ordering = ['razao_social',]
        verbose_name = 'Distribuidora'
        verbose_name_plural = 'Distribuidoras'

    def __str__(self):
        return "%s" % self.razao_social

    def get_absolute_url(self):
        return reverse('core:distribuidora-detalhe', kwargs={'pk': self.pk})

class Filme(models.Model):
    titulo = models.CharField('Título em Português', max_length=150) 
    titulo_original = models.CharField('Título Original', max_length=150)
    sinopse = models.TextField('Sinopse')
    classificacao = models.CharField('Classificação Indicativa', max_length=2, choices=tipo_classificacao)
    duracao = models.TimeField('Duração')
    diretor = models.ManyToManyField(Artista)
    ano = models.PositiveSmallIntegerField('Ano de Lançamento')
    pais = models.CharField('País', max_length=150)
    genero = models.ManyToManyField(Genero)
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.DO_NOTHING, null=True)
    capa = models.ImageField('Capa do Filme', upload_to = 'capas/', blank=True, null=True)

    class Meta:
        ordering = ['titulo',]
        verbose_name = 'Filme'
        verbose_name_plural = 'Filmes'

    def __str__(self):
        return "%s (%s)" % (self.titulo, self.titulo_original)
    
    def get_absolute_url(self):
        return reverse('core:filme-detalhe', kwargs={'pk': self.pk})

class Elenco(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE)
    ator =  models.ForeignKey(Artista, on_delete=models.CASCADE)
    personagem = models.CharField('Personagem', max_length=150, null=True, blank=True)
    principal = models.BooleanField('Principal ?', default=False)

    class Meta:
        unique_together = ('filme', 'ator')
        ordering = ['ator', 'principal',]
        verbose_name = 'Elenco'
        verbose_name_plural = 'Elencos'

    def __str__(self):
        return "%s (%s)" % (self.ator, self.personagem)

    def get_absolute_url(self):
        return reverse('core:elenco-detalhe', kwargs={'pk': self.pk})

    def clean(self):
        if self.ator and not self.personagem:
            raise ValidationError({'personagem': _("É obrigatório informar o nome do personagem para o ator: '%s'." % self.ator)})

class Midia(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)
    valor = models.DecimalField('Valor da Locação', max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['nome',]
        verbose_name = 'Tipo de Mídia'
        verbose_name_plural = 'Tipos de Mídias'

    def __str__(self):
        return "%s" % self.nome

    def get_absolute_url(self):
        return reverse('core:midia-detalhe', kwargs={'pk': self.pk})

class Item(models.Model):
    numero_serie = models.CharField('Número de Série', max_length=150)
    data_aquisicao = models.DateField('Data de Aquisição')
    tipo_midia = models.ForeignKey(Midia, on_delete=models.DO_NOTHING)
    filme = models.ForeignKey(Filme, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['data_aquisicao',]
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'

    def __str__(self):
        return "%s (%s)" % (self.filme, self.tipo_midia)

    def get_absolute_url(self):
        return reverse('core:item-detalhe', kwargs={'pk': self.pk})
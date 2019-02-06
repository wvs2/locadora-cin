from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField
from core.choices import *
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.managers import UserManager
from datetime import date
from django.conf import settings
from django.utils.text import slugify
from django.template.defaultfilters import slugify as slug_template

# Create your models here.
class Role(models.Model):
    CLIENTE = 1
    FUNCIONARIO = 2
    ADMIN = 3
    SUPER_USER = 4
    ROLE_CHOICES = (
        (CLIENTE, 'Cliente'),
        (FUNCIONARIO, 'Funcionário'),
        (ADMIN, 'Admin'),
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    roles = models.ManyToManyField(Role)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

class Genero(models.Model):
    nome = models.CharField('Nome', max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    class Meta:
        ordering = ['nome',]
        verbose_name = 'Gênero'
        verbose_name_plural = 'Gêneros'

    def __str__(self):
        return "%s" % self.nome 

    def get_absolute_url(self):
        return reverse('core:genero-detalhe', kwargs={'pk': self.pk})

    def clean(self):
        self.slug = slugify(self.nome)

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
        unique_together = ('nome', 'sigla')
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return "%s" % self.nome

    def get_absolute_url(self):
        return reverse('core:estado-detalhe', kwargs={'pk': self.pk})
    
    def clean(self):
        self.nome = self.nome.lower().capitalize()
        self.sigla = self.sigla.upper()

class Cidade(models.Model):
    nome = models.CharField('Nome', max_length=60)
    capital = models.BooleanField('Capital ?', default=False)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    class Meta:
        ordering = ['nome', 'estado',]
        unique_together = ('nome', 'estado')
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
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    class Meta:
        ordering = ['logradouro', 'numero', 'cidade',]
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return "%s, nº %d - %s - %s - CEP %s" % (self.logradouro, self.numero, self.bairro, self.cidade, self.cep)

    def get_absolute_url(self):
        return reverse('core:endereco-detalhe', kwargs={'pk': self.pk})

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
    pais = models.CharField('Nacionalidade', max_length=150)
    genero = models.ManyToManyField(Genero)
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.PROTECT)
    capa = models.ImageField('Capa do Filme', upload_to = 'capas/', blank=True, null=True)
    is_lancamento = models.BooleanField(
        'Lançamento',
        default=False,
        help_text='Designa se este filme deve ser tratado como lançamento. Desmarque esta opção se não for um lançamento.',
    )

    class Meta:
        ordering = ['titulo',]
        verbose_name = 'Filme'
        verbose_name_plural = 'Filmes'

    def __str__(self):
        if self.titulo.strip() != self.titulo_original.strip():
            return "%s (%s)" % (self.titulo, self.titulo_original)
        else:
            return "%s" % self.titulo
    
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
    tipo_midia = models.ForeignKey(Midia, on_delete=models.PROTECT, related_name='itens_midia', related_query_name='item_midia')
    filme = models.ForeignKey(Filme, on_delete=models.PROTECT, related_name='itens_filme', related_query_name='item_filme')
    quantidade = models.PositiveIntegerField('Número de Cópias', default=1)

    class Meta:
        ordering = ['data_aquisicao',]
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'

    def __str__(self):
        return "%s (%s)" % (self.filme, self.tipo_midia)

    def get_absolute_url(self):
        return reverse('core:item-detalhe', kwargs={'pk': self.pk})

class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cpf = models.CharField('CPF', max_length=15, unique=True, blank=True, null=True)
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)
    sexo = models.CharField('Sexo', max_length=2, choices=tipo_sexo)
    endereco = models.OneToOneField(Endereco, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        # ordering = ['data_aquisicao',]
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
    instance.perfil.save()

class Telefone(models.Model):
    numero = models.CharField('Número', max_length=30)
    tipo = models.CharField('Tipo de Telefone', max_length=15, choices=tipo_telefone)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    class Meta:
        ordering = ['tipo',]
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'

    def __str__(self):
        return "%s - %s" % (self.numero, self.tipo)

class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codigo = models.CharField('Código', max_length=150, unique=True)
    local_trabalho = models.CharField('Local de Trabalho', max_length=150, null=True, blank=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this client should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    titular = models.ForeignKey('self', on_delete=models.PROTECT, related_name='clientes', blank=True, null=True)

    class Meta:
        # ordering = ['data_aquisicao',]
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return "%s" % (self.user.get_full_name())

    def get_absolute_url(self):
        return reverse('core:cliente-detalhe', kwargs={'pk': self.pk})


class HistoricoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='historico_cliente')
    titular = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='historico_dependente', null=True, blank=True)
    situacao_cliente = models.BooleanField('Situação do Cliente', default=True)
    data_alteracao = models.DateTimeField(_('update date'), auto_now_add=True)

    class Meta:
        ordering = ['data_alteracao',]
        verbose_name = 'Histórico do Cliente'
        verbose_name_plural = 'Históricos dos Clientes'

    def __str__(self):
        return "%s - Titular: %s (%s)" % (self.cliente.user.get_full_name(), self.titular if self.titular else 'Não tem titular', str(self.data_alteracao))
    

class Reserva(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.PROTECT)
    filme = models.ForeignKey(Filme, on_delete=models.PROTECT, related_name='reservas_filme', related_query_name='reserva')
    midia = models.ForeignKey(Midia, on_delete=models.PROTECT, related_name='reservas_midia', related_query_name='reserva', null=True, blank=True)
    data_reserva = models.DateTimeField(_('booking date'), auto_now_add=True)
    status = models.CharField('Situação da Reserva', max_length=10, choices=tipo_reserva, default='Pendente')
    # vincular a locação quando for atendida

    class Meta:
        ordering = ['data_reserva',]
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reserva'

    def __str__(self):
        return "%s - %s (%s)" % (self.cliente.user.get_full_name(), self.filme, self.midia)

    def get_absolute_url(self):
        return reverse('core:reserva-detalhe', kwargs={'pk': self.pk})

    def clean(self):
        if not self.status:
            self.status = 'Pendente'

class Locacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    valor_total = models.DecimalField('Valor Total da Locação', max_digits=8, decimal_places=2, default=0)
    data_locacao = models.DateTimeField('Data de Locação', auto_now_add=True)
    situacao = models.CharField('Situação da Locação', max_length=20, choices=tipo_locacao, default='EM_ANDAMENTO')

    class Meta:
        ordering = ['data_locacao',]
        verbose_name = 'Locação'
        verbose_name_plural = 'Locações'

    def __str__(self):
        return "%s - %s" % (self.cliente.user.get_full_name(), str(self.data_locacao))


class ItemLocacao(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    is_lancamento = models.BooleanField(
        'Lançamento',
        default=False,
        help_text='Designa se este filme deve ser tratado como lançamento. Desmarque esta opção se não for um lançamento.',
    )
    valor = models.DecimalField('Valor da Locação', max_digits=8, decimal_places=2, default=0)
    data_devolucao_prevista = models.DateField('Data de Devolução Prevista', blank=True, null=True)
    locacao = models.ForeignKey(Locacao, on_delete=models.PROTECT)
    
    class Meta:
        # ordering = ['data_reserva',]
        verbose_name = 'Item de Locação'
        verbose_name_plural = 'Itens de Locação'

    def __str__(self):
        return "%s - %s" % (self.item, str(self.data_devolucao_prevista))

    def serialize(self):
        return self.__dict__
    

class FormaPagamento(models.Model):
    descricao = models.CharField('Descrição', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Forma de Pagamento'
        verbose_name_plural = 'Formas de Pagamento'

    def __str__(self):
        return self.descricao


class ArgumentoPagamento(models.Model):
    argumento = models.CharField('Nome do argumento', max_length=100)
    requerido = models.BooleanField('Argumento obrigatório?', default=False)
    tipo_dado = models.CharField('Tipo de dado do argumento', max_length=20, choices=tipo_dado)
    forma_pagamento = models.ManyToManyField(FormaPagamento)
    
    class Meta:
        verbose_name = 'Argumento do Pagamento'
        verbose_name_plural = 'Argumentos dos Pagamentos'

    def __str__(self):
        return '%s' % (self.argumento)

    def pagamentos(self):
        return ', '.join([p.descricao for p in self.forma_pagamento.all()])
    pagamentos.short_description = "Formas de Pagamentos associados ao argumento"

    def slug(self):
        return slug_template(self.argumento)


class Pagamento(models.Model):
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT)
    data_pagamento = models.DateTimeField('Data de Pagamento', auto_now_add=True)
    locacao = models.ForeignKey(Locacao, on_delete=models.PROTECT)
    # devolucao = models.ForeignKey(Pagamento)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'


class InformacaoPagamento(models.Model):
    argumento = models.ForeignKey(ArgumentoPagamento, related_name='informacoes_argumentos', on_delete=models.PROTECT)
    valor_texto = models.TextField('Valor da informação em Texto', blank=True, null=True)
    valor_inteiro = models.IntegerField('Valor da informação em Número Inteiro', blank=True, null=True)
    valor_decimal = models.DecimalField('Valor da informação em Número Decimal', decimal_places=2, max_digits=10, blank=True, null=True)
    valor_data_hora = models.DateTimeField('Valor da informação em Data/Hora', blank=True, null=True)
    valor_boolean = models.BooleanField('Valor da informação Verdadeiro ou Falso', blank=True, null=True)
    valor_arquivo = models.FileField('Valor da informação em Arquivo', upload_to='arquivo_pessoa/', blank=True, null=True)
    pagamento = models.ForeignKey(Pagamento, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Informação do Pagamento'
        verbose_name_plural = 'Informações dos Pagamentos'
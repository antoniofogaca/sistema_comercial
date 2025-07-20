# core/models.py
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator # Certifique-se de importar esses validadores
from django.utils import timezone
from django.contrib.auth.models import User

# Seu modelo Cliente existente (NÃO APAGUE!)
class Cliente(models.Model):
    codigo_interno = models.CharField(max_length=20, unique=True)
    matricula = models.CharField(max_length=20, blank=True, null=True)
    cancelado = models.BooleanField(default=False)
    nome_completo = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    logradouro = models.CharField(max_length=200, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nome_completo} ({self.cpf_cnpj})"

    # Adicione a classe Meta aqui para o Cliente, se não tiver (é uma boa prática)
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo'] # Exemplo de ordenação padrão


# --- NOVO MODELO: Empresa (ADICIONE ESTE BLOCO ABAIXO DO SEU MODELO CLIENTE) ---
class Empresa(models.Model):
    # Choices for fields
    PORTE_CHOICES = [
        ('MEI', 'Microempreendedor Individual (MEI)'),
        ('ME', 'Microempresa (ME)'),
        ('EPP', 'Empresa de Pequeno Porte (EPP)'),
        ('Outros', 'Outros'),
    ]

    SITUACAO_CHOICES = [
        ('Ativa', 'Ativa'),
        ('Inativa', 'Inativa'),
        ('Suspensa', 'Suspensa'),
        ('Baixada', 'Baixada'),
    ]

    CRT_CHOICES = [
        ('1', 'Simples Nacional'),
        ('2', 'Simples Nacional – excesso de sublimite de receita bruta'),
        ('3', 'Regime Normal (Empresas modalidade Geral)'),
    ]

    # 3.2 Identificação da Empresa

    codigo_loja = models.CharField(max_length=50, unique=True, verbose_name="Código da Loja")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ", validators=[MinLengthValidator(14)]) # Max 18 for masked CNPJ
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, blank=True, null=True, verbose_name="Porte")
    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='Ativa', verbose_name="Situação")
    data_abertura = models.DateField(blank=True, null=True, verbose_name="Data de Abertura")

    # 3.9 Nome da Empresa
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    razao_social = models.CharField(max_length=255, unique=True, verbose_name="Razão Social")
    fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")

    # 3.12 Contato
    contato = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome do Contato")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail")

    # 3.15 Endereço
    logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")

    # 3.22 Dados Fiscais
    cnae_principal = models.CharField(max_length=100, blank=True, null=True, verbose_name="CNAE Principal") # Could be ForeignKey to CNAE model
    aliquota_simples = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Alíquota do Simples") # Consider using FloatField if exact decimal places aren't strict
    codigo_regime_tributario = models.CharField(
        max_length=1,
        choices=CRT_CHOICES,
        default='1',
        verbose_name="Código de Regime Tributário (CRT)"
    )

    # 3.26 Cancelado (checkbox)
    cancelado = models.BooleanField(default=False, verbose_name="Cancelado") # True if canceled, False if active

    def __str__(self):
        return f"{self.fantasia or self.razao_social} ({self.cnpj})"

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['fantasia', 'razao_social'] # Default ordering

# NOVO MODELO: Usuario
class Usuario(models.Model):
    NIVEL_CHOICES = [
        ('Admin', 'Administrador'),
        ('Gerente', 'Gerente'),
        ('Operador', 'Operador'),
        ('Visualizador', 'Visualizador'),
    ]

    PERMISSAO_CHOICES = [
        ('Total', 'Acesso Total'),
        ('Parcial', 'Acesso Parcial'),
        ('Nenhum', 'Nenhum Acesso'),
    ]

    # 1.1.1 Id_usuario - Django cria automaticamente um campo 'id' como PK
    # 1.1.2 Id_loja - Chave estrangeira para Empresa
    id_loja = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loja Associada")
    # 1.1.3 Id_nivel
    id_nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, verbose_name="Nível de Acesso")
    # 1.1.4 Id_permisao
    id_permissao = models.CharField(max_length=20, choices=PERMISSAO_CHOICES, verbose_name="Permissão de Acesso")
    # 1.1.5 Nome
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    # 1.1.6 Usuario
    usuario = models.CharField(max_length=100, unique=True, verbose_name="Nome de Usuário")
    # 1.1.7 Senha (usar com cuidado, Django tem um sistema de autenticação próprio)
    # Por enquanto, vamos manter como CharField, mas em um sistema real usaria o User model do Django.
    senha = models.CharField(max_length=128, verbose_name="Senha") # Django usa 128 para senhas hasheadas
    # 1.1.8 Cancelado (checkbox)
    cancelado = models.BooleanField(default=False, verbose_name="Cancelado")

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['nome'] # Ordena por nome por padrão

    def __str__(self):
        return self.nome

# Modelo de Setor
class Setor(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código do Setor")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    cancelado = models.BooleanField(default=False, verbose_name="Cancelado")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ['descricao'] # Ordem padrão por descrição

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

# Modelo de Categoria
class Categoria(models.Model):
    id_cat = models.CharField(max_length=20, unique=True, verbose_name="Código da Categoria")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    cancelado = models.BooleanField(default=False, verbose_name="Cancelado")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['descricao'] # Ordem padrão por descrição

    def __str__(self):
        return f"{self.id_cat} - {self.descricao}"

# Modelo de Setor
class Grupo(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código do Grupo")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    cancelado = models.BooleanField(default=False, verbose_name="Cancelado")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ['descricao'] # Ordem padrão por descrição

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

# MODELO PARA NCM
class Ncm(models.Model):
    ncm              = models.CharField(max_length=10,unique=True,verbose_name="NCM",help_text="Código NCM (Nomenclatura Comum do Mercosul).")
    descricao        = models.CharField(max_length=300,verbose_name="Descrição",help_text="Descrição detalhada do NCM.")
    inicio_vigencia  = models.DateField(null=True,blank=True, verbose_name="Início da Vigência", help_text="Data de início da validade do NCM." )
    fim_vigencia     = models.DateField(null=True, blank=True, verbose_name="Fim da Vigência", help_text="Data de fim da validade do NCM."  )
    ano              = models.CharField(max_length=4,null=True,blank=True,verbose_name="Ano",help_text="Ano de referência do NCM." )
    numero           = models.CharField(max_length=10,null=True,blank=True, verbose_name="Número", help_text="Número de identificação do NCM." )
    cancelado        = models.BooleanField(default=False,verbose_name="Cancelado",help_text="Indica se o NCM está cancelado." )
    segmento         = models.CharField(max_length=100,null=True,blank=True,verbose_name="Segmento", help_text="Segmento de mercado relacionado ao NCM." )
    data_cadastro    = models.DateTimeField(auto_now_add=True,verbose_name="Data de Cadastro" )
    data_atualizacao = models.DateTimeField(auto_now=True,verbose_name="Última Atualização" )

    class Meta:
        verbose_name = "NCM"
        verbose_name_plural = "NCMs"
        # Podemos ordenar por NCM ou descrição por padrão
        ordering = ['ncm']

    def __str__(self):
        # Representação amigável para o Django Admin e depuração
        return f"{self.ncm} - {self.descricao}"

# --- NOVO MODELO: CFOP ---
class Cfop(models.Model):
    # Campo CFOP (VARCHAR(4) NOT NULL)
    cfop = models.CharField(
        max_length=4,
        unique=True,  # CFOP geralmente é único
        null=False,
        blank=False,
        verbose_name='CFOP',
        help_text='Código Fiscal de Operações e Prestações (4 dígitos).'
    )

    # Campo CATEGORIA (VARCHAR(800) NOT NULL)
    categoria = models.CharField(
        max_length=800,
        null=False,
        blank=False,
        verbose_name='Categoria',
        help_text='Categoria do CFOP (ex: Entradas, Saídas).'
    )

    # Campo DESCRICAO (VARCHAR(900) NOT NULL)
    descricao = models.CharField(
        max_length=900,
        null=False,
        blank=False,
        verbose_name='Descrição',
        help_text='Descrição detalhada do CFOP.'
    )

    # Campo Cancelado (Checkbox)
    cancelado = models.BooleanField(
        default=False,
        verbose_name='Cancelado',
        help_text='Indica se o CFOP está desativado/cancelado.'
    )

    # Campos de auditoria/timestamps
    data_cadastro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Cadastro'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'CFOP'
        verbose_name_plural = 'CFOPs'
        # Adicionar uma ordenação padrão, por exemplo, pelo próprio CFOP
        ordering = ['cfop']

    def __str__(self):
        # Representação string do objeto Cfop
        return f'{self.cfop} - {self.descricao}'

# --- NOVO MODELO: CEST ---
class Cest(models.Model):
    # Campo CD_CEST (VARCHAR(9) NOT NULL)
    cd_cest = models.CharField(
        max_length=9,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Código CEST',
        help_text='Código Especificador da Substituição Tributária (9 dígitos).'
    )

    # Campo DESCRICAO (VARCHAR(900) NOT NULL)
    descricao = models.CharField(
        max_length=900,
        null=False,
        blank=False,
        verbose_name='Descrição',
        help_text='Descrição detalhada do CEST.'
    )

    # Campo CD_NCM (VARCHAR(300))
    cd_ncm = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name='Código NCM',
        help_text='Código Nomenclatura Comum do Mercosul associado (opcional).'
    )

    # Campo Cancelado (Checkbox) - NOVO CAMPO AQUI
    cancelado = models.BooleanField(
        default=False,
        verbose_name='Cancelado',
        help_text='Indica se o CEST está desativado/cancelado.'
    )

    # Campos de auditoria/timestamps
    data_cadastro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Cadastro'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'CEST'
        verbose_name_plural = 'CESTs'
        ordering = ['cd_cest']

    def __str__(self):
        return f'{self.cd_cest} - {self.descricao}'

# --- NOVO MODELO: CstCson ---
class CstCson(models.Model):
    # Campo CD_CST_CSON (VARCHAR(3) NOT NULL)
    cd_cst_cson = models.CharField(
        max_length=3,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Código CST/CSOSN',
        help_text='Código de Situação Tributária ou Código de Situação da Operação do Simples Nacional (3 dígitos).'
    )

    # Campo DESCRICAO (VARCHAR(600) NOT NULL)
    descricao = models.CharField(
        max_length=600,
        null=False,
        blank=False,
        verbose_name='Descrição',
        help_text='Descrição detalhada do CST/CSOSN.'
    )

    # Campo CD_REGIME_TRIB (CHAR(1))
    cd_regime_trib = models.CharField(
        max_length=1,
        null=False,
        blank=False,
        verbose_name='Regime Tributário',
        help_text='Código do Regime Tributário (ex: 1=Simples Nacional, 3=Regime Normal).'
    )

    # Campo Cancelado (Checkbox)
    cancelado = models.BooleanField(
        default=False,
        verbose_name='Cancelado',
        help_text='Indica se o CST/CSOSN está desativado/cancelado.'
    )

    # Campos de auditoria/timestamps
    data_cadastro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Cadastro'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'CST/CSOSN'
        verbose_name_plural = 'CSTs/CSOSNs'
        ordering = ['cd_cst_cson']

    def __str__(self):
        return f'{self.cd_cst_cson} - {self.descricao}'

class SubGrupo(models.Model):
    # Opções para o campo status
    STATUS_CHOICES = [
        ('A', 'Ativo'),
        ('C', 'Cancelado'),
    ]

    id_sub_grupo = models.SmallAutoField(primary_key=True, db_column='ID_SUB_GRUPO')
    id_grupo = models.ForeignKey('Grupo', on_delete=models.CASCADE, db_column='ID_GRUPO')
    nome_sub_grupo = models.CharField(max_length=50, db_column='NOME_SUB_GRUPO')
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
        db_column='STATUS'
    )

    class Meta:
        db_table = 'SUB_GRUPO'
        verbose_name = 'Sub Grupo'
        verbose_name_plural = 'Sub Grupos'

    def __str__(self):
        return self.nome_sub_grupo
#---------------------------------------------------------------------------------------
# --- NOVO MODELO: Produto (Adicione este bloco no seu core/models.py) ---
class Produto(models.Model):
    # Choices para campos com opções fixas
    UNIDADE_VENDA_CHOICES = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
        ('PC', 'Peça'),
        # Adicione mais conforme necessário
    ]

    TIPO_PRODUTO_CHOICES = [ # <<-- Estas são as CHOICES
        ('V', 'Venda'),
        ('S', 'Serviço'),
    ]

    SITUACAO_PRODUTO_CHOICES = [
        ('A', 'Ativo'),
        ('I', 'Inativo'),
    ]

    TIPO_TRIBUTACAO_CHOICES = [
        ('T', 'Tributado'),
        ('I', 'Isento'),
        ('F', 'Não Tributado'),
    ]

    # Campos do formulário
    codigo_ean_dun = models.CharField(max_length=50, unique=True, verbose_name="Código EAN/DUN")
    descricao_produto = models.CharField(max_length=255, verbose_name="Descrição Produto (Nome - Marca - Modelo - Peso)")
    descricao_pdv = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição Produto PDV")
    unidade_venda = models.CharField(max_length=2, choices=UNIDADE_VENDA_CHOICES, verbose_name="Unidade Venda")
    qtd_por_embalagem = models.DecimalField(max_digits=10, decimal_places=3, default=1.000, verbose_name="Qtd Por Embalagem")

    # Adicione este campo para usar as TIPO_PRODUTO_CHOICES
    tipo_produto = models.CharField(max_length=1, choices=TIPO_PRODUTO_CHOICES, default='V', verbose_name="Tipo de Produto")

    # Campos de Booleano (Sim/Não)
    peso = models.BooleanField(default=False, verbose_name="Peso")
    pode_multiplicar = models.BooleanField(default=False, verbose_name="Pode Multiplicar")
    uso_consumo = models.BooleanField(default=False, verbose_name="Uso/Consumo")

    # Situação do Produto
    situacao = models.CharField(max_length=1, choices=SITUACAO_PRODUTO_CHOICES, default='A', verbose_name="Situação")

    # Campos numéricos
    percentual_icms_venda = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="%ICMS Venda")
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=3, default=0.000, verbose_name="Estoque Atual")
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Peso Líquido")
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Peso Bruto")
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Venda")

    classificacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Classificação")
    tipo_tributacao = models.CharField(max_length=1, choices=TIPO_TRIBUTACAO_CHOICES, verbose_name="Tipo de Tributação")

    # Relacionamentos (Foreign Keys)
    id_setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Setor")
    id_grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Grupo")
    id_sub_grupo = models.ForeignKey('SubGrupo', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sub-Grupo") # Assumindo que SubGrupo está definida em models.py
    id_cfop = models.ForeignKey(Cfop, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="CFOP")
    id_cstcson = models.ForeignKey(CstCson, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="CST/CSOSN")
    id_ncm = models.ForeignKey(Ncm, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="NCM")
    id_cest = models.ForeignKey(Cest, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="CEST")

    # Campos de auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['descricao_produto']

    def __str__(self):
        return f"{self.codigo_ean_dun} - {self.descricao_produto}"

class ConvenioAbertura(models.Model):
    # MES_REFERENCIA_CHOICES removido porque não é mais usado para o campo mes_referencia
    # que agora é um CharField de texto livre no formato MM/AAAA.
    # Se você tiver outro uso para esta lista de escolhas em outro lugar, mantenha-o.
    # Caso contrário, pode ser removido para limpar o código.

    STATUS_CHOICES = [
        ('A', 'Ativo'),
        ('F', 'Fechado'),
    ]

    mes_referencia = models.CharField(
        max_length=7, # Ajustado para 7 caracteres para acomodar "MM/AAAA" (01/2025 = 7 caracteres)
        null=False,
        blank=False,
        verbose_name="Mês/Ano Referência",
        help_text="Formato: MM/AAAA"
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
        verbose_name="Status"
    )
    data_abertura = models.DateField(
        verbose_name="Data de Abertura"
    )
    data_fechamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Fechamento"
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Pagamento"
    )

    class Meta:
        verbose_name = "Abertura de Convênio"
        verbose_name_plural = "Aberturas de Convênios"
        ordering = ['-mes_referencia', 'data_abertura']

    def __str__(self):
        return f"Convênio Ref.: {self.mes_referencia} - Status: {self.get_status_display()}"

#------------------------------------------ MODELO PARA CONVÊNIOS ------------------------------------------------------

class Convenio(models.Model):
    """
    Model para armazenar os dados dos convênios com clientes.
    """
    # Em Django, uma chave primária auto-incrementável (id) é criada por padrão.
    # Se você precisa que o nome seja exatamente ID_CONVENIO, pode declará-la assim:
    # id_convenio = models.AutoField(primary_key=True)
    # Mas, por convenção, geralmente deixamos o Django gerenciar o campo 'id'.

    # Se 'cd_loja' for uma referência a outra tabela (como uma tabela de Lojas),
    # o ideal seria usar uma ForeignKey. Ex:
    # cd_loja = models.ForeignKey('Loja', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Loja")
    cd_loja          = models.IntegerField(null=True, blank=True, verbose_name="Código da Loja")

    nome_convenio    = models.CharField(max_length=100, verbose_name="Nome do Convênio", help_text="Nome de identificação do convênio.")
    cnpj             = models.CharField(max_length=18, unique=True, verbose_name="CNPJ", help_text="CNPJ do conveniado. Formato: XX.XXX.XXX/XXXX-XX")
    contato          = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pessoa de Contato")
    email            = models.EmailField(max_length=100, null=True, blank=True, verbose_name="E-mail de Contato")
    telefone         = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone de Contato")

    # Para um campo como 'ATIVO', um BooleanField é mais idiomático em Django.
    # True representa 'Ativo' e False representa 'Inativo'.
    ativo            = models.BooleanField(default=True, verbose_name="Ativo", help_text="Indica se o convênio está ativo.")

    qtd_parc_permi   = models.IntegerField(default=1, verbose_name="Parcelas Permitidas", help_text="Quantidade máxima de parcelas permitidas para este convênio.")
    cod_evento       = models.CharField(max_length=20, null=True, blank=True, verbose_name="Código do Evento", help_text="Código de evento relacionado para integração.")

    # O tipo BLOB do banco de dados é melhor representado em Django por um FileField ou ImageField.
    # Isso evita armazenar arquivos grandes no banco de dados.
    # Lembre-se de configurar MEDIA_URL e MEDIA_ROOT no seu settings.py.
    logo             = models.ImageField(upload_to='convenios/logos/', null=True, blank=True, verbose_name="Logo")

    data_cadastro    = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Convênio"
        verbose_name_plural = "Convênios"
        # Ordenar por nome do convênio por padrão
        ordering = ['nome_convenio']

    def __str__(self):
        # Representação amigável para o Django Admin e outras partes do sistema
        return f"{self.nome_convenio} ({self.cnpj})"
#-----------------------------------------------------------------------------------------------------------------------
# EMISSÃO DE CONVENIO
#-----------------------------------------------------------------------------------------------------------------------
class ConvenioEmissao(models.Model):

    # ID (chave primária) será gerado automaticamente pelo Django (id)

    # CPF será digitado e usado para buscar o cliente
    # Não é uma ForeignKey direta aqui, mas um campo CharField para pesquisa
    # A ID_CLIENTE será uma ForeignKey.
    CPF = models.CharField(max_length=14, verbose_name="CPF do Cliente")

    # ID_CLIENTE será preenchido com o id_cliente da model Cliente
    ID_CLIENTE = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT, # Garante que não apague clientes associados a emissões
        related_name='emissoes_convenio',
        verbose_name="ID do Cliente"
    )

    # SALDO será preenchido com o saldo da model Cliente
    SALDO = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Saldo do Cliente")

    MES_REFERENCIA = models.CharField(max_length=7, verbose_name="Mês de Referência",
                                      help_text="Mês e ano de referência (ex: 122023)")

    # ID_CONVENIO será preenchido com o id_convenio da model Convenio
    # Usaremos uma ForeignKey para a model Convenio.
    ID_CONVENIO = models.ForeignKey(
        'Convenio',
        on_delete=models.PROTECT, # Garante que não apague convênios associados a emissões
        related_name='emissoes',
        verbose_name="ID do Convênio"
    )

    # QTD_PARCELA será preenchido com a QTD_PARC_PERMI da model Convenio
    QTD_PARCELA = models.IntegerField(verbose_name="Quantidade de Parcelas")

    VALOR = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total da Transação")

    # DATA_TRANSACAO e HORA_TRANSACAO serão automáticas
    DATA_TRANSACAO = models.DateField(default=timezone.now, verbose_name="Data da Transação")
    HORA_TRANSACAO = models.TimeField(default=timezone.now, verbose_name="Hora da Transação")

    class Meta:
        db_table = 'CONVENIO_EMISSAO' # Define o nome da tabela no banco de dados
        verbose_name = "Emissão de Convênio"
        verbose_name_plural = "Emissões de Convênios"
        ordering = ['-DATA_TRANSACAO', '-HORA_TRANSACAO'] # Ordenar pelas transações mais recentes

    def __str__(self):
        return f"Emissão ID: {self.pk} - Cliente: {self.ID_CLIENTE.cpf_cnpj} - Convênio: {self.ID_CONVENIO.nome_convenio}"

    # Adicione este método para garantir que o ID da emissão possa ser referenciado
    def get_id(self):
        return self.pk

#-----------------------------------------------------------------------------------------------------------------------
# CONVENIO EMISSAO DETALHE
#-----------------------------------------------------------------------------------------------------------------------

class ConvenioEmiDet(models.Model):

    # ID_DET (chave primária) será gerado automaticamente pelo Django (id)

    # ID será uma ForeignKey para ConvenioEmissao
    ID = models.ForeignKey(
        'ConvenioEmissao',
        on_delete=models.CASCADE, # Se a emissão principal for deletada, os detalhes também são
        related_name='detalhes',
        verbose_name="ID da Emissão"
    )

    # ID_CONVENIO será uma ForeignKey para Convenio (se necessário manter a redundância)
    # Geralmente, se ID já referencia a emissão, e a emissão já referencia o convênio,
    # este campo seria redundante aqui. Mas, como é de um sistema legado, estamos incluindo.
    ID_CONVENIO = models.ForeignKey(
        'Convenio',
        on_delete=models.PROTECT, # Garante que não apague convênios se ainda houver detalhes
        related_name='detalhes_emissao',
        verbose_name="ID do Convênio"
    )

    N_PARCELA = models.IntegerField(verbose_name="Número da Parcela")

    DATA_EMISSAO = models.DateTimeField(default=timezone.now, verbose_name="Data e Hora da Emissão")

    DATA_VENCIMENTO = models.DateField(verbose_name="Data de Vencimento")

    # STATUS_PG (Status do Pagamento)
    STATUS_PAGAMENTO_CHOICES = [
        ('A', 'Aberto'), # Usando 'A' para 'Aberto' como padrão
        ('P', 'Pago'),
        ('C', 'Cancelado'),
        # Adicione outros status se houver
    ]
    STATUS_PG = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES,
                                 default='A', verbose_name="Status do Pagamento")

    VALOR_PARCELA = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor da Parcela")

    class Meta:
        db_table = 'CONVENIO_EMI_DET' # Define o nome da tabela no banco de dados
        verbose_name = "Detalhe da Emissão de Convênio"
        verbose_name_plural = "Detalhes da Emissão de Convênio"
        # Garante que não haja parcelas duplicadas para a mesma emissão
        unique_together = ('ID', 'N_PARCELA')
        ordering = ['ID__pk', 'N_PARCELA'] # Ordenar por emissão e número da parcela

    def __str__(self):
        return f"Emissão ID: {self.ID.pk} - Parcela: {self.N_PARCELA} - Valor: {self.VALOR_PARCELA}"

#-----------------------------------------------------------------------------------------------------------------------
# Modelo de Vendas
#-----------------------------------------------------------------------------------------------------------------------
from core.models import Usuario
class Venda(models.Model):
    # id_venda (chave primaria) - Será gerado automaticamente pelo Django (pk)

    # id_usuario (ForeignKey para a tabela de usuários do Django ou sua própria UserProfile)
    # Por simplicidade, vamos usar o User padrão do Django. Certifique-se de importá-lo:
    # from django.contrib.auth.models import User
    # Se você tiver um UserProfile customizado, use-o.
    # Exemplo com User padrão:
    # id_usuario = models.ForeignKey(
    #     'auth.User', # 'auth.User' se você estiver usando o modelo de usuário padrão do Django
    #     on_delete=models.PROTECT,
    #     related_name='vendas_realizadas',
    #     verbose_name="Usuário"
    # )

    id_usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)

    # id_requisicao (chave estrangeira) tabela (convenio_emissao)
    id_requisicao = models.ForeignKey(
        'ConvenioEmissao', # Referencia o seu modelo ConvenioEmissao
        on_delete=models.PROTECT, # Garante que não apague requisições associadas a vendas
        related_name='vendas',
        verbose_name="ID da Requisição (Emissão de Convênio)"
    )

    # id_cliente vai preencher ao buscar a requisição na tabela (convenio_emissao)
    # Embora o cliente já esteja na requisição, é bom ter uma referência direta aqui
    id_cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        related_name='vendas_cliente',
        verbose_name="Cliente"
    )

    # id_convenio (ForeignKey para a tabela Convenio)
    id_convenio = models.ForeignKey(
        'Convenio', # Referencia o seu modelo Convenio
        on_delete=models.PROTECT,
        related_name='vendas',
        verbose_name="Convênio"
    )

    Data_venda = models.DateField(default=timezone.now, verbose_name="Data da Venda")
    Hora_venda = models.TimeField(default=timezone.now, verbose_name="Hora da Venda")
    Valor_venda = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor da Venda")
    Numero_Parcelas = models.IntegerField(verbose_name="Número de Parcelas")

    class Meta:
        db_table = 'VENDAS' # Define o nome da tabela no banco de dados
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-Data_venda', '-Hora_venda'] # Ordenar pelas vendas mais recentes

    def __str__(self):
        return f"Venda ID: {self.pk} - Requisição: {self.id_requisicao.pk} - Cliente: {self.id_cliente.nome_completo}"

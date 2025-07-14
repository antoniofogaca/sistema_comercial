from django import forms
from .models import Cliente,Empresa,Usuario,Setor,Categoria,Grupo,Ncm,Cfop,Cest,CstCson,Produto,ConvenioAbertura,Venda,Convenio,ConvenioEmissao
from django.forms import PasswordInput
import re
from django.utils import timezone # Se for usar timezone.now().year na validação do ano
import datetime
from decimal import Decimal
from django.forms.widgets import NumberInput, DateInput, TimeInput, Select
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'codigo_interno',
            'matricula',
            'cancelado',
            'nome_completo',
            'cpf_cnpj',
            'rg',
            'telefone',
            'email',
            'logradouro',
            'cep',
            'cidade',
            'uf',
            'salario',
            'percentual',
            'saldo',
        ]
        widgets = {
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salario': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'background-color: #e0f7fa;',  # azul claro
                'placeholder': 'R$ 0,00'
            }),
            'percentual': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'background-color: #fff9c4;',  # amarelo claro
                'placeholder': '0%'
            }),
            'saldo': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'background-color: #1565c0; color: white;',  # azul escuro
                'placeholder': 'R$ 0,00',
                'readonly': 'readonly' # <--- Adicione esta linha para tornar o campo somente leitura
            }),
            'cep': forms.TextInput(attrs={ # Adicionado attrs para o campo CEP
                'class': 'form-control',
                'maxlength': '9', # Ex: 00000-000
                'placeholder': '00000-000'
            }),
            'cpf_cnpj': forms.TextInput(attrs={ # Adicionado attrs para o campo CPF/CNPJ
                'class': 'form-control',
                'maxlength': '18', # Ex: 00.000.000/0000-00 ou 000.000.000-00
                'placeholder': '000.000.000-00 ou 00.000.000/0000-00'
            }),
            'telefone': forms.TextInput(attrs={ # Adicionado attrs para o campo Telefone
                'class': 'form-control',
                'maxlength': '20', # Ex: (00) 00000-0000
                'placeholder': '(00) 00000-0000'
            }),
        }

    def clean_cpf_cnpj(self):
        value = self.cleaned_data.get('cpf_cnpj')
        if not value:
            raise forms.ValidationError("CPF/CNPJ é obrigatório.")
        return value

    def clean_nome_completo(self):
        nome = self.cleaned_data.get('nome_completo')
        if not nome:
            raise forms.ValidationError("Nome completo é obrigatório.")
        return nome

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("E-mail é obrigatório.")
        return email

    def clean_uf(self):
        uf = self.cleaned_data.get('uf')
        if not uf:
            raise forms.ValidationError("UF é obrigatório.")
        return uf

    def clean_cidade(self):
        cidade = self.cleaned_data.get('cidade')
        if not cidade:
            raise forms.ValidationError("Cidade é obrigatória.")
        return cidade

    # Opcional: Para garantir que o saldo seja calculado e salvo corretamente no banco de dados,
    # mesmo que o JavaScript falhe ou esteja desativado no navegador do usuário,
    # é uma boa prática recalcular o saldo no método `clean` do formulário.
    def clean(self):
        cleaned_data = super().clean()
        salario = cleaned_data.get('salario')
        percentual = cleaned_data.get('percentual')

        if salario is not None and percentual is not None:
            saldo = salario * (percentual / 100)
            cleaned_data['saldo'] = saldo
        return cleaned_data

# --- NOVO FORMULÁRIO: EmpresaForm ---
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__' # Include all fields from the model
        widgets = {
            'data_abertura': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'porte': forms.Select(attrs={'class': 'form-select'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'codigo_regime_tributario': forms.RadioSelect(attrs={'class': 'form-check-input'}), # Use RadioSelect for radio buttons
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo_loja': 'Código da Loja',
            'cnpj': 'CNPJ',
            'inscricao_estadual': 'Inscrição Estadual',
            'porte': 'Porte da Empresa',
            'situacao': 'Situação Cadastral',
            'data_abertura': 'Data de Abertura',
            'nome_empresa': 'Nome da Empresa',
            'razao_social': 'Razão Social',
            'fantasia': 'Nome Fantasia',
            'contato': 'Nome do Contato',
            'telefone': 'Telefone do Contato',
            'email': 'E-mail do Contato',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'uf': 'UF',
            'cep': 'CEP',
            'cnae_principal': 'CNAE Principal',
            'aliquota_simples': 'Alíquota do Simples Nacional (%)',
            'codigo_regime_tributario': 'Código de Regime Tributário (CRT)',
            'cancelado': 'Empresa Cancelada',
        }

# NOVO FORMULÁRIO: UsuarioForm
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'id_loja': forms.Select(attrs={'class': 'form-control'}), # Se for um Select
            'id_nivel': forms.Select(attrs={'class': 'form-control'}),
            'id_permissao': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'senha': PasswordInput(attrs={'class': 'form-control'}), # Campo de senha mascarado
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'id_loja': 'Loja Associada',
            'id_nivel': 'Nível de Acesso',
            'id_permissao': 'Permissão de Acesso',
            'nome': 'Nome Completo',
            'usuario': 'Nome de Usuário',
            'senha': 'Senha',
            'cancelado': 'Cancelado',
        }

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['codigo', 'descricao', 'cancelado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: DPTO-RH'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Departamento de Recursos Humanos'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo': 'Código',
            'descricao': 'Descrição',
            'cancelado': 'Cancelado',
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['id_cat', 'descricao', 'cancelado']
        widgets = {
            'id_cat': forms.TextInput(attrs={'class': 'form-control' }),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Informática'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'id_cat': 'id_cat',
            'descricao': 'Descrição',
            'cancelado': 'Cancelado',
        }


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['codigo', 'descricao', 'cancelado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: DPTO-RH'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Medicamentos'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'codigo': 'Código',
            'descricao': 'Descrição',
            'cancelado': 'Cancelado',
        }

# --- NOVO FORMULÁRIO: NcmForm ---
class NcmForm(forms.ModelForm):
    class Meta:
        model = Ncm
        fields = '__all__' # Inclui todos os campos do modelo Ncm
        widgets = {
            'ncm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234.56.78'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do NCM'}),
            'inicio_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fim_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2023'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'segmento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Produtos Agrícolas'}),
        }
        labels = {
            'ncm': 'NCM',
            'descricao': 'Descrição do NCM',
            'inicio_vigencia': 'Início da Vigência',
            'fim_vigencia': 'Fim da Vigência',
            'ano': 'Ano',
            'numero': 'Número',
            'cancelado': 'Cancelado',
            'segmento': 'Segmento',
        }


# --- NOVO FORMULÁRIO: CfopForm ---
class CfopForm(forms.ModelForm):
    class Meta:
        model = Cfop
        exclude = ['data_cadastro', 'data_atualizacao']
        #fields = '__all__'  # Inclui todos os campos do modelo Cfop
        widgets = {
            'cfop': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234', 'maxlength': '4'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Entrada de Mercadoria'}),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do CFOP'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # data_cadastro e data_atualizacao são manipulados pelo modelo, não precisam de widget no form se forem readonly/auto
        }
        labels = {
            'cfop': 'CFOP',
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'cancelado': 'Cancelado',
            'data_cadastro': 'Data de Cadastro',
            'data_atualizacao': 'Última Atualização',
        }

    # Exemplo de clean method específico para o CFOP
    def clean_cfop(self):
        cfop = self.cleaned_data.get('cfop')
        if cfop and len(cfop) != 4:
            raise forms.ValidationError("O CFOP deve ter exatamente 4 dígitos.")
        return cfop

# --- NOVO FORMULÁRIO: CestForm ---

class CestForm(forms.ModelForm):
    class Meta:
        model = Cest
        # Adicione 'cancelado' aos campos que não são automaticamente gerenciados ou que você quer expor
        exclude = ['data_cadastro', 'data_atualizacao'] # ou fields = '__all__' se preferir

        widgets = {
            'cd_cest': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 01.001.00', 'maxlength': '9'}),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do CEST'}),
            'cd_ncm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 0123.45.67 (Opcional)', 'maxlength': '300'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # NOVO WIDGET AQUI
        }
        labels = {
            'cd_cest': 'Código CEST',
            'descricao': 'Descrição',
            'cd_ncm': 'Código NCM',
            'cancelado': 'Cancelado', # NOVO LABEL AQUI
            'data_cadastro': 'Data de Cadastro',
            'data_atualizacao': 'Última Atualização',
        }

    def clean_cd_cest(self):
        cd_cest = self.cleaned_data.get('cd_cest')
        cleaned_cest = ''.join(filter(str.isdigit, cd_cest))

        if cd_cest and len(cleaned_cest) != 7 and len(cleaned_cest) != 9:
             raise forms.ValidationError("O Código CEST deve ter 7 ou 9 dígitos numéricos.")
        return cd_cest

# --- NOVO FORMULÁRIO: CstCsonForm ---
class CstCsonForm(forms.ModelForm):
    class Meta:
        model = CstCson
        exclude = ['data_cadastro', 'data_atualizacao']

        widgets = {
            'cd_cst_cson': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 000 ou 101', 'maxlength': '3'}),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição detalhada do CST/CSOSN'}),
            'cd_regime_trib': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1 (SN) ou 3 (Normal)', 'maxlength': '1'}),
            'cancelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'cd_cst_cson': 'Código CST/CSOSN',
            'descricao': 'Descrição',
            'cd_regime_trib': 'Regime Tributário',
            'cancelado': 'Cancelado',
            'data_cadastro': 'Data de Cadastro',
            'data_atualizacao': 'Última Atualização',
        }

    # Exemplo de clean method específico para CD_CST_CSON
    def clean_cd_cst_cson(self):
        cd_cst_cson = self.cleaned_data.get('cd_cst_cson')
        if cd_cst_cson and len(cd_cst_cson) != 3:
            raise forms.ValidationError("O Código CST/CSOSN deve ter exatamente 3 dígitos.")
        if cd_cst_cson and not cd_cst_cson.isdigit():
            raise forms.ValidationError("O Código CST/CSOSN deve conter apenas números.")
        return cd_cst_cson

    # Exemplo de clean method específico para CD_REGIME_TRIB
    def clean_cd_regime_trib(self):
        cd_regime_trib = self.cleaned_data.get('cd_regime_trib')
        if cd_regime_trib not in ['1', '3']:
            raise forms.ValidationError("O Código do Regime Tributário deve ser '1' (Simples Nacional) ou '3' (Regime Normal).")
        return cd_regime_trib

# --- FORMULÁRIO PARA PRODUTO ---

class ProdutoForm(forms.ModelForm):
    SIM_NAO_CHOICES = [
        (True, 'Sim'),
        (False, 'Não'),
    ]

    peso = forms.TypedChoiceField(
        choices=SIM_NAO_CHOICES,
        coerce=lambda x: x == 'True', # Converte a string 'True'/'False' para booleano
        widget=forms.RadioSelect,
        label='Peso',
        required=False
    )
    pode_multiplicar = forms.TypedChoiceField(
        choices=SIM_NAO_CHOICES,
        coerce=lambda x: x == 'True',
        widget=forms.RadioSelect,
        label='Pode Multiplicar',
        required=False
    )
    uso_consumo = forms.TypedChoiceField(
        choices=SIM_NAO_CHOICES,
        coerce=lambda x: x == 'True',
        widget=forms.RadioSelect,
        label='Uso/Consumo',
        required=False
    )

    class Meta:
        model = Produto
        fields = [
            'codigo_ean_dun', 'descricao_produto', 'descricao_pdv', 'unidade_venda',
            'qtd_por_embalagem', 'tipo_produto', 'situacao', 'tipo_tributacao',
            'peso', 'pode_multiplicar', 'uso_consumo',
            'percentual_icms_venda', 'estoque_atual', 'peso_liquido', 'peso_bruto',
            'valor_venda', 'classificacao',
            'id_setor', 'id_grupo', 'id_sub_grupo', 'id_cfop',
            'id_cstcson', 'id_ncm', 'id_cest',
        ]
        widgets = {
            'qtd_por_embalagem': forms.NumberInput(attrs={'step': '0.001'}),
            'percentual_icms_venda': forms.NumberInput(attrs={'step': '0.01'}),
            'estoque_atual': forms.NumberInput(attrs={'step': '0.001'}),
            'peso_liquido': forms.NumberInput(attrs={'step': '0.001'}),
            'peso_bruto': forms.NumberInput(attrs={'step': '0.001'}),
            'valor_venda': forms.NumberInput(attrs={'step': '0.01'}),
            'unidade_venda': forms.Select(attrs={'class': 'form-select'}),
            'tipo_produto': forms.RadioSelect, # Usar RadioSelect para 'Tipo de Produto'
            'situacao': forms.RadioSelect,    # Usar RadioSelect para 'Situação'
            'tipo_tributacao': forms.RadioSelect, # Usar RadioSelect para 'Tipo de Tributação'
            'id_setor': forms.Select(attrs={'class': 'form-select'}),
            'id_grupo': forms.Select(attrs={'class': 'form-select'}),
            'id_sub_grupo': forms.Select(attrs={'class': 'form-select'}),
            'id_cfop': forms.Select(attrs={'class': 'form-select'}),
            'id_cstcson': forms.Select(attrs={'class': 'form-select'}),
            'id_ncm': forms.Select(attrs={'class': 'form-select'}),
            'id_cest': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'codigo_ean_dun': 'Código EAN/DUN',
            'descricao_produto': 'Descrição Produto (Nome - Marca - Modelo - Peso)',
            'descricao_pdv': 'Descrição Produto PDV',
            'unidade_venda': 'Unidade de Venda',
            'qtd_por_embalagem': 'Qtd Por Embalagem',
            'tipo_produto': 'Tipo de Produto',
            'situacao': 'Situação',
            'percentual_icms_venda': '%ICMS Venda',
            'estoque_atual': 'Estoque Atual',
            'peso_liquido': 'Peso Líquido',
            'peso_bruto': 'Peso Bruto',
            'valor_venda': 'Valor Venda',
            'classificacao': 'Classificação',
            'tipo_tributacao': 'Tipo de Tributação',
            'id_setor': 'Setor',
            'id_grupo': 'Grupo',
            'id_sub_grupo': 'Sub-Grupo',
            'id_cfop': 'CFOP',
            'id_cstcson': 'CST/CSOSN',
            'id_ncm': 'NCM',
            'id_cest': 'CEST',
        }

    def clean(self):
        cleaned_data = super().clean()
        uso_consumo = cleaned_data.get('uso_consumo')
        tipo_produto = cleaned_data.get('tipo_produto')
        peso = cleaned_data.get('peso') # Obtenha o valor do campo 'peso'

        # Validações condicionais
        if tipo_produto == 'S': # Se o tipo de produto for 'Serviço'
            if peso: # Se 'Peso' estiver marcado como Sim
                self.add_error('peso', 'Um produto do tipo "Serviço" não deve ter peso.')
            if uso_consumo: # Se 'Uso/Consumo' estiver marcado como Sim
                self.add_error('uso_consumo', 'Um produto do tipo "Serviço" não pode ser de "Uso/Consumo".')

        return cleaned_data


class ConvenioAberturaForm(forms.ModelForm):
    # Não defina os campos de data explicitamente aqui como forms.DateField
    # se eles já são models.DateField no seu modelo. O ModelForm os inferirá.
    # Se você precisar de validações extras, adicione-as no método clean() geral.

    class Meta:
        model = ConvenioAbertura
        fields = [
            'mes_referencia',
            'status',
            'data_abertura',
            'data_fechamento',
            'data_pagamento',
        ]
        widgets = {
            'mes_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM/AAAA'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            # Mantemos como TextInput, mas o campo subjacente do Django
            # (inferido do ModelForm) ainda será um DateField, que valida o formato.
            'data_abertura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AAAA-MM-DD'
            }),
            'data_fechamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AAAA-MM-DD'
            }),
            'data_pagamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AAAA-MM-DD'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Esta lógica é para garantir que o formulário exiba corretamente
        # as datas existentes no formato AAAA-MM-DD, ou vazio se não houver.
        for field_name in ['data_abertura', 'data_fechamento', 'data_pagamento']:
            # Pega o valor inicial do campo, que já é um objeto date/datetime se existir.
            initial_value = self.initial.get(field_name)

            if isinstance(initial_value, (datetime.date, datetime.datetime)):
                # Se for uma data, formata para 'AAAA-MM-DD' para o input
                self.fields[field_name].initial = initial_value.strftime('%Y-%m-%d')
            elif initial_value is None:
                # Se for None, define como string vazia para não exibir 'None'
                self.fields[field_name].initial = ''

    def clean_mes_referencia(self):
        mes_referencia = self.cleaned_data['mes_referencia']
        if not re.match(r'^(0[1-9]|1[0-2])/\d{4}$', mes_referencia):
            raise forms.ValidationError("Formato inválido. Use MM/AAAA (ex: 01/2025).")

        try:
            mes_str, ano_str = mes_referencia.split('/')
            ano_int = int(ano_str)
            # Você pode ajustar o range de anos conforme sua necessidade.
            # Ano atual no Brasil (Porto Velho) é 2025.
            if not (1900 <= ano_int <= datetime.datetime.now(timezone.get_current_timezone()).year + 50):
                raise forms.ValidationError(f"Ano inválido. Por favor, insira um ano entre 1900 e {datetime.datetime.now(timezone.get_current_timezone()).year + 50}.")
        except ValueError:
            raise forms.ValidationError("Formato de ano inválido.")

        return mes_referencia

    # REMOVIDOS os métodos clean_data_abertura, clean_data_fechamento, clean_data_pagamento
    # pois o forms.DateField (inferido do ModelForm) já faz essa validação e conversão.
    # Se o usuário digitar algo inválido no TextInput, o forms.DateField interno
    # capturará o ValueError e adicionará o erro ao formulário.

    def clean(self):
        cleaned_data = super().clean()

        # Agora, data_abertura, data_fechamento e data_pagamento
        # em cleaned_data já serão objetos datetime.date (ou None se o campo não for preenchido
        # e não for obrigatório, ou se a validação do DateField falhou).

        data_abertura = cleaned_data.get('data_abertura')
        data_fechamento = cleaned_data.get('data_fechamento')
        data_pagamento = cleaned_data.get('data_pagamento')

        # Verificações de datas só se todas as datas forem válidas e não nulas.
        # Se data_abertura não for válida (por exemplo, erro de formato), ela pode ser None aqui.
        # Você deve tratar isso se o campo for obrigatório no seu modelo.
        if data_abertura: # Somente se data_abertura foi validada com sucesso como um objeto date
            if data_fechamento and data_fechamento < data_abertura:
                self.add_error('data_fechamento', "A data de fechamento não pode ser anterior à data de abertura.")

            if data_pagamento and data_pagamento < data_abertura:
                self.add_error('data_pagamento', "A data de pagamento não pode ser anterior à data de abertura.")
        # else:
            # Se data_abertura é None aqui e é um campo obrigatório no seu modelo,
            # o erro já terá sido adicionado pelo DateField padrão.
            # Você pode adicionar um erro personalizado se precisar, mas geralmente não é necessário.

        return cleaned_data

class ConvenioForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = '__all__' # Inclui todos os campos do modelo Convenio
        widgets = {
            'cd_loja': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código da Loja'}),
            'nome_convenio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Convênio'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX.XXX.XXX/XXXX-XX', 'data-mask': '00.000.000/0000-00'}), # Adicionado data-mask para formato de CNPJ
            'contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pessoa de Contato'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX ou (XX) XXXXX-XXXX', 'data-mask': '(00) 0000-0000||(00) 00000-0000'}), # Adicionado data-mask para formato de telefone
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'qtd_parc_permi': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12'}),
            'cod_evento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de Evento'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}), # Para upload de arquivos/imagens
        }
        labels = {
            'cd_loja': 'Código da Loja',
            'nome_convenio': 'Nome do Convênio',
            'cnpj': 'CNPJ',
            'contato': 'Pessoa de Contato',
            'email': 'E-mail de Contato',
            'telefone': 'Telefone de Contato',
            'ativo': 'Ativo',
            'qtd_parc_permi': 'Parcelas Permitidas',
            'cod_evento': 'Código do Evento',
            'logo': 'Logo',
        }

#-----------------------------------------------------------------------------------------------------------------------

class ConvenioEmissaoForm(forms.ModelForm):
    # CPF é um CharField no formulário e também no modelo ConvenioEmissao.
    CPF = forms.CharField(label="CPF/CNPJ do Cliente", max_length=18, required=True)

    class Meta:
        model = ConvenioEmissao
        # APENAS OS CAMPOS QUE EXISTEM NO SEU MODELO CONVENIOEMISSAO E SÃO EDITÁVEIS MANUALMENTE
        fields = ['CPF', 'ID_CLIENTE', 'SALDO', 'ID_CONVENIO', 'VALOR',
                  'QTD_PARCELA', 'MES_REFERENCIA']  # Removidos DATA_TRANSACAO e HORA_TRANSACAO
        widgets = {
            'ID_CLIENTE': forms.HiddenInput(),  # Campo oculto para o ID do cliente
            'SALDO': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control text-success'}),
            'CPF': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CPF/CNPJ do cliente'}),
            'MES_REFERENCIA': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AAAAMM (Ex: 202312)'}),
            'VALOR': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'QTD_PARCELA': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            # Tornar readonly se for preenchido via JS
            'ID_CONVENIO': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'CPF': "CPF/CNPJ do Cliente",
            'ID_CLIENTE': "ID Cliente (oculto)",
            'SALDO': "Saldo Disponível",
            'MES_REFERENCIA': "Mês de Referência",
            'ID_CONVENIO': "Convênio",
            'QTD_PARCELA': "Quantidade de Parcelas",
            'VALOR': "Valor Total da Transação",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # Preenche o campo CPF e ID_CLIENTE do formulário se for uma instância existente (edição)
        # E se o ID_CLIENTE não for None nessa instância.
        if self.instance.pk and self.instance.ID_CLIENTE:  # Verifica se a instância já existe (tem PK) e se ID_CLIENTE não é None
            self.initial['CPF'] = self.instance.ID_CLIENTE.cpf_cnpj
            self.initial['ID_CLIENTE'] = self.instance.ID_CLIENTE.pk
            # O SALDO salvo na emissão pode ser diferente do saldo atual do cliente
            # No __init__, pega o que está salvo na instância, o JS pegará o atual
            self.initial['SALDO'] = self.instance.SALDO

        # Aplica classes Bootstrap padrão a campos que ainda não foram definidos nos widgets attrs
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets:  # Aplica apenas se não tem widget customizado
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.Textarea)):
                    field.widget.attrs.update({'class': 'form-control'})
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-select'})

        # Garante que campos somente leitura não sejam obrigatórios na validação do Django
        # Pois serão preenchidos via JS ou são ocultos
        self.fields['ID_CLIENTE'].required = False
        self.fields['SALDO'].required = False
        self.fields['QTD_PARCELA'].required = False  # Será preenchido via JS, não pelo usuário

    def clean(self):
        cleaned_data = super().clean()
        cpf_digitado = cleaned_data.get('CPF')
        id_cliente_from_form_pk = cleaned_data.get('ID_CLIENTE')
        valor = cleaned_data.get('VALOR')
        qtd_parcela = cleaned_data.get('QTD_PARCELA')
        id_convenio_obj = cleaned_data.get('ID_CONVENIO')
        mes_referencia = cleaned_data.get('MES_REFERENCIA')

        cliente_encontrado = None

        # 1. Validar e buscar o cliente pelo CPF/CNPJ digitado
        if cpf_digitado:
            cleaned_cpf_cnpj = ''.join(filter(str.isdigit, cpf_digitado))
            if cleaned_cpf_cnpj:
                try:
                    cliente_encontrado = Cliente.objects.get(cpf_cnpj=cleaned_cpf_cnpj)
                except Cliente.DoesNotExist:
                    self.add_error('CPF',
                                   "CPF/CNPJ do Cliente não encontrado. Por favor, verifique ou cadastre o cliente.")
                except Cliente.MultipleObjectsReturned:
                    self.add_error('CPF', "Múltiplos clientes encontrados com este CPF/CNPJ. Contate o suporte.")
            else:
                self.add_error('CPF', "Por favor, digite um CPF/CNPJ válido.")
        else:
            self.add_error('CPF', "O campo CPF/CNPJ é obrigatório.")

        # 2. Consistência entre CPF digitado e ID_CLIENTE oculto
        # Se cliente_encontrado existe (ou seja, o CPF digitado encontrou um cliente)
        if cliente_encontrado:
            # Se o ID_CLIENTE oculto foi enviado (vindo do JS), verifica consistência
            if id_cliente_from_form_pk:
                id_cliente_pk = id_cliente_from_form_pk.pk if hasattr(id_cliente_from_form_pk, 'pk') else int(
                    id_cliente_from_form_pk)
                if cliente_encontrado.pk != id_cliente_pk:
                    self.add_error(None, "Inconsistência: O CPF/CNPJ digitado não corresponde ao cliente selecionado.")

            # Atualiza os dados no cleaned_data com base no cliente encontrado
            cleaned_data['ID_CLIENTE'] = cliente_encontrado
            cleaned_data['CPF'] = cliente_encontrado.cpf_cnpj
            cleaned_data['SALDO'] = cliente_encontrado.saldo  # O saldo a ser salvo na emissão
        elif id_cliente_from_form_pk:
            # Se ID_CLIENTE veio do JS mas o CPF não encontrou (ou não foi digitado) um cliente correspondente
            try:
                cliente_via_id = Cliente.objects.get(pk=id_cliente_from_form_pk)
                cleaned_data['ID_CLIENTE'] = cliente_via_id
                cleaned_data['CPF'] = cliente_via_id.cpf_cnpj
                cleaned_data['SALDO'] = cliente_via_id.saldo
            except Cliente.DoesNotExist:
                self.add_error('ID_CLIENTE', "ID do Cliente inválido ou não encontrado.")
        else:
            # Só adiciona erro se for uma submissão de um novo formulário ou edição sem ID_CLIENTE válido
            # Se ID_CLIENTE é um campo obrigatório no modelo (null=False), essa validação é crucial aqui.
            if not id_cliente_from_form_pk:  # Se nenhum ID_CLIENTE foi fornecido
                self.add_error('ID_CLIENTE',
                               "Nenhum cliente válido associado. Por favor, digite um CPF/CNPJ e selecione um cliente.")

        # 3. Validação de Mês de Referência (Formato MMAAAA)
        if mes_referencia:
            mes_referencia = mes_referencia.strip().replace(' ', '')
            if '/' not in mes_referencia:
                self.add_error('MES_REFERENCIA', "Formato inválido. Use MM/AAAA (Ex: 07/2025).")
            else:
                try:
                    mes, ano = mes_referencia.split('/')
                    if len(mes) != 2 or len(ano) != 4 or not mes.isdigit() or not ano.isdigit():
                        raise ValueError
                    mes_int = int(mes)
                    ano_int = int(ano)
                    if not (1 <= mes_int <= 12 and 1900 <= ano_int <= 2100):
                        raise ValueError
                    # Grava no formato MMYYYY
                    cleaned_data['MES_REFERENCIA'] = f"{mes}{ano}"
                except ValueError:
                    self.add_error('MES_REFERENCIA', "Formato inválido. Use MM/AAAA (Ex: 07/2025).")
        else:
            self.add_error('MES_REFERENCIA', "O Mês de Referência é obrigatório.")

        # 4. Validação do valor em relação ao saldo do cliente *no momento da transação*
        if valor is not None:
            if valor <= 0:
                self.add_error('VALOR', "O valor da transação deve ser maior que zero.")
            # Validar contra o saldo ATUAL do cliente (cliente_encontrado.saldo)
            elif cliente_encontrado and valor > cliente_encontrado.saldo:
                self.add_error('VALOR',
                               f"Valor da transação (R$ {valor:.2f}) excede o saldo disponível do cliente (R$ {cliente_encontrado.saldo:.2f}).")
        else:
            self.add_error('VALOR', "O valor do convênio é obrigatório.")

        # 5. Validação da QTD_PARCELA em relação ao convênio
        if qtd_parcela is not None:
            if qtd_parcela <= 0:
                self.add_error('QTD_PARCELA', "A quantidade de parcelas deve ser maior que zero.")
            # Assume que 'Convenio' tem um campo 'qtd_parc_permi'
            elif id_convenio_obj and hasattr(id_convenio_obj,
                                             'qtd_parc_permi') and qtd_parcela > id_convenio_obj.qtd_parc_permi:
                self.add_error('QTD_PARCELA',
                               f"Quantidade de parcelas excede o limite permitido para este convênio ({id_convenio_obj.qtd_parc_permi}).")
        else:
            # QTD_PARCELA é preenchido via JS, mas pode ser nulo se JS falhar
            self.add_error('QTD_PARCELA', "A quantidade de parcelas é obrigatória.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Para o caso de criação (não edição), garante que data/hora sejam preenchidos
        if not instance.DATA_TRANSACAO:
            instance.DATA_TRANSACAO = timezone.now().date()

        if not instance.HORA_TRANSACAO:
            instance.HORA_TRANSACAO = timezone.now().time()

        return super().save(commit=commit)


#---------------------------------------------------------------------------------------------------------------
# Formulário de Vendas
#---------------------------------------------------------------------------------------------------------------

class VendaForm(forms.ModelForm):
    # Campo para o CPF do Cliente (não é um campo do modelo Venda, mas é usado para busca)
    cpf_cliente_busca = forms.CharField(
        label="CPF/CNPJ do Cliente",
        max_length=18,  # Para incluir máscara (000.000.000-00 ou 00.000.000/0000-00)
        required=True,
        help_text="Digite o CPF/CNPJ do cliente para buscar a requisição."
    )
    # Campo para o nome do cliente, que será preenchido automaticamente
    nome_cliente_exibicao = forms.CharField(
        label="Nome do Cliente",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    # Campo para o número da requisição (ID da ConvenioEmissao)
    numero_requisicao_busca = forms.IntegerField(
        label="Número da Requisição",
        required=True,
        help_text="Digite o ID da requisição (Emissão de Convênio)."
    )

    class Meta:
        model = Venda
        fields = [
            'id_usuario',  # Será preenchido na view com o usuário logado
            'id_requisicao',
            'id_cliente',
            'id_convenio',
            'Data_venda',
            'Hora_venda',
            'Valor_venda',
            'Numero_Parcelas',
        ]
        widgets = {
            'id_requisicao': forms.HiddenInput(),  # Campo hidden, preenchido via JS/backend
            'id_cliente': forms.HiddenInput(),  # Campo hidden, preenchido via JS/backend
            'id_convenio': forms.HiddenInput(),  # Campo hidden, preenchido via JS/backend
            'Data_venda': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Hora_venda': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'Valor_venda': NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'Numero_Parcelas': NumberInput(attrs={'min': '1', 'max': '12', 'class': 'form-control'}),
            # Ou Select se preferir dropdown
            # 'Numero_Parcelas': Select(choices=[(i, str(i)) for i in range(1, 13)], attrs={'class': 'form-control'}), # Se for dropdown
        }
        labels = {
            'id_requisicao': 'Requisição',  # Rótulo para display, embora seja hidden
            'id_cliente': 'Cliente',
            'id_convenio': 'Convênio',
        }

    # Custom clean method para validação de campos não-modelo e para associar IDs
    def clean(self):
        cleaned_data = super().clean()
        cpf_cliente_busca = cleaned_data.get('cpf_cliente_busca')
        numero_requisicao_busca = cleaned_data.get('numero_requisicao_busca')

        # Validação do CPF e busca do cliente
        if cpf_cliente_busca:
            cpf_cleaned = ''.join(filter(str.isdigit, cpf_cliente_busca))
            try:
                cliente_encontrado = Cliente.objects.get(cpf_cnpj=cpf_cleaned)
                cleaned_data['id_cliente'] = cliente_encontrado
            except Cliente.DoesNotExist:
                self.add_error('cpf_cliente_busca', 'Cliente não encontrado com o CPF/CNPJ informado.')
            except Exception as e:
                self.add_error('cpf_cliente_busca', f'Erro ao buscar cliente: {e}')

        # Validação da Requisição e associação de Cliente e Convênio
        if numero_requisicao_busca:
            try:
                requisicao_encontrada = ConvenioEmissao.objects.get(pk=numero_requisicao_busca)
                cleaned_data['id_requisicao'] = requisicao_encontrada
                # Preenche id_cliente e id_convenio com base na requisição
                cleaned_data['id_cliente'] = requisicao_encontrada.ID_CLIENTE
                cleaned_data['id_convenio'] = requisicao_encontrada.ID_CONVENIO
            except ConvenioEmissao.DoesNotExist:
                self.add_error('numero_requisicao_busca',
                               'Requisição de Convênio não encontrada com o ID informado.')
            except Exception as e:
                self.add_error('numero_requisicao_busca', f'Erro ao buscar requisição: {e}')

        return cleaned_data
Receita de Bolo: Criando um Novo Módulo no Django (Passo a Passo) 🍰
Este guia vai te mostrar como adicionar uma nova funcionalidade (um "módulo") ao seu projeto Django, cobrindo os arquivos essenciais e a ordem das ações. Vamos usar um exemplo genérico de um modelo chamado Item.

Módulo: Item
Nosso objetivo é criar um módulo completo para Item, permitindo listar, criar, editar e excluir itens.

Passo 1: Definição do Modelo (Model) 🏛️
Tudo começa com a estrutura dos dados. Você define como o seu Item será armazenado no banco de dados.

Arquivo: core/models.py
O que fazer: Crie a classe do seu modelo Item que herda de models.Model.
Python

# core/models.py

from django.db import models

# Seus modelos existentes...
# class Cliente(models.Model):
#    ...

# class Empresa(models.Model):
#    ...

class Item(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ['nome'] # Opcional: define uma ordenação padrão

    def __str__(self):
        return self.nome

    # Método para URL de detalhe, se for usar (opcional neste guia, mas boa prática)
    # from django.urls import reverse
    # def get_absolute_url(self):
    #     return reverse('item_detail', kwargs={'pk': self.pk})

Passo 2: Gerar e Aplicar Migrações 🔄
Após definir o modelo, você precisa informar ao Django para criar a tabela correspondente no banco de dados.

Local: Terminal (na raiz do seu projeto Django, onde está manage.py)

Comandos:

Bash

python manage.py makemigrations core
python manage.py migrate
O que faz:

makemigrations core: Cria um arquivo em core/migrations/ que descreve as mudanças no seu modelo.
migrate: Aplica essas mudanças ao banco de dados (cria a tabela Item).
Passo 3: Criação do Formulário (Form) 📝
Para interagir com o seu modelo (criar/editar), você precisa de um formulário.

Arquivo: core/forms.py
O que fazer: Crie a classe do seu formulário, herdando de forms.ModelForm.
Python

# core/forms.py

from django import forms
from .models import Cliente, Empresa, Usuario, Item # <-- Importe o novo modelo Item

# Seus formulários existentes...
# class ClienteForm(forms.ModelForm):
#    ...

# class EmpresaForm(forms.ModelForm):
#    ...

# class UsuarioForm(forms.ModelForm):
#    ...

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'descricao', 'preco', 'ativo']
        # ou fields = '__all__' para incluir todos os campos
        # ou exclude = ['data_cadastro'] para excluir campos específicos

    # Opcional: Customizações do formulário, como adicionar classes CSS
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or \
               isinstance(field.widget, forms.Textarea) or \
               isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})

Passo 4: Implementação das Views (Funções de Lógica) 🖥️
As views são as funções que processam as requisições e retornam as respostas (HTML, redirecionamentos, etc.).

Arquivo: core/views.py
O que fazer: Adicione as views para listar, criar, editar e excluir Item.
Python

# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages # Importe messages
from django.http import JsonResponse
from .models import Cliente, Empresa, Usuario, Item # <-- Importe o novo modelo Item
from .forms import ClienteForm, EmpresaForm, UsuarioForm, ItemForm # <-- Importe o novo formulário ItemForm

# ... (Suas views existentes de home, usuarios, clientes, empresas, produtos, convenios) ...

# --- NOVAS VIEWS PARA ITEM ---

def item_list(request):
    search = request.GET.get('search', '')
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10

    sort = request.GET.get('sort', 'nome') # Ordenação padrão para Item
    order = request.GET.get('order', 'asc')
    page_number = request.GET.get('page')
    status_filter = request.GET.get('status', 'all')

    itens = Item.objects.all()

    if search:
        itens = itens.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )

    if status_filter == 'ativo':
        itens = itens.filter(ativo=True)
    elif status_filter == 'inativo': # Considere um status 'inativo' para o booleano 'ativo'
        itens = itens.filter(ativo=False)

    if order == 'desc':
        itens = itens.order_by(f'-{sort.replace("-", "")}')
    else:
        itens = itens.order_by(sort.replace("-", ""))

    paginator = Paginator(itens, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'sort': sort.replace('-', ''),
        'order': order,
        'status_filter': status_filter,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'core/item_table_partial.html', context)
    else:
        return render(request, 'core/item_list.html', context)

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item criado com sucesso!')
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'core/item_form.html', {'form': form, 'title': 'Novo Item'})

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item atualizado com sucesso!')
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'core/item_form.html', {'form': form, 'title': 'Editar Item'})

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item excluído com sucesso!')
        return redirect('item_list')
    return render(request, 'core/item_confirm_delete.html', {'object': item})

Passo 5: Definição das Rotas (URLs) 🗺️
As URLs mapeiam os caminhos da web para as suas views.

Arquivo: core/urls.py
O que fazer: Adicione as novas rotas para o módulo Item.
Python

# core/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    # ... (Suas URLs existentes) ...

    # Módulo de Usuários
    path('usuarios/', views.usuario_list, name='usuarios_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.usuario_update, name='usuario_update'),
    path('usuarios/excluir/<int:pk>/', views.usuario_delete, name='usuario_delete'),

    # Módulo de Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),

    # --- NOVO MÓDULO: Itens ---
    path('itens/', views.item_list, name='item_list'),
    path('itens/novo/', views.item_create, name='item_create'),
    path('itens/<int:pk>/editar/', views.item_update, name='item_update'),
    path('itens/<int:pk>/excluir/', views.item_delete, name='item_delete'),

    # Produtos (apenas se for um item genérico, senão, pode renomear)
    # path('produtos/', views.produtos, name='produtos'), # Mantenha ou remova dependendo da sua intenção com "Itens"

    # Convênios
    # path('convenios/', views.convenios, name='convenios'), # Mantenha

    # Login
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'), # Mantenha
]
Passo 6: Criação dos Templates HTML (Interface do Usuário) 🎨
Aqui você define como os dados serão exibidos e como o usuário irá interagir.

Pasta: core/templates/core/
O que fazer: Crie os arquivos HTML para cada view.
a) core/templates/core/item_list.html (Lista de Itens)
Este será o template principal que exibe a lista de itens e inclui o template parcial da tabela.

HTML

{% extends 'base.html' %}
{% load static %}
{% load widget_tweaks %}

{% block title %}Lista de Itens{% endblock %}

{% block content %}
    <h1 class="mb-4">Itens</h1>

    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="card-title mb-0">Gerenciar Itens</h5>
                <a href="{% url 'item_create' %}" class="btn btn-primary btn-sm">
                    <i class="bi bi-plus-circle"></i> Novo Item
                </a>
            </div>

            <form id="search-form" method="GET" action="{% url 'item_list' %}" class="mb-3">
                <div class="row g-3 align-items-center">
                    <div class="col-md-4">
                        <label for="search" class="form-label visually-hidden">Pesquisar</label>
                        <input type="text" class="form-control" id="search" name="search" placeholder="Pesquisar por nome ou descrição..." value="{{ search }}">
                    </div>
                    <div class="col-md-3">
                        <label for="status" class="form-label visually-hidden">Status</label>
                        <select class="form-select" id="status" name="status">
                            <option value="all" {% if status_filter == 'all' %}selected{% endif %}>Todos os Status</option>
                            <option value="ativo" {% if status_filter == 'ativo' %}selected{% endif %}>Ativos</option>
                            <option value="inativo" {% if status_filter == 'inativo' %}selected{% endif %}>Inativos</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label for="per_page" class="form-label visually-hidden">Itens por Página</label>
                        <select class="form-select" id="per_page" name="per_page">
                            <option value="5" {% if per_page == 5 %}selected{% endif %}>5</option>
                            <option value="10" {% if per_page == 10 %}selected{% endif %}>10</option>
                            <option value="20" {% if per_page == 20 %}selected{% endif %}>20</option>
                            <option value="50" {% if per_page == 50 %}selected{% endif %}>50</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-dark w-100"><i class="bi bi-filter"></i> Filtrar</button>
                    </div>
                </div>
            </form>

            <div id="item-table-container">
                {% include 'core/item_table_partial.html' %}
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchForm = document.getElementById('search-form');
            const itemTableContainer = document.getElementById('item-table-container');

            searchForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Impede o envio tradicional do formulário
                const formData = new FormData(searchForm);
                const queryString = new URLSearchParams(formData).toString();
                const url = `{% url 'item_list' %}?${queryString}`;

                fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest' // Indica que é uma requisição AJAX
                    }
                })
                .then(response => response.text())
                .then(html => {
                    itemTableContainer.innerHTML = html;
                    // Atualiza a URL no navegador sem recarregar a página
                    window.history.pushState(null, '', url);
                })
                .catch(error => console.error('Erro ao buscar itens:', error));
            });

            // Lidar com cliques na paginação AJAX (delegando para o container da tabela)
            itemTableContainer.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && e.target.closest('.pagination')) {
                    e.preventDefault();
                    const url = e.target.href;
                    fetch(url, {
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    })
                    .then(response => response.text())
                    .then(html => {
                        itemTableContainer.innerHTML = html;
                        window.history.pushState(null, '', url);
                    })
                    .catch(error => console.error('Erro na paginação AJAX:', error));
                }
            });

            // Lidar com cliques nos cabeçalhos de ordenação AJAX
            itemTableContainer.addEventListener('click', function(e) {
                if (e.target.closest('.sortable-header')) {
                    e.preventDefault();
                    const url = e.target.closest('.sortable-header').href;
                    fetch(url, {
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    })
                    .then(response => response.text())
                    .then(html => {
                        itemTableContainer.innerHTML = html;
                        window.history.pushState(null, '', url);
                    })
                    .catch(error => console.error('Erro na ordenação AJAX:', error));
                }
            });
        });
    </script>
{% endblock %}
b) core/templates/core/item_table_partial.html (Tabela Parcial de Itens para AJAX)
Este é o trecho HTML que a requisição AJAX carrega quando o filtro ou a paginação é acionada.

HTML

<div class="table-responsive">
    <table class="table table-hover table-striped">
        <thead>
            <tr>
                <th>
                    <a href="{% url 'item_list' %}?search={{ search }}&per_page={{ per_page }}&status={{ status_filter }}&sort=nome{% if sort == 'nome' and order == 'asc' %}&order=desc{% else %}&order=asc{% endif %}" class="sortable-header text-decoration-none text-dark">
                        Nome
                        {% if sort == 'nome' %}
                            {% if order == 'asc' %}<i class="bi bi-caret-up-fill"></i>{% else %}<i class="bi bi-caret-down-fill"></i>{% endif %}
                        {% endif %}
                    </a>
                </th>
                <th>Descrição</th>
                <th>
                    <a href="{% url 'item_list' %}?search={{ search }}&per_page={{ per_page }}&status={{ status_filter }}&sort=preco{% if sort == 'preco' and order == 'asc' %}&order=desc{% else %}&order=asc{% endif %}" class="sortable-header text-decoration-none text-dark">
                        Preço
                        {% if sort == 'preco' %}
                            {% if order == 'asc' %}<i class="bi bi-caret-up-fill"></i>{% else %}<i class="bi bi-caret-down-fill"></i>{% endif %}
                        {% endif %}
                    </a>
                </th>
                <th>Status</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for item in page_obj %}
                <tr>
                    <td>{{ item.nome }}</td>
                    <td>{{ item.descricao|default:"N/A" }}</td>
                    <td>R$ {{ item.preco|floatformat:2 }}</td>
                    <td>
                        {% if item.ativo %}
                            <span class="badge bg-success">Ativo</span>
                        {% else %}
                            <span class="badge bg-danger">Inativo</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{% url 'item_update' item.pk %}" class="btn btn-sm btn-info me-2" title="Editar">
                            <i class="bi bi-pencil-square"></i>
                        </a>
                        <a href="{% url 'item_delete' item.pk %}" class="btn btn-sm btn-danger" title="Excluir">
                            <i class="bi bi-trash"></i>
                        </a>
                    </td>
                </tr>
            {% empty %}
                <tr>
                    <td colspan="5" class="text-center">Nenhum item encontrado.</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<nav aria-label="Navegação da lista de itens">
    <ul class="pagination justify-content-center">
        {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="{% url 'item_list' %}?page={{ page_obj.previous_page_number }}&search={{ search }}&per_page={{ per_page }}&sort={{ sort }}&order={{ order }}&status={{ status_filter }}">Anterior</a>
            </li>
        {% endif %}

        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}
                <li class="page-item active"><span class="page-link">{{ num }}</span></li>
            {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item">
                    <a class="page-link" href="{% url 'item_list' %}?page={{ num }}&search={{ search }}&per_page={{ per_page }}&sort={{ sort }}&order={{ order }}&status={{ status_filter }}">{{ num }}</a>
                </li>
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="{% url 'item_list' %}?page={{ page_obj.next_page_number }}&search={{ search }}&per_page={{ per_page }}&sort={{ sort }}&order={{ order }}&status={{ status_filter }}">Próxima</a>
            </li>
        {% endif %}
    </ul>
</nav>

c) core/templates/core/item_form.html (Formulário de Criação/Edição)
HTML

{% extends 'base.html' %}
{% load static %}
{% load widget_tweaks %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
    <h1 class="mb-4">{{ title }}</h1>

    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <form method="POST">
                {% csrf_token %}

                {% for field in form %}
                    <div class="mb-3">
                        <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}</label>
                        {% if field.field.widget.input_type == 'checkbox' %}
                            <div class="form-check form-switch">
                                {{ field|add_class:"form-check-input" }}
                                <label class="form-check-label" for="{{ field.id_for_label }}">{{ field.label }}</label>
                            </div>
                        {% else %}
                            {{ field|add_class:"form-control" }}
                        {% endif %}
                        {% for error in field.errors %}
                            <div class="invalid-feedback d-block">{{ error }}</div>
                        {% endfor %}
                    </div>
                {% endfor %}

                <a href="{% url 'item_list' %}" class="btn btn-secondary me-2">Voltar</a>
                <button type="submit" class="btn btn-primary">Salvar</button>
            </form>
        </div>
    </div>
{% endblock %}

d) core/templates/core/item_confirm_delete.html (Confirmação de Exclusão)
HTML

{% extends 'base.html' %}
{% load static %}

{% block title %}Excluir Item{% endblock %}

{% block content %}
    <h1 class="mb-4">Excluir Item</h1>

    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <p>Você tem certeza que deseja excluir o item "<strong>{{ object.nome }}</strong>"?</p>
            <form method="POST">
                {% csrf_token %}
                <a href="{% url 'item_list' %}" class="btn btn-secondary me-2">Cancelar</a>
                <button type="submit" class="btn btn-danger">Confirmar Exclusão</button>
            </form>
        </div>
    </div>
{% endblock %}

Passo 7: Adicionar o Link ao Menu (Base Template) 🔗
Para que o usuário possa navegar para o seu novo módulo.

Arquivo: base.html (ou o arquivo do seu sidebar/menu)
O que fazer: Adicione um novo item de menu para Itens.
HTML

<a href="{% url 'clientes_list' %}" class="{% if request.path|slice:'0:9' == '/clientes' %}active{% endif %}">
                <i class="bi bi-people"></i> <span>Clientes</span>
            </a>
            <a href="{% url 'empresas_list' %}" class="{% if request.path|slice:'0:9' == '/empresas' %}active{% endif %}"> {# Ajustado para pegar /empresas/novo/etc também #}
                <i class="bi bi-building"></i> <span>Empresas</span>
            </a>
            <a href="{% url 'item_list' %}" class="{% if request.path|slice:'0:6' == '/itens' %}active{% endif %}"> {# NOVO LINK PARA ITENS #}
                <i class="bi bi-box"></i> <span>Itens</span>
            </a>
            <a href="{% url 'produtos' %}" class="{% if request.path == '/produtos/' %}active{% endif %}">
                <i class="bi bi-box"></i> <span>Produtos</span>
            </a>
Nota sobre |slice:'0:6' == '/itens': Usamos '0:6' porque /itens tem 6 caracteres. Se você tiver URLs como /itens/novo/, isso garantirá que o item do menu continue ativo.

Resumo da Receita 📝
models.py: Defina a estrutura do seu novo dado.
Terminal: Execute makemigrations e migrate.
forms.py: Crie o formulário para criar/editar esse dado.
views.py: Implemente as funções para listar, criar, editar e excluir. Lembre-se de importar o modelo e o formulário aqui!
urls.py: Mapeie as URLs para as suas views.
templates/core/: Crie os arquivos HTML para cada view (_list.html, _form.html, _confirm_delete.html, e o _table_partial.html para AJAX).
base.html: Adicione o link para o novo módulo no seu menu de navegação.
Sempre siga essa ordem lógica, e você terá um fluxo de trabalho claro para adicionar novas funcionalidades ao seu projeto Django. Essa "receita" é a base para a maioria das operações CRUD (Create, Read, Update, Delete) em Django.
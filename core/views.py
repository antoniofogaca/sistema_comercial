# core/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Cliente, Empresa, Usuario, Setor, Categoria, Grupo, Ncm, Cfop, Cest, CstCson, Produto, \
    ConvenioAbertura, Convenio, ConvenioEmissao
from .forms import ClienteForm,EmpresaForm,UsuarioForm,SetorForm,CategoriaForm,GrupoForm,NcmForm,CfopForm,CestForm,CstCsonForm,ProdutoForm,ConvenioAberturaForm,ConvenioForm,ConvenioEmissaoForm
from django.contrib import messages
from django.http import JsonResponse # Para AJAX
from django.template.loader import render_to_string
from django.db import transaction
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt  # Cuidado com CSRF em APIs, considere outras proteções
from django.utils import timezone
from datetime import timedelta, date
import calendar  # Para calcular o último dia do mês
from django.views.decorators.http import require_http_methods, require_GET

# Páginas estáticas
def home(request):
    return render(request, 'core/home.html')

def empresas(request):
    return render(request, 'core/empresas.html')

def produtos(request):
    return render(request, 'core/produtos.html')

def convenios(request):
    return render(request, 'core/convenios.html')

# Redirecionamento antigo
def clientes(request):
    return redirect('core:clientes_list')

# View dinâmica com filtro, ordenação e paginação
def clientes_list(request):
    search = request.GET.get('search', '')
    # Tenta converter per_page para int, com fallback seguro para 10
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10 # Define um valor padrão seguro em caso de erro na conversão

    sort = request.GET.get('sort', 'nome_completo')
    order = request.GET.get('order', 'asc')
    page_number = request.GET.get('page')
    status_filter = request.GET.get('status', 'all') # NOVO: Obter parâmetro de status

    # Iniciar a queryset
    clientes = Cliente.objects.all()

    # --- Lógica de Filtro por Nome/CPF/CNPJ ---
    if search:
        clientes = clientes.filter(
            Q(nome_completo__icontains=search) |
            Q(cpf_cnpj__icontains=search)
        )

    # --- Lógica de Filtro por Status ---
    if status_filter == 'ativo':
        clientes = clientes.filter(cancelado=False)
    elif status_filter == 'cancelado':
        clientes = clientes.filter(cancelado=True)

    # --- Lógica de Ordenação ---
    # Para garantir que a ordenação descendente funcione corretamente com o '-'
    # E para evitar duplicidade de '-' caso o parâmetro 'sort' já venha com ele (improvável, mas boa prática)
    if sort.startswith('-'):
        clean_sort = sort[1:]
    else:
        clean_sort = sort

    if order == 'desc':
        clientes = clientes.order_by(f'-{clean_sort}')
    else:
        clientes = clientes.order_by(clean_sort)


    # Paginação
    paginator = Paginator(clientes, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'sort': sort.replace('-', ''), # Passa o nome do campo sem o '-' para o template (para os links de ordenação)
        'order': order,
        'status_filter': status_filter, # NOVO: Passar o status atual para o template
    }

    # AJAX - Retorna apenas a tabela (HTML parcial)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'core/clientes_table_partial.html', context)
    else:
        return render(request, 'core/clientes_list.html', context)

# CRUD Cliente
# ... (restante do seu código CRUD para cliente_create, cliente_update, cliente_delete permanece o mesmo)
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            # Adicionar mensagem de sucesso
            from django.contrib import messages
            messages.success(request, 'Cliente criado com sucesso!')
            return redirect('core:clientes_list')
    else:
        form = ClienteForm()
    return render(request, 'core/clientes_form.html', {'form': form, 'title': 'Novo Cliente'})

def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            # Adicionar mensagem de sucesso
            from django.contrib import messages
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('core:clientes_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'core/clientes_form.html', {'form': form, 'title': 'Editar Cliente'})

def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        # Adicionar mensagem de sucesso
        from django.contrib import messages
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('core:clientes_list')
    return render(request, 'core/clientes_confirm_delete.html', {'cliente': cliente})


# --- NOVAS VIEWS PARA EMPRESA ---
def empresas_list(request):
    search = request.GET.get('search', '')
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10

    sort = request.GET.get('sort', 'fantasia') # Default sort for Empresa
    order = request.GET.get('order', 'asc')
    page_number = request.GET.get('page')
    status_filter = request.GET.get('status', 'all')

    empresas = Empresa.objects.all()

    if search:
        empresas = empresas.filter(
            Q(fantasia__icontains=search) |
            Q(razao_social__icontains=search) |
            Q(cnpj__icontains=search) |
            Q(logradouro__icontains=search)
        )

    # Filter by 'cancelado' status
    if status_filter == 'ativo':
        empresas = empresas.filter(cancelado=False)
    elif status_filter == 'cancelado':
        empresas = empresas.filter(cancelado=True)

    # Sorting logic
    if order == 'desc':
        empresas = empresas.order_by(f'-{sort.replace("-", "")}')
    else:
        empresas = empresas.order_by(sort.replace("-", ""))

    paginator = Paginator(empresas, per_page)
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
        return render(request, 'core/empresas_table_partial.html', context)
    else:
        return render(request, 'core/empresas_list.html', context)


def empresa_create(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa criada com sucesso!')
            return redirect('core:empresas_list')
    else:
        form = EmpresaForm()
    return render(request, 'core/empresas_form.html', {'form': form, 'title': 'Nova Empresa'})

def empresa_update(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa atualizada com sucesso!')
            return redirect('core:empresas_list')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'core/empresas_form.html', {'form': form, 'title': 'Editar Empresa'})

def empresa_delete(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'Empresa excluída com sucesso!')
        return redirect('core:empresas_list')
    return render(request, 'core/empresas_confirm_delete.html', {'empresa': empresa})

# --- NOVAS Views de Usuário ---

def usuario_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status') # 'ativo' ou 'cancelado'
    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(Q(nome__icontains=query) | Q(usuario__icontains=query))
    if status_filter == 'ativo':
        usuarios = usuarios.filter(cancelado=False)
    elif status_filter == 'cancelado':
        usuarios = usuarios.filter(cancelado=True)

    paginator = Paginator(usuarios, 10) # 10 usuários por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Verifica se a requisição é AJAX para retornar apenas a tabela
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render(request, 'core/usuario_list_table.html', {'page_obj': page_obj})
        return JsonResponse({'html': html.content.decode('utf-8')})

    return render(request, 'core/usuario_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter
    })

def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('core:usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'core/usuario_form.html', {'form': form, 'form_title': 'Novo Usuário'})

def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('core:usuarios_list')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'core/usuario_form.html', {'form': form, 'form_title': 'Editar Usuário'})

def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('core:usuarios_list')
    return render(request, 'core/usuario_confirm_delete.html', {'object': usuario})

# View para listar setores
# @login_required # Removido/comentado conforme solicitado
def setor_list(request):
    setores_list = Setor.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'descricao')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        setores_list = setores_list.filter(Q(codigo__icontains=search_query) | Q(descricao__icontains=search_query))

    if status_filter != 'all':
        setores_list = setores_list.filter(cancelado=(status_filter == 'cancelado'))

    # Ordenação
    if sort_by:
        allowed_sort_fields = ['codigo', 'descricao', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            setores_list = setores_list.order_by(sort_by)
        else:
            setores_list = setores_list.order_by('descricao') # Fallback padrão

    paginator = Paginator(setores_list, per_page)
    page_number = request.GET.get('page')

    try:
        setores = paginator.page(page_number)
    except PageNotAnInteger:
        setores = paginator.page(1)
    except EmptyPage:
        setores = paginator.page(paginator.num_pages)

    context = {
        'setores': setores,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/setor_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/setor_list.html', context)

# View para criar um novo setor
# @login_required # Removido/comentado conforme solicitado
def setor_create(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Setor cadastrado com sucesso!")
            return redirect('core:setor_list')
    else:
        form = SetorForm()
    return render(request, 'core/setor_form.html', {'form': form, 'title': 'Novo Setor'})

# View para atualizar um setor existente
# @login_required # Removido/comentado conforme solicitado
def setor_update(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, "Setor atualizado com sucesso!")
            return redirect('core:setor_list')
    else:
        form = SetorForm(instance=setor)
    return render(request, 'core/setor_form.html', {'form': form, 'title': 'Editar Setor'})

# View para confirmar exclusão de um setor
# @login_required # Removido/comentado conforme solicitado
def setor_confirm_delete(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    return render(request, 'core/setor_confirm_delete.html', {'setor': setor})

# View para excluir um setor (POST request)
# @login_required # Removido/comentado conforme solicitado
def setor_delete(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    if request.method == 'POST':
        setor.delete()
        messages.success(request, "Setor excluído com sucesso!")
        return redirect('core:setor_list')
    # Redireciona de volta para a lista se não for uma requisição POST
    return redirect('core:setor_list')

#-------------------------------------------------------------------------------
# View para listar categorias
# @login_required # Removido/comentado conforme solicitado
def categoria_list(request):
    categorias_list = Categoria.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'descricao')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        categorias_list = categorias_list.filter(Q(id_cat__icontains=search_query) | Q(descricao__icontains=search_query))

    if status_filter != 'all':
        categorias_list = categorias_list.filter(cancelado=(status_filter == 'cancelado'))

    # Ordenação
    if sort_by:
        allowed_sort_fields = ['id_cat', 'descricao', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            categorias_list = categorias_list.order_by(sort_by)
        else:
            categorias_list = categorias_list.order_by('descricao') # Fallback padrão

    paginator = Paginator(categorias_list, per_page)
    page_number = request.GET.get('page')

    try:
        categorias = paginator.page(page_number)
    except PageNotAnInteger:
        categorias = paginator.page(1)
    except EmptyPage:
        categorias = paginator.page(paginator.num_pages)

    context = {
        'categorias': categorias,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/categoria_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/categoria_list.html', context)

# View para criar uma nova categoria
# @login_required # Removido/comentado conforme solicitado
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria cadastrada com sucesso!")
            return redirect('core:categoria_list')
    else:
        form = CategoriaForm()
    return render(request, 'core/categoria_form.html', {'form': form, 'title': 'Nova Categoria'})

# View para atualizar uma categoria existente
# @login_required # Removido/comentado conforme solicitado
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso!")
            return redirect('core:categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'core/categoria_form.html', {'form': form, 'title': 'Editar Categoria'})

# View para confirmar exclusão de uma categoria
# @login_required # Removido/comentado conforme solicitado
def categoria_confirm_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return render(request, 'core/categoria_confirm_delete.html', {'categoria': categoria})

# View para excluir uma categoria (POST request)
# @login_required # Removido/comentado conforme solicitado
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, "Categoria excluída com sucesso!")
        return redirect('core:categoria_list')
    # Redireciona de volta para a lista se não for uma requisição POST
    return redirect('core:categoria_list')
#----------------------------------------------------------------------------------------------------
# View para listar grupos
# @login_required # Removido/comentado conforme solicitado
def grupo_list(request):
    grupos_list = Grupo.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'descricao')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        grupos_list = grupos_list.filter(Q(codigo__icontains=search_query) | Q(descricao__icontains=search_query))

    if status_filter != 'all':
        grupos_list = grupos_list.filter(cancelado=(status_filter == 'cancelado'))

    # Ordenação
    if sort_by:
        allowed_sort_fields = ['codigo', 'descricao', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            grupos_list = grupos_list.order_by(sort_by)
        else:
            grupos_list = grupos_list.order_by('descricao') # Fallback padrão

    paginator = Paginator(grupos_list, per_page)
    page_number = request.GET.get('page')

    try:
        grupos = paginator.page(page_number)
    except PageNotAnInteger:
        grupos = paginator.page(1)
    except EmptyPage:
        grupos = paginator.page(paginator.num_pages)

    context = {
        'grupos': grupos,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/grupo_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/grupo_list.html', context)

# View para criar um novo grupo
# @login_required # Removido/comentado conforme solicitado
def grupo_create(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo cadastrado com sucesso!")
            return redirect('core:grupo_list')
    else:
        form = GrupoForm()
    return render(request, 'core/grupo_form.html', {'form': form, 'title': 'Novo Grupo'})

# View para atualizar um grupo existente
# @login_required # Removido/comentado conforme solicitado
def grupo_update(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo atualizado com sucesso!")
            return redirect('core:grupo_list')
    else:
        form = GrupoForm(instance=grupo)
    return render(request, 'core/grupo_form.html', {'form': form, 'title': 'Editar grupo'})

# View para confirmar exclusão de um grupo
# @login_required # Removido/comentado conforme solicitado
def grupo_confirm_delete(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    return render(request, 'core/grupo_confirm_delete.html', {'grupo': grupo})

# View para excluir um grupo (POST request)
# @login_required # Removido/comentado conforme solicitado
def grupo_delete(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)
    if request.method == 'POST':
        grupo.delete()
        messages.success(request, "Grupo excluído com sucesso!")
        return redirect('core:grupo_list')
    # Redireciona de volta para a lista se não for uma requisição POST
    return redirect('core:grupo_list')


# -------------------------------------------------------------------------------
# NOVAS VIEWS PARA NCM
# -------------------------------------------------------------------------------

def ncm_list(request):
    ncms_list = Ncm.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')  # 'all', 'true', 'false' (para cancelado)
    sort_by = request.GET.get('sort_by', 'ncm')  # Default sort for NCM
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        # Busca por 'ncm' ou 'descricao'
        ncms_list = ncms_list.filter(Q(ncm__icontains=search_query) | Q(descricao__icontains=search_query))

    # Filtro de status 'cancelado' (BooleanField)
    if status_filter == 'true':  # Para NCMs cancelados
        ncms_list = ncms_list.filter(cancelado=True)
    elif status_filter == 'false':  # Para NCMs não cancelados (ativos)
        ncms_list = ncms_list.filter(cancelado=False)

    # Ordenação
    if sort_by:
        allowed_sort_fields = ['ncm', 'descricao', 'inicio_vigencia', 'fim_vigencia', 'ano', 'numero', 'cancelado',
                               'segmento', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            ncms_list = ncms_list.order_by(sort_by)
        else:
            ncms_list = ncms_list.order_by('ncm')  # Fallback padrão

    paginator = Paginator(ncms_list, per_page)
    page_number = request.GET.get('page')

    try:
        ncms = paginator.page(page_number)
    except PageNotAnInteger:
        ncms = paginator.page(1)
    except EmptyPage:
        ncms = paginator.page(paginator.num_pages)

    context = {
        'page_obj': ncms,  # Passar como page_obj para o partial e ncm_list.html
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/ncm_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/ncm_list.html', context)


# View para criar um novo NCM
def ncm_create(request):
    if request.method == 'POST':
        form = NcmForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'NCM cadastrado com sucesso!')
            return redirect('core:ncm_list')
        else:
            messages.error(request, 'Erro ao cadastrar NCM. Verifique os campos.')
    else:
        form = NcmForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo NCM'
    }
    return render(request, 'core/ncm_form.html', context)


# View para atualizar um NCM existente
def ncm_update(request, pk):
    ncm_instance = get_object_or_404(Ncm, pk=pk)
    if request.method == 'POST':
        form = NcmForm(request.POST, instance=ncm_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'NCM atualizado com sucesso!')
            return redirect('core:ncm_list')
        else:
            messages.error(request, 'Erro ao atualizar NCM. Verifique os campos.')
    else:
        form = NcmForm(instance=ncm_instance)

    context = {
        'form': form,
        'title': 'Editar NCM'
    }
    return render(request, 'core/ncm_form.html', context)


# View para exibir a página de confirmação de exclusão do NCM
def ncm_confirm_delete(request, pk):
    ncm = get_object_or_404(Ncm, pk=pk)
    context = {
        'ncm': ncm,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/ncm_confirm_delete.html', context)


# View para excluir um NCM (POST request)
def ncm_delete(request, pk):
    ncm = get_object_or_404(Ncm, pk=pk)
    if request.method == 'POST':
        ncm.delete()
        messages.success(request, 'NCM excluído com sucesso!')
        return redirect('core:ncm_list')
    else:
        # Se alguém tentar acessar diretamente via GET, redireciona para a confirmação
        return redirect('core:ncm_confirm_delete', pk=pk)


# -------------------------------------------------------------------------------
# NOVAS VIEWS PARA CFOP
# -------------------------------------------------------------------------------

# View para listar CFOPs
def cfop_list(request):
    cfops_list = Cfop.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')  # 'all', 'true', 'false' (para cancelado)
    sort_by = request.GET.get('sort_by', 'cfop')  # Default sort for CFOP
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        # Busca por 'cfop', 'categoria' ou 'descricao'
        cfops_list = cfops_list.filter(
            Q(cfop__icontains=search_query) |
            Q(categoria__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )

    # Filtro de status 'cancelado' (BooleanField)
    if status_filter == 'true':  # Para CFOPs cancelados
        cfops_list = cfops_list.filter(cancelado=True)
    elif status_filter == 'false':  # Para CFOPs não cancelados (ativos)
        cfops_list = cfops_list.filter(cancelado=False)

    # Ordenação
    if sort_by:
        allowed_sort_fields = ['cfop', 'categoria', 'descricao', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            cfops_list = cfops_list.order_by(sort_by)
        else:
            cfops_list = cfops_list.order_by('cfop')  # Fallback padrão

    paginator = Paginator(cfops_list, per_page)
    page_number = request.GET.get('page')

    try:
        cfops = paginator.get_page(page_number)  # Alterado de .page para .get_page para melhor tratamento de erros
    except EmptyPage:
        cfops = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:  # Adicionado para garantir que sempre retorne a primeira página para não inteiros
        cfops = paginator.get_page(1)

    context = {
        'page_obj': cfops,  # Passar como page_obj para o partial e cfop_list.html
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/cfop_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/cfop_list.html', context)


# View para criar um novo CFOP
def cfop_create(request):
    if request.method == 'POST':
        form = CfopForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'CFOP cadastrado com sucesso!')
            return redirect('core:cfop_list')
        else:
            messages.error(request, 'Erro ao cadastrar CFOP. Verifique os campos.')
    else:
        form = CfopForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo CFOP'
    }
    return render(request, 'core/cfop_form.html', context)


# View para atualizar um CFOP existente
def cfop_update(request, pk):
    cfop_instance = get_object_or_404(Cfop, pk=pk)
    if request.method == 'POST':
        form = CfopForm(request.POST, instance=cfop_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'CFOP atualizado com sucesso!')
            return redirect('core:cfop_list')
        else:
            messages.error(request, 'Erro ao atualizar CFOP. Verifique os campos.')
    else:
        form = CfopForm(instance=cfop_instance)

    context = {
        'form': form,
        'title': 'Editar CFOP'
    }
    return render(request, 'core/cfop_form.html', context)


# View para exibir a página de confirmação de exclusão do CFOP
def cfop_confirm_delete(request, pk):
    cfop = get_object_or_404(Cfop, pk=pk)
    context = {
        'cfop': cfop,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/cfop_confirm_delete.html', context)


# View para excluir um CFOP (POST request)
def cfop_delete(request, pk):
    cfop = get_object_or_404(Cfop, pk=pk)
    if request.method == 'POST':
        cfop.delete()
        messages.success(request, 'CFOP excluído com sucesso!')
        return redirect('core:cfop_list')
    else:
        # Se alguém tentar acessar diretamente via GET, redireciona para a confirmação
        return redirect('core:cfop_confirm_delete', pk=pk)

# --- NOVAS VIEWS: CEST ---
def cest_list(request): # <-- ESTA DEVE ESTAR AQUI
    cests_list = Cest.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'cd_cest')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        cests_list = cests_list.filter(
            Q(cd_cest__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(cd_ncm__icontains=search_query)
        )

    if status_filter == 'true':
        cests_list = cests_list.filter(cancelado=True)
    elif status_filter == 'false':
        cests_list = cests_list.filter(cancelado=False)

    if sort_by:
        allowed_sort_fields = ['cd_cest', 'descricao', 'cd_ncm', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            cests_list = cests_list.order_by(sort_by)
        else:
            cests_list = cests_list.order_by('cd_cest')

    paginator = Paginator(cests_list, per_page)
    page_number = request.GET.get('page')

    try:
        cests = paginator.get_page(page_number)
    except EmptyPage:
        cests = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        cests = paginator.get_page(1)

    context = {
        'page_obj': cests,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/cest_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/cest_list.html', context)


def cest_create(request):
    if request.method == 'POST':
        form = CestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'CEST cadastrado com sucesso!')
            return redirect('core:cest_list')
        else:
            messages.error(request, 'Erro ao cadastrar CEST. Verifique os campos.')
    else:
        form = CestForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo CEST'
    }
    return render(request, 'core/cest_form.html', context)


def cest_update(request, pk):
    cest_instance = get_object_or_404(Cest, pk=pk)
    if request.method == 'POST':
        form = CestForm(request.POST, instance=cest_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'CEST atualizado com sucesso!')
            return redirect('core:cest_list')
        else:
            messages.error(request, 'Erro ao atualizar CEST. Verifique os campos.')
    else:
        form = CestForm(instance=cest_instance)

    context = {
        'form': form,
        'title': 'Editar CEST'
    }
    return render(request, 'core/cest_form.html', context)


def cest_confirm_delete(request, pk):
    cest = get_object_or_404(Cest, pk=pk)
    context = {
        'cest': cest,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/cest_confirm_delete.html', context)


def cest_delete(request, pk):
    cest = get_object_or_404(Cest, pk=pk)
    if request.method == 'POST':
        cest.delete()
        messages.success(request, 'CEST excluído com sucesso!')
        return redirect('core:cest_list')
    else:
        return redirect('core:cest_confirm_delete', pk=pk)


# -------------------------------------------------------------------------------
# NOVAS VIEWS: CST/CSOSN
# -------------------------------------------------------------------------------

def cst_cson_list(request):
    cst_cson_list = CstCson.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'cd_cst_cson')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        cst_cson_list = cst_cson_list.filter(
            Q(cd_cst_cson__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )

    if status_filter == 'true':
        cst_cson_list = cst_cson_list.filter(cancelado=True)
    elif status_filter == 'false':
        cst_cson_list = cst_cson_list.filter(cancelado=False)

    if sort_by:
        allowed_sort_fields = ['cd_cst_cson', 'descricao', 'cancelado', 'data_cadastro', 'data_atualizacao']
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            cst_cson_list = cst_cson_list.order_by(sort_by)
        else:
            cst_cson_list = cst_cson_list.order_by('cd_cst_cson')

    paginator = Paginator(cst_cson_list, per_page)
    page_number = request.GET.get('page')

    try:
        cst_cson_objects = paginator.get_page(page_number)
    except EmptyPage:
        cst_cson_objects = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        cst_cson_objects = paginator.get_page(1)

    context = {
        'page_obj': cst_cson_objects,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/cst_cson_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/cstcson_list.html', context)


def cst_cson_create(request):
    if request.method == 'POST':
        form = CstCsonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'CST/CSOSN cadastrado com sucesso!')
            return redirect('core:cst_cson_list')
        else:
            messages.error(request, 'Erro ao cadastrar CST/CSOSN. Verifique os campos.')
    else:
        form = CstCsonForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo CST/CSOSN'
    }
    return render(request, 'core/cstcson_form.html', context)


def cst_cson_update(request, pk):
    cst_cson_instance = get_object_or_404(CstCson, pk=pk)
    if request.method == 'POST':
        form = CstCsonForm(request.POST, instance=cst_cson_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'CST/CSOSN atualizado com sucesso!')
            return redirect('core:cst_cson_list')
        else:
            messages.error(request, 'Erro ao atualizar CST/CSOSN. Verifique os campos.')
    else:
        form = CstCsonForm(instance=cst_cson_instance)

    context = {
        'form': form,
        'title': 'Editar CST/CSOSN'
    }
    return render(request, 'core/cstcson_form.html', context)


def cst_cson_confirm_delete(request, pk):
    cst_cson = get_object_or_404(CstCson, pk=pk)
    context = {
        'cst_cson': cst_cson,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/cstcson_confirm_delete.html', context)


def cst_cson_delete(request, pk):
    cst_cson = get_object_or_404(CstCson, pk=pk)
    if request.method == 'POST':
        cst_cson.delete()
        messages.success(request, 'CST/CSOSN excluído com sucesso!')
        return redirect('core:cst_cson_list')
    else:
        return redirect('core:cst_cson_confirm_delete', pk=pk)


# -------------------------------------------------------------------------------
# NOVAS VIEWS: PRODUTO
# -------------------------------------------------------------------------------

def produto_list(request):
    produtos_list = Produto.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')  # 'all', 'A' (Ativo), 'I' (Inativo)
    sort_by = request.GET.get('sort_by', 'descricao_produto')  # Default sort by descricao_produto
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        produtos_list = produtos_list.filter(
            Q(codigo_ean_dun__icontains=search_query) |
            Q(descricao_produto__icontains=search_query)
        )

    # Filtrar por situação
    if status_filter == 'A':
        produtos_list = produtos_list.filter(situacao='A')
    elif status_filter == 'I':
        produtos_list = produtos_list.filter(situacao='I')

    if sort_by:
        # Campos permitidos para ordenação baseados no seu modelo Produto
        allowed_sort_fields = [
            'codigo_ean_dun', 'descricao_produto', 'valor_venda', 'estoque_atual',
            'situacao', 'data_cadastro', 'data_atualizacao'
        ]
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            produtos_list = produtos_list.order_by(sort_by)
        else:
            produtos_list = produtos_list.order_by('descricao_produto') # Fallback para um campo válido

    paginator = Paginator(produtos_list, per_page)
    page_number = request.GET.get('page')

    try:
        produtos = paginator.get_page(page_number)
    except EmptyPage:
        produtos = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        produtos = paginator.get_page(1)

    context = {
        'page_obj': produtos,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/produto_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/produto_list.html', context)


def produto_create(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('core:produto_list')
        else:
            messages.error(request, 'Erro ao cadastrar Produto. Verifique os campos.')
    else:
        form = ProdutoForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo Produto'
    }
    return render(request, 'core/produto_form.html', context)


def produto_update(request, pk):
    produto_instance = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:produto_list')
        else:
            messages.error(request, 'Erro ao atualizar Produto. Verifique os campos.')
    else:
        form = ProdutoForm(instance=produto_instance)

    context = {
        'form': form,
        'title': 'Editar Produto'
    }
    return render(request, 'core/produto_form.html', context)


def produto_confirm_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    context = {
        'produto': produto,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/produto_confirm_delete.html', context)


def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('core:produto_list')
    else:
        return redirect('core:produto_confirm_delete', pk=pk)


# -------------------------------------------------------------------------------
# NOVAS VIEWS: CONVENIO ABERTURA
# -------------------------------------------------------------------------------
def convenio_abertura_list(request):
    """
    Lista todos os convênios de abertura, com funcionalidades de busca, filtro e paginação.
    Suporta requisições AJAX para atualização parcial da tabela.
    """
    convenios_abertura_list = ConvenioAbertura.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', '-mes_referencia') # Ordem padrão: mais recente primeiro
    per_page = int(request.GET.get('per_page', 10))

    # Lógica de busca
    if search_query:
        convenios_abertura_list = convenios_abertura_list.filter(
            Q(mes_referencia__icontains=search_query) | # Busca pelo mês/ano de referência
            Q(status__icontains=search_query)           # Permite buscar por 'A' ou 'F' no status
        )

    # Lógica de filtro por status (Ativo/Fechado)
    if status_filter != 'all':
        convenios_abertura_list = convenios_abertura_list.filter(status=status_filter)

    # Lógica de ordenação
    if sort_by:
        # Campos permitidos para ordenação. Certifique-se de que correspondem aos campos do seu modelo.
        allowed_sort_fields = [
            'id', 'mes_referencia', 'data_abertura',
            'data_fechamento', 'data_pagamento', 'status'
        ]
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            convenios_abertura_list = convenios_abertura_list.order_by(sort_by)
        else:
            # Caso o sort_by seja inválido, retorne à ordenação padrão
            convenios_abertura_list = convenios_abertura_list.order_by('-mes_referencia')

    # Configuração da Paginação
    paginator = Paginator(convenios_abertura_list, per_page)
    page_number = request.GET.get('page')

    try:
        convenios_abertura = paginator.get_page(page_number)
    except EmptyPage:
        # Se a página estiver fora do intervalo (ex: 9999), entrega a última página de resultados.
        convenios_abertura = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        # Se a página não for um inteiro, entrega a primeira página.
        convenios_abertura = paginator.get_page(1)

    context = {
        'convenios': convenios_abertura, # Nome 'convenios' para corresponder ao partial template
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    # Resposta AJAX para atualização da tabela
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/convenio_abertura_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    # Resposta normal para a primeira carga da página
    return render(request, 'core/convenio_abertura_list.html', context)

def convenio_abertura_create(request):
    """
    Permite cadastrar um novo convênio de abertura.
    Redireciona para a lista após sucesso, ou exibe erros do formulário.
    """
    if request.method == 'POST':
        form = ConvenioAberturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio de Abertura cadastrado com sucesso!')
            # **CORREÇÃO:** Usando o namespace 'core'
            return redirect('core:convenio_abertura_list')
        else:
            messages.error(request, 'Erro ao cadastrar Convênio de Abertura. Verifique os campos.')
    else:
        form = ConvenioAberturaForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo Convênio de Abertura'
    }
    return render(request, 'core/convenio_abertura_form.html', context)

def convenio_abertura_update(request, pk):
    """
    Permite editar um convênio de abertura existente.
    """
    convenio_abertura_instance = get_object_or_404(ConvenioAbertura, pk=pk)
    if request.method == 'POST':
        form = ConvenioAberturaForm(request.POST, instance=convenio_abertura_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio de Abertura atualizado com sucesso!')
            # **CORREÇÃO:** Usando o namespace 'core'
            return redirect('core:convenio_abertura_list')
        else:
            messages.error(request, 'Erro ao atualizar Convênio de Abertura. Verifique os campos.')
    else:
        form = ConvenioAberturaForm(instance=convenio_abertura_instance)

    context = {
        'form': form,
        'title': 'Editar Convênio de Abertura'
    }
    return render(request, 'core/convenio_abertura_form.html', context)

def convenio_abertura_confirm_delete(request, pk):
    """
    Exibe uma página de confirmação antes de excluir um convênio de abertura.
    """
    convenio_abertura = get_object_or_404(ConvenioAbertura, pk=pk)
    context = {
        'convenio_abertura': convenio_abertura,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/convenio_abertura_confirm_delete.html', context)

def convenio_abertura_delete(request, pk):
    """
    Exclui um convênio de abertura após a confirmação.
    """
    convenio_abertura = get_object_or_404(ConvenioAbertura, pk=pk)
    if request.method == 'POST':
        convenio_abertura.delete()
        messages.success(request, 'Convênio de Abertura excluído com sucesso!')
        # **CORREÇÃO:** Usando o namespace 'core'
        return redirect('core:convenio_abertura_list')
    else:
        # Redireciona para a página de confirmação se não for POST
        return redirect('core:convenio_abertura_confirm_delete', pk=pk)

# -------------------------------------------------------------------------------
# NOVAS VIEWS: CONVENIO
# -------------------------------------------------------------------------------

def convenio_list(request):
    convenios_list = Convenio.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'nome_convenio') # Alterado o sort_by padrão para 'nome_convenio'
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        convenios_list = convenios_list.filter(
            Q(cd_loja__icontains=search_query) |         # CORRIGIDO: Usando 'cd_loja'
            Q(nome_convenio__icontains=search_query) |   # CORRIGIDO: Usando 'nome_convenio'
            Q(cnpj__icontains=search_query) |
            Q(contato__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(telefone__icontains=search_query) |
            Q(cod_evento__icontains=search_query)
        )

    # CORRIGIDO: Lógica de filtro para o campo 'ativo'
    if status_filter == 'true':
        convenios_list = convenios_list.filter(ativo=True)
    elif status_filter == 'false':
        convenios_list = convenios_list.filter(ativo=False)

    if sort_by:
        # CORRIGIDO: Lista de campos permitidos para ordenação
        allowed_sort_fields = [
            'cd_loja', 'nome_convenio', 'cnpj', 'contato', 'email',
            'telefone', 'ativo', 'qtd_parc_permi', 'cod_evento',
            'data_cadastro', 'data_atualizacao'
        ]
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            convenios_list = convenios_list.order_by(sort_by)
        else:
            # Garante uma ordenação padrão caso o campo solicitado não seja válido
            convenios_list = convenios_list.order_by('nome_convenio')

    paginator = Paginator(convenios_list, per_page)
    page_number = request.GET.get('page')

    try:
        convenios = paginator.get_page(page_number)
    except EmptyPage:
        # Se a página estiver fora do intervalo (ex: 9999), entrega a última página de resultados.
        convenios = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        # Se o parâmetro de página não for um inteiro, entrega a primeira página.
        convenios = paginator.get_page(1)

    context = {
        'page_obj': convenios,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    # Verifica se a requisição é AJAX para retornar apenas o HTML da tabela
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/convenio_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/convenio_list.html', context)


def convenio_create(request):
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES) # Adicionado request.FILES para lidar com o upload de logo
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio cadastrado com sucesso!')
            return redirect('core:convenio_list')
        else:
            messages.error(request, 'Erro ao cadastrar Convênio. Verifique os campos.')
    else:
        form = ConvenioForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo Convênio'
    }
    return render(request, 'core/convenio_form.html', context)


def convenio_update(request, pk):
    convenio_instance = get_object_or_404(Convenio, pk=pk)
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES, instance=convenio_instance) # Adicionado request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio atualizado com sucesso!')
            return redirect('core:convenio_list')
        else:
            messages.error(request, 'Erro ao atualizar Convênio. Verifique os campos.')
    else:
        form = ConvenioForm(instance=convenio_instance)

    context = {
        'form': form,
        'title': 'Editar Convênio'
    }
    return render(request, 'core/convenio_form.html', context)


def convenio_confirm_delete(request, pk):
    convenio = get_object_or_404(Convenio, pk=pk)
    context = {
        'convenio': convenio,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/convenio_confirm_delete.html', context)


def convenio_delete(request, pk):
    convenio = get_object_or_404(Convenio, pk=pk)
    if request.method == 'POST':
        convenio.delete()
        messages.success(request, 'Convênio excluído com sucesso!')
        return redirect('core:convenio_list')
    else:
        # Se alguém tentar acessar a URL de exclusão diretamente via GET, redireciona para a confirmação
        return redirect('core:convenio_confirm_delete', pk=pk)
# -------------------------------------------------------------------------------
# VIEWS DE CRUD PARA CONVENIO_EMISSAO
# -------------------------------------------------------------------------------

def convenio_emissao_list(request):
    convenios_emissao_list = ConvenioEmissao.objects.all()

    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', '-DATA_TRANSACAO')
    per_page = int(request.GET.get('per_page', 10))

    if search_query:
        convenios_emissao_list = convenios_emissao_list.filter(
            Q(ID_CLIENTE__cpf_cnpj__icontains=search_query) |
            Q(ID_CLIENTE__nome_completo__icontains=search_query) |
            Q(ID_CONVENIO__nome_convenio__icontains=search_query) |
            Q(MES_REFERENCIA__icontains=search_query)
        )

    if sort_by:
        allowed_sort_fields = [
            'id', 'CPF', 'ID_CLIENTE__nome_completo', 'ID_CONVENIO__nome_convenio',
            'VALOR', 'QTD_PARCELA', 'MES_REFERENCIA', 'DATA_TRANSACAO', 'HORA_TRANSACAO'
        ]
        if sort_by in allowed_sort_fields or (sort_by.startswith('-') and sort_by[1:] in allowed_sort_fields):
            convenios_emissao_list = convenios_emissao_list.order_by(sort_by)
        else:
            convenios_emissao_list = convenios_emissao_list.order_by('-DATA_TRANSACAO')

    paginator = Paginator(convenios_emissao_list, per_page)
    page_number = request.GET.get('page')

    try:
        convenios_emissao = paginator.get_page(page_number)
    except EmptyPage:
        convenios_emissao = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        convenios_emissao = paginator.get_page(1)

    context = {
        'emissoes': convenios_emissao,
        'search': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'per_page': per_page,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('core/convenio_emissao_table_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'core/convenio_emissao_list.html', context)


def convenio_emissao_create(request):
    if request.method == 'POST':
        print("\n===== DEBUG POST DATA =====")
        print(request.POST)
        print("===========================\n")

        form = ConvenioEmissaoForm(request.POST)
        if form.is_valid():
            print("\n===== DEBUG CLEANED DATA (VALID) =====")
            print(form.cleaned_data)
            print("======================================\n")

            form.save()
            messages.success(request, 'Convênio de Emissão cadastrado com sucesso!')
            return redirect('core:convenio_emissao_list')
        else:
            print("\n===== DEBUG FORM ERRORS =====")
            print(form.errors)
            print("==============================\n")

            messages.error(request, 'Erro ao cadastrar Convênio de Emissão. Verifique os campos.')
            context = {
                'form': form,
                'title': 'Cadastrar Novo Convênio de Emissão'
            }
            return render(request, 'core/convenio_emissao_form.html', context)
    else:
        form = ConvenioEmissaoForm()

    context = {
        'form': form,
        'title': 'Cadastrar Novo Convênio de Emissão'
    }
    return render(request, 'core/convenio_emissao_form.html', context)

def convenio_emissao_update(request, pk):
    convenio_emissao = get_object_or_404(ConvenioEmissao, pk=pk)
    if request.method == 'POST':
        form = ConvenioEmissaoForm(request.POST, instance=convenio_emissao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio de Emissão atualizado com sucesso!')
            return redirect('core:convenio_emissao_list')
        else:
            messages.error(request, 'Erro ao atualizar Convênio de Emissão. Verifique os campos.')
            context = {
                'form': form,
                'title': 'Editar Convênio de Emissão',
            }
            return render(request, 'core/convenio_emissao_form.html', context)
    else:
        form = ConvenioEmissaoForm(instance=convenio_emissao)

    context = {
        'form': form,
        'title': 'Editar Convênio de Emissão',
    }
    return render(request, 'core/convenio_emissao_form.html', context)


def convenio_emissao_confirm_delete(request, pk):
    convenio_emissao = get_object_or_404(ConvenioEmissao, pk=pk)
    context = {
        'convenio_emissao': convenio_emissao,
        'title': 'Confirmar Exclusão'
    }
    return render(request, 'core/convenio_emissao_confirm_delete.html', context)


def convenio_emissao_delete(request, pk):
    convenio_emissao = get_object_or_404(ConvenioEmissao, pk=pk)
    if request.method == 'POST':
        convenio_emissao.delete()
        messages.success(request, 'Convênio de Emissão excluído com sucesso!')
        return redirect('core:convenio_emissao_list')
    else:
        return redirect('core:convenio_emissao_confirm_delete', pk=pk)


# -------------------------------------------------------------------------------
# VIEWS DE API PARA CONVENIOEMISSAOFORM (AJAX)
# -------------------------------------------------------------------------------
@require_GET
@csrf_exempt # Apenas para desenvolvimento, se tiver problemas de CSRF em GET. Remova em produção se não for estritamente necessário.
def search_client_by_cpf(request):
    cpf = request.GET.get('cpf', None)
    if not cpf:
        return JsonResponse({'error': 'CPF/CNPJ não fornecido.'}, status=400)

    try:
        # Limpa o CPF/CNPJ para a busca no banco de dados
        # O campo 'cpf_cnpj' no seu modelo Cliente já armazena o CPF/CNPJ limpo.
        cpf_cleaned = ''.join(filter(str.isdigit, cpf))

        # Busca o cliente usando o campo cpf_cnpj
        cliente = Cliente.objects.get(cpf_cnpj=cpf_cleaned)

        data = {
            'id': cliente.pk, # ou cliente.id
            'nome_completo': cliente.nome_completo,
            'saldo': str(cliente.saldo) # Converte o DecimalField para string para JSON
        }
        return JsonResponse(data)
    except Cliente.DoesNotExist:
        # Cliente não encontrado. Retorna status 200 com id=None.
        # Isso permite ao JavaScript interpretar como "não encontrado" sem erro HTTP.
        return JsonResponse({'id': None, 'nome_completo': 'Cliente não encontrado.', 'saldo': '0.00'}, status=200)
    except Exception as e:
        # Loga o erro no console do servidor para depuração
        print(f"Erro inesperado ao buscar dados do cliente: {e}")
        return JsonResponse({'error': f'Erro interno do servidor: {str(e)}'}, status=500)

# @require_GET
# def search_client_by_cpf(request):
#     cpf = request.GET.get('cpf', None)
#     if not cpf:
#         return JsonResponse({'error': 'CPF/CNPJ não fornecido.'}, status=400)
#
#     try:
#         # Remova caracteres não numéricos para a busca no banco
#         cpf_cleaned = ''.join(filter(str.isdigit, cpf))
#
#         # Use o cpf_cleaned para a busca
#         cliente = Cliente.objects.get(cpf_cnpj=cpf_cleaned)
#         data = {
#             'id': cliente.pk,
#             'nome_completo': cliente.nome_completo,  # Nome do campo no seu model Cliente
#             'saldo': float(cliente.saldo) if cliente.saldo is not None else 0.0
#             # **CORRIGIDO**: Alterado de 'saldo_cliente' para 'saldo'
#         }
#         return JsonResponse(data)
#     except Cliente.DoesNotExist:
#         return JsonResponse({'error': 'Cliente não encontrado.'}, status=404)
#     except Exception as e:
#         print(f"Erro ao buscar dados do cliente: {e}")
#         return JsonResponse({'error': f'Erro interno ao buscar cliente: {str(e)}'}, status=500)


@require_GET
def get_convenio_details(request):
    convenio_id = request.GET.get('id', None)
    if not convenio_id:
        return JsonResponse({'error': 'ID do Convênio não fornecido.'}, status=400)
    try:
        convenio = Convenio.objects.get(pk=convenio_id)
        data = {
            'qtd_parc_permi': convenio.qtd_parc_permi,  # Nome real do campo no seu model Convenio
            # 'mes_referencia': convenio.mes_referencia, # Você pode incluir este se precisar no JS
        }
        return JsonResponse(data)
    except Convenio.DoesNotExist:
        return JsonResponse({'error': 'Convênio não encontrado.'}, status=404)
    except Exception as e:
        print(f"Erro ao buscar dados do convênio: {e}")
        return JsonResponse({'error': f'Erro interno ao buscar convênio: {str(e)}'}, status=500)
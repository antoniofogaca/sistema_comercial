# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # <<< CORREÇÃO AQUI: Importe 'views' como 'auth_views'
from django.contrib.auth.views import LogoutView    # <<< Mantenha esta importação para LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'), # <<< APENAS ESTA LINHA PARA LOGIN

    # ... suas outras URLs (o restante do seu arquivo está correto)
    # Módulo de Vendas
    path('vendas/', views.venda_list, name='venda_list'),
    path('vendas/nova/', views.venda_create, name='venda_create'),
    path('vendas/editar/<int:pk>/', views.venda_update, name='venda_update'),
    path('vendas/excluir/<int:pk>/', views.venda_delete, name='venda_delete'),
    path('vendas/confirmar-exclusao/<int:pk>/', views.venda_confirm_delete, name='venda_confirm_delete'),

    # API para buscar Requisição por ID (se precisar, pode usar a mesma do cliente para o CPF)
    path('api/vendas/search_requisicao/', views.search_requisicao_details, name='search_requisicao_details'),

    # Módulo de Convênios (Listagem principal de convênios - "Incluir Convênio")
    path('convenios/', views.convenio_list, name='convenio_list'), # URL principal para a lista de convênios
    path('convenios/novo/', views.convenio_create, name='convenio_create'),
    path('convenios/editar/<int:pk>/', views.convenio_update, name='convenio_update'),
    path('convenios/excluir/<int:pk>/', views.convenio_delete, name='convenio_delete'),
    path('convenios/confirmar-exclusao/<int:pk>/', views.convenio_confirm_delete, name='convenio_confirm_delete'),

    # Módulo de Convênio Emissão
    path('convenios/emissao/', views.convenio_emissao_list, name='convenio_emissao_list'), # Caminho distinto
    path('convenios/emissao/novo/', views.convenio_emissao_create, name='convenio_emissao_create'),
    path('convenios/emissao/editar/<int:pk>/', views.convenio_emissao_update, name='convenio_emissao_update'),
    path('convenios/emissao/excluir/<int:pk>/', views.convenio_emissao_delete, name='convenio_emissao_delete'),
    path('convenios/emissao/confirmar-exclusao/<int:pk>/', views.convenio_emissao_confirm_delete, name='convenio_emissao_confirm_delete'),

    # NOVAS URLs para Abertura de Convênio (Já estão boas)
    path('convenios/abertura/', views.convenio_abertura_list, name='convenio_abertura_list'),
    path('convenios/abertura/novo/', views.convenio_abertura_create, name='convenio_abertura_create'),
    path('convenios/abertura/editar/<int:pk>/', views.convenio_abertura_update, name='convenio_abertura_update'),
    path('convenios/abertura/excluir/<int:pk>/', views.convenio_abertura_delete, name='convenio_abertura_delete'),
    path('convenios/abertura/confirmar-exclusao/<int:pk>/', views.convenio_abertura_confirm_delete, name='convenio_abertura_confirm_delete'),

    # PRODUTOS
    path('produtos/', views.produto_list, name='produto_list'),
    path('produtos/novo/', views.produto_create, name='produto_create'),
    path('produtos/editar/<int:pk>/', views.produto_update, name='produto_update'),
    path('produtos/excluir/<int:pk>/confirmar/', views.produto_confirm_delete, name='produto_confirm_delete'),
    path('produtos/excluir/<int:pk>/', views.produto_delete, name='produto_delete'),

    # CST_CSON
    path('cstcson/', views.cst_cson_list, name='cst_cson_list'),
    path('cstcson/novo/', views.cst_cson_create, name='cst_cson_create'),
    path('cstcson/editar/<int:pk>/', views.cst_cson_update, name='cst_cson_update'),
    path('cstcson/excluir/<int:pk>/', views.cst_cson_delete, name='cst_cson_delete'),
    path('cstcson/confirmar-exclusao/<int:pk>/', views.cst_cson_confirm_delete, name='cst_cson_confirm_delete'),

    # CEST
    path('cest/', views.cest_list, name='cest_list'),
    path('cest/novo/', views.cest_create, name='cest_create'),
    path('cest/editar/<int:pk>/', views.cest_update, name='cest_update'),
    path('cest/excluir/<int:pk>/', views.cest_delete, name='cest_delete'),
    path('cest/confirmar-exclusao/<int:pk>/', views.cest_confirm_delete, name='cest_confirm_delete'),

    # CFOPs
    path('cfop/', views.cfop_list, name='cfop_list'),
    path('cfop/novo/', views.cfop_create, name='cfop_create'),
    path('cfop/editar/<int:pk>/', views.cfop_update, name='cfop_update'),
    path('cfop/excluir/<int:pk>/', views.cfop_delete, name='cfop_delete'),
    path('cfop/confirmar-exclusao/<int:pk>/', views.cfop_confirm_delete, name='cfop_confirm_delete'),

    # NCMs
    path('ncm/', views.ncm_list, name='ncm_list'),
    path('ncm/novo/', views.ncm_create, name='ncm_create'),
    path('ncm/editar/<int:pk>/', views.ncm_update, name='ncm_update'),
    path('ncm/excluir/<int:pk>/', views.ncm_delete, name='ncm_delete'),
    path('ncm/confirmar-exclusao/<int:pk>/', views.ncm_confirm_delete, name='ncm_confirm_delete'),

    # Grupos
    path('grupos/', views.grupo_list, name='grupo_list'),
    path('grupos/novo/', views.grupo_create, name='grupo_create'),
    path('grupos/editar/<int:pk>/', views.grupo_update, name='grupo_update'),
    path('grupos/excluir/<int:pk>/', views.grupo_delete, name='grupo_delete'),
    path('grupos/confirmar-exclusao/<int:pk>/', views.grupo_confirm_delete, name='grupo_confirm_delete'),

    # Categoria
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/novo/', views.categoria_create, name='categoria_create'),
    path('categorias/editar/<int:pk>/', views.categoria_update, name='categoria_update'),
    path('categorias/excluir/<int:pk>/', views.categoria_delete, name='categoria_delete'),
    path('categorias/confirmar-exclusao/<int:pk>/', views.categoria_confirm_delete, name='categoria_confirm_delete'),

    # Setores
    path('setores/', views.setor_list, name='setor_list'),
    path('setores/novo/', views.setor_create, name='setor_create'),
    path('setores/editar/<int:pk>/', views.setor_update, name='setor_update'),
    path('setores/excluir/<int:pk>/', views.setor_delete, name='setor_delete'),
    path('setores/confirmar-exclusao/<int:pk>/', views.setor_confirm_delete, name='setor_confirm_delete'),

    # Usuários
    path('usuarios/', views.usuario_list, name='usuarios_list'),
    path('usuarios/novo/', views.usuario_create, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.usuario_update, name='usuario_update'),
    path('usuarios/excluir/<int:pk>/', views.usuario_delete, name='usuario_delete'),

    # Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete, name='cliente_delete'),

    # Empresas
    path('empresas/', views.empresas_list, name='empresas_list'),
    path('empresas/novo/', views.empresa_create, name='empresa_create'),
    path('empresas/<int:pk>/editar/', views.empresa_update, name='empresa_update'),
    path('empresas/<int:pk>/excluir/', views.empresa_delete, name='empresa_delete'),

    # APIs (Mantenha se necessário)
    path('api/clientes/search_by_cpf/', views.search_client_by_cpf, name='search_client_by_cpf'),
    path('api/convenios/get_details/', views.get_convenio_details, name='get_convenio_details'),

    # As URLs antigas `produtos` e `convenios` que apontavam para views genéricas foram removidas
    # ou substituídas por caminhos mais específicos para evitar conflitos.
]
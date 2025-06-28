from django.contrib import admin

# Register your models here.
# core/admin.py
from django.contrib import admin
from .models import ConvenioEmissao, ConvenioEmiDet, Convenio, Cliente # Importe todos os seus modelos

admin.site.register(ConvenioEmissao)
admin.site.register(ConvenioEmiDet)
# ... outros registros (ex: admin.site.register(Convenio), admin.site.register(Cliente)) ...
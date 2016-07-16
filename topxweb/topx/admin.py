from django.contrib import admin
from .models import Comentario, Produto, Tipo

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 3

class ProdutoAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Produto', {'fields': ['nome']}),
    ]
    inlines = [ComentarioInline]

admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Tipo)
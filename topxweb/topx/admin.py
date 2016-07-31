from django.contrib import admin
from .models import Comentario, Produto, Tipo, Marca

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
admin.site.register(Marca)
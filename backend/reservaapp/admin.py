from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CentroEsportivo, EspacoEsportivo, Agenda, Reserva, Pagamento

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'tipo', 'nome_completo', 'cpf')
    list_filter = ('tipo',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo', 'nome_completo', 'cpf')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo', 'nome_completo','email', 'cpf')}),
    )

class CentroEsportivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'UF', 'media_avaliacao')
    search_fields = ('nome', 'cidade')
    list_filter = ('cidade', 'UF')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CentroEsportivo, CentroEsportivoAdmin)
admin.site.register(EspacoEsportivo)
admin.site.register(Agenda)    
admin.site.register(Reserva)
admin.site.register(Pagamento)

# Register your models here.
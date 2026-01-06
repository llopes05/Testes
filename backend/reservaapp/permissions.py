from rest_framework import permissions

from .models import CentroEsportivo, EspacoEsportivo, Agenda

class IsGerente(permissions.BasePermission):
    """
    Permite apenas ao gerente dono do centro esportivo editar ou deletar.
    """
    message = 'Apenas o gerente proprietário deste recurso pode realizar esta ação.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.tipo == 'gerente'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, CentroEsportivo):
            return obj.gerente == request.user

        if isinstance(obj, EspacoEsportivo):
            return obj.centro_esportivo.gerente == request.user

        if isinstance(obj, Agenda):
            return obj.espacoesportivo.centro_esportivo.gerente == request.user

        return False


class IsOrganizador(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas usuários do tipo 'organizador'.
    """
    message = 'Apenas organizadores podem realizar esta ação.'

    def has_permission(self, request, view):  
        if not request.user.is_authenticated:
            return False
        return request.user.tipo == 'organizador'        


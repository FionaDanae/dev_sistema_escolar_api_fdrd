from django.db.models import *
from django.db import transaction
from dev_sistema_escolar_api.serializers import UserSerializer
from dev_sistema_escolar_api.serializers import *
from dev_sistema_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
import json
from django.shortcuts import get_object_or_404

class MaestrosAll(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestroSerializer(maestros, many=True).data
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    maestro["materias_json"] = []
        return Response(lista, 200)
    
class MaestrosView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] # POST no requiere autenticación  

    # Obtener maestro por ID
    def get(self, request, *args, **kwargs):
        maestro_id = kwargs.get("id") or request.GET.get("id")
        maestro = get_object_or_404(Maestros, id=maestro_id)
        data = MaestroSerializer(maestro, many=False).data
        if isinstance(data, dict) and "materias_json" in data:
            try:
                data["materias_json"] = json.loads(data["materias_json"])
            except Exception:
                data["materias_json"] = []
        return Response(data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)
            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)
            user.save()
            user.set_password(password)
            user.save()
            
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()
            maestro = Maestros.objects.create(user=user,
                                            id_trabajador= request.data["id_trabajador"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            cubiculo= request.data["cubiculo"],
                                            area_investigacion= request.data["area_investigacion"],
                                            materias_json = json.dumps(request.data["materias_json"]))
            maestro.save()
            return Response({"maestro_created_id": maestro.id }, 201)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del maestro
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        maestro_id = kwargs.get("id") or request.data.get("id")
        maestro = get_object_or_404(Maestros, id=maestro_id)
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"].upper()
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        materias = request.data.get("materias_json", [])
        try:
            maestro.materias_json = json.dumps(materias)
        except Exception:
            maestro.materias_json = json.dumps([])
        maestro.save()

        user = maestro.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        data = MaestroSerializer(maestro).data
        if isinstance(data, dict) and "materias_json" in data:
            try:
                data["materias_json"] = json.loads(data["materias_json"])
            except Exception:
                data["materias_json"] = []

        return Response({"message": "Maestro actualizado correctamente", "maestro": data}, 200)

    # Eliminar maestro
    @transaction.atomic
    def delete(self, request, id, *args, **kwargs):
        try:
            maestro = Maestros.objects.get(id=id)
        except Maestros.DoesNotExist:
            return Response(
                {"error": "Maestro no encontrado"},
                status=status.HTTP_404_NOT_FOUND
                )
        user_to_delete = maestro.user
        maestro.delete()
        user_to_delete.is_active = 0
        user_to_delete.save()

        return Response(
            {"message": "Maestro eliminado correctamente"},
            status=status.HTTP_204_NO_CONTENT
        )
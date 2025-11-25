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
from django.shortcuts import get_object_or_404

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [] # POST no requiere autenticación  

    def get(self, request, *args, **kwargs):
        alumno_id = kwargs.get("id") or request.GET.get("id")
        alumno = get_object_or_404(Alumnos, id=alumno_id)
        data = AlumnoSerializer(alumno, many=False).data
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

            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID: ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del alumno
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        alumno_id = kwargs.get("id") or request.data.get("id")
        alumno = get_object_or_404(Alumnos, id=alumno_id)
        alumno.matricula = request.data["matricula"]
        alumno.curp = request.data["curp"].upper()
        alumno.rfc = request.data["rfc"].upper()
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.edad = request.data["edad"]
        alumno.telefono = request.data["telefono"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.save()

        user = alumno.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        return Response({"message": "Alumno actualizado correctamente", "alumno": AlumnoSerializer(alumno).data}, 200)

    # Eliminar alumno
    @transaction.atomic
    def delete(self, request, id, *args, **kwargs):
        try:
            alumno = Alumnos.objects.get(id=id)
        except Alumnos.DoesNotExist:
            return Response(
                {"error": "Alumno no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        user_to_delete = alumno.user
        alumno.delete()
        user_to_delete.is_active = 0
        user_to_delete.save()

        return Response(
            {"message": "Alumno eliminado correctamente"},
            status=status.HTTP_204_NO_CONTENT
        )
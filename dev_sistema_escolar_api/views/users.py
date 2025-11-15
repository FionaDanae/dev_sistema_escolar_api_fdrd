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

class AdminAll(generics.CreateAPIView):
    # Listado público para cumplir con la práctica de tablas
    permission_classes = (permissions.AllowAny,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    # Permisos dinámicos: permitir creación sin autenticación, proteger lectura/actualización/eliminación
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # Obtener administrador por ID
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data
        return Response(admin, 200)

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Serializamos los datos del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            #Cifrar la contraseña
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

        return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar datos del administrador
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.data["id"]) 
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"].upper()
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()

        user = admin.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        return Response({"message": "Administrador actualizado correctamente", "admin": AdminSerializer(admin).data}, 200)
    
    # Eliminar administrador
    @transaction.atomic
    def delete(self, request, id, *args, **kwargs):
        try:
            admin = Administradores.objects.get(id=id)
        except Administradores.DoesNotExist:
            return Response(
                {"error": "Administrador no encontrado"},
                status=status.HTTP_404_NOT_FOUND
                )
        user_to_delete = admin.user
        admin.delete()
        user_to_delete.is_active = 0
        user_to_delete.save()

        return Response(
            {"message": "Administrador eliminado correctamente"},
            status=status.HTTP_204_NO_CONTENT
        )

class BootstrapAdminView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Permite crear administrador solo si no existe ninguno
        if Administradores.objects.exists():
            return Response({"message": "Ya existe al menos un administrador"}, status=status.HTTP_403_FORBIDDEN)

        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            password = request.data.get('password')

            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response({"message": "Username "+email+", is already taken"}, 400)

            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )
            user.save()
            user.set_password(password)
            user.save()

            # Asignar rol administrador
            group, _ = Group.objects.get_or_create(name='administrador')
            group.user_set.add(user)
            user.save()

            # Crear perfil Administradores
            admin = Administradores.objects.create(
                user=user,
                clave_admin=request.data.get("clave_admin"),
                telefono=request.data.get("telefono"),
                rfc=(request.data.get("rfc") or "").upper(),
                edad=request.data.get("edad"),
                ocupacion=request.data.get("ocupacion")
            )
            admin.save()

            return Response({"admin_bootstrap_id": admin.id}, status=status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

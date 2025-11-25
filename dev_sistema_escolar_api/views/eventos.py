from django.db.models import *
from django.db import transaction
from dev_sistema_escolar_api.serializers import EventoSerializer
from dev_sistema_escolar_api.models import Eventos, Administradores, Maestros
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class EventosAll(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, *args, **kwargs):
        eventos = Eventos.objects.all().order_by("-creation")
        lista = EventoSerializer(eventos, many=True).data
        return Response(lista, 200)

class EventosView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    def get(self, request, *args, **kwargs):
        evento_id = kwargs.get("id") or request.GET.get("id")
        evento = get_object_or_404(Eventos, id=evento_id)
        data = EventoSerializer(evento, many=False).data
        return Response(data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            nombre_evento = request.data.get('nombre_evento')
            tipo_evento = request.data.get('tipo_evento')
            fecha_realizacion = request.data.get('fecha_realizacion')
            hora_inicio = request.data.get('hora_inicio')
            hora_fin = request.data.get('hora_fin')
            lugar = request.data.get('lugar')
            publico_estudiantes = request.data.get('publico_estudiantes', False)
            publico_profesores = request.data.get('publico_profesores', False)
            publico_general = request.data.get('publico_general', False)
            programa_educativo = request.data.get('programa_educativo', '')
            responsable_id = request.data.get('responsable_id')
            descripcion = request.data.get('descripcion')
            cupo_maximo = request.data.get('cupo_maximo')

            if not all([nombre_evento, tipo_evento, fecha_realizacion, hora_inicio, 
                       hora_fin, lugar, responsable_id, descripcion, cupo_maximo]):
                return Response(
                    {"message": "Todos los campos obligatorios deben estar completos"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not (publico_estudiantes or publico_profesores or publico_general):
                return Response(
                    {"message": "Debe seleccionar al menos un tipo de público objetivo"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            responsable_tipo = None
            try:
                admin = Administradores.objects.get(id=responsable_id)
                responsable_tipo = 'admin'
            except Administradores.DoesNotExist:
                try:
                    maestro = Maestros.objects.get(id=responsable_id)
                    responsable_tipo = 'maestro'
                except Maestros.DoesNotExist:
                    return Response(
                        {"message": "El responsable seleccionado no existe"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            evento = Eventos.objects.create(
                nombre_evento=nombre_evento,
                tipo_evento=tipo_evento,
                fecha_realizacion=fecha_realizacion,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                lugar=lugar,
                publico_estudiantes=publico_estudiantes,
                publico_profesores=publico_profesores,
                publico_general=publico_general,
                programa_educativo=programa_educativo if publico_estudiantes else '',
                responsable_id=responsable_id,
                responsable_tipo=responsable_tipo,
                descripcion=descripcion,
                cupo_maximo=cupo_maximo
            )
            evento.save()

            return Response(
                {
                    "message": "Evento registrado exitosamente",
                    "evento_created_id": evento.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"message": f"Error al registrar el evento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Actualizar evento existente"""
        try:
            evento_id = kwargs.get("id") or request.data.get("id")
            evento = get_object_or_404(Eventos, id=evento_id)

            evento.nombre_evento = request.data.get('nombre_evento', evento.nombre_evento)
            evento.tipo_evento = request.data.get('tipo_evento', evento.tipo_evento)
            evento.fecha_realizacion = request.data.get('fecha_realizacion', evento.fecha_realizacion)
            evento.hora_inicio = request.data.get('hora_inicio', evento.hora_inicio)
            evento.hora_fin = request.data.get('hora_fin', evento.hora_fin)
            evento.lugar = request.data.get('lugar', evento.lugar)
            evento.publico_estudiantes = request.data.get('publico_estudiantes', evento.publico_estudiantes)
            evento.publico_profesores = request.data.get('publico_profesores', evento.publico_profesores)
            evento.publico_general = request.data.get('publico_general', evento.publico_general)
            evento.descripcion = request.data.get('descripcion', evento.descripcion)
            evento.cupo_maximo = request.data.get('cupo_maximo', evento.cupo_maximo)

            if evento.publico_estudiantes:
                evento.programa_educativo = request.data.get('programa_educativo', evento.programa_educativo)
            else:
                evento.programa_educativo = ''

            responsable_id = request.data.get('responsable_id')
            if responsable_id and responsable_id != evento.responsable_id:
                try:
                    Administradores.objects.get(id=responsable_id)
                    evento.responsable_tipo = 'admin'
                except Administradores.DoesNotExist:
                    try:
                        Maestros.objects.get(id=responsable_id)
                        evento.responsable_tipo = 'maestro'
                    except Maestros.DoesNotExist:
                        return Response(
                            {"message": "El responsable seleccionado no existe"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                evento.responsable_id = responsable_id

            evento.save()

            data = EventoSerializer(evento).data
            return Response(
                {
                    "message": "Evento actualizado correctamente",
                    "evento": data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": f"Error al actualizar el evento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def delete(self, request, id, *args, **kwargs):
        """Eliminar evento"""
        try:
            evento = get_object_or_404(Eventos, id=id)
            evento.delete()

            return Response(
                {"message": "Evento eliminado correctamente"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"message": f"Error al eliminar el evento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
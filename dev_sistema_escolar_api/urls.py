from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from dev_sistema_escolar_api.views import bootstrap
from dev_sistema_escolar_api.views import users
from dev_sistema_escolar_api.views import alumnos
from dev_sistema_escolar_api.views import maestros
from dev_sistema_escolar_api.views import auth
from dev_sistema_escolar_api.views import eventos

urlpatterns = [
    path('admin-django/', admin.site.urls),
    path('version/', bootstrap.VersionView.as_view()),
   #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Delete Admin
        path('admin/<int:id>/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
    #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
    #Delete Alumno
        path('alumnos/<int:id>/', alumnos.AlumnosView.as_view()),
    # Alumno Data 
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
    #Delete Maestro
        path('maestros/<int:id>/', maestros.MaestrosView.as_view()),
    # Maestro Data
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    #Total Users
        path('total-usuarios/', users.TotalUsers.as_view()),
    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view()),
    #Create Evento
        path('eventos/', eventos.EventosView.as_view()),
    #Delete Evento
        path('eventos/<int:id>/', eventos.EventosView.as_view()),
    # Evento Data
        path('lista-eventos/', eventos.EventosAll.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

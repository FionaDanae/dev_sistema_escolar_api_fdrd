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

urlpatterns = [
   #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    # Alias API Admin (compatibilidad con frontend)
        path('api/admins/crear/', users.AdminView.as_view()),
        path('api/admins/', users.AdminAll.as_view()),
        path('api/admins/bootstrap/', users.BootstrapAdminView.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
    #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
    # Alias API Alumno (compatibilidad con frontend)
        path('api/alumnos/crear/', alumnos.AlumnosView.as_view()),
        path('api/alumnos/', alumnos.AlumnosAll.as_view()),
        path('api/alumnos/<int:id>/', alumnos.AlumnosView.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
    # Maestro Data (compatibilidad con API original)
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    # Alias API Maestro (compatibilidad con frontend)
        path('api/maestros/crear/', maestros.MaestrosView.as_view()),
        path('api/maestros/', maestros.MaestrosAll.as_view()),
        path('api/maestros/<int:id>/', maestros.MaestrosView.as_view()),
    #Login
        path('token/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path

from . import views

app_name='web'

urlpatterns = [
    path('', views.index,name='index'),
    path('producto/<int:producto_id>',views.producto,name='producto'),
    path('carrito',views.carrito,name='carrito'),
    path('agregarCarrito/<int:producto_id>',views.agregarCarrito,name='agregarCarrito'),
    path('eliminarCarrito/<int:producto_id>',views.eliminarProductoCarrito,name='eliminarCarrito'),
    path('limpiarCarrito',views.limpiarCarrito,name='limpiarCarrito'),
    path('crearUsuario',views.crearUsuario,name='crearUsuario'),
    path('cuenta',views.cuentaUsuario,name='cuentaUsuario'),
    path('login',views.loginUsuario,name='loginUsuario'),
    path('actualizarCliente',views.actualizarCliente,name='actualizarCliente'),
    path('registrarPedido',views.registrarPedido,name='registrarPedido'),
    path('confirmarPedido',views.confirmarPedido,name='confirmarPedido'),
    path('gracias',views.gracias,name='gracias')
]
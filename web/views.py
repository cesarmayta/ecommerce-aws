from django.shortcuts import render,redirect

from django.urls import reverse
# Create your views here.
from .models import (Categoria,Marca,
                     Producto,ProductoImagen,
                     ProductoRelacionado,Cliente,
                     Pedido,PedidoDetalle)
"""
VISTAS PARA EL CATALOGO DE PRODUCTOS
"""
def index(request):
    listaCategorias = Categoria.objects.all()
    listaMarcas = Marca.objects.all()
    listaProductos = Producto.objects.all()
    context = {
        'categorias':listaCategorias,
        'marcas':listaMarcas,
        'productos':listaProductos
    }
    return render(request,'index.html',context)

def producto(request,producto_id):
    objProducto = Producto.objects.get(pk=producto_id)
    context = {
        'producto':objProducto
    }
    return render(request,'producto.html',context)

""" CARRITO DE COMPRAS """
from .carrito import Cart

def carrito(request):
    return render(request,'carrito.html')

def agregarCarrito(request,producto_id):
    if request.method == "POST":
        cantidad = int(request.POST['cantidad'])
    else:
        cantidad = 1
    
    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.add(objProducto,cantidad)
    
    #print(request.session.get("cart"))
    if request.method == "GET":
        return redirect("/")
    
    
    return render(request,'carrito.html')

def eliminarProductoCarrito(request,producto_id):
    objProducto = Producto.objects.get(pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.delete(objProducto)

    return render(request,'carrito.html')

def limpiarCarrito(request):
    carritoProducto = Cart(request)
    carritoProducto.clear()
    
    return render(request,'carrito.html')
      
      
""" USUARIOS Y CLIENTES """
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate

def crearUsuario(request):
    if request.method == "POST":
        dataUsuario = request.POST['nuevo_usuario']
        dataPassword = request.POST['nuevo_password']
        
        objUsuario = User.objects.create_user(username=dataUsuario,password=dataPassword)
        if objUsuario is not None:
            login(request,objUsuario)
            return redirect("/cuenta")
            
    return render(request,'login.html')

def loginUsuario(request):
    paginaDestino = request.GET.get('next',None)
    context = {
        'destino':paginaDestino
    }
    if request.method == "POST":
        dataUsuario = request.POST["usuario"]
        dataPassword = request.POST["password"]
        dataDestino = request.POST['destino']
        
        objUsuario = authenticate(request,username=dataUsuario,password=dataPassword)
        if objUsuario is not None:
            login(request,objUsuario)
            
            if dataDestino != 'None':
                return redirect(dataDestino)
            
            return redirect("/cuenta")
        else:
            context = {
                'mensajeError':'Datos Incorrectos'
            }
        
        
    return render(request,'login.html',context)

from .forms import ClienteForm

def cuentaUsuario(request):
    
    try:
        objCliente = Cliente.objects.get(usuario=request.user)
        
        dataCliente = {
            'dni':objCliente.dni,
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email': request.user.email,
            'direccion':objCliente.direccion,
            'telefono':objCliente.telefono,
            'sexo':objCliente.sexo,
            'fecha_nacimiento':objCliente.fecha_nacimiento
        }
    except:
        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email
        }
    
    frmCliente = ClienteForm(dataCliente)
    context = {
        'frmCliente':frmCliente
    }
    return render(request,'cuenta.html',context)

def actualizarCliente(request):
    mensaje = ""
    frmCliente = ClienteForm(request.POST)
    if frmCliente.is_valid():
        dataCliente = frmCliente.cleaned_data
            
        #actualizar usuario
        actUsuario = User.objects.get(pk=request.user.id)
        actUsuario.first_name = dataCliente["nombre"]
        actUsuario.last_name = dataCliente["apellidos"]
        actUsuario.email = dataCliente["email"]
        actUsuario.save()
            
        #registrar Cliente
        try:
            objCliente = Cliente.objects.get(usuario=request.user)
        except:
            objCliente = Cliente()
                
        objCliente.usuario = actUsuario
        objCliente.nombre = dataCliente["nombre"] + " " + dataCliente["apellidos"]
        objCliente.dni = dataCliente["dni"]
        objCliente.direccion = dataCliente["direccion"]
        objCliente.telefono = dataCliente["telefono"]
        objCliente.sexo = dataCliente["sexo"]
        objCliente.fecha_nacimiento = dataCliente["fecha_nacimiento"]
        objCliente.save()
            
        mensaje = "Datos Actualizados"
            
    context = {
        'mensaje':mensaje,
        'frmCliente':frmCliente
    }
                
    return render(request,'cuenta.html',context)

""" VISTAS PARA PEDIDOS """
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login')
def registrarPedido(request):
    try:
        objCliente = Cliente.objects.get(usuario=request.user)
        
        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
            'direccion':objCliente.direccion,
            'telefono':objCliente.telefono,
            'dni':objCliente.dni,
            'sexo':objCliente.sexo,
            'fecha_nacimiento':objCliente.fecha_nacimiento
        }
    except:
        dataCliente = {
            'nombre':request.user.firt_name,
            'apellidos':request.user.last_name,
            'email':request.user.email
        }
    
    frmCliente = ClienteForm(dataCliente)
    context = {
        'frmCliente':frmCliente
    }
    return render(request,'pedido.html',context)

from paypal.standard.forms import PayPalPaymentsForm

@login_required(login_url='/login')
def confirmarPedido(request):
    context = {}
    if request.method == "POST":
        actUsuario = User.objects.get(pk=request.user.id)
        actUsuario.first_name = request.POST['nombre']
        actUsuario.last_name = request.POST['apellidos']
        actUsuario.email = request.POST['email']
        actUsuario.save()
        
        try:
            clientePedido = Cliente.objects.get(usuario=request.user)
            clientePedido.telefono = request.POST['telefono']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.dni = request.POST['dni']
            clientePedido.save()
        except:
            clientePedido = Cliente()
            clientePedido.usuario = actUsuario
            clientePedido.dni = request.POST['dni']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.telefono = request.POST['telefono']
            clientePedido.save()
        #registramos nuevo pedido
        nroPedido = ''
        montoTotal = float(request.session.get('total'))
        nuevoPedido = Pedido()
        nuevoPedido.cliente = clientePedido
        nuevoPedido.monto_total = 0
        nuevoPedido.save()
        
        #registrmaos el detalle del pedido con el carrito de compras
        carritoPedido = request.session.get('cart')
        for key,value in carritoPedido.items():
            productoPedido = Producto.objects.get(pk=value['producto_id'])
            detalle = PedidoDetalle()
            detalle.pedido = nuevoPedido
            detalle.producto = productoPedido
            detalle.cantidad = int(value['cantidad'])
            detalle.subtotal = float(value['subtotal'])
            detalle.save()
        
        #actualizar pedido
        nroPedido = 'PED' + nuevoPedido.fecha_registro.strftime('%Y') + str(nuevoPedido.id)
        nuevoPedido.nro_pedido = nroPedido
        nuevoPedido.monto_total = montoTotal
        nuevoPedido.save()
        
        #crear boton paypal
        paypal_dict = {
            "business": "sb-ebxbd25387557@business.example.com",
            "amount": montoTotal,
            "item_name": "NRO PEDIDO : " + nroPedido,
            "invoice": nroPedido,
            "notify_url": request.build_absolute_uri('paypal/paypal-ipn'),
            "return": request.build_absolute_uri('/gracias'),
            "cancel_return": request.build_absolute_uri('/'),
        }

        # Create the instance.
        formPaypal = PayPalPaymentsForm(initial=paypal_dict)
        
                
        context = {
            'formPaypal':formPaypal,
            'pedido':nuevoPedido
        }
        
        request.session['pedidoId'] = nuevoPedido.id
        
        carrito = Cart(request)
        carrito.clear()
        
    return render(request,'compra.html',context)
@login_required(login_url='/login')
def gracias(request):
    context = {}
    PayerID = request.GET.get('PayerID',None)
    if PayerID is not None:
        pedidoId = request.session.get('pedidoId')
        pedido = Pedido.objects.get(pk=pedidoId)
        pedido.estado = '1'
        pedido.forma_pago = 'PAYPAL'
        pedido.codigo_pago = PayerID
        pedido.save()
        context = {
            'pedido':pedido
        }
        
    return render(request,'gracias.html',context)
        
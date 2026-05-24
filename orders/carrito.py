from marketplace.models import Producto


class Carrito:
    SESION_KEY = 'carrito'

    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get(self.SESION_KEY)
        if not carrito:
            carrito = {}
            self.session[self.SESION_KEY] = carrito
        self.carrito = carrito

    def agregar(self, producto, cantidad):
        pid = str(producto.pk)
        if pid in self.carrito:
            self.carrito[pid]['cantidad'] += float(cantidad)
        else:
            self.carrito[pid] = {
                'nombre':          producto.nombre,
                'precio_unitario': str(producto.precio_unitario),
                'unidad':          producto.get_unidad_display(),
                'imagen':          producto.imagen.url if producto.imagen else None,
                'cantidad':        float(cantidad),
            }
        self._guardar()

    def actualizar(self, producto_id, cantidad):
        pid = str(producto_id)
        if pid in self.carrito:
            if float(cantidad) <= 0:
                self.eliminar(producto_id)
            else:
                self.carrito[pid]['cantidad'] = float(cantidad)
                self._guardar()

    def eliminar(self, producto_id):
        pid = str(producto_id)
        if pid in self.carrito:
            del self.carrito[pid]
            self._guardar()

    def limpiar(self):
        del self.session[self.SESION_KEY]
        self.session.modified = True

    def _guardar(self):
        self.session.modified = True

    def __iter__(self):
        for pid, item in self.carrito.items():
            yield {
                'producto_id':     int(pid),
                'nombre':          item['nombre'],
                'precio_unitario': float(item['precio_unitario']),
                'unidad':          item['unidad'],
                'imagen':          item['imagen'],
                'cantidad':        item['cantidad'],
                'subtotal':        float(item['precio_unitario']) * item['cantidad'],
            }

    def total(self):
        return sum(
            float(i['precio_unitario']) * i['cantidad']
            for i in self.carrito.values()
        )

    def cantidad_total(self):
        return sum(i['cantidad'] for i in self.carrito.values())

    def __len__(self):
        return len(self.carrito)
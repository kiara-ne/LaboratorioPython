# Herramientas de FastAPI:
#   - FastAPI: crea la aplicación (la API)
#   - HTTPException: permite devolver errores con un código HTTP (por ejemplo, 404)
#   - status: constantes con nombre para los códigos HTTP (status.HTTP_404_NOT_FOUND en vez de 404)
from fastapi import FastAPI, HTTPException, status

# Traigo desde mi archivo database.py:
#   - Product: la clase que representa la tabla "products"
#   - session: la sesión para leer y guardar datos en la base
from database import Product, session, Sale, Cart, CartProduct
from schema import ProductResponse,ProductCreate, SalesResponse, SalesCreate, CartCreate, CartResponse,CartItemResponse,CartProductCreate

# Instancia de la API: a esta variable se le van a ir registrando todos los endpoints
app = FastAPI()


# Decorador: crea el endpoint GET en la ruta "/products".
# response_model: lo que devuelve es una LISTA de ProductResponse (id, name, price)
@app.get("/products", response_model=list[ProductResponse])
def list_products():

    try:
        # Le pido a la sesión TODAS las filas de la tabla Product (una lista de objetos)
        products = session.query(Product).all()
        return products
    # except: se ejecuta solo si hubo un error inesperado dentro del try
    except Exception as e:
        # Deshago cambios a medias para que la sesión quede limpia
        session.rollback()
        # Devuelvo un error 500 (falló el servidor) con el detalle del error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get products: {e}",
        )

@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id:int):

    try:
        product = session.get(Product, id)   

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"The product does not exist"
            )
    
        return product

    except HTTPException:        # acá se atrapa ese error (solo para dejarlo pasar)
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get product: {e}",
        )

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate):

    try:
        new_product = Product(name=data.name, price=data.price)
        session.add(new_product)
        session.commit()
        session.refresh(new_product) # traer de la base el id que se generó

        return new_product

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to create the product: {e}",
        )

@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id:int, data:ProductCreate):

    try:
        # Busco el producto que quiero modificar
        product = session.get(Product, id)   
        # Qué pasa si no existe
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The product does not exist"
            )
        product.name=data.name
        product.price=data.price
        session.commit() #Guardo los cambios en la base
        session.refresh(product) # Recargo el producto desde la base con los datos ya guardados
        return product

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to update the product: {e}",
        )

@app.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id:int):
    try:
        product = session.get(Product,id)
        # Que pasa si no existe
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The product does not exist"
            )

        session.delete(product)
        session.commit()

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to delete the product: {e}",
        )       





@app.get("/sales", response_model=list[SalesResponse])
def list_sales():

    try:
        sales = session.query(Sale).all()
        return sales
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get sales {e}",
        )

@app.get("/sales/{id}", response_model=SalesResponse)
def get_sale (id:int):
    try:
        sale = session.get(Sale, id)

        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The sale does not exist"
            )
        return sale
        
    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get sale: {e}",
        )

@app.post("/sales", response_model=SalesResponse, status_code=status.HTTP_201_CREATED)
def create_sale(data:SalesCreate):

    try:
        product = session.get(Product, data.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "the product does not exist",
            )

        total = product.price * data.amount

        new_sale = Sale (
            date = data.date,
            time = data.time,
            product_id = data.product_id,
            amount = data.amount,
            total_price = total
        )

        session.add(new_sale)
        session.commit()
        session.refresh(new_sale) # traer de la base el id que se generó

        return new_sale

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to create a new sale: {e}",
        )

@app.put("/sales/{id}", response_model=SalesResponse)
def update_sale(id:int, data:SalesCreate):

    try:

        sale = session.get(Sale, id)

        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The sale does not exist",
            )

        # Busco el producto nuevo (el del body) para poder leer su precio
        product = session.get(Product, data.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The product does not exist",
            )

        # Recalculo el total con el precio del producto y la cantidad nueva
        total = product.price * data.amount

        sale.date = data.date
        sale.time = data.time
        sale.product_id = data.product_id
        sale.amount = data.amount
        sale.total_price = total

        session.commit()
        session.refresh(sale)
        return sale

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to update the sale: {e}",
        )

@app.delete("/sales/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale (id:int):
    try:
        sale=session.get(Sale, id)

        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The sale does not exist"
            )

        session.delete(sale)
        session.commit()

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to delete the sale: {e}",
        )



@app.get ("/carts", response_model=list[CartResponse])
def list_carts():

    try:
        carts = session.query(Cart).all()
        return carts
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get carts {e}",
        )

@app.get("/carts/{id}", response_model=CartResponse)
def get_cart (id:int):

    try: 
        cart = session.get(Cart, id)

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart does not exist"
            )
        return cart
    
    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to get cart: {e}",
        )

@app.post ("/carts", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart (data:CartCreate):

    try:
        new_cart = Cart (creation_date=data.creation_date,state=data.state)
        session.add(new_cart)
        session.commit()
        session.refresh(new_cart)

        return new_cart

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to create the cart: {e}",
        )

@app.put ("/carts/{id}", response_model=CartResponse)
def update_cart (id:int, data:CartCreate):

    try:
        cart = session.get(Cart, id)

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart does not exist",
            )

        cart.state = data.state
        session.commit()
        session.refresh(cart)
        return cart

    
    except HTTPException:
        raise
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to update the cart: {e}",
        )

@app.delete ("/carts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(id: int):
    try:
        cart = session.get(Cart, id)

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart does not exist",
            )

        session.query(CartProduct).filter(CartProduct.cart_id == id).delete()
        session.delete(cart)
        session.commit()

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to delete the cart: {e}",
        )


# POST /carts/{id}/products: agrega un producto a un carrito abierto y devuelve el carrito con sus items
@app.post("/carts/{id}/products", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_product_to_cart(id: int, data: CartProductCreate):
    try:
        # Busco el carrito con el id que llegó en la URL
        cart = session.get(Cart, id)

        # Si el carrito no existe, devuelvo 404
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart does not exist",
            )

        # Solo se pueden agregar productos a un carrito abierto; si no, 400
        if cart.state != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The cart is not open",
            )

        # Busco el producto usando el product_id que llegó en el body
        product = session.get(Product, data.product_id)

        # Si el producto no existe, devuelvo 404
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The product does not exist",
            )

        # La cantidad tiene que ser mayor a 0; si no, 400
        if data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The amount must be greater than 0",
            )

        # Busco si ese producto ya está cargado en este carrito (fila de cart_product)
        cart_product = session.query(CartProduct).filter_by(cart_id=cart.id, product_id=data.product_id).first()

        if cart_product:
            # Ya estaba en el carrito: le sumo la cantidad nueva, sin crear otra fila
            cart_product.amount += data.amount
        else:
            # No estaba: creo una fila nueva en cart_product
            cart_product = CartProduct(cart_id=cart.id, product_id=data.product_id, amount=data.amount)
            session.add(cart_product)

        # Guardo los cambios en la base
        session.commit()

        # Recargo el carrito para que su lista items incluya la fila nueva o actualizada
        session.refresh(cart)

        # Devuelvo el carrito (no la fila), porque el response_model es el del carrito
        return cart

    # Dejo pasar los 404 y 400 que levanté yo, para que el except de abajo no los convierta en 500
    except HTTPException:
        raise

    # Cualquier otro error inesperado (por ejemplo, falla la base) cae acá
    except Exception as e:
        # Deshago lo que quedó a medias para dejar la sesión limpia
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to add the product to the cart: {e}",
        )

# DELETE /carts/{id}/products/{product_id}: quita un producto de un carrito abierto y devuelve el carrito actualizado
@app.delete("/carts/{id}/products/{product_id}", response_model=CartResponse)
def remove_product_from_cart(id: int, product_id: int):
    try:
        # Busco el carrito con el id que llegó en la URL
        cart = session.get(Cart, id)

        # Si el carrito no existe, devuelvo 404
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart does not exist",
            )

        # Solo se pueden quitar productos de un carrito abierto; si no, 400
        if cart.state != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The cart must be open",
            )

        # Busco la fila de cart_product que une este carrito con este producto
        cart_product = session.query(CartProduct).filter_by(cart_id=cart.id, product_id=product_id).first()

        # Si el producto no está en el carrito, devuelvo 404
        if cart_product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="That product does not exist in the cart",
            )

        # Borro la fila y guardo el cambio en la base
        session.delete(cart_product)
        session.commit()

        # Recargo el carrito para que items ya no incluya el producto quitado
        session.refresh(cart)

        # Devuelvo el carrito actualizado
        return cart

    # Dejo pasar los 404 y 400 que levanté yo, para que el except de abajo no los convierta en 500
    except HTTPException:
        raise

    # Cualquier otro error inesperado cae acá
    except Exception as e:
        # Deshago lo que quedó a medias para dejar la sesión limpia
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trying to remove the product from the cart: {e}",
        )
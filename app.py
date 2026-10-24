# Herramientas de FastAPI:
#   - FastAPI: crea la aplicación (la API)
#   - HTTPException: permite devolver errores con un código HTTP (por ejemplo, 404)
#   - status: constantes con nombre para los códigos HTTP (status.HTTP_404_NOT_FOUND en vez de 404)
from fastapi import FastAPI, HTTPException, status

# Traigo desde mi archivo database.py:
#   - Product: la clase que representa la tabla "products"
#   - session: la sesión para leer y guardar datos en la base
from database import Product, session, Sale
from schema import ProductResponse,ProductCreate, SalesResponse, SalesCreate

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
                detail="The sale does not exists"
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




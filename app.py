# Herramientas de FastAPI:
#   - FastAPI: crea la aplicación (la API)
#   - HTTPException: permite devolver errores con un código HTTP (por ejemplo, 404)
#   - status: constantes con nombre para los códigos HTTP (status.HTTP_404_NOT_FOUND en vez de 404)
from fastapi import FastAPI, HTTPException, status

# Traigo desde mi archivo database.py:
#   - Product: la clase que representa la tabla "products"
#   - session: la sesión para leer y guardar datos en la base
from database import Product, session
from schema import ProductResponse,ProductCreate


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


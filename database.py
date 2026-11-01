from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Motor: la conexión con la base de datos SQLite
engine = create_engine("sqlite:///database.db", echo=True)

# Base: de esta clase van a heredar todos los modelos (tablas)
Base = declarative_base()

# Fábrica de sesiones: cada sesión es una "conversación" con la base
SessionLocal = sessionmaker(bind=engine)


# Modelo: la clase Product representa la tabla "products"
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

# Venta: tiene fecha, hora, un único carrito y el total calculado a partir de ese carrito
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), unique=True, nullable=False)
    total_price = Column(Float, nullable=False)

    # Atajo para llegar al carrito completo de esta venta
    cart = relationship("Cart")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    creation_date = Column(Date, nullable=False)
    state = Column(String, nullable=False)

    items = relationship("CartProduct", back_populates="cart")


class CartProduct(Base):
    __tablename__ = "cart_product"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    amount = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

# Crea las tablas en el archivo database.db si todavía no existen
Base.metadata.create_all(engine)

# Sesión: es el "canal de conversación" entre mi código Python y la base de datos.
# SessionLocal es la fábrica (prepara cómo se crean las sesiones) y
# SessionLocal() usa esa fábrica para abrir una sesión concreta, que guardo en "session".
# Esta línea no crea tablas ni guarda datos por sí sola: solo deja lista la conexión.
session = SessionLocal()

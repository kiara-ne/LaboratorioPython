from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

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


# Crea las tablas en el archivo database.db si todavía no existen
Base.metadata.create_all(engine)

# Sesión: es el "canal de conversación" entre mi código Python y la base de datos.
# SessionLocal es la fábrica (prepara cómo se crean las sesiones) y
# SessionLocal() usa esa fábrica para abrir una sesión concreta, que guardo en "session".
# Esta línea no crea tablas ni guarda datos por sí sola: solo deja lista la conexión.
session = SessionLocal()

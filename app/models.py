from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.database import Base

class Estado(PyEnum):
    SIN_EMPEZAR = "Sin Empezar"
    EMPEZADA = "Empezada"
    FINALIZADA = "Finalizada"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, unique=True, index=True, nullable=False)
    contrasena = Column(String, nullable=False)
    imagen_perfil = Column(String, nullable=False)

    tareas = relationship("Tarea", back_populates="usuario")
    categorias = relationship("Categoria", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    tareas = relationship("Tarea", back_populates="categoria")
    usuario = relationship("Usuario", back_populates="categorias")

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    texto_tarea = Column(String, nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    fecha_tentativa_finalizacion = Column(Date, nullable=False)
    estado = Column(Enum(Estado), default=Estado.SIN_EMPEZAR, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="tareas")
    categoria = relationship("Categoria", back_populates="tareas")
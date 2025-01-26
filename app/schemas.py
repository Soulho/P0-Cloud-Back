from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

class EstadoEnum(str, Enum):
    SIN_EMPEZAR = "Sin Empezar"
    EMPEZADA = "Empezada"
    FINALIZADA = "Finalizada"

class UsuarioBase(BaseModel):
    nombre_usuario: str
    imagen_perfil: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioLogin(BaseModel):
    nombre_usuario: str
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id: int
    tareas: List["TareaResponse"] = []

    class Config:
        orm_mode = True

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        orm_mode = True

class TareaBase(BaseModel):
    texto_tarea: str
    fecha_creacion: date
    fecha_tentativa_finalizacion: date
    estado: EstadoEnum

class TareaCreate(TareaBase):
    id_usuario: int
    id_categoria: int

class TareaResponse(TareaBase):
    id: int
    categoria: CategoriaResponse

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
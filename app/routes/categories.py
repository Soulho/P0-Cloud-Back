from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaCreate, CategoriaResponse
from app.auth import get_current_user_id
from typing import List

router = APIRouter()

# **1. Crear Categoría**
@router.post("/categories", response_model=CategoriaResponse)
def create_category(categoria: CategoriaCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):

    nueva_categoria = Categoria(
        nombre=categoria.nombre,
        descripcion=categoria.descripcion,
        id_usuario=current_user_id  # Relacionar con el usuario autenticado
    )
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

# **2. Actualizar Categoría**
@router.put("/categories/{id}", response_model=CategoriaResponse)
def update_category(id: int, categoria: CategoriaCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):

    categoria_db = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )

    # Verificar que el usuario autenticado sea el dueño de la categoría
    if categoria_db.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para actualizar esta categoría"
        )

    # Actualizar los campos
    categoria_db.nombre = categoria.nombre
    categoria_db.descripcion = categoria.descripcion
    db.commit()
    db.refresh(categoria_db)
    return categoria_db

# **3. Eliminar Categoría**
@router.delete("/categories/{id}")
def delete_category(id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):

    categoria_db = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Categoría no encontrada"
        )

    # Verificar que el usuario autenticado sea el dueño de la categoría
    if categoria_db.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para eliminar esta categoría"
        )

    # Eliminar la categoría
    db.delete(categoria_db)
    db.commit()
    return {"message": "Categoría eliminada exitosamente"}

@router.get("/categories", response_model=List[CategoriaResponse])
def get_all_categories(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    categorias = db.query(Categoria).filter(Categoria.id_usuario == current_user_id).all()
    return categorias
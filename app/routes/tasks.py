from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Estado, Tarea, Categoria, Usuario
from app.schemas import TareaCreate, TareaResponse
from app.auth import get_current_user_id
from typing import List
from datetime import date

router = APIRouter()

@router.get("/usuarios/{id}/tareas", response_model=List[TareaResponse])
def get_tasks_by_user(id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    # Validar que el usuario autenticado corresponde al usuario solicitado
    if current_user_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver las tareas de este usuario"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return usuario.tareas

@router.post("/tareas", response_model=TareaResponse)
def create_task(task: TareaCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    # Validar si la fecha tentativa es menor a la fecha actual
    if task.fecha_tentativa_finalizacion < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha tentativa de finalización no puede ser anterior a la fecha actual",
        )
    
    # Autenticar el usuario
    if task.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear una tarea para otro usuario"
        )
    
    # Validar si la categoría existe
    categoria = db.query(Categoria).filter(Categoria.id == task.id_categoria).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    try:
        new_estado = Estado(task.estado)  # Convierte el string a Enum
    except ValueError:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    nueva_tarea = Tarea(
        texto_tarea=task.texto_tarea,
        fecha_creacion=date.today(),
        fecha_tentativa_finalizacion=task.fecha_tentativa_finalizacion,
        estado=new_estado,
        id_usuario=current_user_id,
        id_categoria=task.id_categoria,
    )
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea

@router.put("/tareas/{id}", response_model=TareaResponse)
def update_task(id: int, updated_task: TareaCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    tarea = db.query(Tarea).filter(Tarea.id == id).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    
    # Validar el usuario
    if tarea.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta tarea"
        )

    try:
        new_estado = Estado(updated_task.estado)  # Convierte el string a Enum
    except ValueError:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    tarea.texto_tarea = updated_task.texto_tarea
    tarea.estado = new_estado
    tarea.fecha_tentativa_finalizacion = updated_task.fecha_tentativa_finalizacion
    tarea.id_categoria = updated_task.id_categoria
    db.commit()
    db.refresh(tarea)
    return tarea

@router.delete("/tareas/{id}")
def delete_task(id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    tarea = db.query(Tarea).filter(Tarea.id == id).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    
    # Validar  el usuario
    if tarea.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta tarea"
        )
    
    db.delete(tarea)
    db.commit()
    return {"message": "Tarea eliminada exitosamente"}

@router.get("/tareas/{id}", response_model=TareaResponse)
def get_task_by_id(id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    tarea = db.query(Tarea).filter(Tarea.id == id).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    
    # Validar el usuario
    if tarea.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta tarea"
        )
    
    return tarea

@router.patch("/tareas/{id}/estado", response_model=TareaResponse)
def update_task_status(id: int, estado: str, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    
    tarea = db.query(Tarea).filter(Tarea.id == id).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    
    # Validar el usuario
    if tarea.id_usuario != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar esta tarea"
        )
    try:
        new_estado = Estado(estado)  # Convierte el string a Enum
    except ValueError:
        raise HTTPException(status_code=400, detail="Estado inválido")
    # Actualizar el estado
    tarea.estado = new_estado
    db.commit()
    db.refresh(tarea)
    return tarea

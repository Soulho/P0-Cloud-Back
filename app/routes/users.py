from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioLogin, Token, UsuarioResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

DEFAULT_PROFILE_IMAGE = "default_profile_icon.png"

@router.post("/users", response_model=Token)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Usuario).filter(Usuario.nombre_usuario == user.nombre_usuario).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    profile_image = user.imagen_perfil if user.imagen_perfil else DEFAULT_PROFILE_IMAGE

    new_user = Usuario(
        nombre_usuario=user.nombre_usuario,
        contrasena=hash_password(user.contrasena),
        imagen_perfil=profile_image
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/login", response_model=Token)
def login(user: UsuarioLogin, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.nombre_usuario == user.nombre_usuario).first()
    if not db_user or not verify_password(user.contrasena, db_user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/logout")
def logout():
    return {"message": "Sesión cerrada exitosamente"}

@router.get("/users", response_model=List[UsuarioResponse])
def get_all_users(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()  # Consulta todos los usuarios de la tabla
    return usuarios
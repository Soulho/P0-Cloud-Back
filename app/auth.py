from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Configuración para hashing de contraseñas y tokens JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obtener el token del encabezado
def get_token_from_header(authorization: str = Depends(lambda: "Bearer token")) -> str:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no provisto o esquema inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

bearer_scheme = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    token = credentials.credentials  # Extraer el token del encabezado Authorization
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # Extraer el campo "sub" del payload
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return int(user_id)  # Convertir el ID del usuario a entero
    except JWTError as e:
        # Registro para depuración
        print(f"Error al validar el token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
            headers={"WWW-Authenticate": "Bearer"},
        )
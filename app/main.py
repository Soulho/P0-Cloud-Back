from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.database import Base, engine
from app.routes import users, tasks, categories
from app import models

app = FastAPI()

# Permitir CORS para evitar bloqueos en las solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos en lugar de "*"
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los encabezados HTTP
)

# Inicializar la base de datos
Base.metadata.create_all(bind=engine)

# Configuración de autenticación con OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

security_scheme = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

# Incluir seguridad en el esquema OpenAPI (Swagger)
@app.on_event("startup")
def customize_openapi():
    if app.openapi_schema:
        app.openapi_schema["components"]["securitySchemes"] = security_scheme
        app.openapi_schema["security"] = [{"BearerAuth": []}]

# Incluir las rutas definidas en los routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])

# Ruta raíz para verificar que la API está funcionando
@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
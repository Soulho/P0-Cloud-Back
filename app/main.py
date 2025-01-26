from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users, tasks, categories
from app import models
from fastapi.security import OAuth2PasswordBearer


app = FastAPI()

Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

security_scheme = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

# Incluir seguridad en el esquema OpenAPI
@app.on_event("startup")
def customize_openapi():
    if app.openapi_schema:
        app.openapi_schema["components"]["securitySchemes"] = security_scheme
        app.openapi_schema["security"] = [{"BearerAuth": []}]

app.include_router(users.router, prefix="/users")
app.include_router(tasks.router, prefix="/tasks")
app.include_router(categories.router, prefix="/categories")

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}


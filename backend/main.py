from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.routes.database_routes import router as database_router
from app.routes.cron_routes import router as cron_router
from app.services.cron_service import cron_service

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Criação da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para sincronização de tabelas entre bancos de dados MySQL",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas
app.include_router(database_router)
app.include_router(cron_router)


@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": "Database Sync API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/database/health"
    }


@app.get("/health")
async def health():
    """Health check simples"""
    return {"status": "healthy", "version": settings.app_version}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado quando a aplicação é encerrada"""
    logger.info("Encerrando aplicação...")
    cron_service.shutdown()


if __name__ == "__main__":
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 
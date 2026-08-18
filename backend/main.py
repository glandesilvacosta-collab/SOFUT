import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from seed import seed_data
from routes.items import router as items_router
from routes.members import router as members_router
from routes.movements import router as movements_router
from routes.stats import router as stats_router

app = FastAPI(
    title="Patrimônio da Família - Gestão de Ativos e Equipamentos",
    description="API REST para controle de empréstimos, inventário, vistorias e castigos da família de Carlos, Maria, Carlinhos, Aninha, Cleusa, Julinha, Didi e Titi.",
    version="1.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Banco e Seed ao iniciar
@app.on_event("startup")
def on_startup():
    init_db()
    seed_data(force=False)

# Incluir rotas da API
app.include_router(items_router)
app.include_router(members_router)
app.include_router(movements_router)
app.include_router(stats_router)

# Caminho do Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

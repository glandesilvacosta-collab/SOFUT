import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# Adicionar pasta backend ao path
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from database import init_db
from seed import seed_data

def open_browser():
    """Abre o navegador automaticamente após o servidor iniciar."""
    time.sleep(1.2)
    print("\n🌐 Abrindo o painel no navegador: http://127.0.0.1:8000")
    webbrowser.open("http://127.0.0.1:8000")

def main():
    print("=" * 60)
    print("🏠⚙️  PATRIMÔNIO DA FAMÍLIA - SISTEMA DE GESTÃO DE ATIVOS")
    print("=" * 60)
    print("📦 Inicializando banco de dados relacional SQLite...")
    init_db()
    seed_data(force=False)
    print("✅ Banco pronto com os 8 integrantes da família e itens!")
    print("🚀 Servidor FastAPI iniciando em http://127.0.0.1:8000")
    print("📖 Documentação Swagger da API: http://127.0.0.1:8000/docs")
    print("=" * 60)

    # Iniciar thread do navegador
    threading.Thread(target=open_browser, daemon=True).start()

    # Rodar servidor Uvicorn
    uvicorn.run("main:app", app_dir=str(BACKEND_DIR), host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

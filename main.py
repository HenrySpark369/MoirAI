"""
Punto de entrada principal para MoirAI (DEPRECATED)

NOTA: Este archivo es solo para compatibilidad. 
La aplicación principal ahora está en app/main.py

Para ejecutar la aplicación:
uvicorn app.main:app --reload

O ejecutar directamente:
python -m app.main
"""

# Importar la aplicación desde la nueva estructura
try:
    from app.main import app
    print("✅ Aplicación cargada desde app/main.py")
except ImportError as e:
    print(f"❌ Error importando aplicación: {e}")
    print("Asegúrese de tener instaladas las dependencias:")
    print("pip install -r requirements.txt")
    raise


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando MoirAI desde main.py (DEPRECATED)")
    print("💡 Use 'uvicorn app.main:app --reload' para desarrollo")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
#!/bin/bash

# Script de configuración inicial segura para MoirAI
echo "🔐 Configurando MoirAI de forma segura..."

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Ejecute este script desde el directorio raíz del proyecto MoirAI"
    exit 1
fi

# Verificar/activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🐍 Usando entorno virtual .venv..."
    source .venv/bin/activate
    PYTHON_CMD="python"
else
    echo "⚠️  Entorno virtual no encontrado, usando Python del sistema..."
    # Intentar diferentes comandos de Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Error: No se encontró Python instalado"
        exit 1
    fi
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    
    # Generar SECRET_KEY segura
    echo "🔑 Generando SECRET_KEY segura..."
    SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Generar ENCRYPTION_KEY segura
    echo "🔐 Generando ENCRYPTION_KEY segura para encriptación..."
    ENCRYPTION_KEY=$($PYTHON_CMD -c "from app.utils.encryption import EncryptionService; print(EncryptionService.generate_key())")
    
    # Reemplazar SECRET_KEY y ENCRYPTION_KEY en .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
        sed -i '' "s/your-encryption-key-change-in-production/$ENCRYPTION_KEY/" .env
    else
        # Linux
        sed -i "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
        sed -i "s/your-encryption-key-change-in-production/$ENCRYPTION_KEY/" .env
    fi
    
    echo "✅ Archivo .env creado con SECRET_KEY y ENCRYPTION_KEY seguras"
    echo "⚠️  IMPORTANTE: Revise y configure las demás variables en .env"
else
    echo "ℹ️  El archivo .env ya existe"
fi

# Crear archivo .env.docker si no existe
if [ ! -f ".env.docker" ]; then
    echo "🐳 Creando archivo .env.docker para Docker Compose..."
    cp .env.docker.example .env.docker
    
    # Generar contraseñas seguras
    DB_PASSWORD=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(16))")
    ADMIN_PASSWORD=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(12))")
    SECRET_KEY_DOCKER=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Reemplazar en .env.docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/change_this_secure_password/$DB_PASSWORD/g" .env.docker
        sed -i '' "s/change_this_admin_password/$ADMIN_PASSWORD/g" .env.docker
        sed -i '' "s/generate_a_secure_secret_key_here/$SECRET_KEY_DOCKER/" .env.docker
    else
        # Linux
        sed -i "s/change_this_secure_password/$DB_PASSWORD/g" .env.docker
        sed -i "s/change_this_admin_password/$ADMIN_PASSWORD/g" .env.docker
        sed -i "s/generate_a_secure_secret_key_here/$SECRET_KEY_DOCKER/" .env.docker
    fi
    
    echo "✅ Archivo .env.docker creado con contraseñas seguras"
else
    echo "ℹ️  El archivo .env.docker ya existe"
fi

echo ""
echo "🎉 Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Revise y configure las variables en .env"
echo "2. Configure las API keys externas si es necesario"
echo "3. Para desarrollo local: python -m uvicorn app.main:app --reload"
echo "4. Para Docker: docker-compose --env-file .env.docker up -d"
echo ""
echo "🔒 Recordatorios de seguridad:"
echo "- Nunca commite archivos .env al repositorio"
echo "- Use contraseñas fuertes en producción"
echo "- Habilite HTTPS en producción"
echo "- Configure firewall apropiadamente"
echo "- La ENCRYPTION_KEY se usa para encriptar campos sensibles (emails, teléfonos)"
echo "- En caso de perder la ENCRYPTION_KEY, no podrá desencriptar datos existentes"

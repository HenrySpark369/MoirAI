"""
Utilidades para procesamiento de archivos
Extracción de texto de PDFs, DOCX y archivos de texto
"""
import io
from typing import Union
from fastapi import UploadFile, HTTPException

# Importaciones de librerías de procesamiento de archivos
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx2txt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from app.middleware.auth import security_middleware


def extract_text_from_upload(file: UploadFile) -> str:
    """
    Extraer texto de archivo subido (PDF, DOCX o TXT)
    
    Args:
        file: Archivo subido a través de FastAPI
        
    Returns:
        str: Texto extraído del archivo
        
    Raises:
        HTTPException: Si hay error en el procesamiento
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
    
    # Leer contenido del archivo
    try:
        content = file.file.read()
        file.file.seek(0)  # Reset para futuras lecturas
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error leyendo archivo: {str(e)}"
        )
    
    # Validar archivo por seguridad
    security_middleware.validate_file_upload(content, file.filename)
    
    # Determinar tipo de archivo y extraer texto
    filename_lower = file.filename.lower()
    
    try:
        if filename_lower.endswith('.pdf'):
            return _extract_text_from_pdf(content)
        elif filename_lower.endswith(('.docx', '.doc')):
            return _extract_text_from_docx(content)
        elif filename_lower.endswith('.txt'):
            return _extract_text_from_txt(content)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado: {file.filename}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando archivo {file.filename}: {str(e)}"
        )


def _extract_text_from_pdf(content: bytes) -> str:
    """Extraer texto de archivo PDF"""
    if not PDF_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Procesamiento de PDF no disponible. Instale pdfminer.six"
        )
    
    try:
        text = pdf_extract_text(io.BytesIO(content))
        if not text or len(text.strip()) < 10:
            raise ValueError("PDF parece estar vacío o contiene solo imágenes")
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extrayendo texto de PDF: {str(e)}"
        )


def _extract_text_from_docx(content: bytes) -> str:
    """Extraer texto de archivo DOCX"""
    if not DOCX_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Procesamiento de DOCX no disponible. Instale python-docx"
        )
    
    try:
        text = docx2txt.process(io.BytesIO(content))
        if not text or len(text.strip()) < 10:
            raise ValueError("Documento DOCX parece estar vacío")
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extrayendo texto de DOCX: {str(e)}"
        )


def _extract_text_from_txt(content: bytes) -> str:
    """Extraer texto de archivo TXT"""
    try:
        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                text = content.decode(encoding)
                if text and len(text.strip()) >= 10:
                    return text
            except UnicodeDecodeError:
                continue
        
        # Si ningún encoding funciona
        raise ValueError("No se pudo decodificar el archivo de texto")
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error procesando archivo de texto: {str(e)}"
        )


def validate_file_for_processing(file: UploadFile) -> bool:
    """
    Validar que el archivo es apropiado para procesamiento
    
    Args:
        file: Archivo a validar
        
    Returns:
        bool: True si el archivo es válido
        
    Raises:
        HTTPException: Si el archivo no es válido
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
    
    # Verificar extensión
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida: {file_ext}. Permitidas: {allowed_extensions}"
        )
    
    # Verificar que el contenido type es apropiado (si está disponible)
    if hasattr(file, 'content_type') and file.content_type:
        allowed_content_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain'
        }
        
        if file.content_type not in allowed_content_types:
            # Advertencia pero no error crítico (content_type puede ser incorrecto)
            pass
    
    return True


def get_file_info(file: UploadFile) -> dict:
    """
    Obtener información del archivo subido
    
    Args:
        file: Archivo subido
        
    Returns:
        dict: Información del archivo
    """
    file_size = None
    try:
        current_pos = file.file.tell()
        file.file.seek(0, 2)  # Ir al final
        file_size = file.file.tell()
        file.file.seek(current_pos)  # Volver a posición original
    except:
        pass
    
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    return {
        'filename': file.filename,
        'content_type': getattr(file, 'content_type', None),
        'size_bytes': file_size,
        'extension': file_ext,
        'size_mb': round(file_size / (1024 * 1024), 2) if file_size else None
    }

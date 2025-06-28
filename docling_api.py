from fastapi import FastAPI, UploadFile, File, HTTPException
from docling.document_converter import DocumentConverter
import uvicorn
import tempfile
import os
from pathlib import Path

app = FastAPI(title="Docling API", description="API para conversão de documentos usando Docling")

# Inicializar o conversor Docling
converter = DocumentConverter()

@app.post("/convert")
async def convert_document(file: UploadFile = File(...)):
    """
    Converte qualquer documento suportado pelo Docling para formato estruturado
    """
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            # Salvar arquivo enviado
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Processar com Docling
            result = converter.convert(temp_file_path)
            
            # Retornar resultado estruturado
            return {
                "status": "success",
                "filename": file.filename,
                "content_type": file.content_type,
                "document": result.document.export_to_dict(),
                "message": "Documento convertido com sucesso"
            }
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docling-api"}

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "service": "Docling API",
        "version": "1.0.0",
        "endpoints": {
            "convert": "POST /convert - Converte documentos",
            "health": "GET /health - Status da API"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
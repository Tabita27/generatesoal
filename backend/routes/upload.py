from fastapi import APIRouter, UploadFile, File, HTTPException
from services.extractor import extract_text_from_pdf, extract_text_from_docx

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    content = await file.read()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(content)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(content)
    elif filename.endswith(".txt"):
        text = content.decode("utf-8")
    else:
        raise HTTPException(
            status_code=400,
            detail="Format file tidak didukung. Gunakan PDF, DOCX, atau TXT."
        )

    if len(text.strip()) < 100:
        raise HTTPException(
            status_code=422,
            detail="Teks terlalu pendek. Minimal 100 karakter."
        )

    return {
        "filename": file.filename,
        "text": text,
        "word_count": len(text.split())
    }
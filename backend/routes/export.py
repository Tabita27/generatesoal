from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Dict
from services.exporter import export_to_docx, export_to_pdf
import io

router = APIRouter()

class Question(BaseModel):
    nomor: int
    pertanyaan: str
    tipe: str
    pilihan: Dict[str, str] = {}
    kunci_jawaban: str
    tingkat_kesulitan: str

class ExportRequest(BaseModel):
    judul: str
    questions: List[Question]
    format: Literal["docx", "pdf"] = "docx"

@router.post("/")
async def export(req: ExportRequest):
    if req.format == "docx":
        file_bytes = export_to_docx(req.judul, req.questions)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{req.judul}.docx"
    else:
        file_bytes = export_to_pdf(req.judul, req.questions)
        media_type = "application/pdf"
        filename = f"{req.judul}.pdf"

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
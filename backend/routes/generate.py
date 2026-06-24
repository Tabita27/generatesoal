from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from services.nlp_service import generate_questions, extract_keywords

router = APIRouter()

class GenerateRequest(BaseModel):
    text: str
    question_type: Literal["pilihan_ganda", "isian", "campuran"] = "campuran"
    jumlah_soal: int = 5
    tingkat_kesulitan: Literal["mudah", "sedang", "sulit", "campuran"] = "campuran"

@router.post("/")
async def generate(req: GenerateRequest):
    if len(req.text.strip()) < 100:
        raise HTTPException(status_code=422, detail="Teks terlalu pendek.")
    if req.jumlah_soal < 1 or req.jumlah_soal > 20:
        raise HTTPException(status_code=422, detail="Jumlah soal harus 1-20.")

    keywords = extract_keywords(req.text)
    questions = generate_questions(
        text=req.text,
        question_type=req.question_type,
        jumlah=req.jumlah_soal,
        kesulitan=req.tingkat_kesulitan
    )

    return {
        "keywords": keywords,
        "questions": questions,
        "total": len(questions)
    }
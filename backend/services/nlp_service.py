import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
from keybert import KeyBERT
from typing import List

# ─── Pilih provider ───────────────────────────────────────────────
# Ubah nilai ini sesuai provider yang kamu pakai:
# "groq" atau "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# ─── Inisialisasi client sesuai provider ─────────────────────────
if LLM_PROVIDER == "groq":
    from groq import Groq
    llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    LLM_MODEL = "llama-3.1-8b-instant"

elif LLM_PROVIDER == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    llm_client = genai.GenerativeModel("gemini-1.5-flash")
    LLM_MODEL = "gemini-1.5-flash"

else:
    raise ValueError(f"LLM_PROVIDER tidak dikenal: {LLM_PROVIDER}. Pilih 'groq' atau 'gemini'.")

kw_model = KeyBERT()


# ─── Fungsi ekstraksi kata kunci (tidak berubah) ─────────────────
def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words=None,
        top_n=top_n
    )
    return [kw[0] for kw in keywords]


# ─── Fungsi bantu: buat prompt ───────────────────────────────────
def _build_prompt(text: str, question_type: str, jumlah: int, kesulitan: str) -> str:
    if question_type == "pilihan_ganda":
        tipe_instruksi = "soal pilihan ganda dengan 4 pilihan (A, B, C, D)"
    elif question_type == "isian":
        tipe_instruksi = "soal isian singkat (jawaban 1-5 kata)"
    else:
        tipe_instruksi = "campuran soal pilihan ganda (4 pilihan A,B,C,D) dan isian singkat"

    if kesulitan == "campuran":
        kesulitan_instruksi = "variasikan tingkat kesulitan: mudah, sedang, dan sulit"
    else:
        kesulitan_instruksi = f"semua soal tingkat kesulitan: {kesulitan}"

    return f"""Kamu adalah sistem pembuat soal otomatis untuk pendidikan Indonesia.

Berdasarkan teks berikut, buatlah {jumlah} {tipe_instruksi}.
{kesulitan_instruksi}.

TEKS:
{text[:3000]}

ATURAN:
- Semua soal dan jawaban dalam Bahasa Indonesia
- Jawaban HARUS tersedia dalam teks
- Untuk pilihan ganda: 1 jawaban benar, 3 pengecoh yang masuk akal
- Untuk isian: jawaban singkat dan jelas

Balas HANYA dengan JSON array berikut ini, tanpa teks tambahan:
[
  {{
    "nomor": 1,
    "tipe": "pilihan_ganda",
    "pertanyaan": "...",
    "pilihan": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "kunci_jawaban": "A",
    "tingkat_kesulitan": "mudah"
  }},
  {{
    "nomor": 2,
    "tipe": "isian",
    "pertanyaan": "...",
    "pilihan": {{}},
    "kunci_jawaban": "...",
    "tingkat_kesulitan": "sedang"
  }}
]"""


# ─── Fungsi bantu: parse JSON dari response ──────────────────────
def _parse_json(raw: str) -> list:
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return []


# ─── Fungsi utama: generate soal ─────────────────────────────────
def generate_questions(
    text: str,
    question_type: str,
    jumlah: int,
    kesulitan: str
) -> list:
    prompt = _build_prompt(text, question_type, jumlah, kesulitan)

    if LLM_PROVIDER == "groq":
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        raw = response.choices[0].message.content.strip()

    elif LLM_PROVIDER == "gemini":
        response = llm_client.generate_content(prompt)
        raw = response.text.strip()

    return _parse_json(raw)
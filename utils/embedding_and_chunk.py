import httpx
import pdfplumber
from config.env_constants import HF_API_URL, HF_TOKEN


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF, page by page."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # some pages are images — skip them
                full_text += page_text + "\n"
    return full_text


def _get_headers():
    token = HF_TOKEN
    if not token:
        raise ValueError("HF_TOKEN environment variable not set")
    return {"Authorization": f"Bearer {token}"}


async def _call_hf_embedding_api(inputs: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            HF_API_URL, headers=_get_headers(), json={"inputs": inputs}
        )
        response.raise_for_status()  # throws on 4xx/5xx — like axios interceptor
        return response.json()


async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return await _call_hf_embedding_api(chunks)


async def embed_query(query: str) -> list[float]:
    vectors = await _call_hf_embedding_api([query])
    return vectors[0]  # unwrap the single-item list

import base64
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright

# Logger
logger = logging.getLogger("pdf-generator")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# FastAPI app
app = FastAPI(title="CV PDF Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeneratePDFRequest(BaseModel):
    html_content: str

@app.get("/")
def root():
    return {"status": "healthy", "service": "cv-pdf-generator", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "cv-pdf-generator", "version": "1.0"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/generate-cv-pdf")
async def generate_cv_pdf(req: GeneratePDFRequest):
    """
    Generates a PDF from HTML content using Playwright.
    Returns base64-encoded PDF with no headers/footers.
    """
    logger.info("📄 Recebendo request para gerar PDF do CV")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set A4 viewport
            await page.set_viewport_size({"width": 794, "height": 1123})
            
            # Load HTML content
            await page.set_content(req.html_content, wait_until="networkidle")
            
            # Wait for fonts to load
            await page.wait_for_timeout(500)
            
            # Generate PDF with A4 format, no headers/footers
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                display_header_footer=False
            )
            
            await browser.close()
            
            # Encode to base64
            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            
            logger.info(f"✅ PDF gerado com sucesso: {len(pdf_bytes)} bytes")
            
            return {
                "success": True,
                "pdf_base64": pdf_b64,
                "size_bytes": len(pdf_bytes)
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "type": type(e).__name__}
        )

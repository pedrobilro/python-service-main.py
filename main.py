from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import base64

app = FastAPI()

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
async def root():
    return {"status": "ok", "service": "python-pdf-service"}

@app.post("/generate-cv-pdf")
async def generate_cv_pdf(request: GeneratePDFRequest):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set A4 viewport
            await page.set_viewport_size({"width": 794, "height": 1123})
            
            # Load HTML content
            await page.set_content(request.html_content, wait_until="networkidle")
            
            # Generate PDF
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
            )
            
            await browser.close()
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
            
            return {"success": True, "pdf_base64": pdf_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

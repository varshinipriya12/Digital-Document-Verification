import os
import cv2
import numpy as np
import pytesseract
import pymupdf as fitz  # PyMuPDF
import logging
from PIL import Image
from services.opencv_service import OpenCVQualityChecker

logger = logging.getLogger(__name__)

class OCRService:

    @staticmethod
    def extract_text(file_path: str) -> dict:
        """
        Extract text from document image or PDF file.
        For PDFs: combines PyMuPDF direct text stream with PyTesseract OCR on rendered page image.
        For Images: runs PyTesseract OCR with OpenCV image preprocessing.
        Works for both born-digital PDFs and scanned PDFs without selectable text.
        """
        ext = os.path.splitext(file_path)[1].lower()
        extracted_parts = []

        # 1. Direct PDF text stream extraction using PyMuPDF
        if ext == '.pdf':
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text = page.get_text()
                    if text and text.strip():
                        extracted_parts.append(text.strip())
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF text extraction warning: {e}")

        # 2. High-res rendered page image OCR via PyTesseract
        try:
            cv_img = OpenCVQualityChecker.load_image(file_path)
            if cv_img is not None and cv_img.size > 0:
                # Preprocessing: Grayscale -> Gaussian Blur -> Otsu Thresholding
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (3, 3), 0)
                thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                pil_img = Image.fromarray(thresholded)
                ocr_text = pytesseract.image_to_string(pil_img)
                if ocr_text and ocr_text.strip():
                    extracted_parts.append(ocr_text.strip())
        except Exception as e:
            logger.warning(f"PyTesseract OCR execution error: {e}")

        combined_text = "\n\n".join(extracted_parts).strip()
        word_count = len(combined_text.split())

        return {
            "extracted_text": combined_text,
            "word_count": word_count,
            "confidence": 90 if word_count > 5 else 30,
            "method": "pymupdf_and_tesseract_combined" if ext == '.pdf' else "pytesseract_ocr"
        }

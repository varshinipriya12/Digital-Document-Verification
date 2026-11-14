import os
import cv2
import numpy as np
import logging
from PIL import Image
import pymupdf as fitz  # PyMuPDF
from config import Config

logger = logging.getLogger(__name__)

class OpenCVQualityChecker:

    @staticmethod
    def load_image(file_path: str) -> np.ndarray:
        """
        Load an image or PDF document into an OpenCV BGR numpy array.
        For PDF files, renders the first page into a high-resolution 200 DPI image using PyMuPDF (fitz).
        Returns None if file cannot be loaded or rendered (no dummy placeholder images).
        """
        if not file_path or not os.path.exists(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return OpenCVQualityChecker._render_pdf_page_to_cv(file_path, page_num=0)
        else:
            try:
                img = cv2.imread(file_path)
                if img is None:
                    # Fallback using Pillow for special image formats
                    pil_img = Image.open(file_path).convert('RGB')
                    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                return img
            except Exception as e:
                logger.error(f"Failed to load image file {file_path}: {e}")
                return None

    @staticmethod
    def _render_pdf_page_to_cv(pdf_path: str, page_num: int = 0) -> np.ndarray:
        """
        Render a PDF page into a high-resolution 200 DPI OpenCV BGR numpy array using PyMuPDF (fitz).
        Handles both born-digital PDFs and scanned-image PDFs.
        Returns None if PyMuPDF rendering fails (never returns a dummy placeholder).
        """
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                doc.close()
                return None

            page_idx = min(page_num, len(doc) - 1)
            page = doc.load_page(page_idx)

            # Render page at 200 DPI for high visual and OCR quality
            pix = page.get_pixmap(dpi=200)

            # Convert pixmap samples to numpy array
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

            if pix.n == 4:  # RGBA -> BGR
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:  # RGB -> BGR
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:  # Gray -> BGR
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
            else:
                img_bgr = img_np

            doc.close()
            return img_bgr
        except Exception as e:
            logger.error(f"PyMuPDF rendering error for {pdf_path}: {e}")
            return None

    @staticmethod
    def analyze_quality(file_path: str) -> dict:
        """
        Analyze document image quality:
        - Blur detection via Laplacian variance
        - Brightness & Contrast
        - Blank / uniform page detection
        - Dimensions / Resolution check
        """
        try:
            img = OpenCVQualityChecker.load_image(file_path)
            if img is None or img.size == 0:
                return {
                    "is_acceptable": False,
                    "blur_score": 0.0,
                    "brightness": 0.0,
                    "width": 0,
                    "height": 0,
                    "issues": ["Unable to decode or render document page image."]
                }

            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 1. Blur Detection using Laplacian Variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            is_blurry = laplacian_var < Config.BLUR_THRESHOLD

            # 2. Brightness evaluation
            mean_brightness = np.mean(gray)
            is_too_dark = mean_brightness < Config.MIN_BRIGHTNESS

            # 3. Standard deviation (Blank image check & contrast)
            std_dev = np.std(gray)
            is_blank = std_dev < 15.0
            is_too_bright = (mean_brightness > Config.MAX_BRIGHTNESS) or (mean_brightness > 240.0 and std_dev < 18.0)

            # 4. Dimension check
            is_low_res = (width < Config.MIN_DIMENSION) or (height < Config.MIN_DIMENSION)

            issues = []
            if is_blurry:
                issues.append(f"Document image appears blurry (blur score: {round(laplacian_var, 1)}). Please upload a sharper document.")
            if is_too_dark:
                issues.append("Document image is too dark. Ensure good lighting when capturing the document.")
            if is_too_bright:
                issues.append("Document image is washed out / overexposed. Reduce camera glare.")
            if is_blank:
                issues.append("Document image appears to be blank or mostly empty.")
            if is_low_res:
                issues.append(f"Document resolution ({width}x{height}px) is too low. Upload a higher resolution document.")

            is_acceptable = len(issues) == 0

            return {
                "is_acceptable": is_acceptable,
                "blur_score": round(float(laplacian_var), 2),
                "brightness": round(float(mean_brightness), 2),
                "contrast_std": round(float(std_dev), 2),
                "width": int(width),
                "height": int(height),
                "issues": issues,
                "summary": "Document quality passed" if is_acceptable else "; ".join(issues)
            }
        except Exception as e:
            return {
                "is_acceptable": False,
                "blur_score": 0.0,
                "brightness": 0.0,
                "width": 0,
                "height": 0,
                "issues": [f"OpenCV quality analysis error: {str(e)}"]
            }

    @staticmethod
    def classify_passport_photo(file_path: str = None, cv_img: np.ndarray = None, ocr_text: str = "", filename: str = "") -> tuple:
        """
        Image-based classification for Passport Size Photograph:
        - Image dimensions and portrait/square aspect ratio (0.70 <= H/W <= 1.80)
        - Color image variation (BGR channels have contrast)
        - Skin tone detection in central face/neck region (YCrCb color space)
        - Rejection of text-heavy documents, certificates, and ID cards
        Returns: (is_photo: bool, reason: str, confidence: int)
        """
        try:
            img = cv_img
            if img is None and file_path:
                img = OpenCVQualityChecker.load_image(file_path)
            if img is None or img.size == 0:
                # If no image array is available, check filename as a fallback cue if text is empty
                clean_txt = (ocr_text or "").strip()
                fn_lower = (filename or (os.path.basename(file_path) if file_path else "")).lower()
                if not clean_txt and any(k in fn_lower for k in ["photo", "passport", "pic", "portrait"]):
                    return True, "Photograph filename signal with no document text", 85
                return False, "Image unavailable or cannot be rendered", 0

            h, w = img.shape[:2]
            if w < 50 or h < 50:
                return False, "Resolution too low for photograph", 0

            aspect_ratio = h / float(max(w, 1))
            # Standard passport photos are square (1.0) or portrait (1.2 - 1.5). Landscape ID cards are ~0.63.
            if aspect_ratio < 0.70 or aspect_ratio > 1.80:
                return False, f"Aspect ratio {aspect_ratio:.2f} does not match portrait photograph", 0

            # Text density check: photographs do not have paragraphs of text
            clean_text = (ocr_text or "").strip().lower()
            words = [word for word in clean_text.split() if len(word) > 1]
            if len(words) >= 6:
                return False, "Document contains structured body text, not a photograph", 0

            # Check for government / certificate keywords
            doc_keywords = [
                "income", "caste", "permanent", "account", "aadhaar", "uidai", "election",
                "electoral", "epic", "birth", "marks", "memo", "passbook", "tahsildar",
                "certificate", "revenue", "secondary", "intermediate", "allotment", "ration", "salary"
            ]
            if any(k in clean_text for k in doc_keywords):
                return False, "Contains government document or certificate text", 0

            # Color and Skin-Tone Analysis
            if len(img.shape) == 3 and img.shape[2] == 3:
                b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
                color_diff = float(np.mean(np.abs(r.astype(int) - b.astype(int))) + np.mean(np.abs(g.astype(int) - b.astype(int))))

                # YCrCb color space for human skin detection
                ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
                ch_s, ch_e = int(h * 0.15), int(h * 0.85)
                cw_s, cw_e = int(w * 0.15), int(w * 0.85)
                center_crop = ycrcb[ch_s:ch_e, cw_s:cw_e]
                cr = center_crop[:, :, 1]
                cb = center_crop[:, :, 2]
                skin_mask = (cr >= 130) & (cr <= 175) & (cb >= 75) & (cb <= 130)
                skin_ratio = float(np.sum(skin_mask)) / float(max(skin_mask.size, 1))

                fn_lower = (filename or (os.path.basename(file_path) if file_path else "")).lower()
                has_photo_fn = any(k in fn_lower for k in ["photo", "passport", "pic", "portrait", "image"])

                # If skin tones are present (portrait face) or rich color variation with photo filename
                if color_diff > 4.0 and (skin_ratio >= 0.04 or (has_photo_fn and skin_ratio >= 0.01) or has_photo_fn):
                    return True, "Valid passport size photograph detected", 95

            # Fallback if image has portrait aspect ratio, zero text, and photo filename
            fn_lower = (filename or (os.path.basename(file_path) if file_path else "")).lower()
            if any(k in fn_lower for k in ["photo", "passport", "pic"]) and len(words) == 0:
                return True, "Photograph filename with valid aspect ratio and zero text", 90

            return False, "Visual features do not match passport photograph", 0
        except Exception as e:
            logger.warning(f"Error in classify_passport_photo: {e}")
            return False, f"Photograph classification error: {str(e)}", 0

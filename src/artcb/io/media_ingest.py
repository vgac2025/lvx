"""Ingestion multimédia — conversion vers texte structuré pour IR ARTCB."""

from __future__ import annotations

import json
import logging
import mimetypes
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("artcb.io.media_ingest")

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv", ".json", ".html", ".htm", ".xml", ".log"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi"}
OFFICE_EXTENSIONS = {".docx"}


class MediaIngestError(Exception):
    """Media ingestion failed."""


@dataclass
class IngestedMedia:
    text: str
    media_type: str
    source_path: str
    segments: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def detect_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in OFFICE_EXTENSIONS:
        return "docx"
    mime, _ = mimetypes.guess_type(str(path))
    if mime and mime.startswith("text/"):
        return "text"
    if mime and mime.startswith("image/"):
        return "image"
    if mime and mime.startswith("audio/"):
        return "audio"
    if mime and mime.startswith("video/"):
        return "video"
    return "unknown"


def ingest_file(path: Path, *, openai_api_key: str | None = None) -> IngestedMedia:
    """Convertit un fichier local en texte pour le pipeline IR."""
    if not path.is_file():
        raise MediaIngestError(f"Fichier introuvable: {path}")
    media_type = detect_media_type(path)
    warnings: list[str] = []

    if media_type == "text":
        text = path.read_text(encoding="utf-8", errors="replace")
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path))

    if media_type == "pdf":
        from artcb.io.pdf_loader import extract_pdf_text

        text = extract_pdf_text(path)
        if not text.strip():
            warnings.append("PDF sans texte extractible — peut être un scan image")
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path), warnings=warnings)

    if media_type == "image":
        text, w = _ingest_image(path, openai_api_key=openai_api_key)
        warnings.extend(w)
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path), warnings=warnings)

    if media_type == "audio":
        text, w = _ingest_audio(path, openai_api_key=openai_api_key)
        warnings.extend(w)
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path), warnings=warnings)

    if media_type == "video":
        text, w = _ingest_video(path, openai_api_key=openai_api_key)
        warnings.extend(w)
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path), warnings=warnings)

    if media_type == "docx":
        text = _ingest_docx(path)
        return IngestedMedia(text=text, media_type=media_type, source_path=str(path))

    raise MediaIngestError(
        f"Format non supporté: {path.suffix} — extensions: "
        f"{', '.join(sorted(TEXT_EXTENSIONS | PDF_EXTENSIONS | IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS))}"
    )


def ingest_folder(
    folder: Path,
    *,
    limit: int = 50,
    offset: int = 0,
    extensions: set[str] | None = None,
    openai_api_key: str | None = None,
) -> tuple[str, int, bool]:
    """Lit un dossier — retourne (texte concaténé, count, has_more)."""
    if not folder.is_dir():
        raise MediaIngestError(f"Dossier introuvable: {folder}")
    allowed = extensions or (TEXT_EXTENSIONS | PDF_EXTENSIONS | IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | OFFICE_EXTENSIONS)
    files = sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in allowed],
        key=lambda p: str(p),
    )
    batch = files[offset : offset + limit]
    parts: list[str] = []
    for fp in batch:
        try:
            ingested = ingest_file(fp, openai_api_key=openai_api_key)
            header = f"--- [{ingested.media_type}] {fp.name} ---"
            parts.append(f"{header}\n{ingested.text}")
            for w in ingested.warnings:
                parts.append(f"[AVERTISSEMENT {fp.name}] {w}")
        except MediaIngestError as exc:
            parts.append(f"--- [ERREUR] {fp.name} ---\n{exc}")
    text = "\n\n".join(parts)
    has_more = offset + limit < len(files)
    return text, len(batch), has_more


def _ingest_image(path: Path, *, openai_api_key: str | None) -> tuple[str, list[str]]:
    warnings: list[str] = []
    # OCR local Tesseract
    try:
        import pytesseract
        from PIL import Image

        text = pytesseract.image_to_string(Image.open(path))
        if text.strip():
            return f"[OCR]\n{text.strip()}", warnings
        warnings.append("OCR Tesseract vide")
    except ImportError:
        warnings.append("pytesseract/Pillow non installés — pip install pytesseract pillow")
    except Exception as exc:
        warnings.append(f"OCR échoué: {exc}")

    # Vision OpenAI si clé fournie
    if openai_api_key:
        try:
            import base64

            import httpx

            b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
            mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
            with httpx.Client(timeout=90.0) as client:
                r = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Décris cette image en français pour mémorisation cognitive. Inclus tous les textes visibles."},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                            ],
                        }],
                        "max_tokens": 2000,
                    },
                )
                r.raise_for_status()
                desc = r.json()["choices"][0]["message"]["content"]
                return f"[VISION]\n{desc}", warnings
        except Exception as exc:
            warnings.append(f"Vision API échouée: {exc}")

    raise MediaIngestError(
        "Image non lisible — installez pytesseract+pillow (OCR local) ou connectez OpenAI pour vision"
    )


def _ingest_audio(path: Path, *, openai_api_key: str | None) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if openai_api_key:
        try:
            import httpx

            with path.open("rb") as f:
                with httpx.Client(timeout=120.0) as client:
                    r = client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {openai_api_key}"},
                        files={"file": (path.name, f, "application/octet-stream")},
                        data={"model": "whisper-1", "language": "fr"},
                    )
                    r.raise_for_status()
                    transcript = r.json().get("text", "")
                    if transcript.strip():
                        return f"[TRANSCRIPT]\n{transcript.strip()}", warnings
        except Exception as exc:
            warnings.append(f"Whisper API échouée: {exc}")

    # ffmpeg + faster-whisper local si dispo
    try:
        result = subprocess.run(
            ["whisper", str(path), "--language", "French", "--output_format", "txt", "--fp16", "False"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        txt_path = path.with_suffix(".txt")
        if txt_path.is_file():
            return f"[TRANSCRIPT-LOCAL]\n{txt_path.read_text(encoding='utf-8')}", warnings
        if result.stderr:
            warnings.append(result.stderr[:200])
    except FileNotFoundError:
        warnings.append("whisper CLI non installé")
    except Exception as exc:
        warnings.append(f"whisper local: {exc}")

    raise MediaIngestError(
        "Audio non transcrit — connectez OpenAI (Whisper API) ou installez openai-whisper CLI"
    )


def _ingest_video(path: Path, *, openai_api_key: str | None) -> tuple[str, list[str]]:
    warnings: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = Path(tmp) / "extracted.wav"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(path), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", str(audio_path)],
                capture_output=True,
                timeout=120,
                check=True,
            )
        except FileNotFoundError:
            raise MediaIngestError("ffmpeg requis pour vidéo — apt install ffmpeg") from None
        except subprocess.CalledProcessError as exc:
            raise MediaIngestError(f"ffmpeg échec extraction audio: {exc.stderr[:200] if exc.stderr else exc}") from exc

        if audio_path.is_file() and audio_path.stat().st_size > 0:
            transcript, w = _ingest_audio(audio_path, openai_api_key=openai_api_key)
            warnings.extend(w)
            meta = {"source_video": str(path), "audio_extracted": True}
            return f"{transcript}\n\n[META]{json.dumps(meta)}", warnings

    raise MediaIngestError("Vidéo sans piste audio extractible")


def _ingest_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise MediaIngestError("pip install python-docx pour fichiers .docx") from exc
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

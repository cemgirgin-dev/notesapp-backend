import io
import re

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_note_or_404(db: Session, note_id: int, user_id: int) -> models.Note:
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == user_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")
    return slug.lower() or "note"


@router.get("/", response_model=list[schemas.NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    notes = (
        db.query(models.Note)
        .filter(models.Note.owner_id == current_user.id)
        .order_by(models.Note.created_at.desc())
        .all()
    )
    return notes


@router.post("/", response_model=schemas.NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    note = models.Note(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=schemas.NoteRead)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    note = _get_note_or_404(db, note_id, current_user.id)
    return note


@router.put("/{note_id}", response_model=schemas.NoteRead)
def update_note(
    note_id: int,
    payload: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if payload.title is None and payload.content is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")

    note = _get_note_or_404(db, note_id, current_user.id)

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
) -> Response:
    note = _get_note_or_404(db, note_id, current_user.id)
    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{note_id}/pdf")
@router.get("/{note_id}/export/pdf")
def download_note_pdf(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    note = _get_note_or_404(db, note_id, current_user.id)

    try:
        from fpdf import FPDF
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF service not available",
        ) from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, note.title)

    pdf.ln(4)
    pdf.set_font("Helvetica", size=12)
    # FPDF core fonts are latin-1. Unsupported characters are replaced to avoid runtime errors.
    safe_content = note.content.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 8, safe_content)

    pdf_output = pdf.output(dest="S")
    pdf_bytes = pdf_output.encode("latin-1") if isinstance(pdf_output, str) else bytes(pdf_output)
    filename = f"{_slugify(note.title)}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

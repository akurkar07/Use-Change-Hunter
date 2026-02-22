from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.export_service import export_excel, export_json, export_pdf

router = APIRouter()


@router.get("/{property_id}/pdf")
async def export_pdf_route(property_id: str, db: AsyncSession = Depends(get_db)):
    """Export property analysis as PDF"""
    content = await export_pdf(property_id, db)
    if not content:
        raise HTTPException(status_code=404, detail="No exportable analysis found")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{property_id}-analysis.pdf"'},
    )


@router.get("/{property_id}/excel")
async def export_excel_route(property_id: str, db: AsyncSession = Depends(get_db)):
    """Export property analysis as Excel"""
    content = await export_excel(property_id, db)
    if not content:
        raise HTTPException(status_code=404, detail="No exportable analysis found")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{property_id}-analysis.xlsx"'},
    )


@router.get("/{property_id}/json")
async def export_json_route(property_id: str, db: AsyncSession = Depends(get_db)):
    """Export property analysis as JSON"""
    data = await export_json(property_id, db)
    if not data:
        raise HTTPException(status_code=404, detail="No exportable analysis found")
    return data

from typing import Optional
from datetime import datetime
from io import BytesIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

try:
    import weasyprint
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False
    logger.warning("weasyprint not installed - PDF export disabled")

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    logger.warning("openpyxl not installed - Excel export disabled")

from app.db.models import OpportunityScore


async def export_analysis_data(
    property_id: str,
    db: AsyncSession
) -> Optional[dict]:
    """
    Retrieve all analysis data for a property (scores, scenarios)
    
    Args:
        property_id: UUID of property to export
        db: Database session
    
    Returns:
        Complete analysis data for export
    """
    logger.info(f"Retrieving analysis data for property {property_id}")
    
    try:
        prop_uuid = UUID(property_id)

        # Get all scores for this property
        result = await db.execute(
            select(OpportunityScore)
            .where(OpportunityScore.property_id == prop_uuid)
            .order_by(OpportunityScore.generated_at.desc())
        )
        scores = result.scalars().all()
        
        if not scores:
            logger.warning(f"No analysis data found for property {property_id}")
            return None
        
        # Build export-ready data structure
        export_data = {
            "property_id": property_id,
            "scores": [
                {
                    "id": str(score.id),
                    "strategy_type": score.strategy_type.value,
                    "score_total": score.score_total,
                    "score_risk": score.score_risk,
                    "score_confidence": score.score_confidence,
                    "breakdown": score.breakdown,
                    "scenario": score.scenario,
                    "generated_at": score.generated_at.isoformat()
                }
                for score in scores
            ]
        }
        
        return export_data
    
    except Exception as e:
        logger.error(f"Error retrieving analysis data for property {property_id}: {e}")
        return None


def _generate_html_report(analysis_data: dict) -> str:
    """Generate HTML report from analysis data"""
    if not analysis_data or not analysis_data.get("scores"):
        return "<html><body><p>No analysis data available</p></body></html>"
    
    scores = analysis_data["scores"]
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Property Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            h2 {{ color: #0066cc; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th {{ background-color: #0066cc; color: white; padding: 10px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 10px; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .score-box {{ display: inline-block; margin: 10px 20px 10px 0; padding: 15px; border-left: 4px solid #0066cc; background-color: #f0f5ff; }}
            .score-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
            .score-label {{ font-size: 12px; color: #666; }}
            .breakdown {{ background-color: #fff; padding: 10px; margin: 10px 0; border-left: 3px solid #0066cc; }}
        </style>
    </head>
    <body>
        <h1>Property Analysis Report</h1>
        <p><strong>Property ID:</strong> {analysis_data['property_id']}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    for score in scores:
        html += f"""
        <h2>Strategy: {score['strategy_type'].title()}</h2>
        
        <div class="score-box">
            <div class="score-label">Total Score</div>
            <div class="score-value">{score['score_total']}/100</div>
        </div>
        
        <div class="score-box">
            <div class="score-label">Risk Score</div>
            <div class="score-value">{score['score_risk']}/100</div>
        </div>
        
        <div class="score-box">
            <div class="score-label">Confidence Score</div>
            <div class="score-value">{score['score_confidence']}/100</div>
        </div>
        
        <h3>Breakdown</h3>
        <div class="breakdown">
        """
        
        if score.get("breakdown"):
            for key, value in score["breakdown"].items():
                html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
        
        if score.get("scenario"):
            html += "<h3>Scenario</h3><div class='breakdown'>"
            for key, value in score["scenario"].items():
                html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
            html += "</div>"
        
        html += f"<p><em>Generated at: {score['generated_at']}</em></p></div>"
    
    html += "</body></html>"
    return html


async def export_pdf(property_id: str, db: AsyncSession) -> Optional[bytes]:
    """
    Export analysis as PDF report
    
    Args:
        property_id: UUID of property to export
        db: Database session
    
    Returns:
        PDF bytes or None if export failed
    """
    if not HAS_WEASYPRINT:
        logger.error("weasyprint not installed - cannot generate PDF")
        return None
    
    logger.info(f"Exporting PDF for property {property_id}")
    
    try:
        analysis_data = await export_analysis_data(property_id, db)
        
        if not analysis_data:
            logger.error(f"No data available to export for property {property_id}")
            return None
        
        # Generate HTML
        html = _generate_html_report(analysis_data)
        
        # Convert to PDF
        pdf_bytes = weasyprint.HTML(string=html).write_pdf()
        logger.info(f"PDF export successful for property {property_id}")
        return pdf_bytes
    
    except Exception as e:
        logger.error(f"PDF export failed for property {property_id}: {e}")
        return None


async def export_excel(property_id: str, db: AsyncSession) -> Optional[bytes]:
    """
    Export analysis as Excel spreadsheet
    
    Args:
        property_id: UUID of property to export
        db: Database session
    
    Returns:
        Excel file bytes or None if export failed
    """
    if not HAS_OPENPYXL:
        logger.error("openpyxl not installed - cannot generate Excel")
        return None
    
    logger.info(f"Exporting Excel for property {property_id}")
    
    try:
        analysis_data = await export_analysis_data(property_id, db)
        
        if not analysis_data:
            logger.error(f"No data available to export for property {property_id}")
            return None
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Analysis"
        
        # Header styling
        header_fill = PatternFill(start_color="0066cc", end_color="0066cc", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        # Title
        ws["A1"] = f"Property Analysis Report"
        ws["A1"].font = Font(size=14, bold=True)
        ws.merge_cells("A1:H1")
        
        ws["A2"] = f"Property ID: {analysis_data['property_id']}"
        ws["A2"].font = Font(size=11)
        ws.merge_cells("A2:H2")
        
        # Headers
        headers = ["Strategy Type", "Total Score", "Risk Score", "Confidence Score", 
                   "Matched Precedents", "Approved Similar", "Refused Similar", "Generated At"]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Data rows
        for row_idx, score in enumerate(analysis_data["scores"], 5):
            ws.cell(row=row_idx, column=1).value = score.get("strategy_type", "").title()
            ws.cell(row=row_idx, column=2).value = score.get("score_total")
            ws.cell(row=row_idx, column=3).value = score.get("score_risk")
            ws.cell(row=row_idx, column=4).value = score.get("score_confidence")
            
            breakdown = score.get("breakdown", {})
            ws.cell(row=row_idx, column=5).value = breakdown.get("matched_precedents")
            ws.cell(row=row_idx, column=6).value = breakdown.get("approved_similar")
            ws.cell(row=row_idx, column=7).value = breakdown.get("refused_similar")
            ws.cell(row=row_idx, column=8).value = score.get("generated_at")
        
        # Adjust column widths
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 12
        ws.column_dimensions["C"].width = 12
        ws.column_dimensions["D"].width = 15
        ws.column_dimensions["E"].width = 18
        ws.column_dimensions["F"].width = 18
        ws.column_dimensions["G"].width = 18
        ws.column_dimensions["H"].width = 20
        
        # Write to bytes
        excel_bytes = BytesIO()
        wb.save(excel_bytes)
        excel_bytes.seek(0)
        
        logger.info(f"Excel export successful for property {property_id}")
        return excel_bytes.getvalue()
    
    except Exception as e:
        logger.error(f"Excel export failed for property {property_id}: {e}")
        return None


async def export_json(property_id: str, db: AsyncSession) -> Optional[dict]:
    """
    Export analysis as JSON (for API responses or integrations)
    
    Args:
        property_id: UUID of property to export
        db: Database session
    
    Returns:
        Analysis data as JSON-serializable dict
    """
    logger.info(f"Exporting JSON for property {property_id}")
    
    return await export_analysis_data(property_id, db)

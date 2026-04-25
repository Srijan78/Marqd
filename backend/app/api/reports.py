"""
Reports API — Generate DMCA takedown notices.
Stub endpoints for Day 1. Gemini + reportlab integration in Day 2.
"""
from flask import Blueprint, jsonify

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports/dmca/<violation_id>", methods=["POST"])
def generate_dmca_report(violation_id):
    """Generate a DMCA takedown PDF for a confirmed violation."""
    import os
    from flask import current_app
    from app.models import db
    from app.models.violation import Violation
    from app.services.gemini_service import GeminiService
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import uuid

    violation = Violation.query.get(violation_id)
    if not violation:
        return jsonify({"error": "Violation not found"}), 404

    try:
        # 1. Generate text via Gemini
        org_name = violation.asset.org_name if violation.asset else "Rights Owner"
        asset_id = violation.asset.asset_id if violation.asset else "UNKNOWN_ASSET"
        watermark_id = asset_id # Assuming watermark ID is the asset ID
        
        dmca_text = GeminiService.generate_dmca_report(
            org_name=org_name,
            asset_id=asset_id,
            violation_url=violation.source_url,
            platform=violation.platform,
            watermark_id=watermark_id,
            detection_date=violation.detected_at.strftime("%Y-%m-%d") if violation.detected_at else None
        )

        # 2. Save as PDF via reportlab
        temp_dir = current_app.config["TEMP_FOLDER"]
        os.makedirs(temp_dir, exist_ok=True)
        pdf_filename = f"DMCA_{asset_id}_{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        textobject = c.beginText()
        textobject.setTextOrigin(50, 750)
        textobject.setFont("Courier", 10)
        
        # Split text into lines to fit page
        lines = dmca_text.split('\n')
        for line in lines:
            textobject.textLine(line[:100]) # simple wrap
            
            # Simple pagination if we run out of vertical space
            if textobject.getY() < 50:
                c.drawText(textobject)
                c.showPage()
                textobject = c.beginText()
                textobject.setTextOrigin(50, 750)
                textobject.setFont("Courier", 10)
                
        c.drawText(textobject)
        c.save()

        # 3. Upload PDF to storage
        from app.services.storage import StorageService
        pdf_url = StorageService.upload_file(
            pdf_path, 
            f"reports/dmca/{pdf_filename}", 
            content_type="application/pdf"
        )
        
        # 4. Update violation record
        violation.status = "dmca_sent"
        violation.dmca_report_url = pdf_url
        db.session.commit()
        
        # Cleanup
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return jsonify({
            "message": "DMCA report generated successfully",
            "violation_id": violation_id,
            "status": "success",
            "report_url": pdf_url
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Report generation failed. Please try again."}), 500

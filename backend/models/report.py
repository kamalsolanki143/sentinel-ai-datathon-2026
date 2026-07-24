"""
Sentinel AI - Intelligence Report SQLAlchemy Model
==================================================
File: backend/models/report.py
Purpose: SQLAlchemy ORM entity representing generated intelligence reports.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from backend.database.postgres import Base


class IntelligenceReport(Base):
    """SQLAlchemy model for intelligence_reports table."""

    __tablename__ = "intelligence_reports"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="TACTICAL_BRIEFING", index=True)
    district = Column(String(100), nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    author_agent = Column(String(100), default="ReportAgent")
    summary = Column(Text, nullable=False)
    full_content = Column(Text, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "report_type": self.report_type,
            "district": self.district,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "author_agent": self.author_agent,
            "summary": self.summary,
            "full_content": self.full_content,
        }

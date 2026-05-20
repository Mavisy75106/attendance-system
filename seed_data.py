"""Seed data for the attendance system."""

from datetime import date
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models.employee import Employee
from models.calendar_event import CalendarEvent

def seed_db():
    """Create all tables and seed with initial data."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(Employee).first():
            print("Database already seeded.")
            return
        
        # Seed employees
        employees = [
            Employee(
                name="王大明",
                employee_id="EMP001",
                department="資訊室",
                position="主任",
                phone="0912-345-678",
                email="wang@david.com",
                status="active",
                hire_date=date(2024, 1, 15)
            ),
            Employee(
                name="李小美",
                employee_id="EMP002",
                department="人事室",
                position="專員",
                phone="0912-345-679",
                email="li@david.com",
                status="active",
                hire_date=date(2024, 3, 1)
            ),
            Employee(
                name="張志豪",
                employee_id="EMP003",
                department="財務室",
                position="專員",
                phone="0912-345-680",
                email="zhang@david.com",
                status="active",
                hire_date=date(2024, 6, 10)
            ),
        ]
        
        for emp in employees:
            db.add(emp)
        
        db.commit()
        
        # Seed calendar events
        meeting = CalendarEvent(
            event_date=date(2026, 5, 26),
            event_type="meeting",
            title="部南分級案_審查會議",
            description="說明本案當前進度",
            location="6f資訊室",
            attendees="全體院內相關單位、資拓、壹立方、雙欣",
        )
        
        db.add(meeting)
        db.commit()
        
        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
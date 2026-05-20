"""Holiday scraper: Fetch government holidays from MOIA holiday site.

This module provides functionality to scrape public holidays from the
Macau Office of the Inspectorate and Ageancy (MOIA) holiday website,
parse the HTML table, and insert records into the calendar_events table.

The scraper is designed to be mockable for testing purposes.
"""

import logging
from datetime import date, datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from models.calendar_event import CalendarEvent

logger = logging.getLogger(__name__)

# MOIA holiday page URL
MOIA_HOLIDAY_URL = "https://www.moia.gov.mo/tc/holidays"

# Known alternative MOIA holiday page URLs to try
MOIA_HOLIDAY_ALTERNATIVES = [
    "https://www.moia.gov.mo/tc/holidays",
    "https://www.moia.gov.mo/tc/holidays/public-holidays",
    "https://www.moia.gov.mo/en/holidays",
]


def _fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch HTML content from a URL.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        The HTML content as a string, or None if the request failed.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def _parse_holidays_from_html(html: str, base_url: str = MOIA_HOLIDAY_URL) -> list[dict]:
    """Parse HTML table and extract holiday dates and names.

    Args:
        html: The HTML content to parse.
        base_url: The base URL for resolving relative URLs.

    Returns:
        A list of dicts with 'date' and 'title' keys.
    """
    soup = BeautifulSoup(html, "html.parser")
    holidays = []

    # Strategy 1: Look for the main holidays table
    # The MOIA site typically uses a table with class 'table' or id 'holidays'
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                # First cell is typically the date, second is the holiday name
                date_cell = cells[0].get_text(strip=True)
                title_cell = cells[1].get_text(strip=True)

                if date_cell and title_cell:
                    holiday_date = _parse_holiday_date(date_cell)
                    if holiday_date:
                        holidays.append({
                            "date": holiday_date,
                            "title": title_cell,
                        })

    # Strategy 2: If no tables found, try to find date/name patterns
    if not holidays:
        # Look for common date formats in the page
        date_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        import re
        for match in re.finditer(date_pattern, html):
            year, month, day = match.groups()
            # Try to find the holiday name nearby
            context_start = match.start()
            context = html[context_start:context_start + 200]
            title = re.search(r"([^\n]*?)$", context, re.MULTILINE)
            if title:
                holiday_title = title.group(1).strip()
                if holiday_title and len(holiday_title) > 1:
                    holidays.append({
                        "date": date(int(year), int(month), int(day)),
                        "title": holiday_title,
                    })

    # Strategy 3: Generic approach - look for any td with year and any following td
    if not holidays:
        for cell in soup.find_all("td"):
            text = cell.get_text(strip=True)
            if "年" in text and "月" in text and "日" in text:
                match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
                if match:
                    year, month, day = match.groups()
                    # Try next td for the title
                    next_td = cell.find_next_sibling("td")
                    title = next_td.get_text(strip=True) if next_td else text
                    holidays.append({
                        "date": date(int(year), int(month), int(day)),
                        "title": title if len(title) > 1 else "公眾假期",
                    })

    return holidays


def _parse_holiday_date(date_str: str) -> Optional[date]:
    """Parse a date string into a date object.

    Handles formats like:
    - "2026-01-01"
    - "01/01/2026"
    - "2026/01/01"
    - "2026年1月1日"

    Args:
        date_str: The date string to parse.

    Returns:
        A date object or None if parsing failed.
    """
    import re

    # Chinese format: 2026年1月1日
    cn_match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if cn_match:
        y, m, d = cn_match.groups()
        try:
            return date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    # ISO format: 2026-01-01
    iso_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if iso_match:
        y, m, d = iso_match.groups()
        try:
            return date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    # European format: 01/01/2026 (DD/MM/YYYY)
    eu_match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if eu_match:
        d, m, y = eu_match.groups()
        try:
            return date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    return None


def _insert_holidays(
    db: Session,
    holidays: list[dict],
    is_imported: bool = True,
    imported_at: datetime | None = None,
) -> dict:
    """Insert parsed holidays into the database, skipping duplicates.

    Args:
        db: SQLAlchemy session.
        holidays: List of holiday dicts with 'date' and 'title' keys.
        is_imported: Whether the event should be marked as imported.
        imported_at: The timestamp when the event was imported.

    Returns:
        A dict with 'inserted', 'skipped', and 'errors' counts.
    """
    inserted = 0
    skipped = 0
    errors = []

    for holiday in holidays:
        event_date = holiday["date"]
        title = holiday["title"]

        # Check for duplicate
        existing = db.query(CalendarEvent).filter(
            CalendarEvent.event_date == event_date,
            CalendarEvent.event_type == "public_holiday",
            CalendarEvent.title == title,
        ).first()

        if existing:
            skipped += 1
            continue

        try:
            new_event = CalendarEvent(
                event_date=event_date,
                event_type="public_holiday",
                title=title,
                description=f"Government public holiday",
                is_imported=is_imported,
                imported_at=imported_at,
            )
            db.add(new_event)
            inserted += 1
        except Exception as e:
            errors.append({
                "date": event_date,
                "title": title,
                "error": str(e),
            })
            logger.warning(f"Failed to insert holiday {event_date} {title}: {e}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database commit error: {e}")
        return {
            "inserted": inserted,
            "skipped": skipped,
            "errors": errors + [{"error": str(e)}],
            "status": "partial",
        }

    return {
        "inserted": inserted,
        "skipped": skipped,
        "errors": errors,
        "status": "success" if not errors else "partial",
    }


def import_holidays(
    db: Session,
    url: str = MOIA_HOLIDAY_URL,
    is_imported: bool = True,
    imported_at: datetime | None = None,
) -> dict:
    """Import holidays from the MOIA holiday site.

    This is the main entry point. It fetches the HTML, parses holidays,
    and inserts them into the database, skipping any duplicates.

    Args:
        db: SQLAlchemy session.
        url: The URL to fetch holidays from.
        is_imported: Whether to mark events as imported.
        imported_at: The import timestamp.

    Returns:
        A dict with import results: 'inserted', 'skipped', 'errors', 'status'.
    """
    # Fetch HTML
    html = _fetch_html(url)
    if not html:
        return {
            "inserted": 0,
            "skipped": 0,
            "errors": [{"error": f"Failed to fetch holidays from {url}"}],
            "status": "error",
        }

    # Parse holidays
    holidays = _parse_holidays_from_html(html, url)
    if not holidays:
        logger.warning("No holidays found in the HTML content")

    # Insert into database
    result = _insert_holidays(db, holidays, is_imported, imported_at)
    result["total_holidays_found"] = len(holidays)

    return result


def import_holidays_to_db(
    db: Session,
    holidays: list[dict],
    is_imported: bool = True,
    imported_at: datetime | None = None,
) -> dict:
    """Insert a list of holidays directly into the database.

    Useful for testing with mock data.

    Args:
        db: SQLAlchemy session.
        holidays: List of dicts with 'date' and 'title' keys.
        is_imported: Whether to mark events as imported.
        imported_at: The import timestamp.

    Returns:
        A dict with import results.
    """
    return _insert_holidays(db, holidays, is_imported, imported_at)

"""
VaakSetu — Mock Government API Integrations
Simulated data for Seva Sindhu, BBMP, BWSSB, Bhoomi, Ration Card, Pension Portal, and 1092 CRM.
These mock fixtures faithfully represent each API's expected schema for hackathon demo purposes.
"""

import random
from datetime import datetime, timedelta
from typing import Optional


# ─── Seva Sindhu API (Government Services) ───────────────────────────────────

SEVA_SINDHU_SERVICES = [
    {
        "service_id": "SS-2024-001",
        "service_name": "Income Certificate",
        "department": "Revenue Department",
        "status": "active",
        "avg_processing_days": 7,
        "pending_applications": 1245,
        "last_updated": "2026-05-01T10:00:00Z",
        "districts_available": ["all"],
        "online_available": True,
    },
    {
        "service_id": "SS-2024-002",
        "service_name": "Caste Certificate",
        "department": "Revenue Department",
        "status": "active",
        "avg_processing_days": 10,
        "pending_applications": 3421,
        "last_updated": "2026-05-01T10:00:00Z",
        "districts_available": ["all"],
        "online_available": True,
    },
    {
        "service_id": "SS-2024-003",
        "service_name": "Ration Card - New Application",
        "department": "Food and Civil Supplies",
        "status": "active",
        "avg_processing_days": 15,
        "pending_applications": 8762,
        "last_updated": "2026-05-01T09:30:00Z",
        "districts_available": ["all"],
        "online_available": True,
    },
    {
        "service_id": "SS-2024-004",
        "service_name": "Ration Card - Update / Correction",
        "department": "Food and Civil Supplies",
        "status": "delayed",
        "avg_processing_days": 21,
        "pending_applications": 15230,
        "last_updated": "2026-05-01T09:30:00Z",
        "districts_available": ["all"],
        "online_available": True,
        "delay_reason": "System migration in progress — backlog expected until June 2026",
    },
    {
        "service_id": "SS-2024-005",
        "service_name": "Senior Citizen ID Card",
        "department": "Social Welfare",
        "status": "active",
        "avg_processing_days": 12,
        "pending_applications": 2100,
        "last_updated": "2026-05-01T10:00:00Z",
        "districts_available": ["all"],
        "online_available": True,
    },
    {
        "service_id": "SS-2024-006",
        "service_name": "Land Conversion (Agriculture to Non-Agriculture)",
        "department": "Revenue Department",
        "status": "active",
        "avg_processing_days": 30,
        "pending_applications": 4560,
        "last_updated": "2026-05-01T08:00:00Z",
        "districts_available": ["Bengaluru Urban", "Mysuru", "Dharwad", "Belagavi"],
        "online_available": False,
    },
]


def get_seva_sindhu_services(query: Optional[str] = None) -> list:
    """Search Seva Sindhu services by keyword."""
    if not query:
        return SEVA_SINDHU_SERVICES
    q = query.lower()
    return [s for s in SEVA_SINDHU_SERVICES if q in s["service_name"].lower() or q in s["department"].lower()]


def get_seva_sindhu_status(service_id: str) -> Optional[dict]:
    """Get status of a specific Seva Sindhu service."""
    for s in SEVA_SINDHU_SERVICES:
        if s["service_id"] == service_id:
            return s
    return None


# ─── BBMP Grievance Feed (Civic Complaints) ─────────────────────────────────

BBMP_GRIEVANCES = [
    {
        "grievance_id": "BBMP-GR-2026-10234",
        "category": "Road and Pothole",
        "subcategory": "Pothole on main road",
        "ward": "Jayanagar",
        "zone": "South",
        "status": "in_progress",
        "filed_date": "2026-04-28",
        "last_update": "2026-04-30",
        "assigned_to": "BBMP South Zone Engineer",
        "priority": "high",
        "description": "Large pothole on 4th Block Jayanagar main road causing traffic issues",
    },
    {
        "grievance_id": "BBMP-GR-2026-10235",
        "category": "Garbage and Waste",
        "subcategory": "Garbage not collected",
        "ward": "Koramangala",
        "zone": "South",
        "status": "pending",
        "filed_date": "2026-04-30",
        "last_update": "2026-04-30",
        "assigned_to": "Unassigned",
        "priority": "medium",
        "description": "Garbage not collected for 3 days in 5th Block Koramangala",
    },
    {
        "grievance_id": "BBMP-GR-2026-10236",
        "category": "Water Logging",
        "subcategory": "Street flooding",
        "ward": "Mahadevpura",
        "zone": "East",
        "status": "resolved",
        "filed_date": "2026-04-25",
        "last_update": "2026-04-29",
        "assigned_to": "BBMP East Zone SWD",
        "priority": "high",
        "description": "Severe water logging near Whitefield signal after rain",
    },
    {
        "grievance_id": "BBMP-GR-2026-10237",
        "category": "Street Light",
        "subcategory": "Not working",
        "ward": "Rajajinagar",
        "zone": "West",
        "status": "pending",
        "filed_date": "2026-05-01",
        "last_update": "2026-05-01",
        "assigned_to": "Unassigned",
        "priority": "low",
        "description": "Multiple street lights not working on 10th Cross Rajajinagar",
    },
    {
        "grievance_id": "BBMP-GR-2026-10238",
        "category": "Tree Fall",
        "subcategory": "Dangerous tree",
        "ward": "Indiranagar",
        "zone": "East",
        "status": "in_progress",
        "filed_date": "2026-04-29",
        "last_update": "2026-04-30",
        "assigned_to": "BBMP East Horticulture",
        "priority": "high",
        "description": "Leaning tree on 12th Main Indiranagar threatening to fall on power lines",
    },
]


def get_bbmp_grievances(category: Optional[str] = None, ward: Optional[str] = None) -> list:
    """Search BBMP grievances by category or ward."""
    results = BBMP_GRIEVANCES
    if category:
        results = [g for g in results if category.lower() in g["category"].lower()]
    if ward:
        results = [g for g in results if ward.lower() in g["ward"].lower()]
    return results


def get_bbmp_trending() -> list:
    """Get trending BBMP issues in last 24 hours."""
    return [
        {"category": "Road and Pothole", "count": 47, "trend": "up"},
        {"category": "Garbage and Waste", "count": 38, "trend": "up"},
        {"category": "Water Logging", "count": 22, "trend": "stable"},
        {"category": "Street Light", "count": 15, "trend": "down"},
        {"category": "Tree Fall", "count": 12, "trend": "up"},
    ]


# ─── BWSSB Status API (Water Supply) ────────────────────────────────────────

BWSSB_STATUS = [
    {
        "area": "Koramangala",
        "zone": "South-East",
        "water_supply_status": "normal",
        "next_supply": "2026-05-02T06:00:00Z",
        "outage_active": False,
        "outage_reason": None,
        "estimated_restoration": None,
    },
    {
        "area": "Whitefield",
        "zone": "East",
        "water_supply_status": "disrupted",
        "next_supply": None,
        "outage_active": True,
        "outage_reason": "Pipeline repair work on Whitefield Main Road",
        "estimated_restoration": "2026-05-02T18:00:00Z",
        "affected_wards": ["Whitefield", "Kadugodi", "Varthur"],
        "tanker_service_available": True,
        "tanker_helpline": "080-2294-3434",
    },
    {
        "area": "Jayanagar",
        "zone": "South",
        "water_supply_status": "normal",
        "next_supply": "2026-05-02T05:30:00Z",
        "outage_active": False,
        "outage_reason": None,
        "estimated_restoration": None,
    },
    {
        "area": "Rajajinagar",
        "zone": "West",
        "water_supply_status": "low_pressure",
        "next_supply": "2026-05-02T06:00:00Z",
        "outage_active": False,
        "outage_reason": "Low reservoir levels due to reduced Cauvery inflow",
        "estimated_restoration": "2026-05-05T06:00:00Z",
    },
    {
        "area": "Yelahanka",
        "zone": "North",
        "water_supply_status": "disrupted",
        "next_supply": None,
        "outage_active": True,
        "outage_reason": "Valve replacement at Yelahanka pump station",
        "estimated_restoration": "2026-05-01T22:00:00Z",
        "affected_wards": ["Yelahanka", "Yelahanka New Town", "Allalasandra"],
        "tanker_service_available": True,
        "tanker_helpline": "080-2294-3434",
    },
]


def get_bwssb_status(area: Optional[str] = None) -> list:
    """Get BWSSB water supply status for an area."""
    if not area:
        return BWSSB_STATUS
    return [s for s in BWSSB_STATUS if area.lower() in s["area"].lower()]


def get_bwssb_outages() -> list:
    """Get all active BWSSB outages."""
    return [s for s in BWSSB_STATUS if s["outage_active"]]


# ─── Bhoomi (Land Records) ──────────────────────────────────────────────────

BHOOMI_RECORDS = [
    {
        "survey_number": "45/2A",
        "village": "Devanahalli",
        "taluk": "Devanahalli",
        "district": "Bengaluru Rural",
        "owner_name": "Ramesh Kumar (mock)",
        "land_type": "Agriculture",
        "area_acres": 3.5,
        "mutation_status": "completed",
        "last_mutation_date": "2025-11-15",
        "encumbrance": False,
    },
    {
        "survey_number": "112/1",
        "village": "Anekal",
        "taluk": "Anekal",
        "district": "Bengaluru Urban",
        "owner_name": "Lakshmi Devi (mock)",
        "land_type": "Non-Agriculture",
        "area_acres": 0.75,
        "mutation_status": "pending",
        "last_mutation_date": "2026-03-01",
        "encumbrance": True,
        "encumbrance_details": "Bank mortgage — SBI Anekal Branch",
    },
    {
        "survey_number": "78/3B",
        "village": "Dharwad",
        "taluk": "Dharwad",
        "district": "Dharwad",
        "owner_name": "Basavaraj Patil (mock)",
        "land_type": "Agriculture",
        "area_acres": 8.0,
        "mutation_status": "disputed",
        "last_mutation_date": "2024-06-20",
        "encumbrance": False,
        "dispute_details": "Ownership dispute filed by adjacent land owner — case pending at Dharwad Tahsildar office",
    },
]


def search_bhoomi(survey_number: Optional[str] = None, village: Optional[str] = None) -> list:
    """Search Bhoomi land records."""
    results = BHOOMI_RECORDS
    if survey_number:
        results = [r for r in results if survey_number.lower() in r["survey_number"].lower()]
    if village:
        results = [r for r in results if village.lower() in r["village"].lower()]
    return results


# ─── Ration Card Database ───────────────────────────────────────────────────

RATION_CARD_RECORDS = [
    {
        "rc_number": "KA-BLR-2024-00123",
        "holder_name": "Suresh Gowda (mock)",
        "card_type": "BPL",
        "family_members": 4,
        "district": "Bengaluru Urban",
        "taluk": "Bengaluru South",
        "fair_price_shop": "FPS-South-042",
        "last_collection_date": "2026-04-15",
        "status": "active",
        "aadhaar_linked": True,
        "pending_update": None,
    },
    {
        "rc_number": "KA-MYS-2023-05678",
        "holder_name": "Kavitha R (mock)",
        "card_type": "APL",
        "family_members": 3,
        "district": "Mysuru",
        "taluk": "Mysuru",
        "fair_price_shop": "FPS-Mysuru-018",
        "last_collection_date": "2026-04-10",
        "status": "active",
        "aadhaar_linked": True,
        "pending_update": "Address change request submitted 2026-03-20 — pending verification",
    },
    {
        "rc_number": "KA-DWD-2022-03456",
        "holder_name": "Mallappa Hadapad (mock)",
        "card_type": "BPL",
        "family_members": 6,
        "district": "Dharwad",
        "taluk": "Dharwad",
        "fair_price_shop": "FPS-Dharwad-007",
        "last_collection_date": "2026-03-28",
        "status": "blocked",
        "aadhaar_linked": False,
        "pending_update": "Card blocked due to Aadhaar not linked. Visit taluk office for resolution.",
    },
]


def search_ration_card(rc_number: Optional[str] = None, name: Optional[str] = None) -> list:
    """Search ration card records."""
    results = RATION_CARD_RECORDS
    if rc_number:
        results = [r for r in results if rc_number.lower() in r["rc_number"].lower()]
    if name:
        results = [r for r in results if name.lower() in r["holder_name"].lower()]
    return results


# ─── Pension Portal ──────────────────────────────────────────────────────────

PENSION_RECORDS = [
    {
        "pension_id": "KA-PEN-2020-11234",
        "beneficiary_name": "Nagamma S (mock)",
        "pension_type": "Old Age Pension",
        "monthly_amount": 2000,
        "district": "Mysuru",
        "last_disbursement": "2026-04-05",
        "next_disbursement": "2026-05-05",
        "status": "active",
        "bank_account": "****5678",
        "arrears_pending": 0,
    },
    {
        "pension_id": "KA-PEN-2019-08765",
        "beneficiary_name": "Venkataramaiah H (mock)",
        "pension_type": "Old Age Pension",
        "monthly_amount": 2000,
        "district": "Tumkur",
        "last_disbursement": "2026-02-05",
        "next_disbursement": "overdue",
        "status": "payment_delayed",
        "bank_account": "****1234",
        "arrears_pending": 6000,
        "delay_reason": "Bank account verification pending — KYC update required",
    },
    {
        "pension_id": "KA-PEN-2021-14567",
        "beneficiary_name": "Shantamma K (mock)",
        "pension_type": "Widow Pension",
        "monthly_amount": 1500,
        "district": "Raichur",
        "last_disbursement": "2026-04-05",
        "next_disbursement": "2026-05-05",
        "status": "active",
        "bank_account": "****9012",
        "arrears_pending": 0,
    },
]


def search_pension(pension_id: Optional[str] = None, name: Optional[str] = None) -> list:
    """Search pension records."""
    results = PENSION_RECORDS
    if pension_id:
        results = [r for r in results if pension_id.lower() in r["pension_id"].lower()]
    if name:
        results = [r for r in results if name.lower() in r["beneficiary_name"].lower()]
    return results


# ─── 1092 CRM Call Logs ─────────────────────────────────────────────────────

def generate_crm_call_logs(count: int = 30) -> list:
    """Generate simulated 1092 CRM call log entries."""
    categories = [
        "Ration Card Issue",
        "Water Supply Complaint",
        "Road / Pothole Complaint",
        "Pension Payment Delayed",
        "Land Record Dispute",
        "Garbage Collection",
        "Street Light Not Working",
        "Seva Sindhu Application Status",
        "BBMP Tax Query",
        "Noise Pollution Complaint",
        "Illegal Construction",
        "Drainage / Sewage Issue",
    ]

    districts = [
        "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Dharwad",
        "Belagavi", "Tumkur", "Raichur", "Mangaluru", "Shimoga", "Hubli",
    ]

    sentiments = ["calm", "frustrated", "distressed", "confused", "angry", "urgent"]

    logs = []
    base_time = datetime.utcnow()

    for i in range(count):
        cat = random.choice(categories)
        logs.append({
            "call_id": f"1092-{base_time.strftime('%Y%m%d')}-{10000 + i}",
            "timestamp": (base_time - timedelta(minutes=random.randint(1, 480))).isoformat() + "Z",
            "category": cat,
            "district": random.choice(districts),
            "language": random.choice(["Kannada", "Hindi", "English"]),
            "sentiment": random.choice(sentiments),
            "duration_seconds": random.randint(30, 600),
            "resolution": random.choice(["resolved", "escalated", "pending", "transferred"]),
            "agent_id": f"AGT-{random.randint(100, 150)}",
            "ai_assisted": random.choice([True, True, True, False]),
            "summary": f"Citizen called regarding {cat.lower()} from {random.choice(districts)}.",
        })

    return sorted(logs, key=lambda x: x["timestamp"], reverse=True)


def get_crm_trends() -> dict:
    """Get real-time CRM trend data for the dashboard."""
    return {
        "total_calls_today": random.randint(180, 250),
        "active_calls": random.randint(3, 12),
        "avg_handle_time_seconds": random.randint(180, 320),
        "ai_assist_rate": round(random.uniform(0.65, 0.85), 2),
        "escalation_rate": round(random.uniform(0.08, 0.18), 2),
        "top_categories": [
            {"category": "Water Supply Complaint", "count": random.randint(30, 55), "trend": "up",
             "last_hour": random.randint(5, 12)},
            {"category": "Ration Card Issue", "count": random.randint(25, 45), "trend": "up",
             "last_hour": random.randint(4, 10)},
            {"category": "Road / Pothole Complaint", "count": random.randint(15, 35), "trend": "stable",
             "last_hour": random.randint(2, 6)},
            {"category": "Pension Payment Delayed", "count": random.randint(10, 25), "trend": "up",
             "last_hour": random.randint(2, 5)},
            {"category": "Garbage Collection", "count": random.randint(8, 20), "trend": "down",
             "last_hour": random.randint(1, 4)},
            {"category": "Seva Sindhu Application Status", "count": random.randint(5, 15), "trend": "stable",
             "last_hour": random.randint(1, 3)},
        ],
        "district_heatmap": [
            {"district": "Bengaluru Urban", "calls": random.randint(60, 100)},
            {"district": "Mysuru", "calls": random.randint(15, 35)},
            {"district": "Dharwad", "calls": random.randint(10, 25)},
            {"district": "Belagavi", "calls": random.randint(8, 20)},
            {"district": "Tumkur", "calls": random.randint(5, 15)},
            {"district": "Mangaluru", "calls": random.randint(5, 12)},
        ],
        "hourly_volume": [
            {"hour": f"{h:02d}:00", "calls": random.randint(5, 25)}
            for h in range(24)
        ],
        "sentiment_distribution": {
            "calm": round(random.uniform(0.30, 0.45), 2),
            "frustrated": round(random.uniform(0.15, 0.25), 2),
            "confused": round(random.uniform(0.10, 0.20), 2),
            "distressed": round(random.uniform(0.05, 0.12), 2),
            "angry": round(random.uniform(0.03, 0.08), 2),
            "urgent": round(random.uniform(0.02, 0.06), 2),
        },
    }


# ─── Unified Context Enrichment ─────────────────────────────────────────────

def enrich_context(transcript: str) -> dict:
    """
    Given a transcript, search all mock data sources for relevant context.
    Returns a dict of enrichment results to inject into the semantic interpretation.
    """
    transcript_lower = transcript.lower()
    enrichment = {
        "seva_sindhu": [],
        "bbmp": [],
        "bwssb": [],
        "bhoomi": [],
        "ration_card": [],
        "pension": [],
        "crm_trends": {},
        "alerts": [],
    }

    # Seva Sindhu keywords
    seva_keywords = ["certificate", "seva sindhu", "application", "service", "online"]
    if any(kw in transcript_lower for kw in seva_keywords):
        enrichment["seva_sindhu"] = get_seva_sindhu_services()

    # Ration card keywords
    ration_keywords = ["ration", "ration card", "bpl", "apl", "fair price", "anna bhagya"]
    if any(kw in transcript_lower for kw in ration_keywords):
        enrichment["ration_card"] = search_ration_card()
        enrichment["alerts"].append("⚠️ Ration card update service is currently DELAYED (Seva Sindhu SS-2024-004)")

    # BBMP keywords
    bbmp_keywords = ["road", "pothole", "garbage", "street light", "bbmp", "corporation", "tree", "water logging"]
    if any(kw in transcript_lower for kw in bbmp_keywords):
        enrichment["bbmp"] = get_bbmp_trending()

    # BWSSB keywords
    water_keywords = ["water", "supply", "bwssb", "pipeline", "tanker", "bore well"]
    if any(kw in transcript_lower for kw in water_keywords):
        outages = get_bwssb_outages()
        enrichment["bwssb"] = [s for s in BWSSB_STATUS]
        if outages:
            for o in outages:
                enrichment["alerts"].append(
                    f"🚰 Active BWSSB outage in {o['area']}: {o['outage_reason']} — "
                    f"Est. restoration: {o.get('estimated_restoration', 'Unknown')}"
                )

    # Land / Bhoomi keywords
    land_keywords = ["land", "survey", "mutation", "bhoomi", "property", "conversion", "encumbrance"]
    if any(kw in transcript_lower for kw in land_keywords):
        enrichment["bhoomi"] = search_bhoomi()

    # Pension keywords
    pension_keywords = ["pension", "old age", "widow pension", "senior citizen", "monthly payment"]
    if any(kw in transcript_lower for kw in pension_keywords):
        enrichment["pension"] = search_pension()
        delayed = [p for p in PENSION_RECORDS if p["status"] == "payment_delayed"]
        for p in delayed:
            enrichment["alerts"].append(
                f"⏳ Pension payment delayed for {p['beneficiary_name']}: {p.get('delay_reason', 'Unknown')}"
            )

    # Always include CRM trends
    enrichment["crm_trends"] = get_crm_trends()

    return enrichment

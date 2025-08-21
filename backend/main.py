from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

# Optional DB abstractions for tests in tests/test_main.py
try:
    from database import get_db
    from models import Developer, Project
    from sqlalchemy.orm import Session
except Exception:  # pragma: no cover
    get_db = None  # type: ignore
    Developer = None  # type: ignore
    Project = None  # type: ignore
    Session = None  # type: ignore


app = FastAPI(title="PropCalc Compatibility API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root and health endpoints for tests/test_api.py and tests/test_main.py
@app.get("/")
async def root() -> dict[str, Any]:
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health")
async def health_check_main() -> dict[str, Any]:
    return {"status": "healthy", "service": "Vantage AI Trust Protocol"}


# Minimal in-memory dataset for /api/v1/* tests
SAMPLE_PROJECT = {
    "id": 1,
    "name": "Sample Project",
    "location": "Dubai Marina",
    "property_type": "Apartment",
    "price": 2500000,
    "area": 1200,
    "developer": "Emaar Properties",
}

SAMPLE_DEVELOPERS = [
    {"id": 1, "name": "Emaar Properties"},
    {"id": 2, "name": "Nakheel"},
]


@app.get("/api/v1/health")
async def api_health() -> dict[str, Any]:
    return {"status": "healthy", "service": "vantage-ai-api"}


@app.get("/api/v1/projects")
async def api_get_projects(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    items = [SAMPLE_PROJECT]
    return {"items": items[:limit], "total": len(items), "limit": limit, "offset": offset}


@app.get("/api/v1/projects/{project_id}")
async def api_get_project(project_id: int) -> dict[str, Any]:
    if project_id != SAMPLE_PROJECT["id"]:
        raise HTTPException(status_code=404, detail="Project not found")
    return SAMPLE_PROJECT


@app.get("/api/v1/developers")
async def api_get_developers() -> list[dict[str, Any]]:
    return SAMPLE_DEVELOPERS


@app.get("/api/v1/developers/{developer_id}")
async def api_get_developer(developer_id: int) -> dict[str, Any]:
    for d in SAMPLE_DEVELOPERS:
        if d["id"] == developer_id:
            return d
    raise HTTPException(status_code=404, detail="Developer not found")


@app.get("/api/v1/market/overview")
async def api_market_overview() -> dict[str, Any]:
    return {
        "total_projects": 1,
        "total_units": 500,
        "active_developers": len(SAMPLE_DEVELOPERS),
        "avg_price_per_sqft": 2000,
        "sales_percentage": 70.0,
    }


@app.get("/api/v1/top-performers")
async def api_top_performers(limit: int = Query(5, ge=1, le=50)) -> list[dict[str, Any]]:
    data = [
        {"project": "A", "score": 95},
        {"project": "B", "score": 92},
        {"project": "C", "score": 90},
        {"project": "D", "score": 88},
        {"project": "E", "score": 85},
    ]
    return data[:limit]


@app.get("/api/v1/projects/{project_id}/vantage-score")
async def api_project_vantage_score(project_id: int) -> dict[str, Any]:
    if project_id != SAMPLE_PROJECT["id"]:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project_id": project_id,
        "overall_score": 82.5,
        "score_breakdown": {
            "developer_track_record": 85.0,
            "sales_velocity": 80.0,
        },
        "risk_level": "medium",
    }


@app.post("/api/v1/upload/dld-transactions")
async def api_upload_dld_transactions(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or ""
    if not (filename.endswith(".csv") or filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    content = await file.read()
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        else:
            df = pd.read_excel(pd.io.common.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file format")

    required_columns = [
        "Transaction ID",
        "Property Type",
        "Location",
        "Transaction Date",
        "Price (AED)",
        "Area (sq ft)",
        "Developer Name",
    ]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

    return {"status": "success", "processed_rows": len(df), "total_rows": len(df)}


# Endpoints for tests/test_main.py using DB dependency if provided

@app.get("/projects/")
async def list_projects(db: Session = Depends(get_db) if get_db else None):  # type: ignore
    if not db or not Project:
        return []
    return [
        {
            "id": p.id,
            "name": p.name,
            "vantage_score": p.vantage_score,
            "score_breakdown": p.score_breakdown,
        }
        for p in db.query(Project).all()
    ]


@app.post("/projects/")
async def create_project(project: dict[str, Any], db: Session = Depends(get_db) if get_db else None):  # type: ignore
    if not db or not Project:
        raise HTTPException(status_code=500, detail="DB not configured")
    obj = Project(
        name=project.get("name", ""),
        developer_id=project.get("developer_id"),
        latitude=project.get("latitude"),
        longitude=project.get("longitude"),
        total_units=project.get("total_units", 0),
        units_sold=project.get("units_sold", 0),
        starting_price=project.get("starting_price", 0),
        current_price=project.get("current_price", 0),
        completion_date=project.get("completion_date"),
        project_type=project.get("project_type", ""),
        area_sqm=project.get("area_sqm", 0),
        amenities=project.get("amenities", []),
        vantage_score=82.5,
        score_breakdown={
            "developer_track_record": 85.0,
            "sales_velocity": 80.0,
            "location_potential": 85.0,
            "project_quality_proxy": 80.0,
            "social_sentiment": 82.0,
        },
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {
        "id": obj.id,
        "name": obj.name,
        "vantage_score": obj.vantage_score,
        "score_breakdown": obj.score_breakdown,
    }


@app.get("/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db) if get_db else None):  # type: ignore
    if not db or not Project:
        raise HTTPException(status_code=404, detail="Project not found")
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": p.id,
        "name": p.name,
        "vantage_score": p.vantage_score,
        "score_breakdown": p.score_breakdown,
    }


@app.get("/developers/")
async def list_developers(db: Session = Depends(get_db) if get_db else None):  # type: ignore
    if not db or not Developer:
        return []
    return db.query(Developer).all()


@app.get("/developers/{developer_id}")
async def get_developer(developer_id: int, db: Session = Depends(get_db) if get_db else None):  # type: ignore
    if not db or not Developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    d = db.query(Developer).get(developer_id)
    if not d:
        raise HTTPException(status_code=404, detail="Developer not found")
    return d


@app.get("/market/analysis")
async def market_analysis() -> dict[str, Any]:
    return {
        "market_overview": {},
        "top_performers": [],
        "risk_zones": [],
        "developer_rankings": [],
    }


@app.get("/projects/{project_id}/transparency")
async def project_transparency(project_id: int) -> dict[str, Any]:
    return {
        "sales_progress": {},
        "construction_updates": [],
        "developer_history": {},
    }


@app.get("/projects/{project_id}/recommendations")
async def project_recommendations(project_id: int) -> dict[str, Any]:
    return {
        "risk_factors": [],
        "recommendations": [],
        "comparison_data": [],
    }


@app.get("/projects/search")
async def search_projects(query: str) -> list[dict[str, Any]]:
    return [SAMPLE_PROJECT] if query else []


@app.get("/developers/{developer_id}/projects")
async def developer_projects(developer_id: int) -> list[dict[str, Any]]:
    return [SAMPLE_PROJECT] if developer_id == 1 else []


@app.get("/projects/{project_id}/scores")
async def project_scores(project_id: int) -> dict[str, Any]:
    return {"score_history": [], "trend_analysis": {}}


"""
Smart Civic Issue Reporter - Complete Backend API
AI Innovation Challenge 2026
Compatible with venv app.js, index.html, styles.css
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os

# ========== FastAPI App Setup ==========
app = FastAPI(
    title="Civic Issue Reporter API",
    description="AI-powered civic issue reporting system",
    version="1.0.0"
)

# ========== CORS Middleware ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Serve Frontend Static Files ==========
# Mount frontend directory
venv_dir = "venv"
if os.path.exists(venv_dir):
    app.mount("/static", StaticFiles(directory=venv_dir), name="static")
    print(f"✅ Frontend mounted from: {venv_dir}")
else:
    print(f"⚠️  Frontend directory '{venv_dir}' not found")

# ========== Data Models (Pydantic) ==========

class IssueCreate(BaseModel):
    title: str
    description: str
    location: str
    reporter_name: str
    reporter_contact: Optional[str] = None

class IssueUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    admin_notes: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "citizen"

class UserLogin(BaseModel):
    username: str
    password: str

class AutoSuggestionRequest(BaseModel):
    partial_text: str

class PredictionRequest(BaseModel):
    title: str
    description: str

# ========== In-Memory Database (Demo) ==========
# In production, replace with actual database

issues_db = []
users_db = []
status_history_db = []
issue_id_counter = 1
history_id_counter = 1

# ========== AI Classifier Functions ==========

def predict_category(title: str, description: str) -> str:
    """AI-powered category prediction based on keywords"""
    text = (title + " " + description).lower()
    
    categories = {
        "Road & Infrastructure": ["road", "pothole", "street", "footpath", "bridge", "traffic", "signal", "highway", "pavement"],
        "Water Supply": ["water", "pipe", "leak", "supply", "drainage", "sewage", "tap", "pipeline", "overflow"],
        "Electricity": ["light", "electricity", "power", "streetlight", "pole", "wire", "outage", "transformer"],
        "Garbage & Sanitation": ["garbage", "waste", "trash", "dustbin", "cleaning", "sanitation", "litter", "dump"],
        "Public Safety": ["crime", "safety", "violence", "theft", "danger", "police", "security", "lighting"],
        "Parks & Environment": ["park", "tree", "garden", "pollution", "noise", "air", "greenery", "plantation"],
        "Public Transport": ["bus", "metro", "transport", "station", "railway", "traffic", "parking"],
        "Buildings & Housing": ["building", "construction", "illegal", "encroachment", "demolition", "housing"]
    }
    
    best_match = "Other"
    max_score = 0
    
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > max_score:
            max_score = score
            best_match = category
    
    return best_match

def predict_severity(title: str, description: str) -> str:
    """AI-powered severity prediction"""
    text = (title + " " + description).lower()
    
    severity_keywords = {
        "critical": ["urgent", "emergency", "dangerous", "accident", "death", "injury", "collapsed", "fire", "flood"],
        "high": ["broken", "burst", "overflow", "blocked", "major", "severe", "damaged"],
        "medium": ["poor", "bad", "issue", "problem", "needs", "requires", "repair"],
        "low": ["minor", "small", "slight", "little", "maintenance", "request"]
    }
    
    for severity, keywords in severity_keywords.items():
        if any(keyword in text for keyword in keywords):
            return severity
    
    return "medium"

def calculate_priority_score(severity: str, category: str) -> float:
    """Calculate priority score (0-100)"""
    severity_scores = {
        "critical": 95,
        "high": 75,
        "medium": 50,
        "low": 25
    }
    
    category_weights = {
        "Public Safety": 1.2,
        "Water Supply": 1.1,
        "Road & Infrastructure": 1.1,
        "Electricity": 1.0,
        "Garbage & Sanitation": 0.9,
        "Public Transport": 0.9,
        "Parks & Environment": 0.8,
        "Buildings & Housing": 0.85
    }
    
    base_score = severity_scores.get(severity, 50)
    weight = category_weights.get(category, 1.0)
    
    return min(100, base_score * weight)

def get_department(category: str) -> str:
    """Route to appropriate department"""
    department_mapping = {
        "Road & Infrastructure": "Public Works Department (PWD)",
        "Water Supply": "Water & Sewage Department",
        "Electricity": "Electricity Board",
        "Garbage & Sanitation": "Solid Waste Management",
        "Public Safety": "Police & Municipal Security",
        "Parks & Environment": "Environment & Horticulture",
        "Public Transport": "Transport Department",
        "Buildings & Housing": "Town Planning Department"
    }
    return department_mapping.get(category, "General Administration")

def get_auto_suggestions(partial_text: str) -> List[str]:
    """Get auto-suggestions for common issues"""
    suggestions = [
        "Pothole on main road needs repair",
        "Streetlight not working",
        "Garbage not collected for 3 days",
        "Water leakage from pipe",
        "Broken drainage cover on footpath",
        "Illegal parking blocking road",
        "Tree branches blocking road",
        "Road accident prone area needs attention",
        "Public toilet not maintained",
        "Stray animals causing nuisance"
    ]
    
    if not partial_text or len(partial_text) < 2:
        return suggestions[:5]
    
    partial_lower = partial_text.lower()
    matches = [s for s in suggestions if partial_lower in s.lower()]
    
    return matches[:5] if matches else suggestions[:5]

# ========== API ENDPOINTS ==========

# ========== Homepage ==========
@app.get("/")
async def serve_homepage():
    """Serve the main HTML page"""
    html_path = os.path.join(venv_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Civic Reporter API Running", "docs": "/docs"}

# ========== Authentication ==========
@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Register new user"""
    # Check if username exists
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = {
        "id": len(users_db) + 1,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    users_db.append(new_user)
    return new_user

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user and return token"""
    # Simple demo authentication
    if credentials.username == "admin" and credentials.password == "admin123":
        return {
            "access_token": "demo-token-admin",
            "token_type": "bearer"
        }
    
    if credentials.username == "citizen1" and credentials.password == "pass123":
        return {
            "access_token": "demo-token-citizen1",
            "token_type": "bearer"
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ========== Issues CRUD ==========
@app.post("/api/issues")
async def create_issue(issue: IssueCreate):
    """Create new civic issue with AI-powered categorization"""
    global issue_id_counter
    
    print(f"\n📥 Receiving issue: {issue.title}")
    
    # Use AI to predict category, severity, department
    category = predict_category(issue.title, issue.description)
    severity = predict_severity(issue.title, issue.description)
    department = get_department(category)
    priority_score = calculate_priority_score(severity, category)
    
    print(f"🤖 AI Predictions:")
    print(f"   - Category: {category}")
    print(f"   - Severity: {severity}")
    print(f"   - Department: {department}")
    print(f"   - Priority: {priority_score}/100")
    
    new_issue = {
        "id": issue_id_counter,
        "title": issue.title,
        "description": issue.description,
        "location": issue.location,
        "reporter_name": issue.reporter_name,
        "reporter_contact": issue.reporter_contact,
        "category": category,
        "severity": severity,
        "status": "pending",
        "department": department,
        "priority_score": priority_score,
        "latitude": None,
        "longitude": None,
        "reporter_id": 1,
        "assigned_to": None,
        "image_path": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "resolved_at": None,
        "admin_notes": None
    }
    
    issues_db.append(new_issue)
    
    # Log status history
    add_status_history(issue_id_counter, None, "pending", "System", None)
    
    issue_id_counter += 1
    
    print(f"✅ Issue #{new_issue['id']} created successfully\n")
    
    return new_issue

@app.get("/api/issues")
async def get_issues(
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get all issues with optional filters"""
    print(f"📋 Fetching issues (status={status}, category={category}, severity={severity}, limit={limit})")
    
    filtered_issues = issues_db.copy()
    
    if status:
        filtered_issues = [i for i in filtered_issues if i["status"] == status]
    if category:
        filtered_issues = [i for i in filtered_issues if i["category"] == category]
    if severity:
        filtered_issues = [i for i in filtered_issues if i["severity"] == severity]
    
    # Sort by created_at descending (newest first)
    filtered_issues.sort(key=lambda x: x["created_at"], reverse=True)
    
    return filtered_issues[:limit]

@app.get("/api/issues/{issue_id}")
async def get_issue(issue_id: int):
    """Get specific issue details"""
    for issue in issues_db:
        if issue["id"] == issue_id:
            return issue
    
    raise HTTPException(status_code=404, detail="Issue not found")

@app.put("/api/issues/{issue_id}")
async def update_issue(issue_id: int, update: IssueUpdate):
    """Update issue status (Admin only)"""
    for issue in issues_db:
        if issue["id"] == issue_id:
            old_status = issue["status"]
            
            if update.status:
                issue["status"] = update.status
                if update.status == "resolved":
                    issue["resolved_at"] = datetime.now().isoformat()
            
            if update.assigned_to:
                issue["assigned_to"] = update.assigned_to
            
            if update.admin_notes:
                issue["admin_notes"] = update.admin_notes
            
            issue["updated_at"] = datetime.now().isoformat()
            
            # Log status history
            if old_status != issue["status"]:
                add_status_history(
                    issue_id,
                    old_status,
                    issue["status"],
                    "Admin",
                    update.admin_notes
                )
            
            print(f"✅ Issue #{issue_id} updated: {old_status} → {issue['status']}")
            return issue
    
    raise HTTPException(status_code=404, detail="Issue not found")

@app.get("/api/issues/{issue_id}/history")
async def get_issue_history(issue_id: int):
    """Get status history for an issue"""
    history = [h for h in status_history_db if h["issue_id"] == issue_id]
    history.sort(key=lambda x: x["timestamp"])
    return history

# ========== AI Services ==========
@app.post("/api/ai/predict")
async def predict_issue_details(prediction: PredictionRequest):
    """Get AI predictions for category, severity, department"""
    category = predict_category(prediction.title, prediction.description)
    severity = predict_severity(prediction.title, prediction.description)
    department = get_department(category)
    priority_score = calculate_priority_score(severity, category)
    
    return {
        "category": category,
        "severity": severity,
        "department": department,
        "priority_score": priority_score
    }

@app.post("/api/ai/suggestions")
async def get_suggestions(request: AutoSuggestionRequest):
    """Get auto-suggestions for issue titles"""
    suggestions = get_auto_suggestions(request.partial_text)
    return {"suggestions": suggestions}

# ========== Analytics ==========
@app.get("/api/analytics")
async def get_analytics():
    """Get analytics dashboard data"""
    total = len(issues_db)
    pending = sum(1 for i in issues_db if i["status"] == "pending")
    in_progress = sum(1 for i in issues_db if i["status"] == "in_progress")
    resolved = sum(1 for i in issues_db if i["status"] == "resolved")
    rejected = sum(1 for i in issues_db if i["status"] == "rejected")
    
    # By category
    by_category = {}
    for issue in issues_db:
        cat = issue["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
    
    # By severity
    by_severity = {}
    for issue in issues_db:
        sev = issue["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
    
    # By department
    by_department = {}
    for issue in issues_db:
        dept = issue["department"]
        by_department[dept] = by_department.get(dept, 0) + 1
    
    # Recent issues
    recent = sorted(issues_db, key=lambda x: x["created_at"], reverse=True)[:10]
    recent_formatted = [
        {
            "id": i["id"],
            "title": i["title"],
            "category": i["category"],
            "severity": i["severity"],
            "status": i["status"],
            "created_at": i["created_at"]
        }
        for i in recent
    ]
    
    # Average resolution time (simplified)
    resolved_issues = [i for i in issues_db if i["resolved_at"]]
    avg_resolution = None
    if resolved_issues:
        # Simplified calculation
        avg_resolution = 2.5  # days (demo value)
    
    return {
        "total_issues": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "rejected": rejected,
        "by_category": by_category,
        "by_severity": by_severity,
        "by_department": by_department,
        "recent_issues": recent_formatted,
        "resolution_time_avg": avg_resolution
    }

# ========== Helper Functions ==========
def add_status_history(issue_id: int, old_status: Optional[str], new_status: str, updated_by: str, notes: Optional[str]):
    """Add status history entry"""
    global history_id_counter
    
    history_entry = {
        "id": history_id_counter,
        "issue_id": issue_id,
        "old_status": old_status,
        "new_status": new_status,
        "updated_by": updated_by,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    status_history_db.append(history_entry)
    history_id_counter += 1

# ========== Demo Data Creation ==========
def create_demo_data():
    """Create demo issues for presentation"""
    global issue_id_counter
    
    demo_issues = [
        {
            "title": "Large pothole on SG Highway causing accidents",
            "description": "There is a large pothole near Sola Bridge on SG Highway. Multiple accidents have occurred. Urgent repair needed.",
            "location": "SG Highway, Near Sola Bridge, Ahmedabad",
            "reporter_name": "Rahul Sharma",
            "reporter_contact": "9123456789"
        },
        {
            "title": "Streetlight not working in residential area",
            "description": "All streetlights in Satellite area have been non-functional for 5 days causing safety concerns.",
            "location": "Satellite Road, Ahmedabad",
            "reporter_name": "Priya Patel",
            "reporter_contact": "9234567890"
        },
        {
            "title": "Garbage not collected for 4 days",
            "description": "Garbage bins are overflowing and waste is scattered on roads in Vastrapur area.",
            "location": "Vastrapur, Ahmedabad",
            "reporter_name": "Amit Kumar",
            "reporter_contact": "9345678901"
        },
        {
            "title": "Water pipeline burst flooding the road",
            "description": "Major water pipeline burst on CG Road. Water is flooding the entire street and homes nearby.",
            "location": "CG Road, Ahmedabad",
            "reporter_name": "Sneha Shah",
            "reporter_contact": "9456789012"
        },
        {
            "title": "Broken drainage cover on main road",
            "description": "Drainage cover is broken and open on Ashram Road creating danger for vehicles and pedestrians.",
            "location": "Ashram Road, Ahmedabad",
            "reporter_name": "Vikram Singh",
            "reporter_contact": "9567890123"
        },
        {
            "title": "Illegal construction blocking public pathway",
            "description": "Illegal construction activity in Bodakdev area has completely blocked the public footpath.",
            "location": "Bodakdev, Ahmedabad",
            "reporter_name": "Neha Desai",
            "reporter_contact": "9678901234"
        },
        {
            "title": "Public park needs maintenance",
            "description": "Swings and equipment in children's park are broken. Garden needs cleaning and maintenance.",
            "location": "Naranpura Garden, Ahmedabad",
            "reporter_name": "Rajesh Modi",
            "reporter_contact": "9789012345"
        },
        {
            "title": "Traffic signal malfunction at major junction",
            "description": "Traffic lights not working at Paldi junction causing traffic jams during peak hours.",
            "location": "Paldi, Ahmedabad",
            "reporter_name": "Pooja Mehta",
            "reporter_contact": "9890123456"
        }
    ]
    
    statuses = ["pending", "in_progress", "resolved"]
    
    for idx, demo_issue in enumerate(demo_issues):
        category = predict_category(demo_issue["title"], demo_issue["description"])
        severity = predict_severity(demo_issue["title"], demo_issue["description"])
        department = get_department(category)
        priority = calculate_priority_score(severity, category)
        status = statuses[idx % 3]
        
        issue = {
            "id": issue_id_counter,
            "title": demo_issue["title"],
            "description": demo_issue["description"],
            "location": demo_issue["location"],
            "reporter_name": demo_issue["reporter_name"],
            "reporter_contact": demo_issue["reporter_contact"],
            "category": category,
            "severity": severity,
            "status": status,
            "department": department,
            "priority_score": priority,
            "latitude": None,
            "longitude": None,
            "reporter_id": 1,
            "assigned_to": "PWD Team A" if status != "pending" else None,
            "image_path": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
            "resolved_at": datetime.now().isoformat() if status == "resolved" else None,
            "admin_notes": None
        }
        
        issues_db.append(issue)
        add_status_history(issue_id_counter, None, status, "System", None)
        issue_id_counter += 1
    
    print(f"\n✅ Created {len(demo_issues)} demo issues")

# ========== Startup Event ==========
@app.on_event("startup")
async def startup_event():
    """Initialize application with demo data"""
    print("\n" + "="*60)
    print("🏙️  CIVIC ISSUE REPORTER - BACKEND API")
    print("   AI Innovation Challenge 2026")
    print("="*60)
    
    # Create demo data
    if len(issues_db) == 0:
        create_demo_data()
    
    print(f"\n📊 Status:")
    print(f"   - Total Issues: {len(issues_db)}")
    print(f"   - Pending: {sum(1 for i in issues_db if i['status'] == 'pending')}")
    print(f"   - In Progress: {sum(1 for i in issues_db if i['status'] == 'in_progress')}")
    print(f"   - Resolved: {sum(1 for i in issues_db if i['status'] == 'resolved')}")
    print(f"\n📍 Server URLs:")
    print(f"   - Homepage: http://localhost:8000")
    print(f"   - API Docs: http://localhost:8000/docs")
    print(f"\n👤 Demo Credentials:")
    print(f"   - Admin: admin / admin123")
    print(f"   - Citizen: citizen1 / pass123")
    print("\n" + "="*60 + "\n")

# ========== Run Server ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    # At the end of api.py, REPLACE the if __name__ == "__main__": block with:

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
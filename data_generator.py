"""
Data Generator for Civic Issue Reporting System
Generates synthetic historical data for AI training and demo purposes
"""

import random
import json
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict
import sqlite3


class CivicDataGenerator:
    """Generate realistic synthetic civic issue data"""
    
    def __init__(self):
        # Gandhinagar, Gujarat coordinates
        self.base_lat = 23.2156
        self.base_lng = 72.6369
        
        # Issue categories with realistic distributions
        self.categories = {
            "pothole": {
                "weight": 0.30,
                "subcategories": ["small", "medium", "large", "dangerous"],
                "titles": [
                    "Large pothole on main road",
                    "Dangerous crater near intersection",
                    "Multiple potholes causing traffic issues",
                    "Deep pothole damaging vehicles",
                    "Road damage needs immediate attention"
                ],
                "descriptions": [
                    "There is a large pothole that has been growing for weeks. It's causing vehicle damage.",
                    "Multiple vehicles have been damaged due to this pothole. Urgent repair needed.",
                    "Deep crater formed after recent rains. Very dangerous for two-wheelers.",
                    "Pothole has expanded significantly and is now a major hazard.",
                    "Road surface damaged with multiple holes. Traffic slowing down considerably."
                ]
            },
            "streetlight_failure": {
                "weight": 0.20,
                "subcategories": ["completely_dark", "flickering", "dim"],
                "titles": [
                    "Street light not working",
                    "Dark area causing safety concerns",
                    "Multiple street lights failed",
                    "Flickering street light",
                    "Street light broken after storm"
                ],
                "descriptions": [
                    "Street light has been non-functional for over a week. Area is completely dark at night.",
                    "Light is flickering continuously. Needs immediate attention.",
                    "Multiple lights in this area are not working. Safety concern for residents.",
                    "Light pole damaged, bulb not working. Creating dark spots on the road.",
                    "After recent storm, several street lights are malfunctioning."
                ]
            },
            "garbage_overflow": {
                "weight": 0.25,
                "subcategories": ["minor", "moderate", "severe"],
                "titles": [
                    "Overflowing garbage bin",
                    "Waste accumulating on street",
                    "Garbage not collected for days",
                    "Unhygienic conditions due to waste",
                    "Urgent garbage collection needed"
                ],
                "descriptions": [
                    "Garbage bin is overflowing. Waste is spilling onto the street.",
                    "Collection has not happened for 3 days. Bad smell and unhygienic conditions.",
                    "Severe overflow with waste scattered around. Health hazard.",
                    "Multiple bins overflowing in this area. Attracting stray animals and insects.",
                    "Garbage accumulation creating serious sanitation issues."
                ]
            },
            "water_logging": {
                "weight": 0.10,
                "subcategories": ["shallow", "moderate", "deep"],
                "titles": [
                    "Water logging after rain",
                    "Drainage system blocked",
                    "Standing water causing problems",
                    "Road flooded, traffic disrupted",
                    "Severe water logging"
                ],
                "descriptions": [
                    "Water has been standing for hours after the rain. Drainage seems blocked.",
                    "Deep water accumulation making the road impassable.",
                    "Drainage system not functioning properly. Water logging every time it rains.",
                    "Street completely flooded. Vehicles cannot pass through.",
                    "Water entering nearby homes due to poor drainage."
                ]
            },
            "broken_road": {
                "weight": 0.10,
                "subcategories": ["minor_crack", "major_damage", "complete_breakdown"],
                "titles": [
                    "Road surface damaged",
                    "Broken road patch",
                    "Major cracks on road",
                    "Road deteriorating rapidly",
                    "Urgent road repair needed"
                ],
                "descriptions": [
                    "Road surface has developed major cracks. Getting worse daily.",
                    "Large section of road has broken down completely.",
                    "Road patch work is failing. Multiple cracks appearing.",
                    "Heavy vehicles causing further damage to already weak road.",
                    "Road condition extremely poor. Repair needed urgently."
                ]
            },
            "traffic_signal_issue": {
                "weight": 0.03,
                "subcategories": ["not_working", "timing_issue", "visibility_issue"],
                "titles": [
                    "Traffic signal not functioning",
                    "Signal timing needs adjustment",
                    "Traffic light visibility poor",
                    "Signal causing traffic jams",
                    "Broken traffic signal"
                ],
                "descriptions": [
                    "Traffic signal has stopped working. Causing confusion and traffic buildup.",
                    "Signal timing is inappropriate for current traffic flow.",
                    "Signal lights are dim and not visible in sunlight.",
                    "All signals showing red, causing complete stoppage.",
                    "Signal damaged, needs immediate repair to prevent accidents."
                ]
            },
            "illegal_dumping": {
                "weight": 0.01,
                "subcategories": ["minor", "moderate", "severe"],
                "titles": [
                    "Illegal waste dumping",
                    "Construction debris dumped",
                    "Unauthorized dumping site",
                    "Hazardous waste dumped illegally"
                ],
                "descriptions": [
                    "Someone has dumped construction waste on public land.",
                    "Illegal dumping of household waste. Creating environmental hazard.",
                    "Large amount of debris dumped without authorization.",
                    "Repeated illegal dumping at this location. Strict action needed."
                ]
            },
            "drainage_blockage": {
                "weight": 0.01,
                "subcategories": ["minor", "moderate", "severe"],
                "titles": [
                    "Drain blocked with debris",
                    "Sewage overflow due to blockage",
                    "Drainage system clogged",
                    "Urgent drain cleaning needed"
                ],
                "descriptions": [
                    "Drain is completely blocked. Causing water overflow.",
                    "Sewage backing up due to drainage blockage.",
                    "Debris and plastic blocking the drain. Needs cleaning.",
                    "Drainage system severely clogged. Creating health hazard."
                ]
            }
        }
        
        # Status distribution (realistic)
        self.statuses = {
            "open": 0.40,
            "in_progress": 0.30,
            "resolved": 0.28,
            "closed": 0.02
        }
        
        # Area names in Gandhinagar
        self.areas = [
            "Sector 1", "Sector 2", "Sector 3", "Sector 4", "Sector 5",
            "Sector 6", "Sector 7", "Sector 8", "Sector 9", "Sector 10",
            "Sector 11", "Sector 12", "Sector 13", "Sector 14", "Sector 15",
            "Sector 16", "Sector 17", "Sector 18", "Sector 19", "Sector 20",
            "Kudasan", "Palaj", "Sargasan", "Infocity", "GIFT City",
            "Koba", "Raysan", "Dehgam", "Mansa"
        ]
    
    def generate_location(self) -> Dict:
        """Generate random location in Gandhinagar area"""
        # Add random offset within ~20km radius
        lat_offset = random.uniform(-0.15, 0.15)
        lng_offset = random.uniform(-0.15, 0.15)
        
        latitude = self.base_lat + lat_offset
        longitude = self.base_lng + lng_offset
        
        area = random.choice(self.areas)
        address = f"{area}, Gandhinagar, Gujarat"
        
        return {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "address": address,
            "area": area
        }
    
    def generate_timestamp(self, days_ago: int) -> str:
        """Generate timestamp for issue creation"""
        # Random time in the past `days_ago` days
        offset_days = random.uniform(0, days_ago)
        timestamp = datetime.now() - timedelta(days=offset_days)
        
        # Random hour during the day (7 AM - 10 PM)
        hour = random.randint(7, 22)
        timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
        
        return timestamp.isoformat()
    
    def select_category(self) -> str:
        """Select category based on realistic distribution"""
        rand = random.random()
        cumulative = 0
        
        for category, weight in self.categories.items():
            cumulative += weight["weight"]
            if rand <= cumulative:
                return category
        
        return "pothole"  # Default
    
    def select_status(self, days_old: float) -> str:
        """Select status based on age and realistic distribution"""
        # Older issues more likely to be resolved
        if days_old > 30:
            statuses = ["open", "in_progress", "resolved", "closed"]
            weights = [0.10, 0.15, 0.70, 0.05]
        elif days_old > 14:
            statuses = ["open", "in_progress", "resolved", "closed"]
            weights = [0.20, 0.35, 0.43, 0.02]
        elif days_old > 7:
            statuses = ["open", "in_progress", "resolved", "closed"]
            weights = [0.40, 0.40, 0.19, 0.01]
        else:
            statuses = ["open", "in_progress", "resolved"]
            weights = [0.60, 0.35, 0.05]
        
        return random.choices(statuses, weights=weights)[0]
    
    def generate_issue(self, issue_id: int, days_ago: int) -> Dict:
        """Generate a single synthetic civic issue"""
        category = self.select_category()
        category_data = self.categories[category]
        
        # Select subcategory
        subcategory = random.choice(category_data["subcategories"])
        
        # Select title and description
        title = random.choice(category_data["titles"])
        description = random.choice(category_data["descriptions"])
        
        # Generate location
        location = self.generate_location()
        
        # Generate timestamp
        created_at = self.generate_timestamp(days_ago)
        created_dt = datetime.fromisoformat(created_at)
        days_old = (datetime.now() - created_dt).days
        
        # Select status based on age
        status = self.select_status(days_old)
        
        # Calculate priority (higher priority for urgent categories and recent issues)
        base_priority = {
            "pothole": 60,
            "streetlight_failure": 55,
            "garbage_overflow": 50,
            "water_logging": 75,
            "broken_road": 65,
            "traffic_signal_issue": 80,
            "illegal_dumping": 40,
            "drainage_blockage": 70
        }
        
        priority_score = base_priority.get(category, 50)
        
        # Adjust priority based on subcategory severity
        if "large" in subcategory or "severe" in subcategory or "major" in subcategory:
            priority_score += 15
        elif "medium" in subcategory or "moderate" in subcategory:
            priority_score += 5
        
        # Adjust for recency (newer issues get slight boost)
        if days_old < 2:
            priority_score += 10
        
        priority_score = min(100, max(0, priority_score))
        
        # Determine priority level
        if priority_score >= 80:
            priority = "urgent"
        elif priority_score >= 60:
            priority = "high"
        elif priority_score >= 40:
            priority = "medium"
        else:
            priority = "low"
        
        # Generate resolution timestamp if resolved
        resolved_at = None
        if status in ["resolved", "closed"]:
            resolution_days = random.uniform(1, min(days_old, 20))
            resolved_dt = created_dt + timedelta(days=resolution_days)
            resolved_at = resolved_dt.isoformat()
        
        # Random upvotes and views
        upvotes = random.randint(0, max(1, int(days_old * 2)))
        views = random.randint(upvotes, max(upvotes + 5, int(days_old * 10)))
        
        return {
            "id": f"issue_{issue_id:04d}",
            "title": title,
            "description": description,
            "category": category,
            "subcategory": subcategory,
            "status": status,
            "priority": priority,
            "priority_score": round(priority_score, 1),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "address": location["address"],
            "area": location["area"],
            "created_at": created_at,
            "resolved_at": resolved_at,
            "upvotes": upvotes,
            "views": views,
            "reported_by": f"user_{random.randint(1, 50):03d}"
        }
    
    def generate_dataset(self, num_issues: int = 500, max_days: int = 90) -> List[Dict]:
        """Generate complete dataset of synthetic issues"""
        print(f"Generating {num_issues} synthetic civic issues...")
        
        issues = []
        for i in range(num_issues):
            issue = self.generate_issue(i + 1, max_days)
            issues.append(issue)
            
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1}/{num_issues} issues...")
        
        print(f"✓ Generated {num_issues} issues successfully!")
        return issues
    
    def save_to_database(self, issues: List[Dict], db_path: str = "civic_issues.db"):
        """Save generated issues to SQLite database"""
        print(f"\nSaving {len(issues)} issues to database...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert issues
        for issue in issues:
            try:
                cursor.execute("""
                    INSERT INTO civic_issues (
                        id, title, description, category, subcategory,
                        status, priority, priority_score,
                        latitude, longitude, address,
                        reported_by, created_at, resolved_at,
                        upvotes, views
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    issue["id"], issue["title"], issue["description"],
                    issue["category"], issue["subcategory"],
                    issue["status"], issue["priority"], issue["priority_score"],
                    issue["latitude"], issue["longitude"], issue["address"],
                    issue["reported_by"], issue["created_at"], issue["resolved_at"],
                    issue["upvotes"], issue["views"]
                ))
            except sqlite3.IntegrityError:
                # Skip if already exists
                pass
        
        conn.commit()
        conn.close()
        print(f"✓ Saved to database: {db_path}")
    
    def save_to_json(self, issues: List[Dict], filename: str = "civic_issues_data.json"):
        """Save issues to JSON file"""
        with open(filename, 'w') as f:
            json.dump(issues, f, indent=2)
        print(f"✓ Saved to JSON: {filename}")
    
    def generate_statistics(self, issues: List[Dict]) -> Dict:
        """Generate statistics about the dataset"""
        stats = {
            "total_issues": len(issues),
            "by_category": {},
            "by_status": {},
            "by_priority": {},
            "by_area": {},
            "date_range": {
                "oldest": None,
                "newest": None
            }
        }
        
        # Category distribution
        for issue in issues:
            cat = issue["category"]
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            
            status = issue["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            priority = issue["priority"]
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            area = issue.get("area", "Unknown")
            stats["by_area"][area] = stats["by_area"].get(area, 0) + 1
        
        # Date range
        dates = [datetime.fromisoformat(i["created_at"]) for i in issues]
        stats["date_range"]["oldest"] = min(dates).isoformat()
        stats["date_range"]["newest"] = max(dates).isoformat()
        
        return stats


def main():
    """Main function to generate synthetic data"""
    print("=" * 60)
    print("  CIVIC ISSUE DATA GENERATOR")
    print("  AI Innovation Challenge 2026 - Gandhinagar")
    print("=" * 60)
    
    generator = CivicDataGenerator()
    
    # Generate 800 issues over last 90 days
    issues = generator.generate_dataset(num_issues=800, max_days=90)
    
    # Save to files
    generator.save_to_json(issues, "civic_issues_data.json")
    generator.save_to_database(issues, "civic_issues.db")
    
    # Generate and display statistics
    print("\n" + "=" * 60)
    print("  DATASET STATISTICS")
    print("=" * 60)
    
    stats = generator.generate_statistics(issues)
    
    print(f"\nTotal Issues: {stats['total_issues']}")
    
    print("\nCategory Distribution:")
    for category, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        percentage = (count / stats['total_issues']) * 100
        print(f"  {category:25s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\nStatus Distribution:")
    for status, count in sorted(stats["by_status"].items(), key=lambda x: -x[1]):
        percentage = (count / stats['total_issues']) * 100
        print(f"  {status:15s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\nPriority Distribution:")
    for priority, count in sorted(stats["by_priority"].items(), key=lambda x: -x[1]):
        percentage = (count / stats['total_issues']) * 100
        print(f"  {priority:10s}: {count:4d} ({percentage:5.1f}%)")
    
    print("\nTop 10 Areas by Issue Count:")
    sorted_areas = sorted(stats["by_area"].items(), key=lambda x: -x[1])[:10]
    for area, count in sorted_areas:
        print(f"  {area:20s}: {count:4d}")
    
    print(f"\nDate Range:")
    print(f"  Oldest: {stats['date_range']['oldest']}")
    print(f"  Newest: {stats['date_range']['newest']}")
    
    print("\n" + "=" * 60)
    print("✓ Data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
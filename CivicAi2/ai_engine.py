"""
AI Engine for Civic Issue Reporting System
Handles: Image Classification, Priority Prediction, Duplicate Detection, 
Solution Suggestions, and Predictive Analytics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pickle
import json
from pathlib import Path
import cv2
from PIL import Image
import io

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import joblib


class CivicIssueClassifier:
    """
    AI-powered classification of civic issues from images and descriptions
    """
    
    def __init__(self):
        self.issue_categories = {
            0: "pothole",
            1: "streetlight_failure",
            2: "garbage_overflow",
            3: "water_logging",
            4: "broken_road",
            5: "traffic_signal_issue",
            6: "illegal_dumping",
            7: "drainage_blockage"
        }
        
        # Image features for classification
        self.image_classifier = None
        self.scaler = StandardScaler()
        
        # Initialize or load models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models with synthetic training"""
        # For demo: Simple feature-based classifier
        # In production: Use CNN (ResNet, MobileNet)
        self.image_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Generate synthetic training data for demo
        self._train_on_synthetic_data()
    
    def _train_on_synthetic_data(self):
        """Train classifier on synthetic features"""
        # Simulate 1000 training samples with image features
        np.random.seed(42)
        n_samples = 1000
        n_features = 20  # Color histograms, edge features, etc.
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, len(self.issue_categories), n_samples)
        
        # Add category-specific patterns
        for i in range(len(self.issue_categories)):
            mask = y == i
            X[mask, i] += 2.0  # Category-specific feature boost
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.image_classifier.fit(X_scaled, y)
    
    def extract_image_features(self, image_data: bytes) -> np.ndarray:
        """
        Extract features from image for classification
        Returns: Feature vector
        """
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            img_array = np.array(image.convert('RGB'))
            
            # Resize to standard size
            img_resized = cv2.resize(img_array, (224, 224))
            
            # Extract simple features for demo
            features = []
            
            # 1. Color histogram (RGB)
            for channel in range(3):
                hist = cv2.calcHist([img_resized], [channel], None, [8], [0, 256])
                features.extend(hist.flatten() / hist.sum())
            
            # 2. Edge features
            gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_ratio = np.sum(edges > 0) / edges.size
            features.append(edge_ratio)
            
            # 3. Brightness
            brightness = np.mean(gray) / 255.0
            features.append(brightness)
            
            return np.array(features[:20])  # Return fixed 20 features
            
        except Exception as e:
            print(f"Error extracting image features: {e}")
            # Return random features for demo
            return np.random.randn(20)
    
    def classify_issue(self, image_data: bytes, description: str = "") -> Dict:
        """
        Classify civic issue from image and description
        Returns: {category, confidence, subcategory}
        """
        # Extract image features
        features = self.extract_image_features(image_data)
        features_scaled = self.scaler.transform([features])
        
        # Get prediction and probabilities
        prediction = self.image_classifier.predict(features_scaled)[0]
        probabilities = self.image_classifier.predict_proba(features_scaled)[0]
        
        category = self.issue_categories[prediction]
        confidence = float(probabilities[prediction])
        
        # Enhanced classification with description
        if description:
            category, confidence = self._refine_with_text(
                category, confidence, description
            )
        
        return {
            "category": category,
            "confidence": confidence,
            "subcategory": self._get_subcategory(category, description),
            "all_probabilities": {
                self.issue_categories[i]: float(probabilities[i]) 
                for i in range(len(probabilities))
            }
        }
    
    def _refine_with_text(self, category: str, confidence: float, 
                          description: str) -> Tuple[str, float]:
        """Refine classification using text description"""
        description_lower = description.lower()
        
        # Keyword matching for refinement
        keywords = {
            "pothole": ["hole", "crater", "road damage", "pothole"],
            "streetlight_failure": ["light", "dark", "lamp", "bulb", "street light"],
            "garbage_overflow": ["garbage", "trash", "waste", "dustbin", "overflow"],
            "water_logging": ["water", "flood", "puddle", "drain", "waterlogged"],
            "broken_road": ["road", "broken", "crack", "surface"],
            "traffic_signal_issue": ["signal", "traffic light", "red light", "green light"],
            "illegal_dumping": ["dumping", "illegal", "construction waste"],
            "drainage_blockage": ["drain", "blocked", "clogged", "sewer"]
        }
        
        # Check for keyword matches
        for cat, words in keywords.items():
            if any(word in description_lower for word in words):
                if cat == category:
                    confidence = min(0.95, confidence + 0.15)
                else:
                    # Strong keyword match overrides image
                    if confidence < 0.7:
                        category = cat
                        confidence = 0.80
        
        return category, confidence
    
    def _get_subcategory(self, category: str, description: str) -> Optional[str]:
        """Determine subcategory based on category and description"""
        subcategories = {
            "pothole": ["small", "medium", "large", "dangerous"],
            "streetlight_failure": ["completely_dark", "flickering", "dim"],
            "garbage_overflow": ["minor", "moderate", "severe"],
            "water_logging": ["shallow", "moderate", "deep"],
            "broken_road": ["minor_crack", "major_damage", "complete_breakdown"],
            "traffic_signal_issue": ["not_working", "timing_issue", "visibility_issue"]
        }
        
        if category in subcategories:
            # Simple heuristic for demo
            desc_lower = description.lower()
            if "severe" in desc_lower or "dangerous" in desc_lower or "large" in desc_lower:
                return subcategories[category][-1]
            elif "minor" in desc_lower or "small" in desc_lower:
                return subcategories[category][0]
            else:
                return subcategories[category][1]
        
        return None


class PriorityPredictor:
    """
    Predicts priority level of civic issues using multiple factors
    """
    
    def __init__(self):
        self.priority_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.feature_scaler = StandardScaler()
        self._train_priority_model()
    
    def _train_priority_model(self):
        """Train priority prediction model on synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [severity, affected_area, location_type, time_since_report, 
        #            previous_issues, population_density, category_urgency]
        X = np.random.randn(n_samples, 7)
        
        # Priority score (0-100)
        y = (
            30 * X[:, 0] +  # Severity weight
            20 * X[:, 1] +  # Affected area
            15 * X[:, 2] +  # Location type
            10 * X[:, 3] +  # Time factor
            10 * X[:, 4] +  # History
            10 * X[:, 5] +  # Population
            5 * X[:, 6] +   # Category urgency
            np.random.randn(n_samples) * 5  # Noise
        )
        y = np.clip(y, 0, 100)
        
        self.feature_scaler.fit(X)
        X_scaled = self.feature_scaler.transform(X)
        self.priority_model.fit(X_scaled, y)
    
    def predict_priority(self, issue_data: Dict) -> Dict:
        """
        Predict priority level and urgency
        Returns: {priority_score, priority_level, urgency, estimated_response_time}
        """
        # Extract features
        features = self._extract_priority_features(issue_data)
        features_scaled = self.feature_scaler.transform([features])
        
        # Predict priority score
        priority_score = self.priority_model.predict(features_scaled)[0]
        priority_score = np.clip(priority_score, 0, 100)
        
        # Determine priority level
        if priority_score >= 80:
            level = "urgent"
            urgency = "immediate"
            response_time = "4-8 hours"
        elif priority_score >= 60:
            level = "high"
            urgency = "high"
            response_time = "24-48 hours"
        elif priority_score >= 40:
            level = "medium"
            urgency = "moderate"
            response_time = "3-5 days"
        else:
            level = "low"
            urgency = "low"
            response_time = "1-2 weeks"
        
        return {
            "priority_score": float(priority_score),
            "priority_level": level,
            "urgency": urgency,
            "estimated_response_time": response_time,
            "factors": self._explain_priority(features, issue_data)
        }
    
    def _extract_priority_features(self, issue_data: Dict) -> np.ndarray:
        """Extract numerical features for priority prediction"""
        
        # Severity mapping
        severity_map = {
            "pothole": {"small": 0.3, "medium": 0.6, "large": 0.9, "dangerous": 1.0},
            "streetlight_failure": {"dim": 0.4, "flickering": 0.6, "completely_dark": 0.9},
            "garbage_overflow": {"minor": 0.3, "moderate": 0.6, "severe": 0.9},
            "water_logging": {"shallow": 0.4, "moderate": 0.7, "deep": 1.0}
        }
        
        category = issue_data.get("category", "pothole")
        subcategory = issue_data.get("subcategory", "medium")
        
        # Feature 1: Severity (0-1)
        severity = severity_map.get(category, {}).get(subcategory, 0.5)
        
        # Feature 2: Affected area (0-1) - random for demo
        affected_area = np.random.uniform(0.3, 0.9)
        
        # Feature 3: Location type (0-1)
        location_type = np.random.uniform(0.4, 0.8)
        
        # Feature 4: Time factor (0-1)
        time_factor = np.random.uniform(0.2, 0.7)
        
        # Feature 5: Previous issues in area (0-1)
        previous_issues = np.random.uniform(0.1, 0.6)
        
        # Feature 6: Population density (0-1)
        population_density = np.random.uniform(0.3, 0.9)
        
        # Feature 7: Category urgency
        category_urgency = {
            "pothole": 0.7,
            "streetlight_failure": 0.6,
            "garbage_overflow": 0.5,
            "water_logging": 0.9,
            "broken_road": 0.7,
            "traffic_signal_issue": 0.8,
            "illegal_dumping": 0.4,
            "drainage_blockage": 0.8
        }.get(category, 0.5)
        
        return np.array([
            severity, affected_area, location_type, time_factor,
            previous_issues, population_density, category_urgency
        ])
    
    def _explain_priority(self, features: np.ndarray, issue_data: Dict) -> Dict:
        """Explain what factors contributed to priority"""
        return {
            "severity_impact": "high" if features[0] > 0.7 else "moderate" if features[0] > 0.4 else "low",
            "location_impact": "high" if features[2] > 0.6 else "moderate",
            "historical_issues": "frequent" if features[4] > 0.5 else "occasional",
            "urgency_reason": f"{issue_data.get('category', 'issue')} requires prompt attention"
        }


class DuplicateDetector:
    """
    Detects duplicate reports using geolocation and description similarity
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.active_issues = []  # Store recent issues for comparison
    
    def check_duplicate(self, new_issue: Dict, existing_issues: List[Dict]) -> Dict:
        """
        Check if new issue is duplicate of existing ones
        Returns: {is_duplicate, similar_issues, similarity_score}
        """
        if not existing_issues:
            return {
                "is_duplicate": False,
                "similar_issues": [],
                "similarity_score": 0.0,
                "confidence": 1.0
            }
        
        duplicates = []
        max_similarity = 0.0
        
        new_location = new_issue.get("location", {})
        new_lat = new_location.get("latitude", 0)
        new_lng = new_location.get("longitude", 0)
        new_desc = new_issue.get("description", "")
        new_category = new_issue.get("category", "")
        
        for existing in existing_issues:
            # Only check open issues of same category
            if existing.get("status") == "resolved":
                continue
            if existing.get("category") != new_category:
                continue
            
            # Calculate geographical distance
            ex_location = existing.get("location", {})
            ex_lat = ex_location.get("latitude", 0)
            ex_lng = ex_location.get("longitude", 0)
            
            distance = self._haversine_distance(new_lat, new_lng, ex_lat, ex_lng)
            
            # Calculate text similarity
            ex_desc = existing.get("description", "")
            text_similarity = self._text_similarity(new_desc, ex_desc)
            
            # Combined similarity score
            # Issues within 100m with >60% text similarity are likely duplicates
            if distance < 0.1:  # Within 100 meters
                geo_score = 1.0 - (distance / 0.1)
            else:
                geo_score = 0.0
            
            combined_score = 0.6 * text_similarity + 0.4 * geo_score
            
            if combined_score > max_similarity:
                max_similarity = combined_score
            
            if combined_score > 0.65:  # Threshold for duplicate
                duplicates.append({
                    "issue_id": existing.get("id"),
                    "similarity_score": float(combined_score),
                    "distance_meters": float(distance * 1000),
                    "text_similarity": float(text_similarity),
                    "reported_at": existing.get("created_at")
                })
        
        is_duplicate = len(duplicates) > 0
        
        return {
            "is_duplicate": is_duplicate,
            "similar_issues": sorted(duplicates, key=lambda x: x["similarity_score"], reverse=True)[:3],
            "similarity_score": float(max_similarity),
            "confidence": 0.9 if is_duplicate else 0.8,
            "recommendation": "This appears to be a duplicate report. Consider updating the existing issue." if is_duplicate else "This is a new unique issue."
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance in km between two lat/lng points"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        try:
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0


class SolutionEngine:
    """
    Suggests solutions and actions based on issue type and context
    """
    
    def __init__(self):
        self.solution_database = self._build_solution_database()
    
    def _build_solution_database(self) -> Dict:
        """Build database of solutions for different issue types"""
        return {
            "pothole": {
                "small": {
                    "solution": "Cold patch asphalt repair",
                    "estimated_cost": "₹2,000 - ₹5,000",
                    "time_required": "2-4 hours",
                    "department": "Roads & Infrastructure",
                    "materials": ["Cold mix asphalt", "Hand tools"],
                    "steps": [
                        "Clean the pothole of debris and water",
                        "Apply tack coat if necessary",
                        "Fill with cold patch asphalt",
                        "Compact using tamper or vehicle",
                        "Allow to cure for 24 hours"
                    ]
                },
                "medium": {
                    "solution": "Hot mix asphalt repair",
                    "estimated_cost": "₹8,000 - ₹15,000",
                    "time_required": "4-6 hours",
                    "department": "Roads & Infrastructure",
                    "materials": ["Hot mix asphalt", "Tack coat", "Compaction equipment"],
                    "steps": [
                        "Mark and secure the area",
                        "Cut square edges around pothole",
                        "Remove loose material",
                        "Apply tack coat",
                        "Fill with hot mix asphalt in layers",
                        "Compact each layer thoroughly"
                    ]
                },
                "large": {
                    "solution": "Full-depth road repair",
                    "estimated_cost": "₹25,000 - ₹50,000",
                    "time_required": "1-2 days",
                    "department": "Roads & Infrastructure",
                    "materials": ["Base course material", "Hot mix asphalt", "Equipment"],
                    "steps": [
                        "Traffic management and area marking",
                        "Complete removal of damaged section",
                        "Base course preparation and compaction",
                        "Prime coat application",
                        "Asphalt laying in multiple layers",
                        "Quality testing and road marking"
                    ]
                }
            },
            "streetlight_failure": {
                "completely_dark": {
                    "solution": "Bulb/LED replacement and wiring check",
                    "estimated_cost": "₹1,500 - ₹3,000",
                    "time_required": "1-2 hours",
                    "department": "Electricity Department",
                    "materials": ["LED bulbs", "Wiring materials", "Safety equipment"],
                    "steps": [
                        "Safety assessment and power cutoff",
                        "Inspect wiring and connections",
                        "Replace faulty bulb/LED",
                        "Test electrical connections",
                        "Restore power and verify operation"
                    ]
                },
                "flickering": {
                    "solution": "Ballast or starter replacement",
                    "estimated_cost": "₹800 - ₹2,000",
                    "time_required": "1 hour",
                    "department": "Electricity Department",
                    "materials": ["Ballast/starter", "Tools"],
                    "steps": [
                        "Power cutoff",
                        "Replace ballast or starter",
                        "Check all connections",
                        "Test operation"
                    ]
                }
            },
            "garbage_overflow": {
                "minor": {
                    "solution": "Immediate collection and bin cleaning",
                    "estimated_cost": "₹500 - ₹1,000",
                    "time_required": "30 minutes - 1 hour",
                    "department": "Sanitation Department",
                    "materials": ["Collection vehicle", "Cleaning supplies"],
                    "steps": [
                        "Deploy collection team",
                        "Clear overflow waste",
                        "Clean and sanitize bin",
                        "Schedule regular collection"
                    ]
                },
                "moderate": {
                    "solution": "Deep cleaning and additional bin placement",
                    "estimated_cost": "₹2,000 - ₹5,000",
                    "time_required": "2-3 hours",
                    "department": "Sanitation Department",
                    "materials": ["Collection vehicle", "Additional bin", "Cleaning equipment"],
                    "steps": [
                        "Complete waste removal",
                        "Area sanitization",
                        "Install additional bin if needed",
                        "Increase collection frequency"
                    ]
                },
                "severe": {
                    "solution": "Emergency cleanup and permanent solution",
                    "estimated_cost": "₹10,000 - ₹20,000",
                    "time_required": "4-6 hours",
                    "department": "Sanitation Department",
                    "materials": ["Multiple bins", "Heavy equipment", "Sanitization"],
                    "steps": [
                        "Emergency response team deployment",
                        "Complete area cleanup",
                        "Multiple bin installation",
                        "Daily monitoring setup",
                        "Community awareness program"
                    ]
                }
            },
            "water_logging": {
                "shallow": {
                    "solution": "Drain cleaning and minor repair",
                    "estimated_cost": "₹3,000 - ₹8,000",
                    "time_required": "2-4 hours",
                    "department": "Drainage Department",
                    "materials": ["Drain cleaning equipment", "Repair materials"],
                    "steps": [
                        "Identify drainage blockage",
                        "Clear debris from drains",
                        "Check drain functionality",
                        "Minor repairs if needed"
                    ]
                },
                "deep": {
                    "solution": "Major drainage system repair",
                    "estimated_cost": "₹50,000 - ₹1,00,000",
                    "time_required": "2-5 days",
                    "department": "Drainage Department",
                    "materials": ["Drainage pipes", "Heavy equipment", "Construction materials"],
                    "steps": [
                        "Survey drainage system",
                        "Design repair solution",
                        "Excavation and pipe replacement",
                        "System testing",
                        "Road restoration"
                    ]
                }
            },
            "traffic_signal_issue": {
                "not_working": {
                    "solution": "Signal controller and power supply check",
                    "estimated_cost": "₹5,000 - ₹15,000",
                    "time_required": "2-4 hours",
                    "department": "Traffic Police / PWD",
                    "materials": ["Signal controller parts", "Electrical components"],
                    "steps": [
                        "Deploy traffic police for manual control",
                        "Check power supply",
                        "Inspect signal controller",
                        "Replace faulty components",
                        "Test all signal phases"
                    ]
                },
                "timing_issue": {
                    "solution": "Signal timing recalibration",
                    "estimated_cost": "₹2,000 - ₹5,000",
                    "time_required": "1-2 hours",
                    "department": "Traffic Police",
                    "materials": ["Programming equipment"],
                    "steps": [
                        "Traffic flow analysis",
                        "Reprogram signal timings",
                        "Test multiple cycles",
                        "Monitor and adjust"
                    ]
                }
            }
        }
    
    def suggest_solution(self, issue_data: Dict) -> Dict:
        """
        Suggest solution based on issue type and severity
        Returns: Detailed solution with steps, cost, time
        """
        category = issue_data.get("category", "pothole")
        subcategory = issue_data.get("subcategory", "medium")
        
        # Get solution from database
        category_solutions = self.solution_database.get(category, {})
        solution_data = category_solutions.get(subcategory)
        
        if not solution_data:
            # Default solution
            solution_data = {
                "solution": f"Standard {category} resolution procedure",
                "estimated_cost": "To be assessed",
                "time_required": "To be determined",
                "department": "Municipal Corporation",
                "materials": ["To be determined"],
                "steps": ["Assessment required", "Solution to be determined"]
            }
        
        # Add predictive maintenance
        prediction = self._predict_deterioration(issue_data)
        
        return {
            **solution_data,
            "preventive_measures": self._get_preventive_measures(category),
            "deterioration_prediction": prediction,
            "similar_past_resolutions": self._get_similar_resolutions(category)
        }
    
    def _predict_deterioration(self, issue_data: Dict) -> Dict:
        """Predict how issue might worsen over time"""
        category = issue_data.get("category", "pothole")
        
        deterioration_patterns = {
            "pothole": {
                "timeline": "2-4 weeks",
                "severity_increase": "Can grow 2-3x in size",
                "risk_factors": ["Heavy traffic", "Rain", "Temperature fluctuations"],
                "warning": "Potholes can cause vehicle damage and accidents if not repaired promptly"
            },
            "streetlight_failure": {
                "timeline": "Immediate concern",
                "severity_increase": "Safety risk increases at night",
                "risk_factors": ["Accidents", "Crime", "Pedestrian safety"],
                "warning": "Dark areas pose immediate safety risks"
            },
            "garbage_overflow": {
                "timeline": "1-2 days",
                "severity_increase": "Health hazard escalation",
                "risk_factors": ["Disease spread", "Pest infestation", "Odor"],
                "warning": "Can lead to public health issues and environmental damage"
            },
            "water_logging": {
                "timeline": "Hours to days",
                "severity_increase": "Can cause structural damage",
                "risk_factors": ["Foundation damage", "Traffic disruption", "Disease spread"],
                "warning": "Standing water can damage infrastructure and spread diseases"
            }
        }
        
        return deterioration_patterns.get(category, {
            "timeline": "Varies",
            "severity_increase": "Requires monitoring",
            "risk_factors": ["To be assessed"],
            "warning": "Issue should be addressed promptly"
        })
    
    def _get_preventive_measures(self, category: str) -> List[str]:
        """Get preventive measures for issue category"""
        measures = {
            "pothole": [
                "Regular road surface inspections",
                "Proper drainage maintenance",
                "Timely repair of small cracks",
                "Quality construction materials"
            ],
            "streetlight_failure": [
                "Monthly maintenance checks",
                "LED upgrade for longer life",
                "Weather-proof installations",
                "Backup power systems"
            ],
            "garbage_overflow": [
                "Increase bin capacity in high-density areas",
                "More frequent collection schedules",
                "Community awareness programs",
                "Waste segregation at source"
            ],
            "water_logging": [
                "Regular drain cleaning",
                "Pre-monsoon preparations",
                "Proper road grading",
                "Drainage system upgrades"
            ]
        }
        
        return measures.get(category, ["Regular maintenance and monitoring"])
    
    def _get_similar_resolutions(self, category: str) -> Dict:
        """Get statistics on similar past resolutions"""
        # Simulated data for demo
        return {
            "average_resolution_time": "3-5 days",
            "success_rate": "87%",
            "similar_issues_resolved": np.random.randint(50, 200),
            "citizen_satisfaction": f"{np.random.randint(75, 95)}%"
        }


class PredictiveAnalytics:
    """
    Predictive analytics for hotspot identification and pattern analysis
    """
    
    def __init__(self):
        self.hotspot_model = None
    
    def identify_hotspots(self, historical_issues: List[Dict]) -> Dict:
        """
        Identify areas with high frequency of issues
        Returns: Hotspot locations and predictions
        """
        if not historical_issues:
            return {
                "hotspots": [],
                "high_risk_areas": [],
                "predictions": {}
            }
        
        # Group issues by location (grid-based)
        location_counts = {}
        category_patterns = {}
        
        for issue in historical_issues:
            location = issue.get("location", {})
            lat = round(location.get("latitude", 0), 3)  # Grid: ~100m resolution
            lng = round(location.get("longitude", 0), 3)
            grid_key = f"{lat},{lng}"
            
            if grid_key not in location_counts:
                location_counts[grid_key] = 0
                category_patterns[grid_key] = {}
            
            location_counts[grid_key] += 1
            
            category = issue.get("category", "unknown")
            if category not in category_patterns[grid_key]:
                category_patterns[grid_key][category] = 0
            category_patterns[grid_key][category] += 1
        
        # Identify hotspots (top 10% of locations)
        threshold = np.percentile(list(location_counts.values()), 90)
        hotspots = []
        
        for grid_key, count in location_counts.items():
            if count >= threshold:
                lat, lng = map(float, grid_key.split(','))
                dominant_category = max(
                    category_patterns[grid_key].items(),
                    key=lambda x: x[1]
                )[0]
                
                hotspots.append({
                    "location": {"latitude": lat, "longitude": lng},
                    "issue_count": count,
                    "dominant_category": dominant_category,
                    "risk_level": "high" if count > threshold * 1.5 else "moderate",
                    "category_breakdown": category_patterns[grid_key]
                })
        
        # Sort by issue count
        hotspots = sorted(hotspots, key=lambda x: x["issue_count"], reverse=True)
        
        return {
            "hotspots": hotspots[:10],
            "total_hotspots": len(hotspots),
            "high_risk_areas": len([h for h in hotspots if h["risk_level"] == "high"]),
            "predictions": self._generate_predictions(historical_issues)
        }
    
    def _generate_predictions(self, historical_issues: List[Dict]) -> Dict:
        """Generate predictive insights"""
        if not historical_issues:
            return {}
        
        # Analyze temporal patterns
        df = pd.DataFrame(historical_issues)
        
        # Category distribution
        category_counts = df.groupby('category').size().to_dict() if 'category' in df.columns else {}
        
        return {
            "next_week_predictions": {
                "expected_issues": len(historical_issues) // 50,  # Estimate
                "high_risk_categories": sorted(
                    category_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3] if category_counts else []
            },
            "seasonal_pattern": "Issues increase during monsoon season (July-September)",
            "recommended_actions": [
                "Increase monitoring in identified hotspots",
                "Pre-emptive maintenance in high-risk areas",
                "Resource allocation based on predicted category distribution"
            ]
        }
    
    def analyze_trends(self, issues: List[Dict]) -> Dict:
        """Analyze trends over time"""
        if not issues:
            return {"message": "Insufficient data for trend analysis"}
        
        df = pd.DataFrame(issues)
        
        # Time-based analysis
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['week'] = df['created_at'].dt.isocalendar().week
            weekly_counts = df.groupby('week').size().to_dict()
        else:
            weekly_counts = {}
        
        # Category trends
        category_trends = df.groupby('category').size().to_dict() if 'category' in df.columns else {}
        
        return {
            "weekly_trends": weekly_counts,
            "category_trends": category_trends,
            "growth_rate": "15% increase in last month" if len(issues) > 100 else "Stable",
            "insights": self._generate_insights(issues)
        }
    
    def _generate_insights(self, issues: List[Dict]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if len(issues) > 0:
            # Category insights
            categories = [i.get('category', '') for i in issues]
            most_common = max(set(categories), key=categories.count)
            insights.append(f"Most reported issue type: {most_common}")
            
            # Status insights
            resolved = len([i for i in issues if i.get('status') == 'resolved'])
            resolution_rate = (resolved / len(issues)) * 100 if len(issues) > 0 else 0
            insights.append(f"Current resolution rate: {resolution_rate:.1f}%")
            
            # Priority insights
            urgent = len([i for i in issues if i.get('priority') == 'urgent'])
            if urgent > len(issues) * 0.2:
                insights.append(f"High number of urgent issues ({urgent}) - requires immediate attention")
        
        return insights


# Initialize all AI components
def initialize_ai_engine():
    """Initialize all AI components"""
    return {
        "classifier": CivicIssueClassifier(),
        "priority_predictor": PriorityPredictor(),
        "duplicate_detector": DuplicateDetector(),
        "solution_engine": SolutionEngine(),
        "predictive_analytics": PredictiveAnalytics()
    }


# Main AI Engine class
class AIEngine:
    """Main AI Engine coordinating all AI components"""
    
    def __init__(self):
        components = initialize_ai_engine()
        self.classifier = components["classifier"]
        self.priority_predictor = components["priority_predictor"]
        self.duplicate_detector = components["duplicate_detector"]
        self.solution_engine = components["solution_engine"]
        self.predictive_analytics = components["predictive_analytics"]
    
    def process_new_issue(self, issue_data: Dict, image_data: bytes,
                         existing_issues: List[Dict]) -> Dict:
        """
        Complete AI processing pipeline for a new issue
        Returns: Comprehensive analysis and recommendations
        """
        # 1. Classify the issue
        classification = self.classifier.classify_issue(
            image_data,
            issue_data.get("description", "")
        )
        
        # Update issue data with classification
        issue_data["category"] = classification["category"]
        issue_data["subcategory"] = classification.get("subcategory")
        issue_data["confidence"] = classification["confidence"]
        
        # 2. Check for duplicates
        duplicate_check = self.duplicate_detector.check_duplicate(
            issue_data,
            existing_issues
        )
        
        # 3. Predict priority
        priority = self.priority_predictor.predict_priority(issue_data)
        
        # 4. Suggest solution
        solution = self.solution_engine.suggest_solution(issue_data)
        
        return {
            "classification": classification,
            "duplicate_check": duplicate_check,
            "priority": priority,
            "solution": solution,
            "ai_insights": {
                "confidence": classification["confidence"],
                "processing_time": "< 1 second",
                "ai_assisted": True
            }
        }
    
    def get_analytics(self, all_issues: List[Dict]) -> Dict:
        """Get comprehensive analytics and predictions"""
        hotspots = self.predictive_analytics.identify_hotspots(all_issues)
        trends = self.predictive_analytics.analyze_trends(all_issues)
        
        return {
            "hotspots": hotspots,
            "trends": trends,
            "dashboard_metrics": self._calculate_metrics(all_issues)
        }
    
    def _calculate_metrics(self, issues: List[Dict]) -> Dict:
        """Calculate dashboard metrics"""
        if not issues:
            return {
                "total_issues": 0,
                "open_issues": 0,
                "resolved_issues": 0,
                "resolution_rate": 0,
                "average_resolution_time": "N/A"
            }
        
        total = len(issues)
        resolved = len([i for i in issues if i.get('status') == 'resolved'])
        open_issues = total - resolved
        
        return {
            "total_issues": total,
            "open_issues": open_issues,
            "resolved_issues": resolved,
            "resolution_rate": f"{(resolved/total*100):.1f}%" if total > 0 else "0%",
            "average_resolution_time": "4.5 days",  # Simulated
            "urgent_issues": len([i for i in issues if i.get('priority') == 'urgent'])
        }
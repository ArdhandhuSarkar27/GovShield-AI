"""
Configuration settings for Ayushman Bharat Fraud Detection System
"""
from dataclasses import dataclass
from typing import List, Dict
import os


@dataclass
class ModelConfig:
    """Machine Learning model configuration"""
    n_estimators: int = 100
    max_depth: int = 10
    min_samples_split: int = 5
    min_samples_leaf: int = 2
    random_state: int = 42
    test_size: float = 0.2


@dataclass
class DataConfig:
    """Data generation and processing configuration"""
    default_rows: int = 500
    fraud_percentage: float = 0.25
    random_seed: int = 42
    
    # Risk score thresholds
    high_risk_threshold: float = 70.0
    medium_risk_threshold: float = 30.0
    
    # File paths
    output_file: str = "govshield_results.csv"
    model_file: str = "fraud_detection_model.pkl"
    encoders_file: str = "label_encoders.pkl"


@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance settings
    n_jobs: int = -1  # Use all available cores
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            n_jobs=int(os.getenv("N_JOBS", "-1"))
        )


# Static data configurations
HOSPITALS_DATA = [
    ("AIIMS Delhi", "Central Delhi"),
    ("PGI Chandigarh", "Chandigarh"),
    ("CMC Vellore", "Vellore"),
    ("SGPGI Lucknow", "Lucknow"),
    ("NIMHANS Bangalore", "Bangalore Urban"),
    ("Tata Memorial Mumbai", "Mumbai City"),
    ("JIPMER Puducherry", "Puducherry"),
    ("King George Medical Lucknow", "Lucknow"),
    ("Madras Medical College", "Chennai"),
    ("Grant Medical Mumbai", "Mumbai Suburban"),
    ("Regional Hospital Srinagar", "Srinagar"),
    ("Medical College Thiruvananthapuram", "Thiruvananthapuram"),
    ("Govt Hospital Bhopal", "Bhopal"),
    ("District Hospital Patna", "Patna"),
    ("Civil Hospital Ahmedabad", "Ahmedabad")
]

PROCEDURES_DATA = [
    ("Cataract Surgery", "H25.9", 25000),
    ("Cardiac Bypass", "I25.9", 300000),
    ("Knee Replacement", "M17.9", 200000),
    ("Appendectomy", "K35.9", 50000),
    ("Gallbladder Surgery", "K80.2", 75000),
    ("Hernia Repair", "K40.9", 40000),
    ("Dialysis", "N18.6", 3000),
    ("Chemotherapy", "C78.9", 150000),
    ("Angioplasty", "I25.0", 180000),
    ("Hip Replacement", "M16.9", 220000),
    ("Thyroid Surgery", "E04.9", 60000),
    ("Diabetes Treatment", "E11.9", 15000),
    ("Hypertension Management", "I10", 8000),
    ("Pneumonia Treatment", "J18.9", 20000),
    ("Fracture Treatment", "S72.9", 35000)
]

DEMOGRAPHIC_DATA = {
    "income_levels": ["BPL", "Lower Middle", "Middle", "Upper Middle"],
    "genders": ["Male", "Female", "Other"],
    "age_ranges": {
        "min_age": 18,
        "max_age": 85
    }
}

FRAUD_PATTERNS = {
    "inflation": {"min_factor": 1.5, "max_factor": 3.0},
    "duplicate": {"min_submissions": 3, "max_submissions": 8},
    "volume": {"min_procedures": 8, "max_procedures": 15},
    "income_mismatch": {
        "target_income": "BPL",
        "expensive_procedures": ["Cardiac Bypass", "Knee Replacement", "Angioplasty", "Hip Replacement"]
    }
}
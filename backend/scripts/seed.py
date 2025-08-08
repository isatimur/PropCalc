#!/usr/bin/env python3
"""
Database Seeding Script for Vantage AI
Populates the database with sample data for development and testing
"""

import logging
import os
import random
import sys
from datetime import date, timedelta

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import postgres_db
from schemas import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
SAMPLE_DEVELOPERS = [
    {
        "name": "Emaar Properties",
        "established_year": 1997,
        "track_record_score": 95.5,
        "financial_stability_score": 92.0,
        "customer_satisfaction_score": 88.5,
        "completed_projects_count": 45,
        "average_delay_days": 15,
        "total_project_value": 15000000000,
        "website_url": "https://www.emaar.com",
        "contact_email": "info@emaar.com",
        "phone_number": "+971-4-366-8888",
        "address": "Sheikh Zayed Road, Dubai, UAE"
    },
    {
        "name": "Nakheel",
        "established_year": 2001,
        "track_record_score": 88.0,
        "financial_stability_score": 85.5,
        "customer_satisfaction_score": 82.0,
        "completed_projects_count": 32,
        "average_delay_days": 25,
        "total_project_value": 12000000000,
        "website_url": "https://www.nakheel.com",
        "contact_email": "info@nakheel.com",
        "phone_number": "+971-4-390-3333",
        "address": "Palm Jumeirah, Dubai, UAE"
    },
    {
        "name": "Meraas",
        "established_year": 2007,
        "track_record_score": 92.5,
        "financial_stability_score": 89.0,
        "customer_satisfaction_score": 90.5,
        "completed_projects_count": 28,
        "average_delay_days": 12,
        "total_project_value": 8000000000,
        "website_url": "https://www.meraas.com",
        "contact_email": "info@meraas.com",
        "phone_number": "+971-4-317-7777",
        "address": "Dubai Design District, Dubai, UAE"
    },
    {
        "name": "Damac Properties",
        "established_year": 2002,
        "track_record_score": 85.0,
        "financial_stability_score": 87.5,
        "customer_satisfaction_score": 84.0,
        "completed_projects_count": 38,
        "average_delay_days": 30,
        "total_project_value": 10000000000,
        "website_url": "https://www.damacproperties.com",
        "contact_email": "info@damac.com",
        "phone_number": "+971-4-373-1111",
        "address": "Sheikh Zayed Road, Dubai, UAE"
    },
    {
        "name": "Sobha Realty",
        "established_year": 2005,
        "track_record_score": 90.0,
        "financial_stability_score": 91.0,
        "customer_satisfaction_score": 89.5,
        "completed_projects_count": 25,
        "average_delay_days": 18,
        "total_project_value": 6000000000,
        "website_url": "https://www.sobharealty.com",
        "contact_email": "info@sobharealty.com",
        "phone_number": "+971-4-377-2222",
        "address": "Dubai Silicon Oasis, Dubai, UAE"
    }
]

SAMPLE_PROJECTS = [
    {
        "name": "Burj Vista",
        "location": "Downtown Dubai",
        "latitude": 25.1972,
        "longitude": 55.2744,
        "price_range": "Premium",
        "total_units": 1200,
        "units_sold": 1080,
        "completion_date": "2024-06-15",
        "project_type": "Residential",
        "avg_price_per_sqft": 2500.0,
        "sales_percentage": 90.0,
        "vantage_score": 92.5,
        "progress": 95.0,
        "description": "Luxury residential towers with stunning Burj Khalifa views",
        "amenities": ["Swimming Pool", "Gym", "Spa", "Concierge", "Parking"],
        "payment_plan": "40/60",
        "handover_date": "2024-06-15"
    },
    {
        "name": "Palm Vista",
        "location": "Palm Jumeirah",
        "latitude": 25.1124,
        "longitude": 55.1390,
        "price_range": "Luxury",
        "total_units": 800,
        "units_sold": 720,
        "completion_date": "2024-08-20",
        "project_type": "Residential",
        "avg_price_per_sqft": 3500.0,
        "sales_percentage": 90.0,
        "vantage_score": 94.0,
        "progress": 88.0,
        "description": "Exclusive beachfront residences on Palm Jumeirah",
        "amenities": ["Private Beach", "Marina", "Golf Course", "Butler Service"],
        "payment_plan": "30/70",
        "handover_date": "2024-08-20"
    },
    {
        "name": "Dubai Hills Estate",
        "location": "Dubai Hills",
        "latitude": 25.0669,
        "longitude": 55.2458,
        "price_range": "Mid-Range",
        "total_units": 2000,
        "units_sold": 1800,
        "completion_date": "2024-12-10",
        "project_type": "Mixed",
        "avg_price_per_sqft": 1800.0,
        "sales_percentage": 90.0,
        "vantage_score": 88.5,
        "progress": 75.0,
        "description": "Family-friendly community with golf course and parks",
        "amenities": ["Golf Course", "Parks", "Schools", "Shopping Center"],
        "payment_plan": "50/50",
        "handover_date": "2024-12-10"
    },
    {
        "name": "Bluewaters Residences",
        "location": "Bluewaters Island",
        "latitude": 25.0789,
        "longitude": 55.1364,
        "price_range": "Luxury",
        "total_units": 600,
        "units_sold": 540,
        "completion_date": "2024-09-30",
        "project_type": "Residential",
        "avg_price_per_sqft": 3200.0,
        "sales_percentage": 90.0,
        "vantage_score": 91.0,
        "progress": 82.0,
        "description": "Premium island living with Ain Dubai views",
        "amenities": ["Private Beach", "Marina", "Restaurants", "Shopping"],
        "payment_plan": "35/65",
        "handover_date": "2024-09-30"
    },
    {
        "name": "Dubai Creek Harbour",
        "location": "Dubai Creek Harbour",
        "latitude": 25.1972,
        "longitude": 55.2744,
        "price_range": "Premium",
        "total_units": 1500,
        "units_sold": 1200,
        "completion_date": "2025-03-15",
        "project_type": "Mixed",
        "avg_price_per_sqft": 2800.0,
        "sales_percentage": 80.0,
        "vantage_score": 89.5,
        "progress": 65.0,
        "description": "Future-focused community with Creek Tower",
        "amenities": ["Creek Tower", "Marina", "Parks", "Shopping"],
        "payment_plan": "45/55",
        "handover_date": "2025-03-15"
    }
]

def generate_dld_transactions():
    """Generate sample DLD transactions"""
    locations = ["Dubai Marina", "Palm Jumeirah", "Downtown Dubai", "Dubai Hills", "Bluewaters Island", "Dubai Creek Harbour"]
    property_types = ["Apartment", "Villa", "Townhouse"]
    developers = ["Emaar Properties", "Nakheel", "Meraas", "Damac Properties", "Sobha Realty"]

    transactions = []
    base_date = date(2024, 1, 1)

    for i in range(100):  # Generate 100 transactions
        transaction_date = base_date + timedelta(days=random.randint(0, 365))
        location = random.choice(locations)
        property_type = random.choice(property_types)
        developer = random.choice(developers)

        # Generate realistic prices based on property type and location
        if property_type == "Villa":
            base_price = random.randint(3000000, 8000000)
        elif property_type == "Townhouse":
            base_price = random.randint(2000000, 5000000)
        else:  # Apartment
            base_price = random.randint(800000, 3000000)

        # Adjust price based on location
        if location in ["Palm Jumeirah", "Bluewaters Island"]:
            base_price *= 1.3
        elif location in ["Downtown Dubai", "Dubai Marina"]:
            base_price *= 1.2

        area_sqft = random.randint(800, 4000)
        base_price / area_sqft

        transaction = {
            "transaction_id": f"TXN{str(i+1).zfill(6)}",
            "property_type": property_type,
            "location": location,
            "transaction_date": transaction_date.isoformat(),
            "price_aed": base_price,
            "area_sqft": area_sqft,
            "developer_name": developer,
            "project_name": f"{location} Residences",
            "unit_number": f"#{random.randint(1, 1000)}",
            "floor_number": random.randint(1, 50),
            "bedrooms": random.randint(1, 5),
            "bathrooms": random.randint(1, 4),
            "parking_spaces": random.randint(0, 3)
        }
        transactions.append(transaction)

    return transactions

def seed_database():
    """Seed the database with sample data"""
    try:
        logger.info("Starting database seeding...")

        # Initialize database connection
        postgres_db.init_connection_pool()

        # Seed developers
        logger.info("Seeding developers...")
        developer_ids = []
        for developer_data in SAMPLE_DEVELOPERS:
            developer_id = postgres_db.create_developer(developer_data)
            if developer_id:
                developer_ids.append(developer_id)
                logger.info(f"Created developer: {developer_data['name']} (ID: {developer_id})")

        # Seed projects
        logger.info("Seeding projects...")
        for i, project_data in enumerate(SAMPLE_PROJECTS):
            if i < len(developer_ids):
                project_data["developer_id"] = developer_ids[i]
                project_id = postgres_db.create_project(project_data)
                if project_id:
                    logger.info(f"Created project: {project_data['name']} (ID: {project_id})")

        # Seed DLD transactions
        logger.info("Seeding DLD transactions...")
        dld_transactions = generate_dld_transactions()
        for transaction in dld_transactions:
            transaction_id = postgres_db.create_dld_transaction(transaction)
            if transaction_id:
                logger.info(f"Created DLD transaction: {transaction['transaction_id']}")

        logger.info("Database seeding completed successfully!")

        # Print summary
        print("\n=== Database Seeding Summary ===")
        print(f"Developers created: {len(developer_ids)}")
        print(f"Projects created: {len(SAMPLE_PROJECTS)}")
        print(f"DLD transactions created: {len(dld_transactions)}")
        print("===============================\n")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        # Close database connections
        postgres_db.close_connection_pool()

if __name__ == "__main__":
    seed_database()

"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theatrical productions and performances",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "lily@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums and techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivitiesEndpoint:
    """Test the GET /activities endpoint"""
    
    def test_get_all_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_activities_have_participants(self):
        """Test that some activities have participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) > 0
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]
    
    def test_signup_updates_participants_list(self):
        """Test that signup actually adds participant to list"""
        client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "newstudent@mergington.edu" in chess_club["participants"]
    
    def test_signup_nonexistent_activity(self):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_participants(self):
        """Test multiple participants can sign up for same activity"""
        client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        tennis_club = data["Tennis Club"]
        
        assert "student1@mergington.edu" in tennis_club["participants"]
        assert "student2@mergington.edu" in tennis_club["participants"]


class TestRemoveParticipantEndpoint:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant(self):
        """Test removing a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael%40mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
    
    def test_remove_updates_participants_list(self):
        """Test that removal actually removes participant"""
        client.delete(
            "/activities/Chess%20Club/participants/daniel%40mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "daniel@mergington.edu" not in chess_club["participants"]
    
    def test_remove_nonexistent_activity(self):
        """Test removing participant from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants/student%40mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_nonexistent_participant(self):
        """Test removing non-existent participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/nonexistent%40mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_then_remove_workflow(self):
        """Test complete workflow: signup then remove"""
        # Sign up
        signup_response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "john doe@mergington.edu"}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        get_response = client.get("/activities")
        data = get_response.json()
        assert "john doe@mergington.edu" in data["Basketball Team"]["participants"]
        
        # Remove
        remove_response = client.delete(
            "/activities/Basketball%20Team/participants/john%20doe%40mergington.edu"
        )
        assert remove_response.status_code == 200
        
        # Verify removed
        get_response = client.get("/activities")
        data = get_response.json()
        assert "john doe@mergington.edu" not in data["Basketball Team"]["participants"]
    
    def test_full_activity_workflow(self):
        """Test full activity interaction"""
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Drama Club"]["participants"])
        
        # Add 3 participants
        for i in range(3):
            client.post(
                "/activities/Drama%20Club/signup",
                params={"email": f"actor{i}@mergington.edu"}
            )
        
        # Check count increased
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Drama Club"]["participants"])
        assert updated_count == initial_count + 3
        
        # Remove one
        client.delete(
            "/activities/Drama%20Club/participants/actor0%40mergington.edu"
        )
        
        # Check count decreased
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Drama Club"]["participants"])
        assert final_count == updated_count - 1

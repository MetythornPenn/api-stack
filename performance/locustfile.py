# performance/locustfile.py
from typing import Dict, List, Optional

import json
import random
from uuid import uuid4

from locust import HttpUser, TaskSet, between, task

# Sample test data
TEST_USERNAMES = [f"testuser_{i}" for i in range(1, 11)]
TEST_PASSWORDS = "testpassword123"
TEST_ITEM_NAMES = [
    "Laptop", "Smartphone", "Headphones", "Monitor", "Keyboard", 
    "Mouse", "Tablet", "Camera", "Printer", "Speaker"
]
TEST_ITEM_DESCRIPTIONS = [
    "High-performance device", "Latest model", "Professional quality",
    "Best value", "Premium build", "Budget friendly", "Top rated",
    "Most popular", "New release", "Limited edition"
]


class ItemBehavior(TaskSet):
    """
    TaskSet for item-related operations.
    """
    def on_start(self):
        """Login before starting item operations."""
        self.login()
        self.item_ids = []
    
    def login(self):
        """Login to get access token."""
        username = random.choice(TEST_USERNAMES)
        
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": TEST_PASSWORDS,
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            self.username = username
        else:
            # Register if login fails
            self.register_and_login()
    
    def register_and_login(self):
        """Register a new user and login."""
        username = f"loadtest_{uuid4().hex[:8]}"
        
        # Register
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": TEST_PASSWORDS,
                "full_name": f"Load Test User {username}",
            },
        )
        
        if response.status_code == 201:
            # Login
            response = self.client.post(
                "/api/v1/auth/login",
                json={
                    "username": username,
                    "password": TEST_PASSWORDS,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                self.username = username
                TEST_USERNAMES.append(username)
    
    @task(2)
    def get_items(self):
        """Get list of items."""
        self.client.get("/api/v1/items")
    
    @task(1)
    def create_item(self):
        """Create a new item."""
        item_data = {
            "name": random.choice(TEST_ITEM_NAMES),
            "description": random.choice(TEST_ITEM_DESCRIPTIONS),
            "price": round(random.uniform(10.0, 1000.0), 2),
        }
        
        response = self.client.post("/api/v1/items", json=item_data)
        
        if response.status_code == 201:
            data = response.json()
            self.item_ids.append(data["id"])
    
    @task(3)
    def get_item(self):
        """Get a specific item."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            self.client.get(f"/api/v1/items/{item_id}")
    
    @task(1)
    def update_item(self):
        """Update an item."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            
            item_data = {
                "name": f"Updated {random.choice(TEST_ITEM_NAMES)}",
                "price": round(random.uniform(10.0, 1000.0), 2),
            }
            
            self.client.put(f"/api/v1/items/{item_id}", json=item_data)
    
    @task(1)
    def delete_item(self):
        """Delete an item."""
        if self.item_ids:
            item_id = random.choice(self.item_ids)
            
            response = self.client.delete(f"/api/v1/items/{item_id}")
            
            if response.status_code == 200:
                self.item_ids.remove(item_id)


class AuthBehavior(TaskSet):
    """
    TaskSet for authentication operations.
    """
    @task(3)
    def login(self):
        """Login task."""
        username = random.choice(TEST_USERNAMES)
        
        self.client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": TEST_PASSWORDS,
            },
        )
    
    @task(1)
    def register(self):
        """Register task."""
        username = f"loadtest_{uuid4().hex[:8]}"
        
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": TEST_PASSWORDS,
                "full_name": f"Load Test User {username}",
            },
        )
        
        if response.status_code == 201:
            TEST_USERNAMES.append(username)


class WebsiteUser(HttpUser):
    """
    Simulated user for load testing.
    """
    host = "http://localhost:8000"
    wait_time = between(1, 3)
    tasks = {
        ItemBehavior: 3,
        AuthBehavior: 1,
    }


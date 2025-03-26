
# scripts/create_dummy_data.py
import asyncio
import random
from typing import List, Optional
from uuid import UUID

import httpx
import typer
from pydantic import BaseModel, EmailStr

app = typer.Typer()

# Base URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Sample data
USERS = [
    {"username": "admin", "email": "admin@example.com", "password": "adminpassword", "is_superuser": True},
    {"username": "user1", "email": "user1@example.com", "password": "userpassword1"},
    {"username": "user2", "email": "user2@example.com", "password": "userpassword2"},
    {"username": "user3", "email": "user3@example.com", "password": "userpassword3"},
    {"username": "user4", "email": "user4@example.com", "password": "userpassword4"},
    {"username": "user5", "email": "user5@example.com", "password": "userpassword5"},
]

ITEMS = [
    {"name": "Laptop", "description": "High-performance laptop", "price": 1299.99},
    {"name": "Smartphone", "description": "Latest model smartphone", "price": 799.99},
    {"name": "Headphones", "description": "Noise-cancelling headphones", "price": 249.99},
    {"name": "Monitor", "description": "4K curved monitor", "price": 399.99},
    {"name": "Keyboard", "description": "Mechanical gaming keyboard", "price": 129.99},
    {"name": "Mouse", "description": "Wireless ergonomic mouse", "price": 59.99},
    {"name": "Tablet", "description": "10-inch tablet with stylus", "price": 499.99},
    {"name": "Camera", "description": "Digital mirrorless camera", "price": 899.99},
    {"name": "Printer", "description": "All-in-one color printer", "price": 199.99},
    {"name": "Speaker", "description": "Bluetooth portable speaker", "price": 149.99},
]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_superuser: bool = False


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


async def register_user(client: httpx.AsyncClient, user_data: dict) -> Optional[dict]:
    """Register a new user."""
    try:
        response = await client.post(
            f"{API_BASE_URL}/auth/register",
            json=user_data,
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to register user {user_data['username']}: {response.text}")
            return None
    except Exception as e:
        print(f"Error registering user {user_data['username']}: {e}")
        return None


async def login_user(client: httpx.AsyncClient, username: str, password: str) -> Optional[str]:
    """Login and get access token."""
    try:
        response = await client.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"Failed to login as {username}: {response.text}")
            return None
    except Exception as e:
        print(f"Error logging in as {username}: {e}")
        return None


async def create_item(
    client: httpx.AsyncClient,
    item_data: dict,
    token: str,
) -> Optional[dict]:
    """Create a new item."""
    try:
        response = await client.post(
            f"{API_BASE_URL}/items",
            json=item_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Failed to create item {item_data['name']}: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating item {item_data['name']}: {e}")
        return None


@app.command()
def create_data(
    num_users: int = typer.Option(len(USERS), help="Number of users to create"),
    num_items_per_user: int = typer.Option(5, help="Number of items per user"),
):
    """Create dummy data for testing."""
    asyncio.run(_create_data(num_users, num_items_per_user))


async def _create_data(num_users: int, num_items_per_user: int):
    """Async implementation of create_data."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register users
        print("Registering users...")
        users = []
        for i in range(min(num_users, len(USERS))):
            user = await register_user(client, USERS[i])
            if user:
                users.append(USERS[i])
                print(f"Registered user: {USERS[i]['username']}")
        
        # Create items for each user
        print("\nCreating items...")
        for user in users:
            # Login as user
            token = await login_user(client, user["username"], user["password"])
            
            if token:
                print(f"\nCreating items for user: {user['username']}")
                
                # Create items
                for _ in range(num_items_per_user):
                    item_data = random.choice(ITEMS)
                    item = await create_item(client, item_data, token)
                    
                    if item:
                        print(f"Created item: {item_data['name']}")
        
        print("\nDummy data creation completed!")


if __name__ == "__main__":
    app()


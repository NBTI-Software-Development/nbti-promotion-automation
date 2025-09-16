import pytest
import json
from src.models.user import User, Role, db
from werkzeug.security import generate_password_hash


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
    
    def test_register_duplicate_username(self, client, app):
        """Test registration with duplicate username."""
        # Create first user
        client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'first@example.com',
            'first_name': 'First',
            'last_name': 'User',
            'password': 'pass123'
        })
        
        # Try to create second user with same username
        response = client.post('/api/auth/register', json={
            'username': 'duplicate',
            'email': 'second@example.com',
            'first_name': 'Second',
            'last_name': 'User',
            'password': 'pass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'username' in data['error'].lower()
    
    def test_register_duplicate_email(self, client, app):
        """Test registration with duplicate email."""
        # Create first user
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'duplicate@example.com',
            'first_name': 'First',
            'last_name': 'User',
            'password': 'pass123'
        })
        
        # Try to create second user with same email
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'first_name': 'Second',
            'last_name': 'User',
            'password': 'pass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data."""
        # Missing required fields
        response = client.post('/api/auth/register', json={
            'username': 'incomplete'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_success(self, client, app):
        """Test successful login."""
        # Create a user first
        with app.app_context():
            staff_role = Role.query.filter_by(name='Staff Member').first()
            user = User(
                username='loginuser',
                email='login@example.com',
                first_name='Login',
                last_name='User',
                password_hash=generate_password_hash('loginpass123')
            )
            user.roles.append(staff_role)
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'loginpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'loginuser'
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower()
    
    def test_login_invalid_password(self, client, app):
        """Test login with invalid password."""
        # Create a user first
        with app.app_context():
            staff_role = Role.query.filter_by(name='Staff Member').first()
            user = User(
                username='wrongpass',
                email='wrongpass@example.com',
                first_name='Wrong',
                last_name='Pass',
                password_hash=generate_password_hash('correctpass123')
            )
            user.roles.append(staff_role)
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'wrongpass',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower()
    
    def test_login_missing_data(self, client):
        """Test login with missing data."""
        response = client.post('/api/auth/login', json={
            'username': 'incomplete'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'msg' in data
    
    def test_logout(self, client, auth_headers):
        """Test user logout."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'logged out' in data['message'].lower()
    
    def test_change_password_success(self, client, auth_headers, app):
        """Test successful password change."""
        response = client.post('/api/auth/change-password', 
                             headers=auth_headers,
                             json={
                                 'current_password': 'testpass123',
                                 'new_password': 'newtestpass123'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'changed' in data['message'].lower()
        
        # Verify new password works
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'newtestpass123'
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password."""
        response = client.post('/api/auth/change-password', 
                             headers=auth_headers,
                             json={
                                 'current_password': 'wrongpassword',
                                 'new_password': 'newtestpass123'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'current password' in data['error'].lower()
    
    def test_change_password_unauthorized(self, client):
        """Test password change without authentication."""
        response = client.post('/api/auth/change-password', 
                             json={
                                 'current_password': 'testpass123',
                                 'new_password': 'newtestpass123'
                             })
        
        assert response.status_code == 401


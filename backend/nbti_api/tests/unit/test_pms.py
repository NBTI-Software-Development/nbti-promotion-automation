import pytest
import json
from datetime import datetime
from src.models.user import User, Role, db
from src.models.pms import Evaluation, Goal


class TestPMSEndpoints:
    """Test PMS (Performance Management System) endpoints."""
    
    def test_get_dashboard_success(self, client, auth_headers):
        """Test successful dashboard retrieval."""
        response = client.get('/api/pms/dashboard', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'stats' in data
        assert 'total_evaluations' in data['stats']
        assert 'completed_evaluations' in data['stats']
        assert 'active_goals' in data['stats']
    
    def test_get_dashboard_unauthorized(self, client):
        """Test dashboard access without authentication."""
        response = client.get('/api/pms/dashboard')
        
        assert response.status_code == 401
    
    def test_create_evaluation_success(self, client, auth_headers):
        """Test successful evaluation creation."""
        response = client.post('/api/pms/evaluations', 
                             headers=auth_headers,
                             json={
                                 'quarter': 'Q1',
                                 'year': 2024,
                                 'goals': [
                                     {
                                         'description': 'Complete project A',
                                         'target': 'Finish by end of quarter',
                                         'weight': 1.0
                                     }
                                 ]
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'evaluation' in data
        assert data['evaluation']['quarter'] == 'Q1'
        assert data['evaluation']['year'] == 2024
        assert len(data['evaluation']['goals']) == 1
    
    def test_create_evaluation_invalid_data(self, client, auth_headers):
        """Test evaluation creation with invalid data."""
        response = client.post('/api/pms/evaluations', 
                             headers=auth_headers,
                             json={
                                 'quarter': 'Q1'
                                 # Missing year and goals
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_evaluations_success(self, client, auth_headers, sample_evaluation):
        """Test successful evaluations retrieval."""
        response = client.get('/api/pms/evaluations', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'evaluations' in data
        assert isinstance(data['evaluations'], list)
    
    def test_get_evaluation_by_id_success(self, client, auth_headers, sample_evaluation):
        """Test successful evaluation retrieval by ID."""
        response = client.get(f'/api/pms/evaluations/{sample_evaluation.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'evaluation' in data
        assert data['evaluation']['id'] == sample_evaluation.id
    
    def test_get_evaluation_by_id_not_found(self, client, auth_headers):
        """Test evaluation retrieval with non-existent ID."""
        response = client.get('/api/pms/evaluations/999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_update_evaluation_success(self, client, auth_headers, sample_evaluation):
        """Test successful evaluation update."""
        response = client.put(f'/api/pms/evaluations/{sample_evaluation.id}', 
                            headers=auth_headers,
                            json={
                                'status': 'Completed',
                                'final_score': 4.5
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'evaluation' in data
        assert data['evaluation']['status'] == 'Completed'
        assert data['evaluation']['final_score'] == 4.5
    
    def test_add_goal_success(self, client, auth_headers, sample_evaluation):
        """Test successful goal addition to evaluation."""
        response = client.post(f'/api/pms/evaluations/{sample_evaluation.id}/goals', 
                             headers=auth_headers,
                             json={
                                 'description': 'New goal',
                                 'target': 'Achieve target by deadline',
                                 'weight': 1.0
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'goal' in data
        assert data['goal']['description'] == 'New goal'
        assert data['goal']['evaluation_id'] == sample_evaluation.id
    
    def test_update_goal_success(self, client, auth_headers, sample_goal):
        """Test successful goal update."""
        response = client.put(f'/api/pms/goals/{sample_goal.id}', 
                            headers=auth_headers,
                            json={
                                'staff_rating': 4,
                                'staff_comment': 'Goal completed successfully'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'goal' in data
        assert data['goal']['staff_rating'] == 4
        assert data['goal']['staff_comment'] == 'Goal completed successfully'
    
    def test_supervisor_rate_goal_success(self, client, admin_headers, sample_goal):
        """Test successful supervisor rating of goal."""
        response = client.put(f'/api/pms/goals/{sample_goal.id}/supervisor-rating', 
                            headers=admin_headers,
                            json={
                                'supervisor_rating': 5,
                                'supervisor_comment': 'Excellent work'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'goal' in data
        assert data['goal']['supervisor_rating'] == 5
        assert data['goal']['supervisor_comment'] == 'Excellent work'
    
    def test_supervisor_rate_goal_unauthorized(self, client, auth_headers, sample_goal):
        """Test supervisor rating without proper permissions."""
        response = client.put(f'/api/pms/goals/{sample_goal.id}/supervisor-rating', 
                            headers=auth_headers,
                            json={
                                'supervisor_rating': 5,
                                'supervisor_comment': 'Excellent work'
                            })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_agree_goal_success(self, client, auth_headers, sample_goal):
        """Test successful goal agreement."""
        response = client.post(f'/api/pms/goals/{sample_goal.id}/agree', 
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'goal' in data
        assert data['goal']['agreed'] is True
    
    def test_delete_goal_success(self, client, auth_headers, sample_goal):
        """Test successful goal deletion."""
        response = client.delete(f'/api/pms/goals/{sample_goal.id}', 
                               headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'deleted' in data['message'].lower()
    
    def test_get_team_evaluations_success(self, client, admin_headers):
        """Test successful team evaluations retrieval for supervisors."""
        response = client.get('/api/pms/team/evaluations', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'evaluations' in data
        assert isinstance(data['evaluations'], list)
    
    def test_get_team_evaluations_unauthorized(self, client, auth_headers):
        """Test team evaluations access without supervisor permissions."""
        response = client.get('/api/pms/team/evaluations', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_get_reports_success(self, client, admin_headers):
        """Test successful reports retrieval."""
        response = client.get('/api/pms/reports', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'reports' in data
    
    def test_get_analytics_success(self, client, admin_headers):
        """Test successful analytics retrieval."""
        response = client.get('/api/pms/analytics', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'analytics' in data
    
    def test_evaluation_workflow_complete(self, client, auth_headers, admin_headers):
        """Test complete evaluation workflow from creation to completion."""
        # 1. Create evaluation
        create_response = client.post('/api/pms/evaluations', 
                                    headers=auth_headers,
                                    json={
                                        'quarter': 'Q2',
                                        'year': 2024,
                                        'goals': [
                                            {
                                                'description': 'Workflow test goal',
                                                'target': 'Complete workflow test',
                                                'weight': 1.0
                                            }
                                        ]
                                    })
        
        assert create_response.status_code == 201
        evaluation_id = create_response.get_json()['evaluation']['id']
        goal_id = create_response.get_json()['evaluation']['goals'][0]['id']
        
        # 2. Staff rates goal
        staff_rate_response = client.put(f'/api/pms/goals/{goal_id}', 
                                       headers=auth_headers,
                                       json={
                                           'staff_rating': 4,
                                           'staff_comment': 'Goal achieved'
                                       })
        
        assert staff_rate_response.status_code == 200
        
        # 3. Supervisor rates goal
        supervisor_rate_response = client.put(f'/api/pms/goals/{goal_id}/supervisor-rating', 
                                            headers=admin_headers,
                                            json={
                                                'supervisor_rating': 5,
                                                'supervisor_comment': 'Excellent performance'
                                            })
        
        assert supervisor_rate_response.status_code == 200
        
        # 4. Complete evaluation
        complete_response = client.put(f'/api/pms/evaluations/{evaluation_id}', 
                                     headers=admin_headers,
                                     json={
                                         'status': 'Completed',
                                         'final_score': 4.5
                                     })
        
        assert complete_response.status_code == 200
        final_evaluation = complete_response.get_json()['evaluation']
        assert final_evaluation['status'] == 'Completed'
        assert final_evaluation['final_score'] == 4.5


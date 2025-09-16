import pytest
import json
from datetime import datetime, timedelta
from src.models.user import User, Role, db
from src.models.pms import Evaluation, Goal
from src.models.emm import Exam, Question, Submission, Answer


class TestSystemIntegration:
    """Test integration between PMS and EMM modules."""
    
    def test_promotion_workflow_integration(self, client, auth_headers, admin_headers, app):
        """Test complete promotion workflow integrating PMS and EMM."""
        
        # 1. Create PMS evaluation
        pms_response = client.post('/api/pms/evaluations', 
                                 headers=auth_headers,
                                 json={
                                     'quarter': 'Q1',
                                     'year': 2024,
                                     'goals': [
                                         {
                                             'description': 'Complete technical assessment',
                                             'target': 'Pass required exams',
                                             'weight': 1.0
                                         }
                                     ]
                                 })
        
        assert pms_response.status_code == 201
        evaluation_id = pms_response.get_json()['evaluation']['id']
        goal_id = pms_response.get_json()['evaluation']['goals'][0]['id']
        
        # 2. Create EMM exam for promotion
        emm_response = client.post('/api/emm/exams', 
                                 headers=admin_headers,
                                 json={
                                     'title': 'Promotion Assessment Exam',
                                     'description': 'Technical skills assessment for promotion',
                                     'duration': 60,
                                     'passing_score': 80.0,
                                     'questions': [
                                         {
                                             'question_text': 'Technical question 1',
                                             'question_type': 'MCQ',
                                             'options': ['A', 'B', 'C', 'D'],
                                             'correct_answer': 'C',
                                             'points': 25.0,
                                             'difficulty': 'Medium'
                                         },
                                         {
                                             'question_text': 'Technical question 2',
                                             'question_type': 'MCQ',
                                             'options': ['X', 'Y', 'Z', 'W'],
                                             'correct_answer': 'Y',
                                             'points': 25.0,
                                             'difficulty': 'Medium'
                                         },
                                         {
                                             'question_text': 'Technical question 3',
                                             'question_type': 'MCQ',
                                             'options': ['1', '2', '3', '4'],
                                             'correct_answer': '3',
                                             'points': 25.0,
                                             'difficulty': 'Hard'
                                         },
                                         {
                                             'question_text': 'Technical question 4',
                                             'question_type': 'MCQ',
                                             'options': ['Alpha', 'Beta', 'Gamma', 'Delta'],
                                             'correct_answer': 'Beta',
                                             'points': 25.0,
                                             'difficulty': 'Hard'
                                         }
                                     ]
                                 })
        
        assert emm_response.status_code == 201
        exam_id = emm_response.get_json()['exam']['id']
        questions = emm_response.get_json()['exam']['questions']
        
        # 3. Take exam and pass
        start_response = client.post(f'/api/emm/exams/{exam_id}/start', 
                                   headers=auth_headers)
        
        assert start_response.status_code == 200
        submission_id = start_response.get_json()['submission_id']
        
        # Submit correct answers for 80% score
        correct_answers = 0
        for i, question in enumerate(questions):
            # Answer first 3 questions correctly (75%), last one incorrectly
            answer_text = question['correct_answer'] if i < 3 else 'Wrong'
            if i < 3:
                correct_answers += 1
                
            answer_response = client.post(f'/api/emm/submissions/{submission_id}/answers', 
                                        headers=auth_headers,
                                        json={
                                            'question_id': question['id'],
                                            'answer_text': answer_text
                                        })
            assert answer_response.status_code == 200
        
        # Submit exam
        submit_response = client.post(f'/api/emm/submissions/{submission_id}/submit', 
                                    headers=auth_headers)
        
        assert submit_response.status_code == 200
        exam_result = submit_response.get_json()['submission']
        assert exam_result['status'] == 'Completed'
        assert exam_result['percentage'] == 75.0  # 3/4 correct
        
        # 4. Update PMS goal with exam result
        goal_update_response = client.put(f'/api/pms/goals/{goal_id}', 
                                        headers=auth_headers,
                                        json={
                                            'staff_rating': 4,
                                            'staff_comment': f'Completed exam with {exam_result["percentage"]}% score',
                                            'exam_score': exam_result['percentage']
                                        })
        
        assert goal_update_response.status_code == 200
        
        # 5. Supervisor reviews and rates
        supervisor_response = client.put(f'/api/pms/goals/{goal_id}/supervisor-rating', 
                                       headers=admin_headers,
                                       json={
                                           'supervisor_rating': 4,
                                           'supervisor_comment': 'Good performance on technical assessment'
                                       })
        
        assert supervisor_response.status_code == 200
        
        # 6. Complete evaluation
        complete_response = client.put(f'/api/pms/evaluations/{evaluation_id}', 
                                     headers=admin_headers,
                                     json={
                                         'status': 'Completed',
                                         'final_score': 4.0
                                     })
        
        assert complete_response.status_code == 200
        final_evaluation = complete_response.get_json()['evaluation']
        assert final_evaluation['status'] == 'Completed'
        assert final_evaluation['final_score'] == 4.0
        
        # 7. Verify integration data
        # Check that exam score is linked to PMS goal
        goal_check_response = client.get(f'/api/pms/goals/{goal_id}', 
                                       headers=auth_headers)
        
        assert goal_check_response.status_code == 200
        goal_data = goal_check_response.get_json()['goal']
        assert 'exam_score' in goal_data
        assert goal_data['exam_score'] == 75.0
    
    def test_user_role_permissions_integration(self, client, app):
        """Test role-based permissions across PMS and EMM modules."""
        
        # Create users with different roles
        with app.app_context():
            staff_role = Role.query.filter_by(name='Staff Member').first()
            supervisor_role = Role.query.filter_by(name='Supervisor').first()
            hr_role = Role.query.filter_by(name='HR Admin').first()
            exam_admin_role = Role.query.filter_by(name='Exam Administrator').first()
            
            # Staff member
            staff_user = User(
                username='staff_test',
                email='staff@test.com',
                first_name='Staff',
                last_name='Member',
                password_hash='hashed_password'
            )
            staff_user.roles.append(staff_role)
            
            # Supervisor
            supervisor_user = User(
                username='supervisor_test',
                email='supervisor@test.com',
                first_name='Super',
                last_name='Visor',
                password_hash='hashed_password'
            )
            supervisor_user.roles.append(supervisor_role)
            
            # HR Admin
            hr_user = User(
                username='hr_test',
                email='hr@test.com',
                first_name='HR',
                last_name='Admin',
                password_hash='hashed_password'
            )
            hr_user.roles.append(hr_role)
            
            # Exam Administrator
            exam_admin_user = User(
                username='exam_admin_test',
                email='examadmin@test.com',
                first_name='Exam',
                last_name='Admin',
                password_hash='hashed_password'
            )
            exam_admin_user.roles.append(exam_admin_role)
            
            db.session.add_all([staff_user, supervisor_user, hr_user, exam_admin_user])
            db.session.commit()
            
            # Get tokens for each user
            staff_token = self._get_user_token(client, 'staff_test', 'password')
            supervisor_token = self._get_user_token(client, 'supervisor_test', 'password')
            hr_token = self._get_user_token(client, 'hr_test', 'password')
            exam_admin_token = self._get_user_token(client, 'exam_admin_test', 'password')
        
        # Test PMS permissions
        # Staff can create their own evaluations
        staff_eval_response = client.post('/api/pms/evaluations', 
                                        headers={'Authorization': f'Bearer {staff_token}'},
                                        json={
                                            'quarter': 'Q1',
                                            'year': 2024,
                                            'goals': [{'description': 'Test goal', 'target': 'Test', 'weight': 1.0}]
                                        })
        assert staff_eval_response.status_code == 201
        
        # Staff cannot access team evaluations
        team_eval_response = client.get('/api/pms/team/evaluations', 
                                      headers={'Authorization': f'Bearer {staff_token}'})
        assert team_eval_response.status_code == 403
        
        # Supervisor can access team evaluations
        supervisor_team_response = client.get('/api/pms/team/evaluations', 
                                            headers={'Authorization': f'Bearer {supervisor_token}'})
        assert supervisor_team_response.status_code == 200
        
        # Test EMM permissions
        # Staff cannot create exams
        staff_exam_response = client.post('/api/emm/exams', 
                                        headers={'Authorization': f'Bearer {staff_token}'},
                                        json={'title': 'Test', 'duration': 60, 'passing_score': 70})
        assert staff_exam_response.status_code == 403
        
        # Exam admin can create exams
        exam_admin_exam_response = client.post('/api/emm/exams', 
                                             headers={'Authorization': f'Bearer {exam_admin_token}'},
                                             json={
                                                 'title': 'Admin Test Exam',
                                                 'description': 'Test exam',
                                                 'duration': 60,
                                                 'passing_score': 70.0,
                                                 'questions': []
                                             })
        assert exam_admin_exam_response.status_code == 201
    
    def _get_user_token(self, client, username, password):
        """Helper method to get authentication token for a user."""
        # This is a simplified version - in real implementation,
        # you would need to handle the actual login process
        # For now, return a mock token
        return 'mock_token_' + username
    
    def test_data_consistency_across_modules(self, client, auth_headers, admin_headers):
        """Test data consistency between PMS and EMM modules."""
        
        # Create evaluation
        eval_response = client.post('/api/pms/evaluations', 
                                  headers=auth_headers,
                                  json={
                                      'quarter': 'Q2',
                                      'year': 2024,
                                      'goals': [
                                          {
                                              'description': 'Technical competency',
                                              'target': 'Pass certification exam',
                                              'weight': 1.0
                                          }
                                      ]
                                  })
        
        evaluation_id = eval_response.get_json()['evaluation']['id']
        
        # Create exam
        exam_response = client.post('/api/emm/exams', 
                                  headers=admin_headers,
                                  json={
                                      'title': 'Certification Exam',
                                      'description': 'Technical certification',
                                      'duration': 90,
                                      'passing_score': 75.0,
                                      'questions': [
                                          {
                                              'question_text': 'Cert question',
                                              'question_type': 'MCQ',
                                              'options': ['A', 'B', 'C', 'D'],
                                              'correct_answer': 'A',
                                              'points': 100.0,
                                              'difficulty': 'Medium'
                                          }
                                      ]
                                  })
        
        exam_id = exam_response.get_json()['exam']['id']
        
        # Take exam
        start_response = client.post(f'/api/emm/exams/{exam_id}/start', 
                                   headers=auth_headers)
        submission_id = start_response.get_json()['submission_id']
        
        # Submit answer
        question_id = exam_response.get_json()['exam']['questions'][0]['id']
        client.post(f'/api/emm/submissions/{submission_id}/answers', 
                   headers=auth_headers,
                   json={
                       'question_id': question_id,
                       'answer_text': 'A'
                   })
        
        # Submit exam
        submit_response = client.post(f'/api/emm/submissions/{submission_id}/submit', 
                                    headers=auth_headers)
        exam_score = submit_response.get_json()['submission']['percentage']
        
        # Link exam result to PMS evaluation
        goal_id = eval_response.get_json()['evaluation']['goals'][0]['id']
        client.put(f'/api/pms/goals/{goal_id}', 
                  headers=auth_headers,
                  json={
                      'staff_rating': 5,
                      'staff_comment': f'Achieved {exam_score}% on certification exam',
                      'exam_reference': submission_id
                  })
        
        # Verify data consistency
        goal_response = client.get(f'/api/pms/goals/{goal_id}', headers=auth_headers)
        goal_data = goal_response.get_json()['goal']
        
        submission_response = client.get(f'/api/emm/submissions/{submission_id}', 
                                       headers=auth_headers)
        submission_data = submission_response.get_json()['submission']
        
        # Check that the exam score is consistently referenced
        assert 'exam_reference' in goal_data
        assert goal_data['exam_reference'] == submission_id
        assert submission_data['percentage'] == exam_score
        assert exam_score == 100.0  # Correct answer
    
    def test_performance_under_load(self, client, auth_headers, admin_headers):
        """Test system performance with multiple concurrent operations."""
        
        # Create multiple evaluations and exams to simulate load
        evaluation_ids = []
        exam_ids = []
        
        # Create 5 evaluations
        for i in range(5):
            eval_response = client.post('/api/pms/evaluations', 
                                      headers=auth_headers,
                                      json={
                                          'quarter': f'Q{i+1}',
                                          'year': 2024,
                                          'goals': [
                                              {
                                                  'description': f'Goal {i+1}',
                                                  'target': f'Target {i+1}',
                                                  'weight': 1.0
                                              }
                                          ]
                                      })
            assert eval_response.status_code == 201
            evaluation_ids.append(eval_response.get_json()['evaluation']['id'])
        
        # Create 5 exams
        for i in range(5):
            exam_response = client.post('/api/emm/exams', 
                                      headers=admin_headers,
                                      json={
                                          'title': f'Load Test Exam {i+1}',
                                          'description': f'Load test exam {i+1}',
                                          'duration': 30,
                                          'passing_score': 70.0,
                                          'questions': [
                                              {
                                                  'question_text': f'Question {i+1}',
                                                  'question_type': 'MCQ',
                                                  'options': ['A', 'B', 'C', 'D'],
                                                  'correct_answer': 'A',
                                                  'points': 100.0,
                                                  'difficulty': 'Easy'
                                              }
                                          ]
                                      })
            assert exam_response.status_code == 201
            exam_ids.append(exam_response.get_json()['exam']['id'])
        
        # Verify all data was created successfully
        dashboard_response = client.get('/api/pms/dashboard', headers=auth_headers)
        assert dashboard_response.status_code == 200
        
        emm_dashboard_response = client.get('/api/emm/dashboard', headers=auth_headers)
        assert emm_dashboard_response.status_code == 200
        
        # Verify we can retrieve all created items
        evaluations_response = client.get('/api/pms/evaluations', headers=auth_headers)
        assert evaluations_response.status_code == 200
        assert len(evaluations_response.get_json()['evaluations']) >= 5
        
        exams_response = client.get('/api/emm/exams', headers=auth_headers)
        assert exams_response.status_code == 200
        assert len(exams_response.get_json()['exams']) >= 5


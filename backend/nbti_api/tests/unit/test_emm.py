import pytest
import json
from datetime import datetime, timedelta
from src.models.user import User, Role, db
from src.models.emm import Exam, Question, Submission, Answer


class TestEMMEndpoints:
    """Test EMM (Exam Management Module) endpoints."""
    
    def test_get_dashboard_success(self, client, auth_headers):
        """Test successful EMM dashboard retrieval."""
        response = client.get('/api/emm/dashboard', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'stats' in data
        assert 'available_exams' in data['stats']
        assert 'completed_exams' in data['stats']
    
    def test_get_exams_success(self, client, auth_headers, sample_exam):
        """Test successful exams retrieval."""
        response = client.get('/api/emm/exams', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'exams' in data
        assert isinstance(data['exams'], list)
        assert len(data['exams']) >= 1
    
    def test_get_exam_by_id_success(self, client, auth_headers, sample_exam):
        """Test successful exam retrieval by ID."""
        response = client.get(f'/api/emm/exams/{sample_exam.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'exam' in data
        assert data['exam']['id'] == sample_exam.id
        assert data['exam']['title'] == sample_exam.title
    
    def test_get_exam_by_id_not_found(self, client, auth_headers):
        """Test exam retrieval with non-existent ID."""
        response = client.get('/api/emm/exams/999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_start_exam_success(self, client, auth_headers, sample_exam, sample_question):
        """Test successful exam start."""
        response = client.post(f'/api/emm/exams/{sample_exam.id}/start', 
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'submission_id' in data
        assert 'message' in data
        assert 'started' in data['message'].lower()
    
    def test_start_exam_not_found(self, client, auth_headers):
        """Test starting non-existent exam."""
        response = client.post('/api/emm/exams/999/start', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_submission_success(self, client, auth_headers, sample_submission):
        """Test successful submission retrieval."""
        response = client.get(f'/api/emm/submissions/{sample_submission.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'submission' in data
        assert data['submission']['id'] == sample_submission.id
    
    def test_submit_answer_success(self, client, auth_headers, sample_submission, sample_question):
        """Test successful answer submission."""
        response = client.post(f'/api/emm/submissions/{sample_submission.id}/answers', 
                             headers=auth_headers,
                             json={
                                 'question_id': sample_question.id,
                                 'answer_text': 'Hello World'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'answer' in data
        assert data['answer']['question_id'] == sample_question.id
        assert data['answer']['answer_text'] == 'Hello World'
    
    def test_submit_answer_invalid_question(self, client, auth_headers, sample_submission):
        """Test answer submission with invalid question ID."""
        response = client.post(f'/api/emm/submissions/{sample_submission.id}/answers', 
                             headers=auth_headers,
                             json={
                                 'question_id': 999,
                                 'answer_text': 'Some answer'
                             })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_submit_exam_success(self, client, auth_headers, app, sample_submission, sample_question):
        """Test successful exam submission."""
        # First submit an answer
        with app.app_context():
            answer = Answer(
                submission_id=sample_submission.id,
                question_id=sample_question.id,
                answer_text='Hello World'
            )
            db.session.add(answer)
            db.session.commit()
        
        response = client.post(f'/api/emm/submissions/{sample_submission.id}/submit', 
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'submission' in data
        assert data['submission']['status'] == 'Completed'
        assert 'percentage' in data['submission']
    
    def test_submit_exam_not_found(self, client, auth_headers):
        """Test submitting non-existent submission."""
        response = client.post('/api/emm/submissions/999/submit', 
                             headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_results_success(self, client, auth_headers):
        """Test successful results retrieval."""
        response = client.get('/api/emm/results', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data
        assert isinstance(data['results'], list)
    
    def test_create_exam_success(self, client, admin_headers):
        """Test successful exam creation by admin."""
        response = client.post('/api/emm/exams', 
                             headers=admin_headers,
                             json={
                                 'title': 'New Test Exam',
                                 'description': 'A test exam for testing',
                                 'duration': 90,
                                 'passing_score': 75.0,
                                 'questions': [
                                     {
                                         'question_text': 'What is 2+2?',
                                         'question_type': 'MCQ',
                                         'options': ['3', '4', '5', '6'],
                                         'correct_answer': '4',
                                         'points': 10.0,
                                         'difficulty': 'Easy'
                                     }
                                 ]
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'exam' in data
        assert data['exam']['title'] == 'New Test Exam'
        assert len(data['exam']['questions']) == 1
    
    def test_create_exam_unauthorized(self, client, auth_headers):
        """Test exam creation without admin permissions."""
        response = client.post('/api/emm/exams', 
                             headers=auth_headers,
                             json={
                                 'title': 'Unauthorized Exam',
                                 'description': 'Should not be created',
                                 'duration': 60,
                                 'passing_score': 70.0
                             })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_update_exam_success(self, client, admin_headers, sample_exam):
        """Test successful exam update by admin."""
        response = client.put(f'/api/emm/exams/{sample_exam.id}', 
                            headers=admin_headers,
                            json={
                                'title': 'Updated Exam Title',
                                'duration': 120,
                                'status': 'Draft'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'exam' in data
        assert data['exam']['title'] == 'Updated Exam Title'
        assert data['exam']['duration'] == 120
        assert data['exam']['status'] == 'Draft'
    
    def test_delete_exam_success(self, client, admin_headers, sample_exam):
        """Test successful exam deletion by admin."""
        response = client.delete(f'/api/emm/exams/{sample_exam.id}', 
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'deleted' in data['message'].lower()
    
    def test_get_question_bank_success(self, client, admin_headers):
        """Test successful question bank retrieval."""
        response = client.get('/api/emm/questions', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'questions' in data
        assert isinstance(data['questions'], list)
    
    def test_create_question_success(self, client, admin_headers):
        """Test successful question creation."""
        response = client.post('/api/emm/questions', 
                             headers=admin_headers,
                             json={
                                 'question_text': 'What is the capital of France?',
                                 'question_type': 'MCQ',
                                 'options': ['London', 'Berlin', 'Paris', 'Madrid'],
                                 'correct_answer': 'Paris',
                                 'points': 5.0,
                                 'difficulty': 'Easy',
                                 'category': 'Geography'
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'question' in data
        assert data['question']['question_text'] == 'What is the capital of France?'
        assert data['question']['correct_answer'] == 'Paris'
    
    def test_update_question_success(self, client, admin_headers, sample_question):
        """Test successful question update."""
        response = client.put(f'/api/emm/questions/{sample_question.id}', 
                            headers=admin_headers,
                            json={
                                'question_text': 'Updated question text',
                                'points': 15.0,
                                'difficulty': 'Medium'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'question' in data
        assert data['question']['question_text'] == 'Updated question text'
        assert data['question']['points'] == 15.0
        assert data['question']['difficulty'] == 'Medium'
    
    def test_delete_question_success(self, client, admin_headers, sample_question):
        """Test successful question deletion."""
        response = client.delete(f'/api/emm/questions/{sample_question.id}', 
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'deleted' in data['message'].lower()
    
    def test_exam_workflow_complete(self, client, auth_headers, admin_headers, app):
        """Test complete exam workflow from creation to submission."""
        # 1. Create exam with questions
        create_response = client.post('/api/emm/exams', 
                                    headers=admin_headers,
                                    json={
                                        'title': 'Workflow Test Exam',
                                        'description': 'Complete workflow test',
                                        'duration': 30,
                                        'passing_score': 70.0,
                                        'questions': [
                                            {
                                                'question_text': 'Test question 1',
                                                'question_type': 'MCQ',
                                                'options': ['A', 'B', 'C', 'D'],
                                                'correct_answer': 'B',
                                                'points': 50.0,
                                                'difficulty': 'Easy'
                                            },
                                            {
                                                'question_text': 'Test question 2',
                                                'question_type': 'MCQ',
                                                'options': ['X', 'Y', 'Z', 'W'],
                                                'correct_answer': 'Y',
                                                'points': 50.0,
                                                'difficulty': 'Easy'
                                            }
                                        ]
                                    })
        
        assert create_response.status_code == 201
        exam_id = create_response.get_json()['exam']['id']
        questions = create_response.get_json()['exam']['questions']
        
        # 2. Start exam
        start_response = client.post(f'/api/emm/exams/{exam_id}/start', 
                                   headers=auth_headers)
        
        assert start_response.status_code == 200
        submission_id = start_response.get_json()['submission_id']
        
        # 3. Submit answers
        for question in questions:
            answer_response = client.post(f'/api/emm/submissions/{submission_id}/answers', 
                                        headers=auth_headers,
                                        json={
                                            'question_id': question['id'],
                                            'answer_text': question['correct_answer']
                                        })
            assert answer_response.status_code == 200
        
        # 4. Submit exam
        submit_response = client.post(f'/api/emm/submissions/{submission_id}/submit', 
                                    headers=auth_headers)
        
        assert submit_response.status_code == 200
        final_submission = submit_response.get_json()['submission']
        assert final_submission['status'] == 'Completed'
        assert final_submission['percentage'] == 100.0  # All correct answers
        assert final_submission['percentage'] >= 70.0  # Passed


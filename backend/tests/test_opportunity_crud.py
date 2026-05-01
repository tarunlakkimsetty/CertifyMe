import unittest
from app import create_app
from config import Config
from extensions import db


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    JWT_SECRET_KEY = 'test-secret-key-for-jwt-0123456789abcdefgh'


class OpportunityCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def signup(self, full_name, email, password):
        return self.client.post(
            '/auth/signup',
            json={
                'full_name': full_name,
                'email': email,
                'password': password,
                'confirm_password': password,
            },
        )

    def login(self, email, password):
        return self.client.post(
            '/auth/login',
            json={'email': email, 'password': password, 'remember_me': False},
        )

    def test_opportunity_crud_lifecycle(self):
        signup_resp = self.signup('Opportunity Admin', 'opportunity@test.com', 'Password123!')
        self.assertEqual(signup_resp.status_code, 200)

        login_resp = self.login('opportunity@test.com', 'Password123!')
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        create_resp = self.client.post(
            '/opportunities',
            json={
                'name': 'Full Stack Internship',
                'duration': '3 months',
                'start_date': '2026-06-01',
                'description': 'Learn full stack development',
                'skills': 'React,Node,SQL',
                'category': 'Technology',
                'future_opportunities': 'Full-time role',
                'max_applicants': 100,
            },
            headers=headers,
        )
        self.assertEqual(create_resp.status_code, 201)
        data = create_resp.get_json()['data']
        self.assertEqual(data['name'], 'Full Stack Internship')
        self.assertEqual(data['max_applicants'], 100)

        opp_id = data['id']

        list_resp = self.client.get('/opportunities', headers=headers)
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.get_json()['data']), 1)

        get_resp = self.client.get(f'/opportunities/{opp_id}', headers=headers)
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.get_json()['data']['id'], opp_id)

        update_resp = self.client.put(
            f'/opportunities/{opp_id}',
            json={
                'name': 'Updated Internship',
                'duration': '4 months',
                'start_date': '2026-06-10',
                'description': 'Updated desc',
                'skills': 'React,Node,Python',
                'category': 'Technology',
                'future_opportunities': 'Job offer',
                'max_applicants': 150,
            },
            headers=headers,
        )
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.get_json()['data']['name'], 'Updated Internship')

        delete_resp = self.client.delete(f'/opportunities/{opp_id}', headers=headers)
        self.assertEqual(delete_resp.status_code, 200)

        verify_resp = self.client.get(f'/opportunities/{opp_id}', headers=headers)
        self.assertEqual(verify_resp.status_code, 404)

    def test_non_owner_cannot_access_opportunity(self):
        self.signup('Owner', 'owner@test.com', 'Password123!')
        login_resp = self.login('owner@test.com', 'Password123!')
        token = login_resp.get_json()['access_token']
        owner_headers = {'Authorization': f'Bearer {token}'}

        create_resp = self.client.post(
            '/opportunities',
            json={
                'name': 'Owned Position',
                'duration': '1 month',
                'start_date': '2026-06-01',
                'description': 'Example position',
                'skills': 'Skill A, Skill B',
                'category': 'Technology',
                'future_opportunities': 'Yes',
                'max_applicants': 5,
            },
            headers=owner_headers,
        )
        self.assertEqual(create_resp.status_code, 201)
        opp_id = create_resp.get_json()['data']['id']

        self.signup('Other Admin', 'other@test.com', 'Password123!')
        other_login = self.login('other@test.com', 'Password123!')
        other_token = other_login.get_json()['access_token']
        other_headers = {'Authorization': f'Bearer {other_token}'}

        other_resp = self.client.get(f'/opportunities/{opp_id}', headers=other_headers)
        self.assertEqual(other_resp.status_code, 403)
        self.assertEqual(other_resp.get_json()['error'], 'Access denied')

    def test_opportunity_pagination(self):
        self.signup('Paging Admin', 'paging@test.com', 'Password123!')
        login_resp = self.login('paging@test.com', 'Password123!')
        token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        for i in range(5):
            self.client.post(
                '/opportunities',
                json={
                    'name': f'Opportunity {i+1}',
                    'duration': '1 month',
                    'start_date': '2026-06-01',
                    'description': 'Paging test',
                    'skills': 'Skill A',
                    'category': 'Technology',
                    'future_opportunities': 'Yes',
                    'max_applicants': 5,
                },
                headers=headers,
            )

        page_resp = self.client.get('/opportunities?page=1&limit=2', headers=headers)
        self.assertEqual(page_resp.status_code, 200)
        payload = page_resp.get_json()
        self.assertEqual(payload['page'], 1)
        self.assertEqual(payload['limit'], 2)
        self.assertEqual(payload['total'], 5)
        self.assertEqual(len(payload['data']), 2)

    def test_invalid_token_returns_error(self):
        response = self.client.get('/opportunities', headers={'Authorization': 'Bearer invalid.token'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.get_json())


if __name__ == '__main__':
    unittest.main()

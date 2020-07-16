import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import random

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        # add and drop the table for deletion
        pass
    
    # questions get
    def test_get_paginated_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_questions'], len(Question.query.all()))
    
    # question by category
    def test_category_filter(self):
        cat_id = 5
        res = self.client().get('/categories/'+ str(cat_id) +'/questions')
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category == cat_id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), len(questions))

    # question id
    def test_nonexistant_question(self):
        qid = 999999
        res = self.client().get('/questions/' + str(qid))

        self.assertEqual(res.status_code, 405)

    # questions/id delete
    def test_question_deletion(self):
        qs = Question.query.all()
        qid = random.choice(qs).id

        res = self.client().delete('/questions/' + str(qid))
        data = json.loads(res.data)
        del_q = Question.query.filter_by(id=qid).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(del_q, None)

    # questions post
    def test_new_question(self):
        new_q = dict(
            question='test question',
            answer='test answer',
            difficulty=1,
            category=1)

        q_len = len(Question.query.all())        
        res = self.client().post('/questions', json=new_q)
        data = json.loads(res.data)
        del_q = Question.query.filter(Question.question == 'test question')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['tatal_questions'], q_len + 1)

    # searchQuestion post
    def test_question_search(self):
        sub_string = {'searchTerm': 'where is'}
        res = self.client().post('/searchQuestions', json=sub_string)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # cat/id/question get
    def test_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # check category of all questions
    
    # quiz post
    def test_quiz_question_generation(self):
        payload = {
            'previous_questions': [],
            'quiz_category': {'id': 1}
        }

        for i in range(5):
            res = self.client().post('/quizzes', json=payload)
            data = json.loads(res.data)

            payload['previous_questions'].append(data['question']['id'])

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertNotIn(data['question'], payload['previous_questions'])




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

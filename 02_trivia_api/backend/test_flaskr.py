import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

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
        self.assertEqual(data['total_questions'], 19)
    
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
        q_id = 999999
        res = self.client().get('/questions/' + str(q_id))

        self.assertEqual(res.status_code, 405)

    # questions/id delete
    def test_question_deletetion(self):
        qid = 5
        res = self.client().delete('/questions/' + qid)
        data = json.loads(res.data)
        del_q = Question.query.filter_by(id=qid)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(del_q, [])

    # questions post
    def test_new_question(self):
        new_q = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': '1',
            'category': '1'
        } 
        q_payload = jsonify(new_q)

        q_len = len(Question.query.all())        
        res = self.client().post('/questions', data=q_payload)
        data = json.loads(res.data)
        new_q_len = len(Question.query.all())
        del_q = Question.query.filter(Question.question == 'test question')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(new_q_len, q_len + 1)
        self.assertNotIn(new_q, data['questions'])

    # searchQuestion postf
    def test_question_search(self):
        sub_string = "where is"
        res = self.client().post('/searchQuestions', sub_string)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # cat/id/question get
    def test_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.laods(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        # check category of all questions
    
    # quiz post
    def test_quiz_question_generation(self):
        pass
    
    # quiz scoring
    def test_quiz_scoring(self):
        pass



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

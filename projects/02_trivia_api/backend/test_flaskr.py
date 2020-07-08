import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

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
        pass

    def test_get_paginated_books(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_questions'], 19)
    
    def test_category_filter(self):
        cat_id = 5
        res = self.client().get('/categories/'+ str(cat_id) +'/questions')
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category == cat_id).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), len(questions))

    def tets_question_delete(self):
        q_id = -99
        res = self.client().get('/questions/' + str(q_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

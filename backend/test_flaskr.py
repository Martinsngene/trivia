import json
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}@{}/{}'.format('postgres:abc', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.search_term = {"searchTerm": "What"}
        self.quiz_question = {"quiz_category": {"id": 5}, "previous_questions": ["1", "2", "3"]}
        self.question_id = 1
        self.new_question = {"question": "What's my name?", "answer": "Martins Ngene", "category": "5",
                             "difficulty": "3"}

    def tearDown(self):
        """Executed after reach test"""
        pass

        # ====================================Get Categories===========================#

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    # ====================================Get Paginated Questions===========================#

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["categories"])

    # ====================================Post New Question Endpoint====================#

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # ====================================Search A Question=================================#
    def test_search_a_question(self):
        res = self.client().post("/questions/search", json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])

    # ====================================Get A Question By Category=========================#

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    # ====================================Search A Question=================================#
    def test_delete_a_question(self):
        res = self.client().delete("/questions/18")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted_question"])

    # ====================================Get A Quiz Question=================================#
    def test_get_a_quiz_question(self):
        res = self.client().post("/quizzes", json=self.quiz_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

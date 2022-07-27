import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.db_host = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'abc')
        self.db_name = os.getenv('DB_NAME', 'trivia_test')
        self.db_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.db_user, self.db_password, self.db_host,
                                                                  self.db_name)
        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app, self.db_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.test_new_question = {"question": "What's my name?", "answer": None, "category": "5",
                                  "difficulty": "3"}
        self.test_search_term = {"searchTerm": "dfghjguh"}
        self.search_term = {"searchTerm": "What"}
        self.quiz_question = {"quiz_category": {"id": 4},
                              "previous_questions": ["1", "2", "3", "4", "1", "2", "3", "4", "1", "2", "3", "4", "1",
                                                     "2", "3", "4"]}
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

    def test_404_categories_not_found(self):
        res = self.client().get("/category")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")

    # ====================================Get Paginated Questions And Error Handling===========================#

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["categories"])

    def test_404_page_not_found(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")

    # ====================================Post New Question Endpoint And Error Handling====================#

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_422_not_processable(self):
        res = self.client().post("/questions", json=self.test_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    # ====================================Search A Question And Error Handling=================================#
    def test_search_a_question(self):
        res = self.client().post("/questions/search", json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])

    def test_404_search_not_found(self):
        res = self.client().post("/questions/search", json=self.test_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")

    # ====================================Get A Question By Category And Error Handling=========================#

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    def test_405_method_not_allowed(self):
        res = self.client().get("/categories/50/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    # ====================================Delete A Question And Error Handling=================================#
    def test_delete_a_question(self):
        res = self.client().delete("/questions/4")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted_question"])

    def test_404_question_not_found(self):
        res = self.client().delete("/questions/1800")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")

    # ====================================Get A Quiz Question And Error Handling=================================#
    def test_get_a_quiz_question(self):
        res = self.client().post("/quizzes", json=self.quiz_question)

        self.assertEqual(res.status_code, 200)

    def test_400_bad_quiz_request(self):
        res = self.client().post("/quizzes", json=self.quiz_question)

        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

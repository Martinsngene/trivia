# from crypt import methods
# import collections
# import os
import random
import sys

from flask import Flask, request, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

# import random

# Helper methods to avoid code repetition
QUESTIONS_PER_PAGE = 10


def paginate_response(arg, collection):
    page = arg.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_collections = []
    current_collections = []

    for collection in collection:
        formatted_collections.append(collection.format())
        current_collections = formatted_collections[start:end]

    return current_collections


def get_categories(categories):
    organized_categories = {}

    for category in categories:
        organized_categories[category.id] = category.type

    return organized_categories


def get_current_category(category_id):
    current_category = Category.query.all()
    current = ""

    for category in current_category:
        if category_id == category.id:
            current = category.type
    return current


def generate_random_question(paginated_questions):
    if len(paginated_questions) > 1:
        generate_random_index = random.randint(0, len(paginated_questions) - 1)
        next_question = paginated_questions[generate_random_index]
    else:
        next_question = None

    return next_question


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Headers", "GET, POST, DELETE, PUT, PATCH, OPTIONS")
        return response

    # TODO: Create an endpoint to handle GET requests for all available categories.
    @app.route("/categories", methods=["GET"])
    def get_all_categories():
        categories = Category.query.all()

        return jsonify({"success": True, "categories": get_categories(categories)})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            questions = Question.query.all()

            organized_questions = paginate_response(request, questions)

            categories = Category.query.all()

            return jsonify({"questions": organized_questions,
                            "totalQuestions": len(questions),
                            "categories": get_categories(categories),
                            "currentCategory": get_current_category(1)})
        except len(questions) == 0:
            abort(404)

    """
    TODO:
    Create an endpoint to DELETE question using a question ID.
: 100,
  "categories": 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_single_question(question_id):
        try:
            delete_question = Question.query.get(question_id)

            if delete_question is None:
                abort(404)

            delete_question.delete()
            paginate_response(request, Question.query.order_by(Question.id).all())

            return jsonify(
                {
                    "success": True,
                    "deleted_question": question_id,
                }
            )

        except Exception:
            print(sys.exc_info())
            raise abort(422)

    """
    #TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_new_questions():
        body = request.get_json()
        add_question = body.get("question", None)
        add_answer = body.get("answer", None)
        set_category = body.get("category", None)
        set_difficulty = body.get("difficulty", None)

        try:
            new_question = Question(
                question=add_question, category=set_category, difficulty=set_difficulty, answer=add_answer
            )
            new_question.insert()

            return jsonify(
                {
                    "success": True,
                    "question": new_question.id,
                }
            )
        except Exception:
            print(sys.exc_info())
            raise abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():

        try:
            search_result = []
            search_term = request.get_json().get('searchTerm', None)
            search_result = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
            format_search_result = paginate_response(request, search_result)

        except len(format_search_result) == 0:
            abort(404)

        return jsonify(
            {"questions": format_search_result, "totalQuestions": len(search_result), "currentCategory": ""}
        )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questions_by_category(category_id):
        try:

            all_questions = Question.query.filter(str(category_id) == Question.category).all()
            reformat_questions = paginate_response(request, all_questions)

            return jsonify(
                {
                    "questions": reformat_questions,
                    "totalQuestions": len(reformat_questions),
                    "currentCategory": get_current_category(category_id),
                }
            )
        except Exception:
            print(sys.exc_info())
            raise abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    
    This endpoint should take category and previous question parameters
    
    and return a random question within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_next_quiz_question():
        quiz_resources = request.get_json()
        latest_category = quiz_resources.get('quiz_category', None)
        previously_asked = quiz_resources.get('previous_questions', None)
        filter_term = Question.id.notin_(previously_asked)

        try:
            quiz_questions = Question.query.filter(Question.category == latest_category["id"]).filter(
                filter_term).all()
            paginate_questions = paginate_response(request, quiz_questions)
            next_question = generate_random_question(paginate_questions)
            return jsonify({
                "question": next_question,
            })
        except:
            abort(400)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request():
        return (jsonify({
            'success': False,
            'error': 400,
            'message': "Bad Request"
        }), 400)

    @app.errorhandler(404)
    def not_found():
        return (jsonify({
            'success': False,
            'error': 404,
            'message': "Page Not Found"
        }), 404)

    @app.errorhandler(405)
    def not_allowed():
        return (jsonify({
            'success': False,
            'error': 405,
            'message': "Method Not Allowed"
        }), 405)

    @app.errorhandler(422)
    def not_processable():
        return (jsonify({
            'success': False,
            'error': 422,
            'message': "Unprocessable Entity"
        }), 422)

    @app.errorhandler(500)
    def internal_server_error():
        return (jsonify({
            'success': False,
            'error': 500,
            'message': "Internal Server Error"
        }), 500)

    return app

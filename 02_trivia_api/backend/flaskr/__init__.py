import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask import logging
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_helper(req, selection):
  """
  req: a json requst
  select: a sqlAlchemy model (should have format())
  returns subset
  """
  page = req.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  selection_formated = [sel.format() for sel in selection]
  curr_selection = selection_formated[start:end]

  return curr_selection

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/')
  def home():
    return jsonify({'message': 'home'})
  
  @app.route('/categories', methods=['GET'])
  def show_categories():
    cat_list = Category.query.order_by(Category.id).all()
    categories = {cat.id: cat.type for cat in cat_list}
    return jsonify({
      'success': True,
      'categories': categories
    })
  
  @app.route('/questions', methods=['GET'])
  def show_questions():
    q_list = Question.query.all()
    questions = pagination_helper(request, q_list)
    categories = show_categories().get_json()['categories']
  
    if len(questions) == 0: 
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(q_list),
      'categories': categories,
      'current_category': None
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

    except Exception as e:
      abort(400)

    return jsonify({
      'success': True,

    })


  @app.route('/questions', methods=['POST'])
  def add_question():
    payload = request.get_json()

    try:
      new_question = Question(question=payload['question'], answer=payload['answer'],
                              difficulty=payload['difficulty'], category=payload['category'])
      new_question.insert()
    except Exception as e:
      abort(300)
    
    return jsonify({
      'success': True,
      'tatal_questions': len(Question.query.all())
    })


  @app.route('/searchQuestions', methods=['POST'])
  def find_question():
    payload = request.get_json()['searchTerm']
    
    try:
      q_list = Question.query.filter(func.lower(Question.question).contains(payload.lower())).all()
      questions = pagination_helper(request, q_list)

    except Exception as e:
      abort(422)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(Question.query.all()),
      'current_category': None
    })


  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def show_category_questions(cat_id):

    try:
      q_list = Question.query.filter(Question.category==cat_id).all()
      questions = pagination_helper(request, q_list)
    except Exception as e:
      abort(422)
    
    return jsonify({
      'success': True,
      'questions': questions,
      'current_category': cat_id,
      'total_questions': len(Question.query.all())
    })

  @app.route('/quizzes', methods=['POST'])
  def quiz():
    payload = request.get_json()
    prev_q = payload['previous_questions']
    category = payload['quiz_category']['id']
    
    questions = show_category_questions(category).get_json()['questions'] if \
      category != 0 else show_questions().get_json()['questions']

    app.logger.info(questions)
    try:
      if prev_q:
        questions = [q for q in questions if q['id'] not in prev_q]
        question = random.choice(questions)
      else:
        question = random.choice(questions)
    except IndexError:
      question = None

    return jsonify({
      'success': True,
      'question': question
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      "message": "Resourse was not found, try again"
    }), 404
  
  @app.errorhandler(422)
  def unable_to_process(error):
    return jsonify({
      'success': False,
      'error': 422,
      "message": "Unable to process the entity"
    }), 422

  @app.errorhandler(400)
  def invalid_data(error):
    return jsonify({
      'success': False,
      'error': 400,
      "message": "Invalid data request, please try again"
    }), 400
  
  
  return app

 
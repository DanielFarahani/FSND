import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask import logging
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_helper(request, selection):
  """
  req: a json requst
  select: a sqlAlchemy model (should have format())
  returns subset
  """
  page = request.args.get('page', 1, type=int)
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
  

  #TODO: the list doesn't change, double check
  @app.route('/questions', methods=['GET'])
  def show_questions():
    q_list = Question.query.all()
    questions = pagination_helper(request, q_list)

    if len(q_list) == 0: 
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'categories': show_categories().get_json()['categories'],
      'currentCategory': None,
      'totalQuestions': len(q_list)
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_book(question_id):

    try:
      question = Question.query.filter_by(id=question_id).one_or_none()
      
      if question is None:
        abort(404)

      question.delete()

    except Exception as e:
      abort(400)

    return jsonify({
      'success': True
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
      'success': True
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
      'totalQuestions': len(Question.query.all()),
      'currentCategory': None
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
      'currentCategory': cat_id,
      'totalQuestions': len(Question.query.all())
    })


  #TODO: all category condition
  #TODO: remove prev q
  #TODO: test
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    payload = request.get_json()
    prev_q = payload['previous_questions']
    category = payload['quiz_category']
    
    app.logger.info("======")
    app.logger.info(payload)

    if prev_q:
      questions = show_category_questions(category['id']).get_json()['questions']
      # remove prev_q
      question = random.choice(questions)

    else:
      questions = show_category_questions(category['id']).get_json()['questions']
      question = random.choice(questions)
      

    return jsonify({
      'success': True,
      'currentQuestion': question
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      "message": "resourse was not found, try again"
    }), 404
  
  @app.errorhandler(422)
  def unable_to_process(error):
    return jsonify({
      'success': False,
      'error': 422,
      "message": "unable to process the entity"
    }), 422
  
  
  return app

 
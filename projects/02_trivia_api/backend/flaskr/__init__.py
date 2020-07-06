import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask import logging

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

  return selection_formated[start:end]

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

  '''
  @#TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @#TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @#TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

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

 
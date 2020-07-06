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
  select: a sqlAlchemy model
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

  ''' just a place holder '''
  @app.route('/')
  def home():
    return jsonify({'message': 'home'})
  

  '''
  Gives all categories
  '''
  @app.route('/categories', methods=['GET'])
  def show_categories():
    cat_list = Category.query.order_by(Category.id).all()
    categories = [category.format() for category in cat_list]

    return jsonify({
      'success': True,
      'categories': categories
    })
  
  
  '''
  ##TODO: 10 questions at a time

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def show_questions():
    q_list = Question.query.all()
    questions = pagination_helper(request, q_list)
    
    if len(questions) == 0: 
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(q_list)
    })

  '''
  ##TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    return jsonify({
      'success': True
    })

  '''
  @#TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

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

  '''
  @#TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

 
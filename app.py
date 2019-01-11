from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import math
import os

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'online_cookbook'
app.config["MONGO_URI"] = 'mongodb://admin:cook1book2@ds129914.mlab.com:29914/online_cookbook'

mongo = PyMongo(app)

@app.route('/')

@app.route('/index')
def index():
    """
    Return index.html which is the first page the user will see
    """
    if 'username' in session:
        return render_template("home.html", 
        recipes=mongo.db.recipes.find(),
        cuisines=mongo.db.cuisines.find(),
        message='Welcome, ' + str(session['username']) + ', to The Cookery Cove!')
    return render_template("index.html", 
    message='Welcome to The Cookery Cove!',
    recipes=mongo.db.recipes.find(),
    cuisines=mongo.db.cuisines.find())
    
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """
    Direct user to signin page where they can enter their username
    and password and manage their recipes
    """
    if 'username' in session:
        return render_template('index.html',
                                message="You are already signed in!")
    
    if request.method == 'POST':
        users = mongo.db.users
        user_signin = users.find_one({'username': request.form['username']})

        if user_signin:
            if request.form['password'] == user_signin['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        return render_template('signin.html', message='Invalid username or password')
    return render_template('signin.html', message='')
    
@app.route('/signout')
def signout():
    """
    Sign user out of the session
    """
    if 'username' in session:
        session.pop('username')
        return render_template('message.html',
                               message='Signed out. See you later!')
    return render_template('message.html',
                           message='You have already signed out!')
                           
@app.route('/register')
def register():
    """
    Register new user into the database
    """
    if 'username' in session:
        return render_template('register.html', message='You are already signed in and registered')

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})

        if request.form['username'] and request.form['password']:
            # Check for existing user to avoid re-registering the same user
            if existing_user is None:
                password = request.form['password']
                users.insert({'username': request.form['username'], 'password': password})
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            return render_template('register.html',
                                   message='Username ' + str(existing_user['username']) + ' already exists')

        return render_template('register.html',
                                message='Enter a username and password')

    return render_template('register.html', message='')
    
@app.route('/get_recipe/<recipe_id>')
def get_recipe(recipe_id):
    """
    Get recipe and display it on getrecipe.html
    """
    the_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # Splits ingredients input into a list    
    ingredient_split = the_recipe['recipe_ingredients'].split('\n')
    for ingredient in ingredient_split:
        print(ingredient)
    # Splits methods input into a list    
    method_split = the_recipe['recipe_method'].split('\n')
    for method in method_split:
        print(method)
    
    return render_template("getrecipe.html",
                            recipe=the_recipe,
                            ingredient_split=ingredient_split,
                            method_split=method_split)

@app.route('/recipes_by_cuisine/<cuisine_name>')
def recipes_by_cuisine(cuisine_name):
    """
    Get all recipes of a chosen cuisine and display
    these recipes on one page
    """
    
    # Counts total amount of chosen cuisine recipes
    recipes_total = mongo.db.recipes.find({
        "cuisine_name": cuisine_name
    }).count()
    
    return render_template(
        "recipes_by_cuisine.html",
        recipes=mongo.db.recipes.find({"cuisine_name": cuisine_name}),
        cuisines=mongo.db.cuisines.find(),
        cuisine_name=cuisine_name,
        recipes_total=recipes_total)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
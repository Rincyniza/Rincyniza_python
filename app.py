import os

from flask import Flask,render_template ,request,session,redirect,url_for,flash
from flask_login import login_required, login_user, logout_user,LoginManager
import mysql.connector,hashlib,re
from functools import wraps
from wtforms import Form, StringField, TextAreaField
from werkzeug.utils import secure_filename




connection=mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'Inshahallah1234',
    database = 'RECIPE_HUB'

)


mycursor=connection.cursor()




#create a flask application
app= Flask(__name__)
app.config['SECRET_KEY'] = 'edvhjjm'
upload_folder=os.path.join('static','uploads')
app.config['UPLOAD'] = upload_folder


class RecipeForm(Form):
    id=TextAreaField('id')
    name = StringField('name')
    ingredients = TextAreaField('ingredients')
    instructions = TextAreaField('instructions')
    cooking_time=TextAreaField('cooking_time')
    serving_size=TextAreaField('serving_size')
    user_id=TextAreaField('user_id')



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            username = session['username']
        except KeyError:
            username = None
        if username is None:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def home(): 
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        mycursor=connection.cursor()
        labels = request.form['labels']
        # search by title
        query='SELECT name from Recipes WHERE name  LIKE %s'
        data=(labels,)
        mycursor.execute(query,data)

        d = mycursor.fetchall()
        
        # all in the search box will return all the tuples
        if len(d) == 0 and labels == 'all': 
            mycursor.execute("SELECT name from Recipes")
            
            d = mycursor.fetchall()
            
        return redirect(url_for('search',datas=d))
        
    return render_template('search.html')

@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    
        
        if request.method == 'POST':
            username =request.form['username']
            password=request.form['password']
            query='SELECT * FROM Users WHERE username = %s AND  password=%s'
            data=(username,password)
            mycursor.execute(query,data)
            da = mycursor.fetchone()
            if (password, da[3]) and (da[1] == username):
                session['logged_in'] = True
                session['username'] = username
                message='You are now logged in'
                return render_template('user.html',msg=message,user=username)
            else:
                flash('Invalid credentials, try again')

        return render_template('login.html')
            
    
@app.route('/logout/')
@login_required
def logout_page():
    if session['logged_in']:
        session['logged_in'] = False
        session['username'] = None
    return render_template('home.html')



   
        
        
@app.route('/register/',methods=['GET','POST'])
def register():
    
        if request.method == 'POST' :
            id = request.form['id']
            username = request.form['username']
            email = request.form['email_address']
            password =request.form['password']
            query='INSERT INTO Users (id,username, email, password) VALUES (%s,%s,%s,%s)'
            data=(id,username,email,password)
            mycursor.execute(query,data)
            connection.commit()
            message="Thanks for registering!"
            session['logged_in'] = True
            session['username'] = username
            return render_template('Register1.html',msg=message)
           
        return render_template('Register1.html')



@app.route('/recipes')
def recipe():
    return render_template('recipe.html')

@app.route('/upload',methods=['GET','POST'])
def upload_file():
     if request.method=='POST':
          file=request.files['img']
          filename=secure_filename(file.filename)
          file.save(os.path.join(app.config['UPLOAD'],filename))
          img=os.path.join(app.config['UPLOAD'],filename)
          return render_template('seperate_recipes.html',img=img)
     return render_template('share1.html')


@app.route('/featu')
def featu():
    return render_template('featured.html')


@app.route('/categ')
def categ():
    return render_template('category.html')

@app.route('/index/')
def index():
    mycursor=connection.cursor()
    query="select id,name from Recipes"
    mycursor.execute(query)
    recipes = mycursor.fetchall()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<id>')
def list_recipe(id):
            mycursor=connection.cursor()
            query='SELECT * FROM Recipes WHERE id = %s'
            data=(id,)
            mycursor.execute(query,data)
            current = mycursor.fetchone()
            query='SELECT id,comments,date_posted FROM Comments WHERE recipe_id = %s' 
            data1=(id,)
            mycursor.execute(query,data1)
            Current_comment=mycursor.fetchall()
            return render_template('seperate_recipes.html',recipe=current,Comments=Current_comment)
            
          
    

@app.route('/comment/',methods=['GET','POST'])
def comment():
    try:
        logged_in = session['logged_in']
    except KeyError:
            logged_in = False
    if logged_in:
      if request.method=='POST':
        comment=request.form['content']
        recipes_id=request.form['recipe_id']
        comment_id=request.form['comment_id']
        date_posted=request.form['date_posted']
        query = "insert into Comments(id,recipe_id,comments,date_posted) values(%s,%s,%s,%s)"
        data = (comment_id,recipes_id,comment,date_posted)
        mycursor.execute(query,data)
        connection.commit()
        message="Comment committed successfully"
        return render_template('user.html',recipe=recipes_id,msg=message)
      return render_template('seperate_recipes.html')
    


                         

@app.route('/view1')
def view1():
    mycursor=connection.cursor()
    query="select * from Recipes "
    mycursor.execute(query) 
    data=mycursor.fetchall() 
    return render_template('view1.html',sqldata=data)   


@app.route('/share1',methods=['GET','POST'])
@login_required
def share1():
    try:
        logged_in = session['logged_in']
    except KeyError:
            logged_in = False
    if logged_in:
         
      if request.method=='POST':
        id=request.form['id']
        name=request.form['name']
        ingredients=request.form['ingredients']
        instructions=request.form ['instructions'] 
        cooking_time=request.form['cooking_time']
        serving_size=request.form ['serving_size']
        user_id=request.form ['user_id']
        query="insert into Recipes values(%s,%s,%s,%s,%s,%s,%s)"
        data=(id,name,ingredients,instructions,cooking_time,serving_size,user_id)
        mycursor.execute(query,data)
        connection.commit()
        message=f"recipe added successfully"
        return render_template('share1.html',msg=message)
      return render_template('share1.html')
    
    



#run flask application
if __name__== "__main__":
    app.run(debug = True)

import os
from flask import Flask, render_template, request, redirect, session

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jsdfu9fuw9hldhfif'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  complete = db.Column(db.Boolean)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))


@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/login')

  user_id = session['user_id']  
  products = Product.query.filter_by(user_id=user_id).all()
  return render_template('index.html', products=products)


@app.route('/login')
def login():
 return render_template('login.html')
@app.route('/signin', methods=['POST'])
def signin():
 email = request.form.get('email')
 password = request.form.get('password')
 user = User.query.filter_by(email=email).first()
 if not user or not check_password_hash(user.password, password):
  return redirect('/login')
 session['user_id'] = user.id
 return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():
 name = request.form.get('name')
 email = request.form.get('email')
 password = request.form.get('password')
 user = User.query.filter_by(email=email).first()
 if user:
  return redirect('/register')

 new_user = User(
 email=email, name=name,
 password=generate_password_hash(password, method='sha256')
 )
 db.session.add(new_user)
 db.session.commit()
 return redirect('/login')

 @app.route('/logout')
 def logout():
   if 'user_id' in session:
      session.pop('user_od', None)
   return redirect('/login')   

  
@app.route('/create', methods=['POST'])
def create():
  if 'user_id' not in session:
    return redirect('/login')
  user_id = session['user_id']

  title = request.form.get('title')
  new_product = Product(title=title, complete=False, user_id=user_id)
  db.session.add(new_product)
  db.session.commit()
  return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    product = Product.query.filter_by(id=id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect('/')


@app.route('/complete/<int:id>')
def complete(id):
    product = Product.query.filter_by(id=id).first()
    product.complete = True
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    title = request.form.get('title')
    price = request.form.get('price')
    product = Product.query.filter_by(id=id).first()
    product.title = title
    product.price = price
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port = port)

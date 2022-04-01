from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
# from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite') 

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app, resources={r'/*': {'origins': '*'}})
# bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, default = False)
    password = db.Column(db.String(20), default = False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')


user_schema = UserSchema()
multiple_user_schema = UserSchema(many = True)

@app.route('/user', methods = ['POST'])
@cross_origin()
def add_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be in Json format')

    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    possible_duplicate = db.session.query(User).filter(User.username == username).first()

    if possible_duplicate is not None:
        return jsonify("Error: the username you've entered has been taken")

    new_user = User(username, password)
    db.session.add(new_user)
    db. session.commit()

    return jsonify(f'New user {username} has been added.')

@app.route('/user/verify', methods = ['POST'])
@cross_origin()
def verify_user():
    print(request.content_type)
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be in Json format')

    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify('User NOT verified')
    if password != user.password:
        return jsonify('Pass NOT verified')
    
    return jsonify('User has been verified')

@app.route('/user/<id>', methods = ['PUT'])
def edit_user(id):

    post_data = request.get_json()
    username = post_data.get('username')

    user = db.session.query(User).filter(User.id == id).first()

    if username != None:
        user.username = username

    db.session.commit()
    return jsonify(f'{user.username} was Updated')

@app.route('/user/<id>', methods = ['DELETE'])
def delete_user(id):
    user = db.session.query(User).filter(User.id == id).first()
    db.session.delete(user)
    db.session.commit()

    return jsonify(f'The user {user.username} has been deleted')


@app.route('/user', methods = ['GET'])
def get_users():
    users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(users))


if __name__ == "__main__":
    app.run(debug = True)


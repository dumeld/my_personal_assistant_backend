from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d') if data.get('due_date') else None,
        user_id=data['user_id']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created'}), 201

@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    tasks_list = [{'id': task.id, 'title': task.title, 'description': task.description, 'due_date': task.due_date} for task in tasks]
    return jsonify(tasks_list), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt')
    response = requests.post(
        "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
        headers={"Authorization": "Bearer YOUR_HUGGINGFACE_API_KEY"},
        json={"inputs": prompt}
    )
    result = response.json()
    return jsonify({'response': result.get('generated_text', '')}), 200

if __name__ == '__main__':
    app.run(debug=True)

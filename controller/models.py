from controller.database import db 
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True, autoincrement = True) 
    email = db.Column(db.String(64), unique = True, nullable = False) 
    password = db.Column(db.String(128), nullable = False) 
    username = db.Column(db.String(128),unique = True, nullable = False) 
    full_name = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(64), nullable = False)

    quiz_attempts = db.relationship('Score', backref = 'user', lazy = True)
    
    def get_id(self):   #Required for Flask-Login
        return str(self.id)

class Subject(db.Model):
    id = db.Column(db.Integer,primary_key = True, autoincrement = True) 
    name = db.Column(db.String(128), unique = True, nullable = False) 
    description = db.Column(db.Text) 

    chapters = db.relationship('Chapter', backref = 'subject', lazy = True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True) 
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable = False)
    name = db.Column(db.String(128), unique = True, nullable = False) 
    description = db.Column(db.Text) 

    quizzes = db.relationship('Quiz', backref = 'chapter', lazy = True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True) 
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable = False) 
    name = db.Column(db.String(128), nullable = False) 
    date_of_quiz = db.Column(db.Date, nullable = False) 
    duration = db.Column(db.String(64),nullable = False) 
    syllabus = db.Column(db.Text) 
    total_questions = db.Column(db.Integer) 
    maximum_marks = db.Column(db.Integer) 

    questions = db.relationship('Question', backref = 'quiz', lazy = True)
    quiz_attempts = db.relationship('Score', backref = 'quiz', lazy = True)

    

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    statement = db.Column(db.Text, nullable = False) 
    option_a = db.Column(db.String(128), nullable = False)
    option_b = db.Column(db.String(128), nullable = False) 
    option_c = db.Column(db.String(128), nullable = False)
    option_d = db.Column(db.String(128), nullable = False) 
    correct_answer = db.Column(db.String(128), nullable = False)
    marks = db.Column(db.Integer, nullable = False)

    answers = db.relationship('Answers', backref = 'question', lazy = True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False) 
    score = db.Column(db.Integer, default = 0)

    answers = db.relationship('Answers', backref = 'score', lazy = True)

class Answers(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable = False) 
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable = False) 
    user_answer = db.Column(db.String(128), nullable = False) 
    marks_scored = db.Column(db.Integer, nullable = False) 

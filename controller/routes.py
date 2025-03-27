from main import app 
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from controller.models import * 
from datetime import datetime

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard', username = current_user.username))
    else:
         return render_template("home.html") 
    
@app.route('/subject/<int:subject_id>')
@login_required
def subject_details(subject_id): # URL for displaying the details of a subject
    subject = Subject.query.get_or_404(subject_id)
    return render_template('subject_details.html', subject=subject) 

@app.route('/chapter/<int:chapter_id>')
@login_required
def chapter_details(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = chapter.quizzes 
    current_date = datetime.today().date()
    return render_template('chapter_details.html', chapter=chapter, quizzes=quizzes, current_date=current_date) 

@app.route('/quiz/<int:quiz_id>')
@login_required
def quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    current_date = datetime.today().date()
    return render_template('quiz_details.html', quiz=quiz, questions=questions, current_date=current_date)
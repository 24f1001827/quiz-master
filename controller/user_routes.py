from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from main import app
from controller.models import * 
from datetime import datetime 

@app.route('/user_dashboard/<int:user_id>') # URL for the user dashboard
@login_required
def user_dashboard(user_id): 
    user = User.query.get_or_404(user_id)
    quizzes = Quiz.query.all()
    upcoming_quizzes = []
    current_date = datetime.today().date() 
    for quiz in quizzes:
        if quiz.date_of_quiz >= datetime.today().date():
            upcoming_quizzes.append(quiz)
    attempts = Score.query.filter_by(user_id=user_id).all()
    attempted_quizzes = [attempt.quiz_id for attempt in attempts]

    if not user:
        flash("User does not exist", "danger")
        return redirect(url_for('home'))
    
    return render_template('user_dashboard.html', user = user, upcoming_quizzes = upcoming_quizzes, current_date = current_date, attempted_quizzes = attempted_quizzes)

@app.route('/user_profile/<int:user_id>') # URL for the user profile
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)

@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST']) # URL for editing the user profile
@login_required
def edit_profile(user_id):
    if current_user.id != user_id:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form['email']
        user.username = request.form['username']
        user.full_name = request.form['full_name']
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for('user_profile', user_id=user.id))
    return render_template('edit_profile.html', user=user) 

@app.route('/user_search') 
@login_required
def user_search(): # The Search URL for the users 
    search = request.args.get('search')
    if search:
        subjects = Subject.query.filter(Subject.name.like(f'%{search}%')).all()
        chapters = Chapter.query.filter(Chapter.name.like(f'%{search}%')).all()
        quizzes = Quiz.query.filter(Quiz.name.like(f'%{search}%')).all()
        return render_template('search.html', users = None, subjects=subjects, chapters=chapters, quizzes=quizzes) 

@app.route('/subjects')
@login_required
def subjects(): # URL for displaying all the subjects
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects) 

@app.route('/scores')
@login_required
def scores():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return render_template('scores.html', scores=scores)

@app.route('/quiz/statistics/<int:quiz_id>') # URL for the quiz statistics
@login_required
def quiz_statistics(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    user = User.query.get_or_404(current_user.id)
    answers = None
    if score:
        answers = Answers.query.filter_by(attempt_id=score.id).all() 
    return render_template('quiz_statistics.html', quiz=quiz, score=score, answers=answers, user = user)

@app.route('/attempt/quiz/<int:quiz_id>', methods=['GET', 'POST']) # URL for attempting a quiz
@login_required
def attempt_quiz(quiz_id): 
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.date_of_quiz < datetime.today().date(): #Checking if the quiz has already ended
        flash("The quiz has already ended", "danger")
        return redirect(url_for('user_dashboard', user_id = current_user.id))
    questions = quiz.questions
    duration = quiz.duration 

    if request.method == 'POST':
        score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
        if score: #Checking if user has already attempted the quiz
            score.score = 0
            for question in questions:
                user_answer = request.form.get(f'{question.id}')
                answer = Answers.query.filter_by(attempt_id=score.id, question_id=question.id).first()
                answer.user_answer = user_answer
                if answer:
                    answer.user_answer = user_answer if user_answer else None
                    if user_answer == question.correct_answer:
                        answer.marks_scored = question.marks
                        score.score += question.marks 
                    else:
                        answer.marks_scored = 0
                else:
                    answer = Answers(attempt_id=score.id, question_id=question.id, user_answer=user_answer if user_answer else None) 
                    if user_answer == question.correct_answer:
                        answer.marks_scored = question.marks
                        score.score += question.marks
                    else:
                        answer.marks_scored = 0
                    db.session.add(answer)

            db.session.commit()
            return redirect(url_for('quiz_statistics', quiz_id=quiz_id))
        else:
            score = Score(user_id=current_user.id, quiz_id=quiz_id)
            db.session.add(score)
            db.session.commit()
            
            for question in questions:
                user_answer = request.form.get(f'{question.id}')
                answer = Answers(attempt_id=score.id, question_id=question.id, user_answer=user_answer if user_answer else None)
                
                if user_answer:
                    if user_answer == question.correct_answer:
                        answer.marks_scored = question.marks
                        score.score += question.marks 
                    else:
                        answer.marks_scored = 0

                db.session.add(answer)

            db.session.commit()
            return redirect(url_for('quiz_statistics', quiz_id=quiz_id))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions, duration=duration)


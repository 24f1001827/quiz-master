from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from main import app
from controller.models import * 
from datetime import datetime 

@app.route('/user_dashboard/<username>') # URL for the user dashboard
@login_required
def user_dashboard(username):
    user = User.query.filter_by(username = username).first()
    quizzes = Quiz.query.all()
    upcoming_quizzes = []
    for quiz in quizzes:
        if quiz.date_of_quiz >= datetime.today().date():
            upcoming_quizzes.append(quiz)
    if not user:
        flash("User does not exist", "danger")
        return redirect(url_for('home'))
    return render_template('user_dashboard.html', user = user, upcoming_quizzes = upcoming_quizzes)

@app.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
@login_required
def subject_details(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('subject_details.html', subject=subject) #Create the subject_details.html template

@app.route('/chapter/<int:chapter_id>')
@login_required
def chapter_details(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = chapter.quizzes 
    current_date = datetime.today().date()
    return render_template('chapter_details.html', chapter=chapter, quizzes=quizzes, current_date=current_date) 

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
    answers = Answers.query.filter_by(attempt_id = score.id).all()
    return render_template('quiz_statistics.html', quiz=quiz, score=score, answers=answers)

@app.route('/attempt/quiz/<int:quiz_id>', methods=['GET', 'POST']) # URL for attempting a quiz
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    duration = quiz.duration 

    if request.method == 'POST':
        print("Form data received") # Debugging statement
        print(request.form) # Debugging statement

        score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
        if score: #Checking if user has already attempted the quiz
            score.score = 0
            for question in questions:
                user_answer = request.form[(f'{question.id}')]
                answer = Answers.query.filter_by(attempt_id=score.id, question_id=question.id).first()
                answer.user_answer = user_answer

                if user_answer == question.correct_answer:
                    answer.marks_scored = question.marks
                    score.score += question.marks 
                else:
                    answer.marks_scored = 0

            db.session.commit()
            return redirect(url_for('quiz_statistics', quiz_id=quiz_id))
        else:
            score = Score(user_id=current_user.id, quiz_id=quiz_id)
            db.session.add(score)
            db.session.commit()
            
            for question in questions:
                user_answer = request.form[(f'{question.id}')]
                answer = Answers(attempt_id=score.id, question_id=question.id, user_answer=user_answer)
                
                if user_answer == question.correct_answer:
                    answer.marks_scored = question.marks
                    score.score += question.marks

                db.session.add(answer)

            db.session.commit()
            return redirect(url_for('quiz_statistics', quiz_id=quiz_id))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions, duration=duration)


from controller.models import * 
from flask import render_template, flash, redirect, url_for
from main import app
from flask_login import login_required, current_user

@app.route('/user_summary/<int:user_id>')
@login_required
def user_summary(user_id):
    if current_user.role == 'admin' or current_user.id == user_id:
        user = User.query.get_or_404(user_id)
        subjects = Subject.query.all()
        chart_data = []
        for subject in subjects:
            chapters = Chapter.query.filter_by(subject_id=subject.id).all()
            quizzes = []
            for chapter in chapters:
                quizzes.extend(Quiz.query.filter_by(chapter_id=chapter.id).all())
            attempts = Score.query.filter_by(user_id=user.id).all()
            attempted_quizzes = [attempt.quiz_id for attempt in attempts]
            print(attempted_quizzes) #Debugging 
            completion_rate = len([quiz.id for quiz in quizzes if quiz.id in attempted_quizzes]) / len(quizzes) * 100 if quizzes else 0 #What percentage of quizzes of that subject has the user completed

            sum_percent_score = 0 #Sum of the percentage scores of all quizzes of that subject
            count = 0
            for quiz in quizzes:
                if quiz.id in attempted_quizzes:
                    attempt = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
                    percent_score = attempt.score / quiz.maximum_marks * 100 if quiz.maximum_marks > 0 else 0
                    sum_percent_score += percent_score
                    count += 1
            percentage_average_score = sum_percent_score / count if count > 0 else 0
            chart_data.append({'label': subject.name, 'completion_rate': completion_rate, 'percentage_average_score': percentage_average_score})
        return render_template('user_summary.html', user=user, subjects=subjects, chart_data=chart_data) 
    else:
        flash("You are not authorized to view this page", "danger") 
        return redirect(url_for('home'))


@app.route('/user_summary/<int:user_id>/subject/<int:subject_id>')
@login_required
def user_subject_summary(user_id,subject_id):
    if current_user.role == 'admin' or current_user.id == user_id:
        user = User.query.get_or_404(user_id)
        subject = Subject.query.get_or_404(subject_id)
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        quizzes = []
        for chapter in chapters:
            quizzes.extend(Quiz.query.filter_by(chapter_id=chapter.id).all())
        chart_data = []
        for quiz in quizzes:
            attempt = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
            score = attempt.score if attempt else 0
            percentage_score = score / quiz.maximum_marks * 100 if quiz.maximum_marks > 0 else 0
            chart_data.append({'label': quiz.name, 'percentage_score': percentage_score})
        return render_template('user_subject_summary.html', subject=subject, quizzes=quizzes, chart_data=chart_data, user = user) 
    else:
        flash("You are not authorized to view this page", "danger") 
        return redirect(url_for('home'))

@app.route('/user_summary/<int:user_id>/subject/<int:subject_id>/chapter/<int:chapter_id>')
@login_required
def user_chapter_summary(user_id,subject_id, chapter_id):
    if current_user.role == 'admin' or current_user.id == user_id:
        user = User.query.get_or_404(user_id)
        subject = Subject.query.get_or_404(subject_id)
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = chapter.quizzes
        chart_data = []
        for quiz in quizzes:
            user_attempt = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
            score = user_attempt.score if user_attempt else 0
            percentage_score = score / quiz.maximum_marks * 100 if quiz.maximum_marks > 0 else 0 # Getting User score in percentage 

            all_attempts = Score.query.filter_by(quiz_id=quiz.id).all()
            sum_score = 0
            for attempt in all_attempts:
                sum_score += attempt.score
            average_score = sum_score / len(all_attempts) if len(all_attempts) > 0 else 0
            percentage_average_score = average_score / quiz.maximum_marks * 100 if quiz.maximum_marks > 0 else 0 # Getting Average score in percentage

            chart_data.append({'label': quiz.id, 'percentage_score': percentage_score, 'percentage_average_score': percentage_average_score})
        return render_template('user_chapter_summary.html', subject=subject, chapter=chapter, quizzes=quizzes, chart_data=chart_data)
    else:
        flash("You are not authorized to view this page", "danger") 
        return redirect(url_for('home'))
from controller.models import * 
from flask import render_template
from main import app
from flask_login import login_required

@app.route('/summary')
@login_required
def summary():
    subjects = Subject.query.all()
    return render_template('summary.html', subjects=subjects) 

@app.route('/summary/subject/<int:subject_id>')
@login_required
def subject_summary(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = subject.chapters

    chart_data  = []
    for chapter in chapters:
        quiz_count = len(chapter.quizzes)
        chart_data.append({'label': chapter.name, 'value': quiz_count})

    return render_template('subject_summary.html', subject=subject, chapters=chapters, chart_data=chart_data)

@app.route('/summary/subject/<int:subject_id>/chapter/<int:chapter_id>')
@login_required
def chapter_summary(subject_id, chapter_id):
    subject = Subject.query.get_or_404(subject_id)
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = chapter.quizzes

    chart_data = []
    for quiz in quizzes:
        attempts = Score.query.filter_by(quiz_id=quiz.id).count()
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        highest_score = max(score.score for score in scores) if scores else 0
        average_score = sum(score.score for score in scores) / attempts if attempts > 0 else 0
        chart_data.append({'label': quiz.name, 'attempts': attempts, 'average_score': round(average_score, 2), 'highest_score': highest_score,'total_marks': quiz.maximum_marks})


    return render_template('chapter_summary.html', subject=subject, chapter=chapter, quizzes=quizzes, chart_data=chart_data)

@app.route('/quiz_summary/<int:quiz_id>')
@login_required
def quiz_summary(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    questions = []
    chart_data = []
    for question in quiz.questions:
        not_attempted = Score.query.join(Answers).filter(Answers.question_id == question.id).filter(Answers.user_answer == None).count()
        attempted = Score.query.join(Answers).filter(Answers.question_id == question.id).filter(Answers.user_answer != None).count()
        correct_answers = Score.query.join(Answers).filter(Answers.question_id == question.id).filter(Answers.user_answer == question.correct_answer).count()
        attempt_percentage = (attempted / (attempted + not_attempted)) * 100 if attempted + not_attempted > 0 else 0
        correct_percentage = (correct_answers / (attempted + not_attempted)) * 100 if attempted + not_attempted > 0 else 0

        questions.append({
            'id': question.id,
            'Statement': question.statement,
            'not_attempted': not_attempted,
            'attempted': attempted,
            'correct_answers': correct_answers,
            'correct_percentage': round(correct_percentage, 2)
        })
        chart_data.append({'label': question.id, 'attempt_percentage': round(attempt_percentage, 2), 'correct_percentage': round(correct_percentage, 2)})
    print("Chart data:", chart_data)

    return render_template('quiz_summary.html', quiz=quiz, questions=questions, chart_data = chart_data)

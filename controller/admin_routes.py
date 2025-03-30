from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from main import app
from controller.models import * 
from datetime import datetime


@app.route('/admin_dashboard') #URL for ADMIN DASHBOARD
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()   
    current_date = datetime.today().date() 
    return render_template('admin_dashboard.html', quizzes=quizzes, current_date=current_date)
    
@app.route('/admin_search') #URL for ADMIN SEARCH
def admin_search():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    search = request.args.get('search')
    if search:
        users = User.query.filter(User.username.like(f'%{search}%')).all()
        subjects = Subject.query.filter(Subject.name.like(f'%{search}%')).all()
        chapters = Chapter.query.filter(Chapter.name.like(f'%{search}%')).all()
        quizzes = Quiz.query.filter(Quiz.name.like(f'%{search}%')).all()
        questions = Question.query.filter(Question.statement.like(f'%{search}%')).all()

        return render_template('search.html', users=users , subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions) 
    return redirect(url_for('admin_dashboard'))

@app.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('You are not authorized to delete users!', 'danger')
        return redirect(url_for('home')) 
    user = User.query.get_or_404(user_id) 
    for attempt in user.quiz_attempts:
        db.session.delete(attempt) 
        for answers in attempt.answers:
            db.session.delete(answers)
    db.session.delete(user) 
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

      
# Manage Subjects
@app.route('/manage_subjects')
@login_required
def manage_subjects():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    subjects = Subject.query.all()
    return render_template('manage_subjects.html', subjects=subjects)

@app.route('/add_subject', methods=['GET','POST'])
@login_required
def add_subject():
    if current_user.role != 'admin':
        flash('You are not authorized to add subjects!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('add_subject.html') 
    else: 
        name = request.form['name']
        description = request.form['description']
        subject = Subject.query.filter_by(name=name).first()
        if subject:
            flash('Subject already exists!', 'warning')
            return redirect(url_for('manage_subjects')) 
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('manage_subjects'))

@app.route('/edit_subject/<int:subject_id>', methods=['GET','POST']) 
@login_required
def edit_subject(subject_id):
    if current_user.role != 'admin':
        flash('You are not authorized to edit subjects!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('edit_subject.html', subject=Subject.query.get_or_404(subject_id))
    else:
        subject = Subject.query.get_or_404(subject_id)
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('manage_subjects'))

@app.route('/delete_subject/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        flash('You are not authorized to delete subjects!', 'danger')
        return redirect(url_for('home'))
    subject = Subject.query.get_or_404(subject_id)
    for chapter in subject.chapters:
        for quiz in chapter.quizzes: 
            for attempt in quiz.quiz_attempts:
                for answers in attempt.answers:
                    db.session.delete(answers)
                db.session.delete(attempt)

            for question in quiz.questions:
                db.session.delete(question)
            db.session.delete(quiz)
        db.session.delete(chapter)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('manage_subjects'))

# Manage Chapters
@app.route('/manage_chapters')
@login_required
def manage_chapters():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    chapters = Chapter.query.all()
    subjects = Subject.query.all()
    return render_template('manage_chapters.html', chapters=chapters, subjects=subjects)

@app.route('/add_chapter', methods=['GET','POST'])
@app.route('/add_chapter/<int:subject_id>', methods=['GET','POST'])
@login_required
def add_chapter(subject_id=None):
    if current_user.role != 'admin':
        flash('You are not authorized to add chapters!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        subjects = Subject.query.all()
        if not subjects:
            flash('No subjects found! Please add a subject first.', 'warning')
            return redirect(url_for('manage_chapters'))
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            return render_template('add_chapter.html', subjects=subjects, SUBJECT=subject)
        else:
            return render_template('add_chapter.html', subjects=subjects, SUBJECT=None)
    else:
        
        chapter = Chapter.query.filter_by(name=request.form['name']).first()
        if chapter:
            flash('Chapter already exists!', 'warning')
            return redirect(url_for('manage_chapters'))
        
        subject = Subject.query.get_or_404(request.form['subject_id'])
        name = request.form['name']
        description = request.form['description']
        chapter = Chapter(name=name, description=description, subject=subject)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('manage_chapters'))

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET','POST'])
@login_required
def edit_chapter(chapter_id):
    if current_user.role != 'admin':
        flash('You are not authorized to edit chapters!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        chapter = Chapter.query.get_or_404(chapter_id)
        subjects = Subject.query.all()
        return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)
    else:
       
        chapter = Chapter.query.get_or_404(chapter_id)
        chapter.subject = Subject.query.get_or_404(request.form['subject_id'])
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('manage_chapters'))

@app.route('/delete_chapter/<int:chapter_id>')
@login_required
def delete_chapter(chapter_id):
    if current_user.role != 'admin':
        flash('You are not authorized to delete chapters!', 'danger')
        return redirect(url_for('home'))
    chapter = Chapter.query.get_or_404(chapter_id)
    for quiz in chapter.quizzes:
        for attempt in quiz.quiz_attempts:
            for answers in attempt.answers:
                db.session.delete(answers)
            db.session.delete(attempt)

        for question in quiz.questions:
            db.session.delete(question)
        db.session.delete(quiz)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('manage_chapters'))

# Manage Quizzes
@app.route('/manage_quizzes')
@login_required
def manage_quizzes():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all() 
    current_date = datetime.today().date()
    return render_template('manage_quizzes.html', quizzes=quizzes, chapters=chapters, current_date=current_date)

@app.route('/add_quiz', methods=['GET','POST'])
@app.route('/add_quiz/<int:chapter_id>', methods=['GET','POST'])
@login_required
def add_quiz(chapter_id=None):
    if current_user.role != 'admin':
        flash('You are not authorized to add quizzes!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        chapters = Chapter.query.all()
        if not chapters:
            flash('No chapters found! Please add a chapter first.', 'warning')
            return redirect(url_for('manage_quizzes'))
        if chapter_id:
            chapter = Chapter.query.get_or_404(chapter_id)
            return render_template('add_quiz.html', chapters=chapters, CHAPTER=chapter)
        else:
            return render_template('add_quiz.html', chapters=chapters, CHAPTER=None)
    else:
        quiz = Quiz.query.filter_by(name=request.form['name']).first()
        if quiz:
            flash('Quiz already exists!', 'warning')
            return redirect(url_for('manage_quizzes'))
        chapter = Chapter.query.get_or_404(request.form['chapter_id'])
        name = request.form['name']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d').date()
        duration = request.form['duration']
        syllabus = request.form['syllabus']
        total_questions = request.form['total_questions']
        maximum_marks = request.form['maximum_marks']
        quiz = Quiz(name=name, date_of_quiz=date_of_quiz, duration=duration, syllabus=syllabus, total_questions = total_questions, maximum_marks=maximum_marks,chapter=chapter)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('manage_quizzes'))
    
@app.route('/edit_quiz/<int:quiz_id>', methods=['GET','POST'])
@login_required
def edit_quiz(quiz_id):
    if current_user.role != 'admin':
        flash('You are not authorized to edit quizzes!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        quiz = Quiz.query.get_or_404(quiz_id)
        chapters = Chapter.query.all()
        return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)
    else:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.chapter = Chapter.query.get_or_404(request.form['chapter_id'])
        quiz.name = request.form['name']
        quiz.date_of_quiz = request.form['date_of_quiz']
        quiz.duration = request.form['duration']
        quiz.syllabus = request.form['syllabus']
        quiz.total_questions = request.form['total_questions']
        quiz.maximum_marks = request.form['maximum_marks']
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('manage_quizzes'))

@app.route('/delete_quiz/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    if current_user.role != 'admin':
        flash('You are not authorized to delete quizzes!', 'danger')
        return redirect(url_for('home')) 
    quiz = Quiz.query.get_or_404(quiz_id)
    for attempt in quiz.quiz_attempts:
        for answers in attempt.answers:
            db.session.delete(answers)
        db.session.delete(attempt)

    for question in quiz.questions:
        db.session.delete(question)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('manage_quizzes'))

# Manage Questions
@app.route('/manage_questions')
@login_required
def manage_questions():
    if current_user.role != 'admin':
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('home'))
    questions = Question.query.all()
    quizzes = Quiz.query.all()
    return render_template('manage_questions.html', questions=questions, quizzes=quizzes)

@app.route('/add_question', methods=['GET','POST'])
@app.route('/add_question/<int:quiz_id>', methods=['GET','POST'])
@login_required
def add_question(quiz_id=None):
    if current_user.role != 'admin':
        flash('You are not authorized to add questions!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        quizzes = Quiz.query.all()
        if not quizzes:
            flash('No quizzes found! Please add a quiz first.', 'warning')
            return redirect(url_for('manage_questions'))
        if quiz_id:
            quiz = Quiz.query.get_or_404(quiz_id)
            return render_template('add_question.html', quizzes=quizzes, QUIZ=quiz)
        else:
            return render_template('add_question.html', quizzes=quizzes, QUIZ=None)
    else:
        question = Question.query.filter_by(statement=request.form['statement']).first() 
        if question:
            flash('Question already exists!', 'warning')
            return redirect(url_for('manage_questions'))
        quiz = Quiz.query.get_or_404(request.form['quiz_id'])
        statement = request.form['statement']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        marks = request.form['marks']  
        #quiz.maximum_marks += marks
        question = Question(statement=statement, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d, correct_answer=correct_answer, marks=marks, quiz=quiz)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('manage_questions'))
    
@app.route('/edit_question/<int:question_id>', methods=['GET','POST'])
@login_required
def edit_question(question_id):
    if current_user.role != 'admin':
        flash('You are not authorized to edit questions!', 'danger')
        return redirect(url_for('home'))
    if request.method == 'GET':
        question = Question.query.get_or_404(question_id)
        quizzes = Quiz.query.all()
        return render_template('edit_question.html', question=question, quizzes=quizzes) 
    else:
        question = Question.query.get_or_404(question_id)
        question.quiz = Quiz.query.get_or_404(request.form['quiz_id'])
        question.statement = request.form['statement']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_answer = request.form['correct_answer'] 
        #question.quiz.maximum_marks -= question.marks  
        question.marks = request.form['marks'] 
        #question.quiz.maximum_marks += question.marks 
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('manage_questions'))

@app.route('/delete_question/<int:question_id>')
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        flash('You are not authorized to delete questions!', 'danger')
        return redirect(url_for('home'))
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('manage_questions')) 




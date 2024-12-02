from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import tempfile
from database import db, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    language = request.form['language']
    task = Task(filename=file.filename, language=language)
    db.session.add(task)
    db.session.commit()
    
    file.save(os.path.join('uploads', file.filename))  # Сохранение файла в папке uploads
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        os.remove(os.path.join('uploads', task.filename))  # Удаление файла
    return redirect(url_for('index'))

@app.route('/run_task/<int:task_id>', methods=['POST'])
def run_task(task_id):
    task = Task.query.get(task_id)
    
    if task:
        file_path = os.path.join('uploads', task.filename)
        
        if task.language == 'python':
            command = f'python3 {file_path}'
        elif task.language == 'cpp':
            # Компилируем и запускаем C++
            exec_file = file_path.replace('.cpp', '')
            command = f'g++ {file_path} -o {exec_file} && {exec_file}'
        
        # Выполнение команды
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

        return render_template('result.html', output=output, error=error)

    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')  # Создание папки для загрузки файлов
    app.run(debug=True)
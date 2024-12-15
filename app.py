from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import threading
import time
from database import db, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()  # Создание базы данных и таблиц

# Словарь для отслеживания процессов
apps = {}

def status_checker():
    """Функция для периодической проверки статуса выполнения задач."""
    while True:
        with app.app_context():  # Добавляем контекст приложения
            for task_id in list(apps.keys()):
                process = apps[task_id]
                if process.poll() is not None:  # Проверяем, завершился ли процесс
                    task = Task.query.get(task_id)
                    if task:
                        task.status = 'Завершено'
                        db.session.commit()
                    del apps[task_id]  # Удаляем завершенный процесс из словаря
        time.sleep(5)  # Ждем перед следующей проверкой


@app.route('/get_tasks')
def get_tasks():
    tasks = Task.query.all()
    task_data = [{'id': task.id, 'filename': task.filename, 'language': task.language, 'status': task.status} for task in tasks]
    return jsonify(tasks=task_data)

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks, apps=apps)

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
        # if task.output_file and os.path.exists(task.output_file):
            # os.remove(task.output_file)  # Удаление файла с выводом
    return redirect(url_for('index'))

@app.route('/run_task/<int:task_id>', methods=['POST'])
def run_task(task_id):
    task = Task.query.get(task_id)
    
    if task:
        task.status = 'В процессе'
        db.session.commit()  # Обновляем статус в БД
        
        # file_path = os.path.join('uploads', task.filename)
        file_path = task.filename
        # output_file_path = os.path.join('uploads', f"{task.filename}.log")
        # task.output_file = output_file_path  # Сохраняем путь к файлу вывода
        db.session.commit()

        if task.language == 'python':
            command = f'python3 {file_path} > {file_path}.log'
        elif task.language == 'cpp':
            exec_file = file_path.replace('.cpp', '')
            command = f'g++ {file_path} -o {exec_file} && {exec_file} > {file_path}.log 2>&1'
        
        # Выполнение команды
        apps[task_id] = subprocess.Popen(command, shell=True, text=True, cwd=os.path.join('.', 'uploads'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return redirect(url_for('index'))

@app.route('/result/<int:task_id>', methods=['GET'])
def results(task_id):
    task = Task.query.get(task_id)
    
    # if task and task.output_file and os.path.exists(task.output_file):
    #     return send_file(task.output_file, as_attachment=True)  # Отправка файла для скачивания
    
    # return "Результат не найден", 404

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')  # Создание папки для загрузки файлов
    
    # Запускаем поток для проверки статуса задач
    status_thread = threading.Thread(target=status_checker)
    status_thread.daemon = True  # Устанавливаем поток как демон
    status_thread.start()

    app.run(debug=True)

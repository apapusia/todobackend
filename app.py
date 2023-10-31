
from flask_cors import CORS
from flask_cors import cross_origin
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import os

app = Flask(__name__)


@app.route('/delete', methods=['OPTIONS'])
@cross_origin()
def options():
    return '', 204

CORS(app, resources={
    r"/add": {"origins": "*"},
    r"/todo": {"origins": "*"},
    r"/complete/*": {"origins": "*"},
    r"/delete/*": {"origins": "*"},
    r"/delete": {"origins": "*"},
})

#with app.app_context():
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)

# todo
class Todo(db.Model):

    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
   
def todo_to_json(todo):
    return {
        'id': todo.id,
        'text': todo.text,
        'complete': todo.complete
    }


@app.route('/todo')
def index():
    incomplete = Todo.query.filter_by(complete=False).all()
    complete = Todo.query.filter_by(complete=True).all()
    
    
    incomplete_json = [todo_to_json(todo) for todo in incomplete]
    complete_json = [todo_to_json(todo) for todo in complete]
    return jsonify(incomplete=incomplete_json, complete=complete_json)


@app.route('/add', methods=['POST'])
def add():
    try:
        data = request.get_json()
        new_task_text = data.get('todoitem')  # Obtiene el campo 'todoitem'

        if new_task_text:
            new_task = Todo(text=new_task_text, complete=False)
            db.session.add(new_task)
            db.session.commit()
            return jsonify(message='Tarea agregada con éxito')

        return jsonify(error='Falta el campo "todoitem" en la solicitud'), 400

    except Exception as e:
        return jsonify(error='Error al procesar la solicitud'), 500


@app.route('/complete/<id>', methods=['PUT'])
def complete(id):
    try:
        todo = Todo.query.filter_by(id=int(id)).first()
        if todo:
            todo.complete = True
            db.session.commit()
            return jsonify(message='Tarea marcada como completa con éxito')
        else:
            return jsonify(error='Tarea no encontrada'), 404

    except Exception as e:
        return jsonify(error='Error al procesar la solicitud'), 500


@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    try:
        todo = Todo.query.filter_by(id=int(id)).first()
        if todo:
            if todo.complete:
                db.session.delete(todo)
                db.session.commit()
                return jsonify(message='Tarea eliminada con éxito')
            else:
                return jsonify(error='Tarea no está marcada como completa'), 400 
        else:
            return jsonify(error='Tarea no encontrada'), 404 

    except Exception as e:
        return jsonify(error='Error al procesar la solicitud'), 500 


if __name__ == '__main__':
    app.run(debug=True)


from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Select, Update, delete, func, select
import os

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
application.secret_key = "secretkeyprathamesh"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(40), nullable=False)
    addon = Column(DateTime, default=datetime.now())
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Todo(id={self.id},title={self.title},desc={self.desc},completed={self.completed},dateadded={self.addon})"


@application.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        ttitle = request.form.get("ttitle")
        ttext = request.form.get("ttext")
        data1 = Todo(title=ttitle, desc=ttext)
        db.session.add(data1)
        db.session.flush()
        db.session.commit()
    selectstm = Select(Todo.id, Todo.title, Todo.desc, func.strftime(
        "%d/%m/%Y %H:%M", Todo.addon), Todo.completed)
    alltodos = db.session.execute(selectstm).fetchall()
    print(alltodos)
    return render_template("index.html", todo=alltodos, place={"title": "", "desc": ""}, title={"main": "Add Todo", "btn": "ADD"})


@application.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    if request.method == "GET":
        stmt = Select(Todo).where(Todo.id == id)
        data = db.session.execute(stmt).scalar_one()
        return render_template("update.html", place=data, title={"main": "Update Todo", "btn": "Update"})
    else:
        updatstmt = Update(Todo).where(Todo.id == id).values(
            title=request.form.get("ttitle"), desc=request.form.get("ttext"))
        db.session.execute(updatstmt)
        db.session.commit()
        return redirect(url_for("home"))


@application.route("/delete/<int:id>")
def deleterecord(id):
    deletestmt = delete(Todo).where(Todo.id == id)
    db.session.execute(deletestmt)
    db.session.commit()
    return redirect(url_for("home"))


@application.route("/complete/<int:id>")
def completemark(id):
    args = request.args.get("comp")
    if args == "True":
        updatestmt = Update(Todo).where(Todo.id == id).values(completed=False)
    else:
        updatestmt = Update(Todo).where(Todo.id == id).values(completed=True)
    db.session.execute(updatestmt)
    db.session.commit()
    return redirect(url_for("home"))


@application.errorhandler(404)
def errorhtml(error):
    return render_template("error.html")


if __name__ == "__main__":
    with application.app_context():
        db.create_all()
    application.run(debug=True)

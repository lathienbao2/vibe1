from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------
# Database Models
# ------------------------

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.String(50), unique=True)
    class_name = db.Column(db.String(100))
    advisor = db.Column(db.String(100))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    birth_year = db.Column(db.Integer)
    major = db.Column(db.String(100))
    gpa = db.Column(db.Float)

    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

# create database
with app.app_context():
    db.create_all()

# ------------------------
# Routes
# ------------------------

@app.route("/")
def index():

    keyword = request.args.get("search")

    if keyword:
        students = Student.query.filter(Student.name.contains(keyword)).all()
    else:
        students = Student.query.all()

    total_students = Student.query.count()

    avg_gpa = db.session.query(func.avg(Student.gpa)).scalar()

    major_stats = db.session.query(
        Student.major,
        func.count(Student.id)
    ).group_by(Student.major).all()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        avg_gpa=avg_gpa,
        major_stats=major_stats
    )


@app.route("/add", methods=["GET","POST"])
def add_student():

    if request.method == "POST":

        student = Student(
            student_id=request.form["student_id"],
            name=request.form["name"],
            birth_year=request.form["birth_year"],
            major=request.form["major"],
            gpa=request.form["gpa"]
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/")

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_student(id):

    student = Student.query.get(id)

    if request.method == "POST":

        student.student_id = request.form["student_id"]
        student.name = request.form["name"]
        student.birth_year = request.form["birth_year"]
        student.major = request.form["major"]
        student.gpa = request.form["gpa"]

        db.session.commit()

        return redirect("/")

    return render_template("edit.html", student=student)


@app.route("/delete/<int:id>")
def delete_student(id):

    student = Student.query.get(id)

    db.session.delete(student)
    db.session.commit()

    return redirect("/")


# ------------------------
# Export CSV
# ------------------------

@app.route("/export")
def export_csv():

    students = Student.query.all()

    def generate():

        yield "student_id,name,major,gpa\n"

        for s in students:
            yield f"{s.student_id},{s.name},{s.major},{s.gpa}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment;filename=students.csv"
        }
    )


# ------------------------
# Run App
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)
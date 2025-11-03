from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- NEW: Map string form values to integer course IDs ---
# This map is based on the PDF's HTML spec [cite: 82] and DB spec 
COURSE_MAP = {
    "course_1": 1,
    "course_2": 2,
    "course_3": 3,
    "course_4": 4
}

# --- Database Models ---
# (Models are correct and unchanged)
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# --- Routes ---

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'GET':
        return render_template('create.html')
    
    if request.method == 'POST':
        roll = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        # This will be a list of strings like ["course_1", "course_3"]
        courses_from_form = request.form.getlist('courses') 
        
        existing_student = Student.query.filter_by(roll_number=roll).first()
        if existing_student:
            return render_template('exists.html')
        
        new_student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
        db.session.add(new_student)
        db.session.flush()
        
        # --- MODIFIED SECTION ---
        # Loop through the string values and get the integer ID from our map
        for course_name in courses_from_form:
            course_id = COURSE_MAP.get(course_name) # e.g., "course_1" -> 1
            if course_id:
                enrollment = Enrollment(estudent_id=new_student.student_id, ecourse_id=course_id)
                db.session.add(enrollment)
        
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'GET':
        # This logic is fine, it just passes integers to the template
        current_enrollments = [e.ecourse_id for e in student.enrollments]
        return render_template('update.html', student=student, current_enrollments=current_enrollments)
    
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        # This will also be a list of strings like ["course_1", "course_3"]
        courses_from_form = request.form.getlist('courses')
        
        student.first_name = f_name
        student.last_name = l_name
        
        Enrollment.query.filter_by(estudent_id=student_id).delete()
        
        # --- MODIFIED SECTION ---
        # Loop through the string values and get the integer ID from our map
        for course_name in courses_from_form:
            course_id = COURSE_MAP.get(course_name) # e.g., "course_2" -> 2
            if course_id:
                enrollment = Enrollment(estudent_id=student_id, ecourse_id=course_id)
                db.session.add(enrollment)
        
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/student/<int:student_id>')
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(estudent_id=student_id).all()
    enrolled_courses = [Course.query.get(e.ecourse_id) for e in enrollments]
    return render_template('details.html', student=student, courses=enrolled_courses)

if __name__ == '__main__':
    # This block must be empty except for the app.run() call
    # as per the assignment instructions [cite: 12, 15]
    app.run(debug=True)
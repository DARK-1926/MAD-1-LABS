from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# Database Models
class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# API Resources
class CourseAPI(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE001', 'error_message': 'Course not found'}, 404
        
        return {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_code': course.course_code,
            'course_description': course.course_description
        }, 200
    
    def put(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE001', 'error_message': 'Course not found'}, 404
        
        data = request.get_json()
        
        if 'course_name' in data:
            if not data['course_name']:
                return {'error_code': 'COURSE001', 'error_message': 'Course Name is required'}, 400
            course.course_name = data['course_name']
        
        if 'course_code' in data:
            if not data['course_code']:
                return {'error_code': 'COURSE002', 'error_message': 'Course Code is required'}, 400
            course.course_code = data['course_code']
        
        if 'course_description' in data:
            course.course_description = data['course_description']
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error_code': 'COURSE002', 'error_message': 'Course Code already exists'}, 409
        
        return {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_code': course.course_code,
            'course_description': course.course_description
        }, 200
    
    def delete(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE001', 'error_message': 'Course not found'}, 404
        
        db.session.delete(course)
        db.session.commit()
        return {}, 200

class CourseListAPI(Resource):
    def post(self):
        data = request.get_json()
        
        if not data.get('course_name'):
            return {'error_code': 'COURSE001', 'error_message': 'Course Name is required'}, 400
        
        if not data.get('course_code'):
            return {'error_code': 'COURSE002', 'error_message': 'Course Code is required'}, 400
        
        course = Course(
            course_name=data['course_name'],
            course_code=data['course_code'],
            course_description=data.get('course_description')
        )
        
        db.session.add(course)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error_code': 'COURSE002', 'error_message': 'Course Code already exists'}, 409
        
        return {
            'course_id': course.course_id,
            'course_name': course.course_name,
            'course_code': course.course_code,
            'course_description': course.course_description
        }, 201

class StudentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT001', 'error_message': 'Student not found'}, 404
        
        return {
            'student_id': student.student_id,
            'roll_number': student.roll_number,
            'first_name': student.first_name,
            'last_name': student.last_name
        }, 200
    
    def put(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT001', 'error_message': 'Student not found'}, 404
        
        data = request.get_json()
        
        if 'roll_number' in data:
            if not data['roll_number']:
                return {'error_code': 'STUDENT001', 'error_message': 'Roll Number required'}, 400
            student.roll_number = data['roll_number']
        
        if 'first_name' in data:
            if not data['first_name']:
                return {'error_code': 'STUDENT002', 'error_message': 'First Name is required'}, 400
            student.first_name = data['first_name']
        
        if 'last_name' in data:
            student.last_name = data['last_name']
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number already exists'}, 409
        
        return {
            'student_id': student.student_id,
            'roll_number': student.roll_number,
            'first_name': student.first_name,
            'last_name': student.last_name
        }, 200
    
    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT001', 'error_message': 'Student not found'}, 404
        
        db.session.delete(student)
        db.session.commit()
        return {}, 200

class StudentListAPI(Resource):
    def post(self):
        data = request.get_json()
        
        if not data.get('roll_number'):
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number required'}, 400
        
        if not data.get('first_name'):
            return {'error_code': 'STUDENT002', 'error_message': 'First Name is required'}, 400
        
        student = Student(
            roll_number=data['roll_number'],
            first_name=data['first_name'],
            last_name=data.get('last_name')
        )
        
        db.session.add(student)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number already exists'}, 409
        
        return {
            'student_id': student.student_id,
            'roll_number': student.roll_number,
            'first_name': student.first_name,
            'last_name': student.last_name
        }, 201

class EnrollmentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist.'}, 404
        
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        courses = []
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_id)
            if course:
                courses.append({
                    'enrollment_id': enrollment.enrollment_id,
                    'student_id': enrollment.student_id,
                    'course_id': enrollment.course_id
                })
        
        return courses, 200
    
    def post(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist.'}, 404
        
        data = request.get_json()
        course_id = data.get('course_id')
        
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 404
        
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing:
            return {
                'enrollment_id': existing.enrollment_id,
                'student_id': existing.student_id,
                'course_id': existing.course_id
            }, 201
        
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        
        return {
            'enrollment_id': enrollment.enrollment_id,
            'student_id': enrollment.student_id,
            'course_id': enrollment.course_id
        }, 201
    
    def delete(self, student_id, course_id):
        # --- START OF FIX ---
        
        # 1. Check if the student exists (like in GET and POST)
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist.'}, 404
        
        # 2. Check if the course exists (like in POST)
        course = Course.query.get(course_id)
        if not course:
            # Using the same error code as your POST method
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 404
        
        # --- END OF FIX ---

        # 3. Now, find the specific enrollment
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            # This error message is now correct, as we know both student and course exist
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Enrollment for the student not found'}, 404
        
        db.session.delete(enrollment)
        db.session.commit()
        return {}, 200

# Register API endpoints
api.add_resource(CourseAPI, '/api/course/<int:course_id>')
api.add_resource(CourseListAPI, '/api/course')
api.add_resource(StudentAPI, '/api/student/<int:student_id>')
api.add_resource(StudentListAPI, '/api/student')
api.add_resource(EnrollmentAPI, '/api/student/<int:student_id>/course', '/api/student/<int:student_id>/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=True)
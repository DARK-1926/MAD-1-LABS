from app import app, db, Course

with app.app_context():
    # Add courses
    courses = [
        Course(course_id=1, course_code='CSE01', course_name='MAD I', 
               course_description='Modern Application Development - I'),
        Course(course_id=2, course_code='CSE02', course_name='DBMS', 
               course_description='Database management Systems'),
        Course(course_id=3, course_code='CSE03', course_name='PDSA', 
               course_description='Programming, Data Structures and Algorithms using Python'),
        Course(course_id=4, course_code='BST13', course_name='BDM', 
               course_description='Business Data Management')
    ]
    
    for course in courses:
        db.session.add(course)
    
    db.session.commit()
    print("Courses added successfully!")
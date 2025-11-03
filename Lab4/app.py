import csv
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

def load_csv():
    """Load data from CSV file"""
    data = []
    try:
        with open('data.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace from keys and values
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                data.append(cleaned_row)
    except FileNotFoundError:
        pass
    return data

def get_student_details(student_id):
    """Get all courses and marks for a student"""
    data = load_csv()
    student_data = [row for row in data if row['Student id'] == student_id]
    return student_data

def get_course_details(course_id):
    """Get all marks for a course"""
    data = load_csv()
    course_data = [row for row in data if row['Course id'] == course_id]
    return course_data

def generate_histogram(marks, course_id):
    """Generate histogram for course marks"""
    plt.figure(figsize=(8, 5))
    marks_int = [int(m) for m in marks]
    plt.hist(marks_int, bins=10, color='steelblue', edgecolor='black')
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.title(f'Histogram for Course {course_id}')
    plt.grid(axis='y', alpha=0.3)
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
    # POST request
    id_type = request.form.get('ID')
    id_value = request.form.get('id_value', '').strip()
    
    # Validate input
    if not id_type or not id_value:
        return render_template('error.html', message='Please select an option and enter an ID.')
    
    if id_type == 'student_id':
        student_data = get_student_details(id_value)
        if not student_data:
            return render_template('error.html', message=f'Student ID "{id_value}" not found.')
        
        total_marks = sum(int(row['Marks']) for row in student_data)
        return render_template('student_details.html', 
                             student_data=student_data, 
                             total_marks=total_marks)
    
    elif id_type == 'course_id':
        course_data = get_course_details(id_value)
        if not course_data:
            return render_template('error.html', message=f'Course ID "{id_value}" not found.')
        
        marks = [int(row['Marks']) for row in course_data]
        avg_marks = sum(marks) / len(marks)
        max_marks = max(marks)
        plot_url = generate_histogram(marks, id_value)
        
        return render_template('course_details.html',
                             avg_marks=round(avg_marks, 2),
                             max_marks=max_marks,
                             plot_url=plot_url)
    
    else:
        return render_template('error.html', message='Invalid selection.')

def run():
    app.run(debug=True)

if __name__ == '__main__':
    run()
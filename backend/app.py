from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from models import db, User, Student, Attendance, Fee, Activity, ProgressRecord, Homework, Classwork, Timetable, Notice, Feedback
from datetime import datetime, timedelta
from sqlalchemy import or_ as db_or, and_, func, case
import pandas as pd
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

jwt = JWTManager(app)
db.init_app(app)

# Create database tables and seed demo data
def create_tables_and_seed():
    with app.app_context():
        db.create_all()

        # Create demo students if missing
        demo_students = [
            {
                "name": "John Doe",
                "class_name": "10-A",
                "roll_number": "101",
                "parent_contact": "9876543210",
                "total_fees": 5000,
                "fees_paid": 3000,
            },
            {
                "name": "Jane Smith",
                "class_name": "9-B",
                "roll_number": "102",
                "parent_contact": "9876543211",
                "total_fees": 5000,
                "fees_paid": 4500,
            },
            {
                "name": "Bob Johnson",
                "class_name": "8-C",
                "roll_number": "103",
                "parent_contact": "9876543212",
                "total_fees": 5000,
                "fees_paid": 5000,
            }
        ]

        for student_data in demo_students:
            existing_student = Student.query.filter_by(roll_number=student_data["roll_number"]).first()
            if not existing_student:
                new_student = Student(
                    name=student_data["name"],
                    class_name=student_data["class_name"],
                    roll_number=student_data["roll_number"],
                    parent_contact=student_data["parent_contact"],
                    total_fees=student_data["total_fees"],
                    fees_paid=student_data["fees_paid"],
                )
                db.session.add(new_student)

        db.session.commit()

        # Ensure demo users exist
        demo_users = [
            {"email": "admin@school.com", "password": "password", "role": "admin", "student_id": None},
            {"email": "teacher@school.com", "password": "password", "role": "teacher", "student_id": None},
            {"email": "parent@school.com", "password": "password", "role": "parent", "student_id": 1},
        ]

        added_any = False
        for user_data in demo_users:
            existing_user = User.query.filter(func.lower(User.email) == user_data["email"].lower()).first()
            if not existing_user:
                new_user = User(
                    email=user_data["email"],
                    password=user_data["password"],
                    role=user_data["role"],
                    student_id=user_data["student_id"],
                )
                db.session.add(new_user)
                added_any = True

        if added_any:
            db.session.commit()
            print("Demo data seeded successfully.")
        else:
            print("Demo users already exist.")

# Initialize database on startup
create_tables_and_seed()

# Error handler
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "message": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500
    

@app.route('/')
def home():
    return jsonify({"message": "SES Impetus Backend API", "status": "running", "version": "1.0"})

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# ============ AUTHENTICATION & USER MANAGEMENT ============

# -------- LOGIN --------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"status": "fail", "message": "Email and password required"}), 400

        email = data["email"].strip().lower()
        password = data["password"].strip()
        user = User.query.filter(func.lower(User.email) == email).first()

        if user and user.password == password:
            access_token = create_access_token(
                identity=str(user.id), 
                additional_claims={
                    "role": user.role, 
                    "student_id": user.student_id,
                    "user_email": user.email
                }
            )
            return jsonify({
                "status": "success",
                "access_token": access_token,
                "role": user.role,
                "student_id": user.student_id,
                "user_id": user.id,
                "email": user.email
            }), 200
        else:
            return jsonify({"status": "fail", "message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"status": "fail", "message": "Email already exists"}), 409
        
        new_user = User(
            email=data["email"],
            password=data["password"],
            role=data.get("role", "parent"),
            student_id=data.get("student_id")
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "User registered successfully", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/user/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "student_id": user.student_id
    }), 200

# ============ DASHBOARD & STATISTICS ============

@app.route('/dashboard/admin-stats')
@jwt_required()
def admin_stats():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    stats = {
        "total_students": Student.query.count(),
        "total_users": User.query.count(),
        "total_fees_pending": db.session.query(func.sum(Fee.amount)).filter_by(payment_status='pending').scalar() or 0,
        "total_fees_paid": db.session.query(func.sum(Fee.amount)).filter_by(payment_status='paid').scalar() or 0,
        "attendance_rate": db.session.query(func.count(Attendance.id)).filter_by(status='present').scalar() or 0,
        "classes": list(set([s.class_name for s in Student.query.all()]))
    }
    return jsonify(stats), 200

@app.route('/dashboard/teacher-stats')
@jwt_required()
def teacher_stats():
    claims = get_jwt()
    if claims['role'] != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get all unique classes
    classes = list(set([s.class_name for s in Student.query.all()]))
    
    stats = {
        "classes": classes,
        "total_students": Student.query.count(),
        "pending_homeworks": Homework.query.filter_by(status='pending').count(),
        "recent_activities": Activity.query.count()
    }
    return jsonify(stats), 200

@app.route('/dashboard/parent-stats/<int:student_id>')
@jwt_required()
def parent_stats(student_id):
    claims = get_jwt()
    if claims['role'] != 'parent' or claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    stats = {
        "student_name": student.name,
        "class_name": student.class_name,
        "attendance_today": Attendance.query.filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.date == datetime.utcnow().date()
            )
        ).first().status if Attendance.query.filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.date == datetime.utcnow().date()
            )
        ).first() else "Not marked",
        "pending_fees": db.session.query(func.sum(Fee.amount)).filter(
            and_(Fee.student_id == student_id, Fee.payment_status == 'pending')
        ).scalar() or 0,
        "pending_homeworks": Homework.query.filter(
            and_(Homework.student_id == student_id, Homework.status == 'pending')
        ).count()
    }
    return jsonify(stats), 200

# ============ STUDENT MANAGEMENT ============
@app.route('/add_student', methods=['POST'])
@jwt_required()
def add_student():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json

        # Validate required fields
        if not data.get('name') or not data.get('class_name'):
            return jsonify({"error": "Name and class name are required"}), 400

        # Handle date_of_birth properly
        date_of_birth = None
        if data.get('date_of_birth') and data['date_of_birth'].strip():
            try:
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        new_student = Student(
            name=data['name'].strip(),
            class_name=data['class_name'].strip(),
            roll_number=data.get('roll_number', '').strip() if data.get('roll_number') else None,
            date_of_birth=date_of_birth,
            address=data.get('address', '').strip() if data.get('address') else None,
            parent_contact=data.get('parent_contact', '').strip() if data.get('parent_contact') else None,
            total_fees=float(data.get('total_fees', 0.0)),
            fees_paid=float(data.get('fees_paid', 0.0))
        )

        db.session.add(new_student)
        db.session.commit()

        return jsonify({"message": "Student added successfully", "student_id": new_student.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# -------- GET STUDENTS --------
@app.route('/students')
@jwt_required()
def get_students():
    claims = get_jwt()

    query = Student.query

    # Parents can only see their child's info
    if claims['role'] == 'parent' and claims['student_id']:
        query = query.filter_by(id=claims['student_id'])

    # Filter by class if provided
    class_filter = request.args.get('class')
    if class_filter:
        query = query.filter_by(class_name=class_filter)

    # Search by name or roll number
    search = request.args.get('search')
    if search:
        query = query.filter(
            db_or(
                Student.name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%')
            )
        )

    students = query.all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "class_name": s.class_name,
            "roll_number": s.roll_number,
            "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
            "address": s.address,
            "parent_contact": s.parent_contact,
            "fees_paid": s.fees_paid,
            "total_fees": s.total_fees
        } for s in students
    ]), 200

# -------- DELETE STUDENT --------
@app.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    student = Student.query.get(id)

    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted successfully"}), 200

    return jsonify({"error": "Student not found"}), 404

# -------- UPDATE STUDENT --------
@app.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_student(id):
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    student = Student.query.get(id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    try:
        student.name = data.get('name', student.name)
        student.class_name = data.get('class_name', student.class_name)
        student.roll_number = data.get('roll_number', student.roll_number)
        if data.get('date_of_birth'):
            student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        student.address = data.get('address', student.address)
        student.parent_contact = data.get('parent_contact', student.parent_contact)
        student.total_fees = data.get('total_fees', student.total_fees)
        student.fees_paid = data.get('fees_paid', student.fees_paid)

        db.session.commit()
        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ============ ATTENDANCE MANAGEMENT ============
@app.route('/attendance', methods=['POST'])
@jwt_required()
def mark_attendance():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json
        attendance = Attendance(
            student_id=data['student_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status=data['status']
        )
        db.session.add(attendance)
        db.session.commit()
        return jsonify({"message": "Attendance marked successfully", "id": attendance.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/attendance/<int:student_id>')
@jwt_required()
def get_attendance(student_id):
    claims = get_jwt()

    # Parents can only see their child's attendance
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    attendances = Attendance.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": a.id,
            "date": a.date.isoformat(),
            "status": a.status
        } for a in attendances
    ]), 200

@app.route('/attendance/bulk', methods=['POST'])
@jwt_required()
def bulk_attendance():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        for record in data['attendance_records']:
            attendance = Attendance(
                student_id=record['student_id'],
                date=date,
                status=record['status']
            )
            db.session.add(attendance)

        db.session.commit()
        return jsonify({"message": "Bulk attendance marked successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ============ FEES MANAGEMENT ============
@app.route('/fees', methods=['POST'])
@jwt_required()
def add_fee():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json
        fee = Fee(
            student_id=data['student_id'],
            amount=data['amount'],
            description=data['description'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date(),
            payment_status=data.get('payment_status', 'pending')
        )
        db.session.add(fee)
        db.session.commit()
        return jsonify({"message": "Fee record added successfully", "fee_id": fee.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/fees/<int:student_id>')
@jwt_required()
def get_fees(student_id):
    claims = get_jwt()

    # Parents can only see their child's fees
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    fees = Fee.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": f.id,
            "amount": f.amount,
            "description": f.description,
            "date": f.date.isoformat(),
            "payment_status": f.payment_status
        } for f in fees
    ]), 200

@app.route('/fees/pay/<int:fee_id>', methods=['PUT'])
@jwt_required()
def pay_fee(fee_id):
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher', 'parent']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        fee = Fee.query.get(fee_id)
        if not fee:
            return jsonify({"error": "Fee record not found"}), 404

        if claims['role'] == 'parent' and claims['student_id'] != fee.student_id:
            return jsonify({"error": "Unauthorized"}), 403

        fee.payment_status = 'paid'
        student = Student.query.get(fee.student_id)
        student.fees_paid += fee.amount
        db.session.commit()
        return jsonify({"message": "Fee paid successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ---------------- ACTIVITY/ACHIEVEMENT ENDPOINTS ----------------
@app.route('/activities', methods=['POST'])
@jwt_required()
def add_activity():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    activity = Activity(
        student_id=data['student_id'],
        title=data['title'],
        description=data['description'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date(),
        achievement_type=data.get('achievement_type', 'general')
    )
    db.session.add(activity)
    db.session.commit()
    return jsonify({"message": "Activity added successfully"})

@app.route('/activities/<int:student_id>')
@jwt_required()
def get_activities(student_id):
    claims = get_jwt()

    # Parents can only see their child's activities
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    activities = Activity.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "date": a.date.isoformat(),
            "achievement_type": a.achievement_type
        } for a in activities
    ])

# ============ PROGRESS TRACKING ============
@app.route('/progress', methods=['POST'])
@jwt_required()
def add_progress():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json
        progress = ProgressRecord(
            student_id=data['student_id'],
            subject=data['subject'],
            marks_obtained=data['marks_obtained'],
            total_marks=data['total_marks'],
            exam_type=data['exam_type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date(),
            remarks=data.get('remarks', '')
        )
        db.session.add(progress)
        db.session.commit()
        return jsonify({"message": "Progress record added successfully", "id": progress.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/progress/<int:student_id>')
@jwt_required()
def get_progress(student_id):
    claims = get_jwt()

    # Parents can only see their child's progress
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    progress_records = ProgressRecord.query.filter_by(student_id=student_id).all()
    return jsonify([{
        "id": p.id,
        "subject": p.subject,
        "marks_obtained": p.marks_obtained,
        "total_marks": p.total_marks,
        "exam_type": p.exam_type,
        "date": p.date.isoformat(),
        "remarks": p.remarks,
        "percentage": round((p.marks_obtained / p.total_marks) * 100, 2) if p.total_marks > 0 else 0
    } for p in progress_records])

# ============ ANALYTICS & REPORTS ============
@app.route('/analytics/students')
@jwt_required()
def student_analytics():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # Get student statistics
    total_students = Student.query.count()
    class_distribution = db.session.query(
        Student.class_name,
        func.count(Student.id).label('count')
    ).group_by(Student.class_name).all()

    fee_stats = db.session.query(
        func.sum(Student.fees_paid).label('total_paid'),
        func.sum(Student.total_fees - Student.fees_paid).label('total_pending')
    ).first()

    return jsonify({
        "total_students": total_students,
        "class_distribution": [{"class": c.class_name, "count": c.count} for c in class_distribution],
        "fee_summary": {
            "total_paid": fee_stats.total_paid or 0,
            "total_pending": fee_stats.total_pending or 0
        }
    })

@app.route('/analytics/attendance')
@jwt_required()
def attendance_analytics():
    claims = get_jwt()
    if claims['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    # Get attendance statistics for last 30 days
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)

    attendance_stats = db.session.query(
        Attendance.date,
        func.count(Attendance.id).label('total_records'),
        func.sum(case((Attendance.status == 'present', 1), else_=0)).label('present_count')
    ).filter(Attendance.date >= thirty_days_ago)\
     .group_by(Attendance.date)\
     .order_by(Attendance.date)\
     .all()

    return jsonify([{
        "date": stat.date.isoformat(),
        "total_records": stat.total_records,
        "present_count": stat.present_count or 0,
        "attendance_rate": round(((stat.present_count or 0) / stat.total_records) * 100, 2) if stat.total_records > 0 else 0
    } for stat in attendance_stats])

# ---------------- HOMEWORK ENDPOINTS ----------------
@app.route('/homework', methods=['POST'])
@jwt_required()
def add_homework():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    homework = Homework(
        student_id=data['student_id'],
        subject=data['subject'],
        title=data['title'],
        description=data['description'],
        assigned_date=datetime.strptime(data['assigned_date'], '%Y-%m-%d').date() if data.get('assigned_date') else datetime.utcnow().date(),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
        status=data.get('status', 'pending')
    )
    db.session.add(homework)
    db.session.commit()
    return jsonify({"message": "Homework assigned successfully"})

@app.route('/homework/<int:student_id>')
@jwt_required()
def get_homework(student_id):
    claims = get_jwt()

    # Parents can only see their child's homework
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    homeworks = Homework.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": h.id,
            "subject": h.subject,
            "title": h.title,
            "description": h.description,
            "assigned_date": h.assigned_date.isoformat(),
            "due_date": h.due_date.isoformat(),
            "status": h.status
        } for h in homeworks
    ])

@app.route('/homework/update/<int:homework_id>', methods=['PUT'])
@jwt_required()
def update_homework_status(homework_id):
    try:
        data = request.json
        homework = Homework.query.get(homework_id)
        if not homework:
            return jsonify({"error": "Homework not found"}), 404

        homework.status = data['status']
        db.session.commit()
        return jsonify({"message": "Homework status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ---------------- CLASSWORK ENDPOINTS ----------------
@app.route('/classwork', methods=['POST'])
@jwt_required()
def add_classwork():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    classwork = Classwork(
        student_id=data['student_id'],
        subject=data['subject'],
        title=data['title'],
        description=data['description'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date(),
        marks_obtained=data.get('marks_obtained'),
        total_marks=data.get('total_marks')
    )
    db.session.add(classwork)
    db.session.commit()
    return jsonify({"message": "Classwork added successfully"})

@app.route('/classwork/<int:student_id>')
@jwt_required()
def get_classwork(student_id):
    claims = get_jwt()

    # Parents can only see their child's classwork
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    classworks = Classwork.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": c.id,
            "subject": c.subject,
            "title": c.title,
            "description": c.description,
            "date": c.date.isoformat(),
            "marks_obtained": c.marks_obtained,
            "total_marks": c.total_marks
        } for c in classworks
    ])

# ---------------- TIMETABLE ENDPOINTS ----------------
@app.route('/timetable', methods=['POST'])
@jwt_required()
def add_timetable_entry():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    timetable = Timetable(
        class_name=data['class_name'],
        day=data['day'],
        period=data['period'],
        subject=data['subject'],
        teacher=data['teacher'],
        start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
        end_time=datetime.strptime(data['end_time'], '%H:%M').time()
    )
    db.session.add(timetable)
    db.session.commit()
    return jsonify({"message": "Timetable entry added successfully"})

@app.route('/timetable/<class_name>')
@jwt_required()
def get_timetable(class_name):
    timetable_entries = Timetable.query.filter_by(class_name=class_name).all()
    return jsonify([
        {
            "id": t.id,
            "day": t.day,
            "period": t.period,
            "subject": t.subject,
            "teacher": t.teacher,
            "start_time": t.start_time.strftime('%H:%M'),
            "end_time": t.end_time.strftime('%H:%M')
        } for t in timetable_entries
    ])

# ---------------- NOTICE ENDPOINTS ----------------
@app.route('/notices', methods=['POST'])
@jwt_required()
def add_notice():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    notice = Notice(
        title=data['title'],
        content=data['content'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date(),
        target_audience=data.get('target_audience', 'all')
    )
    db.session.add(notice)
    db.session.commit()
    return jsonify({"message": "Notice added successfully"})

@app.route('/notices')
@jwt_required()
def get_notices():
    claims = get_jwt()

    query = Notice.query

    # Filter notices based on user role
    if claims['role'] == 'parent':
        query = query.filter(db_or(Notice.target_audience == 'all', Notice.target_audience == 'parents'))
    elif claims['role'] == 'teacher':
        query = query.filter(db_or(Notice.target_audience == 'all', Notice.target_audience == 'teachers'))

    notices = query.all()
    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "date": n.date.isoformat(),
            "target_audience": n.target_audience
        } for n in notices
    ])

# ---------------- FEEDBACK ENDPOINTS ----------------
@app.route('/feedback', methods=['POST'])
@jwt_required()
def add_feedback():
    claims = get_jwt()
    if claims['role'] != 'parent':
        return jsonify({"error": "Only parents can submit feedback"}), 403

    data = request.json
    feedback = Feedback(
        student_id=claims['student_id'],
        parent_name=data['parent_name'],
        feedback_type=data['feedback_type'],
        subject=data['subject'],
        message=data['message'],
        date=datetime.utcnow().date(),
        status='pending'
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback submitted successfully"})

@app.route('/feedback/<int:student_id>')
@jwt_required()
def get_feedback(student_id):
    claims = get_jwt()

    # Parents can only see feedback for their child
    if claims['role'] == 'parent' and claims['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    # Teachers and admins can see all feedback
    feedbacks = Feedback.query.filter_by(student_id=student_id).all()
    return jsonify([
        {
            "id": f.id,
            "parent_name": f.parent_name,
            "feedback_type": f.feedback_type,
            "subject": f.subject,
            "message": f.message,
            "date": f.date.isoformat(),
            "status": f.status
        } for f in feedbacks
    ])

@app.route('/feedback/update/<int:feedback_id>', methods=['PUT'])
@jwt_required()
def update_feedback_status(feedback_id):
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify({"error": "Feedback not found"}), 404

    feedback.status = data.get('status', feedback.status)
    db.session.commit()
    return jsonify({"message": "Feedback status updated successfully"})

# ---------------- EXCEL IMPORT/EXPORT ENDPOINTS ----------------
@app.route('/export/students')
@jwt_required()
def export_students():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    students = Student.query.all()
    data = [{
        'ID': s.id,
        'Name': s.name,
        'Class': s.class_name,
        'Roll Number': s.roll_number,
        'Date of Birth': s.date_of_birth.isoformat() if s.date_of_birth else '',
        'Address': s.address,
        'Parent Contact': s.parent_contact,
        'Total Fees': s.total_fees,
        'Fees Paid': s.fees_paid
    } for s in students]

    df = pd.DataFrame(data)
    filename = f'students_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(filename, index=False)

    return jsonify({"message": "Students exported successfully", "filename": filename})

@app.route('/import/students', methods=['POST'])
@jwt_required()
def import_students():
    claims = get_jwt()
    if claims['role'] not in ['admin', 'teacher']:
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    df = pd.read_excel(file)
    imported_count = 0

    for _, row in df.iterrows():
        student = Student(
            name=row['Name'],
            class_name=row['Class'],
            roll_number=row.get('Roll Number'),
            date_of_birth=pd.to_datetime(row.get('Date of Birth')).date() if pd.notna(row.get('Date of Birth')) else None,
            address=row.get('Address'),
            parent_contact=row.get('Parent Contact'),
            total_fees=row.get('Total Fees', 0.0)
        )
        db.session.add(student)
        imported_count += 1

    db.session.commit()
    return jsonify({"message": f"Imported {imported_count} students successfully"})

    return jsonify({"message": f"Imported {imported_count} students successfully"})

# Initialize default users
with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        # Create admin user
        admin = User(role="admin", email="admin@ses.edu", password="admin123")
        db.session.add(admin)

        # Create teacher user
        teacher = User(role="teacher", email="teacher@ses.edu", password="teacher123")
        db.session.add(teacher)

        # Create a sample student and parent
        sample_student = Student(
            name="John Doe",
            class_name="10A",
            roll_number="001",
            date_of_birth=datetime(2010, 5, 15).date(),
            address="123 Main St, City",
            parent_contact="9876543210",
            total_fees=50000.0
        )
        db.session.add(sample_student)
        db.session.commit()  # Commit to get student ID

        # Create parent user linked to student
        parent = User(role="parent", email="parent@ses.edu", password="parent123", student_id=sample_student.id)
        db.session.add(parent)

        db.session.commit()
        print("Default users created successfully")

if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

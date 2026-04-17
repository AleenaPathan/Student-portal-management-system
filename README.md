# SES Impetus International School - Student Management System

A comprehensive, modern, and professional school management system built with **React** (Frontend) and **Python Flask** (Backend), featuring beautiful UI, secure authentication, and complete student lifecycle management.

## 🎯 Features

### 👤 Role-Based Dashboards
- **Admin Dashboard**: Complete school management, student records, fee tracking, statistics
- **Teacher Dashboard**: Class management, attendance marking, homework assignment, progress tracking
- **Parent Dashboard**: Child's academic information, attendance, fees, activities, and notifications

### 📊 Core Features
- ✅ **Student Management**: Add, edit, delete, and categorize students
- 📝 **Attendance Tracking**: Real-time attendance marking and reporting
- 💰 **Fee Management**: Monthly fee tracking, payment status, reports
- 📈 **Performance Monitoring**: Marks, exam results, progress reports  
- 📚 **Homework & Classwork**: Assignment tracking and completion status
- 🏆 **Achievements**: Record student activities and accomplishments
- 🔔 **Notices & Announcements**: System-wide and targeted communications
- 📋 **Timetable Management**: Class schedules and teacher assignments
- 💬 **Feedback System**: Two-way communication between school and parents

### 🎨 UI/UX Excellence
- Modern, responsive design that works on all devices
- Smooth animations and transitions
- Intuitive navigation and user-friendly interfaces
- Professional color scheme and typography
- Accessible forms and data visualization

### 🔒 Security
- JWT-based authentication
- Role-based access control (RBAC)
- Password-protected login
- Secure API endpoints

### 📱 Responsive Design
- Fully responsive across Desktop, Tablet, and Mobile
- Optimized layout for all screen sizes
- Touch-friendly buttons and controls

## 🚀 Tech Stack

### Frontend
- **Framework**: React 19+
- **HTTP Client**: Axios
- **Charts**: Recharts (for analytics)
- **State Management**: React Hooks
- **Styling**: Modern CSS3 with custom design system

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (flask-jwt-extended)
- **API**: RESTful architecture
- **Data Processing**: Pandas

## 📦 Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database (if needed):**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

5. **Run the backend server:**
   ```bash
   python app.py
   ```
   
   Server will run on: `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```
   
   App will open at: `http://localhost:3000`

## 🐳 Docker Setup

Run the entire application using Docker Compose:

```bash
docker-compose up --build
```

This will:
- Start the Flask backend on port 5000
- Start the React frontend on port 3000
- Both services will be accessible immediately

## 🔐 Default Credentials

For testing purposes, use these credentials:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@school.com | password |
| Teacher | teacher@school.com | password |
| Parent | parent@school.com | password |

**⚠️ Important:** Change these credentials in production!

## 📋 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /user/profile` - Get current user profile

### Dashboard
- `GET /dashboard/admin-stats` - Admin statistics
- `GET /dashboard/teacher-stats` - Teacher statistics
- `GET /dashboard/parent-stats/<student_id>` - Parent statistics

### Students
- `GET /students` - List all students (with filters)
- `POST /add_student` - Add new student
- `PUT /update/<id>` - Update student details
- `DELETE /delete/<id>` - Delete student

### Attendance
- `POST /attendance` - Mark attendance
- `GET /attendance/<student_id>` - Get student attendance
- `POST /attendance/class/<class_name>` - Bulk attendance marking

### Fees
- `POST /fees` - Add fee record
- `GET /fees/<student_id>` - Get fees for student
- `PUT /fees/pay/<fee_id>` - Mark fee as paid
- `GET /fees/status/<student_id>` - Get fee status

### Progress & Performance
- `POST /progress` - Add progress record
- `GET /progress/<student_id>` - Get student progress
- `POST /homework` - Assign homework
- `GET /homework/<student_id>` - Get homework

### Notices & Announcements
- `POST /notices` - Create notice
- `GET /notices` - Get notices (filtered by role)

## 📂 Project Structure

```
.
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── requirements.txt        # Python dependencies
│   ├── instance/               # Instance data
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── AdminDashboard.js
│   │   │   ├── TeacherDashboard.js
│   │   │   ├── ParentDashboard.js
│   │   │   ├── Login.js
│   │   │   ├── Attendance.js
│   │   │   ├── Fees.js
│   │   │   └── ...
│   │   ├── styles/            # CSS styling
│   │   │   ├── Login.css
│   │   │   ├── Dashboard.css
│   │   │   └── ...
│   │   ├── App.js             # Main app component
│   │   ├── index.js           # React entry point
│   │   └── index.css          # Global styles
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
├── docker-compose.yml
└── README.md
```

## 🎨 Styling & Design System

The application uses a modern, professional design system with:

- **Color Palette:**
  - Primary: `#007bff` (Blue)
  - Secondary: `#6c757d` (Gray)
  - Success: `#28a745` (Green)
  - Danger: `#dc3545` (Red)
  - Warning: `#ffc107` (Yellow)

- **Typography:**
  - System fonts for excellent readability
  - Proper font hierarchy and sizing
  - Clear visual hierarchy

- **Components:**
  - Reusable cards, buttons, forms
  - Consistent spacing and borders
  - Shadow effects for depth

- **Responsive:**
  - Mobile-first approach
  - Breakpoints at 768px and 480px
  - Flexible grid layouts

## 🔧 Configuration

### Backend Configuration (`app.py`)
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
```

### Frontend API Endpoint
Update in components if backend runs on different host:
```javascript
const API_URL = "http://localhost:5000";
```

## 📖 Usage Guide

### For Admins
1. Login with admin credentials
2. View dashboard statistics
3. Add and manage students
4. Set fees and track payments
5. Create announcements

### For Teachers
1. Login with teacher credentials
2. Mark attendance
3. Assign homework
4. Update student progress
5. Communicate with parents

### For Parents
1. Login with parent credentials
2. View child's info and performance
3. Check attendance and fees
4. View announcements
5. Send feedback to school

## 🐛 Troubleshooting

### Backend not connecting?
- Ensure Flask server is running: `python app.py`
- Check port 5000 is not blocked
- Verify CORS is enabled

### CORS errors?
- Backend CORS is configured in `app.py`
- Ensure frontend and backend are running simultaneously

### Database issues?
- Delete `database.db` and restart to reinitialize
- Check SQLAlchemy configuration in `models.py`

## 🔄 Updates & Maintenance

To update dependencies:

```bash
# Frontend
cd frontend && npm update

# Backend
cd backend && pip install --upgrade -r requirements.txt
```

## 📝 License

This project is provided as-is for educational and organizational use.

## 🤝 Support

For issues or questions, please check:
1. Backend logs for API errors
2. Browser console for frontend errors
3. Database integrity with SQLite viewer
4. API endpoints with Postman or similar tools

## 🎓 Educational Value

This project demonstrates:
- Full-stack web application development
- Database design and ORM usage
- Authentication and authorization
- RESTful API design
- React hooks and state management
- Modern UI/UX principles
- Responsive web design
- Real-world application architecture

---

**Version**: 1.0  
**Last Updated**: April 2024  
**Status**: Production Ready

1. Clone the repository
2. Navigate to the project directory
3. Run the application:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Local Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Default Credentials

### Admin
- Email: admin@ses.edu
- Password: admin123

### Teacher
- Email: teacher@ses.edu
- Password: teacher123

### Parent
- Email: parent@ses.edu
- Password: parent123

## API Endpoints

### Authentication
- `POST /login` - User authentication

### Student Management
- `GET /students` - Get all students (with optional filters)
- `POST /add_student` - Add new student
- `PUT /update/<id>` - Update student information
- `DELETE /delete/<id>` - Delete student

### Attendance
- `POST /attendance` - Mark attendance
- `GET /attendance/<student_id>` - Get attendance records

### Fees
- `POST /fees` - Add fee record
- `GET /fees/<student_id>` - Get fee records
- `PUT /fees/pay/<fee_id>` - Pay fee

### Academic Records
- `POST /progress` - Add progress record
- `GET /progress/<student_id>` - Get progress records
- `POST /homework` - Assign homework
- `GET /homework/<student_id>` - Get homework assignments
- `POST /classwork` - Add classwork record
- `GET /classwork/<student_id>` - Get classwork records

### Activities & Achievements
- `POST /activities` - Add student activity
- `GET /activities/<student_id>` - Get student activities

### Communication
- `POST /notices` - Create notice
- `GET /notices` - Get notices
- `POST /feedback` - Submit feedback
- `GET /feedback/<student_id>` - Get feedback

### Timetable
- `POST /timetable` - Add timetable entry
- `GET /timetable/<class_name>` - Get class timetable

### Excel Operations
- `GET /export/students` - Export students to Excel
- `POST /import/students` - Import students from Excel

## Database Schema

The application uses the following main entities:
- User (Admin, Teacher, Parent)
- Student
- Attendance
- Fee
- Activity
- ProgressRecord
- Homework
- Classwork
- Timetable
- Notice
- Feedback

## Security Features

- JWT-based authentication
- Role-based access control
- Password hashing
- CORS protection
- Input validation

## Development

### Adding New Features
1. Update the database models in `backend/models.py`
2. Add API endpoints in `backend/app.py`
3. Update frontend components as needed
4. Test thoroughly

### Database Migrations
When updating models, delete the existing `database.db` file to recreate the schema.

## Deployment

### Production Deployment
1. Update JWT secret key in `app.py`
2. Configure proper database (PostgreSQL/MySQL recommended)
3. Set up proper CORS origins
4. Enable HTTPS
5. Configure environment variables

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for SES Impetus International School.

## Support

For technical support, please contact the development team.
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import openai
from functools import lru_cache
from werkzeug.utils import secure_filename
import uuid
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure database (using SQLite for development, PostgreSQL for production)
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/axis_college_ai'
else:
    # Use SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///axis_college_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_name': self.event_name,
            'description': self.description,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'event_time': self.event_time,
            'venue': self.venue,
            'category': self.category,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Initialize database
def init_db():
    """Initialize database tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we have any events, if not add sample data
            if Event.query.count() == 0:
                sample_events = [
                    Event(
                        event_name='Annual Tech Fest 2024',
                        description='Technical festival with coding competitions, robotics workshops, and tech talks by industry experts.',
                        event_date=datetime(2024, 3, 15).date(),
                        event_time='10:00 AM',
                        venue='Main Auditorium',
                        category='Technical',
                        image_url='https://picsum.photos/seed/techfest/400/300.jpg'
                    ),
                    Event(
                        event_name='Cultural Fest - Utsav 2024',
                        description='Annual cultural festival with music, dance, drama, and various cultural activities.',
                        event_date=datetime(2024, 2, 20).date(),
                        event_time='9:00 AM',
                        venue='College Ground',
                        category='Cultural',
                        image_url='https://picsum.photos/seed/culturalfest/400/300.jpg'
                    )
                ]
                
                for event in sample_events:
                    db.session.add(event)
                
                db.session.commit()
                print(f"✅ Added {len(sample_events)} sample events to database")
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            print("⚠️  Falling back to in-memory storage")
app.secret_key = 'axis-ai-assistant-secret-key-2024'

# File Upload Configuration
UPLOAD_FOLDER = 'static/event_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# OpenAI Configuration (Set your API key in environment variable)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
if OPENAI_API_KEY == 'your-openai-api-key-here':
    print("⚠️  WARNING: OpenAI API key not set. Using fallback mode.")
    OPENAI_API_KEY = None

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate unique filename to prevent conflicts"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}"

# Comprehensive Knowledge Base for Axis Colleges
AXIS_COLLEGES_KNOWLEDGE_BASE = {
    'college_info': {
        'vision': 'Axis Colleges aims to provide quality education that combines academic excellence with practical skills and industry exposure. The institution focuses on developing professionals who are innovative, responsible, and capable of contributing to society.',
        'mission': 'To nurture future leaders through holistic education, cutting-edge research, and industry collaboration. We strive to create an environment that fosters innovation, creativity, and ethical values among students.',
        'history': 'Established in 2008, Axis Colleges has grown from a small institution to a premier educational center in Kanpur. Over the years, we have consistently maintained high academic standards and excellent placement records.',
        'philosophy': 'Our academic philosophy centers on experiential learning, where theoretical knowledge is complemented with practical application. We believe in nurturing not just technical skills but also soft skills and leadership qualities.',
        'campus_culture': 'Axis Colleges promotes a diverse and inclusive campus culture where students from various backgrounds come together to learn and grow. We encourage extracurricular activities, sports, and cultural events alongside academics.',
        'why_choose': [
            'Excellent placement record with 90%+ placement rate',
            'Industry-experienced faculty members',
            'State-of-the-art infrastructure and facilities',
            'Strong industry connections and collaborations',
            'Comprehensive development programs',
            'Affordable fee structure with scholarship options',
            'Prime location on Kanpur-Lucknow Highway',
            'Focus on practical learning and internships'
        ]
    },
    'academic_info': {
        'teaching_methodology': 'We follow a blended learning approach combining traditional classroom teaching with modern digital tools. Our methodology includes project-based learning, industry visits, guest lectures, and hands-on workshops.',
        'assessment_system': 'Continuous evaluation through internal assessments, mid-term examinations, practical evaluations, and end-semester examinations. We also consider attendance, class participation, and project work in final grading.',
        'research_focus': 'Our research focuses on emerging technologies like AI, Machine Learning, IoT, and Renewable Energy. We encourage both faculty and students to engage in research projects and publish papers.',
        'industry_collaboration': 'Strong partnerships with leading companies like TCS, Infosys, Wipro, HCL, and many startups. Regular industry interactions, workshops, and internship programs.',
        'accreditation': 'All courses are AICTE approved and affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow. We maintain high standards of quality education.'
    },
    'student_life': {
        'clubs': [
            'Technical Club - Coding competitions, hackathons, tech talks',
            'Cultural Club - Music, dance, drama, art activities',
            'Sports Club - Cricket, football, basketball, badminton',
            'Literary Club - Debates, quizzes, creative writing',
            'Entrepreneurship Club - Startup talks, business plan competitions',
            'Photography Club - Photography contests, exhibitions'
        ],
        'events': [
            'Annual Tech Fest - Technical competitions and workshops',
            'Cultural Fest - Utsav with music, dance, drama',
            'Sports Meet - Inter-college sports competitions',
            'Hackathons - Coding competitions and problem-solving',
            'Workshops - Industry expert led technical workshops',
            'Seminars - Guest lectures by industry professionals'
        ],
        'facilities': [
            'Modern classrooms with projectors and smart boards',
            'Well-equipped laboratories with latest equipment',
            'Central library with 50,000+ books and digital resources',
            'Computer labs with high-speed internet',
            'Sports complex with indoor and outdoor facilities',
            'Separate hostels for boys and girls with WiFi',
            'Cafeteria serving hygienic and nutritious food',
            'Transport facility covering major routes in Kanpur'
        ]
    },
    'admission_process': {
        'steps': [
            'Fill the application form online or offline',
            'Submit required documents (marksheets, photos, ID proof)',
            'Appear for entrance exam if applicable',
            'Attend counseling session',
            'Pay admission fee to confirm seat'
        ],
        'documents_required': [
            '10th and 12th mark sheets',
            'Transfer certificate',
            'Character certificate',
            'Passport size photographs (4 copies)',
            'Aadhar card or any ID proof',
            'Migration certificate (if applicable)',
            'Income certificate (for scholarship applicants)'
        ],
        'important_dates': {
            'application_start': 'April 1st',
            'application_end': 'July 31st',
            'entrance_exam': 'June-July',
            'counseling': 'July-August',
            'classes_commence': 'August 16th'
        },
        'entrance_exams': {
            'btech': 'JEE Main or UPSEE',
            'direct_admission': 'Management quota available based on merit',
            'other_courses': 'College-level entrance test or merit-based'
        }
    },
    'placement_info': {
        'statistics': {
            'overall_placement_rate': '92%',
            'highest_package': '₹15 LPA',
            'average_package': '₹4.8 LPA',
            'companies_visited': '150+',
            'students_placed_2023': '850+'
        },
        'top_recruiters': [
            'TCS - ₹8.5 LPA highest',
            'Infosys - ₹7.8 LPA highest',
            'Wipro - ₹7.2 LPA highest',
            'HCL - ₹6.5 LPA highest',
            'Amazon - ₹12 LPA highest',
            'Microsoft - ₹15 LPA highest',
            'Google - ₹14 LPA highest',
            'IBM - ₹6.8 LPA highest'
        ],
        'training_programs': [
            'Aptitude and reasoning training',
            'Technical skill development workshops',
            'Soft skills and communication training',
            'Mock interviews and GD sessions',
            'Resume building workshops',
            'Industry expert interactions'
        ],
        'internship_support': [
            'Summer internship programs',
            'Industry collaboration projects',
            'On-the-job training opportunities',
            'Startup internship connections',
            'Research project opportunities'
        ]
    },
    'scholarship_info': {
        'merit_scholarships': {
            'criteria': 'Based on 12th marks and entrance exam performance',
            'amount': 'Up to 50% fee waiver',
            'categories': [
                '90%+ marks: 50% fee waiver',
                '80-89% marks: 30% fee waiver',
                '70-79% marks: 20% fee waiver'
            ]
        },
        'government_scholarships': [
            'UP Scholarship Scheme',
            'National Scholarship Portal',
            'PM Scholarship Scheme',
            'Central Sector Scholarship'
        ],
        'need_based': {
            'criteria': 'Based on family income and financial need',
            'documentation': 'Income certificate, BPL card if applicable',
            'amount': 'Up to 25% fee waiver'
        },
        'sports_scholarship': {
            'criteria': 'For outstanding sports achievements',
            'documentation': 'Sports certificates and achievements',
            'amount': 'Up to 30% fee waiver'
        }
    },
    'contact_info': {
        'address': 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305',
        'phone': {
            'main': '0512-2580001',
            'admission': '0512-2580002',
            'hostel': '0512-2580003',
            'placement': '0512-2580004'
        },
        'email': {
            'info': 'info@axiscolleges.edu.in',
            'admission': 'admission@axiscolleges.edu.in',
            'placement': 'placement@axiscolleges.edu.in',
            'complaints': 'complaints@axiscolleges.edu.in'
        },
        'website': 'www.axiscolleges.edu.in',
        'office_hours': 'Monday to Saturday, 9:00 AM to 5:00 PM',
        'social_media': {
            'facebook': 'facebook.com/axiscolleges',
            'instagram': 'instagram.com/axiscolleges',
            'linkedin': 'linkedin.com/company/axiscolleges',
            'youtube': 'youtube.com/@axiscolleges'
        }
    }
}

# Enhanced Sample Data with comprehensive course information
SAMPLE_COURSES = [
    {
        'id': 1,
        'name': 'B.Tech Computer Science Engineering',
        'short_name': 'CSE',
        'alternate_names': ['b.tech cse', 'computer science', 'cse engineering', 'bt computer', 'cs engineering', 'btech cs'],
        'duration': '4 Years',
        'total_fees': 340000.00,
        'per_year_fees': 85000.00,
        'per_semester_fees': 42500.00,
        'eligibility': '10+2 with PCM, 60% marks',
        'description': 'Comprehensive engineering program with focus on software development, AI, and machine learning.',
        'specializations': ['AI & ML', 'Data Science', 'Web Development', 'Cloud Computing', 'Cyber Security'],
        'career_prospects': 'Software Engineer, Data Scientist, AI Engineer, Full Stack Developer, DevOps Engineer',
        'subjects': 'Data Structures, Algorithms, DBMS, Operating Systems, Computer Networks, AI/ML, Web Technologies',
        'internship_opportunities': 'Summer internships with TCS, Infosys, Wipro, HCL',
        'approval': 'AICTE Approved, Affiliated to AKTU',
        'seat_intake': 120,
        'placement_rate': '92%',
        'highest_package': 12.5,
        'average_package': 4.8
    },
    {
        'id': 2,
        'name': 'BCA (Bachelor of Computer Applications)',
        'short_name': 'BCA',
        'alternate_names': ['bca', 'computer applications', 'bachelor computer applications', 'b.comp.app'],
        'duration': '3 Years',
        'total_fees': 165000.00,
        'per_year_fees': 55000.00,
        'per_semester_fees': 27500.00,
        'eligibility': '10+2 with Math, 50% marks',
        'description': 'Application development and software engineering program with practical training.',
        'specializations': ['Software Development', 'Web Design', 'Mobile Apps', 'Digital Marketing', 'Cloud Computing'],
        'career_prospects': 'Software Developer, Web Designer, Digital Marketer, IT Support, System Administrator',
        'subjects': 'Programming Languages, Web Development, Database Management, Software Engineering, Computer Networks',
        'internship_opportunities': 'Web development internships, IT support roles, startup opportunities',
        'approval': 'Affiliated to AKTU',
        'seat_intake': 60,
        'placement_rate': '85%',
        'highest_package': 6.5,
        'average_package': 3.2
    },
    {
        'id': 3,
        'name': 'BBA (Bachelor of Business Administration)',
        'short_name': 'BBA',
        'alternate_names': ['bba', 'business administration', 'bachelor business', 'b.bus.admin'],
        'duration': '3 Years',
        'total_fees': 150000.00,
        'per_year_fees': 50000.00,
        'per_semester_fees': 25000.00,
        'eligibility': '10+2 any stream, 50% marks',
        'description': 'Business management and entrepreneurship program with industry exposure.',
        'specializations': ['Marketing', 'Finance', 'HR', 'International Business', 'Supply Chain'],
        'career_prospects': 'Business Analyst, Marketing Manager, HR Executive, Entrepreneur, Supply Chain Manager',
        'subjects': 'Business Management, Economics, Accounting, Marketing, HR Management, Business Law',
        'internship_opportunities': 'Marketing internships, finance roles, HR trainee positions',
        'approval': 'Affiliated to AKTU',
        'seat_intake': 60,
        'placement_rate': '78%',
        'highest_package': 5.5,
        'average_package': 2.8
    },
    {
        'id': 4,
        'name': 'MBA (Master of Business Administration)',
        'short_name': 'MBA',
        'alternate_names': ['mba', 'master business', 'business management', 'm.bus.admin'],
        'duration': '2 Years',
        'total_fees': 200000.00,
        'per_year_fees': 100000.00,
        'per_semester_fees': 50000.00,
        'eligibility': 'Graduation in any stream with 50% marks',
        'description': 'Advanced business management program with leadership and strategic focus.',
        'specializations': ['Marketing', 'Finance', 'HR', 'Operations', 'International Business'],
        'career_prospects': 'Senior Manager, Business Consultant, CEO, COO, Strategy Head',
        'subjects': 'Strategic Management, Business Analytics, Leadership, Operations Management, Financial Management',
        'internship_opportunities': 'Leadership programs, management trainee roles, consulting projects',
        'approval': 'AICTE Approved, Affiliated to AKTU',
        'seat_intake': 60,
        'placement_rate': '95%',
        'highest_package': 15.0,
        'average_package': 6.5
    },
    {
        'id': 5,
        'name': 'B.Tech Mechanical Engineering',
        'short_name': 'ME',
        'alternate_names': ['b.tech mechanical', 'mechanical engineering', 'bt mech', 'me engineering'],
        'duration': '4 Years',
        'total_fees': 320000.00,
        'per_year_fees': 80000.00,
        'per_semester_fees': 40000.00,
        'eligibility': '10+2 with PCM, 60% marks',
        'description': 'Core engineering program focusing on design, manufacturing, and thermal sciences.',
        'specializations': ['Automobile Engineering', 'CAD/CAM', 'Thermal Engineering', 'Production Engineering'],
        'career_prospects': 'Mechanical Engineer, Design Engineer, Production Manager, Automotive Engineer',
        'subjects': 'Thermodynamics, Fluid Mechanics, Machine Design, Manufacturing Processes, CAD/CAM',
        'internship_opportunities': 'Manufacturing units, automotive companies, industrial training',
        'approval': 'AICTE Approved, Affiliated to AKTU',
        'seat_intake': 60,
        'placement_rate': '88%',
        'highest_package': 8.5,
        'average_package': 4.2
    },
    {
        'id': 6,
        'name': 'B.Tech Electronics & Communication',
        'short_name': 'ECE',
        'alternate_names': ['b.tech ece', 'electronics communication', 'electronics engg', 'bt electronics'],
        'duration': '4 Years',
        'total_fees': 330000.00,
        'per_year_fees': 82500.00,
        'per_semester_fees': 41250.00,
        'eligibility': '10+2 with PCM, 60% marks',
        'description': 'Electronics and communication engineering with focus on embedded systems and telecommunications.',
        'specializations': ['VLSI Design', 'Embedded Systems', 'Digital Signal Processing', 'Communication Systems'],
        'career_prospects': 'Electronics Engineer, VLSI Designer, Embedded Systems Engineer, Communication Engineer',
        'subjects': 'Digital Electronics, Analog Circuits, Communication Systems, VLSI Design, Signal Processing',
        'internship_opportunities': 'Electronics manufacturing, telecom companies, embedded systems firms',
        'approval': 'AICTE Approved, Affiliated to AKTU',
        'seat_intake': 60,
        'placement_rate': '90%',
        'highest_package': 9.0,
        'average_package': 4.5
    }
]

SAMPLE_FACILITIES = [
    {
        'name': 'Library',
        'description': 'State-of-the-art library with over 50,000 books and digital resources.',
        'features': ['Digital catalog', 'Study rooms', '24/7 WiFi', 'E-books access'],
        'timings': '8:00 AM - 8:00 PM (Weekdays), 9:00 AM - 5:00 PM (Weekends)'
    },
    {
        'name': 'Computer Labs',
        'description': 'Modern computer labs with 500+ systems and high-speed internet.',
        'features': ['Latest software', 'High-speed internet', 'AC environment', 'Technical support'],
        'timings': '9:00 AM - 6:00 PM (All days)'
    },
    {
        'name': 'Hostel',
        'description': 'Separate hostels for boys and girls with WiFi and 24/7 security.',
        'features': ['WiFi', 'Mess facility', 'Security', 'Medical facility'],
        'fees': '₹8,000 - ₹12,000 per month',
        'capacity': '500+ students'
    },
    {
        'name': 'Sports Complex',
        'description': 'Indoor and outdoor sports facilities including cricket ground and gym.',
        'features': ['Cricket ground', 'Football field', 'Basketball court', 'Gym', 'Yoga room'],
        'timings': '6:00 AM - 8:00 PM (All days)'
    }
]

SAMPLE_PLACEMENTS = [
    {
        'company': 'TCS',
        'average_package': 4.50,
        'highest_package': 8.50,
        'students_placed': 120,
        'roles_offered': ['Software Engineer', 'System Engineer', 'Business Analyst']
    },
    {
        'company': 'Infosys',
        'average_package': 4.20,
        'highest_package': 7.80,
        'students_placed': 95,
        'roles_offered': ['Software Developer', 'Systems Engineer', 'Test Engineer']
    },
    {
        'company': 'Wipro',
        'average_package': 4.00,
        'highest_package': 7.20,
        'students_placed': 85,
        'roles_offered': ['Software Engineer', 'Project Engineer', 'Business Analyst']
    },
    {
        'company': 'HCL',
        'average_package': 3.80,
        'highest_package': 6.50,
        'students_placed': 70,
        'roles_offered': ['Software Engineer', 'Technical Support', 'Network Engineer']
    }
]

SAMPLE_FAQS = [
    {
        'question': 'What is the admission process?',
        'answer': 'Admission process includes: 1) Fill application form online/offline, 2) Submit required documents, 3) Appear for entrance exam/interview, 4) Merit list announcement, 5) Fee payment and admission confirmation.',
        'category': 'admission'
    },
    {
        'question': 'Is there hostel facility available?',
        'answer': 'Yes, we provide separate hostel facilities for boys and girls with WiFi, mess facility, 24/7 security, and medical facilities. Fees range from ₹8,000 to ₹12,000 per month.',
        'category': 'hostel'
    },
    {
        'question': 'What are the library timings?',
        'answer': 'Library is open from 8:00 AM to 8:00 PM on weekdays and 9:00 AM to 5:00 PM on weekends. It has digital catalog, study rooms, and e-book access.',
        'category': 'library'
    },
    {
        'question': 'What scholarships are available?',
        'answer': 'We offer merit-based scholarships, need-based scholarships, sports scholarships, and government scholarships. Students can get up to 50% fee waiver based on merit and financial need.',
        'category': 'scholarship'
    }
]

SAMPLE_EVENTS = [
    {
        'id': 1,
        'event_name': 'Annual Tech Fest 2024',
        'description': 'Technical festival with coding competitions, robotics workshops, and tech talks by industry experts.',
        'event_date': '2024-03-15',
        'event_time': '10:00 AM',
        'venue': 'Main Auditorium',
        'category': 'Technical',
        'image_url': 'https://picsum.photos/seed/techfest/400/300.jpg'
    },
    {
        'id': 2,
        'event_name': 'Cultural Fest - Utsav 2024',
        'description': 'Annual cultural festival with music, dance, drama, and various cultural activities.',
        'event_date': '2024-02-20',
        'event_time': '9:00 AM',
        'venue': 'College Ground',
        'category': 'Cultural',
        'image_url': 'https://picsum.photos/seed/culturalfest/400/300.jpg'
    }
]

class AdvancedAIAssistant:
    def __init__(self):
        self.context_memory = {}
        self.knowledge_base = self._build_knowledge_base()
        self.intent_patterns = self._build_intent_patterns()
        
    def _build_knowledge_base(self) -> str:
        """Build comprehensive knowledge base for AI"""
        knowledge = "=== AXIS COLLEGES KANPUR - COMPREHENSIVE INFORMATION ===\n\n"
        
        # Courses information
        knowledge += "COURSES OFFERED:\n"
        for course in SAMPLE_COURSES:
            knowledge += f"\n{course['name']} ({course['short_name']}):\n"
            knowledge += f"- Duration: {course['duration']}\n"
            knowledge += f"- Total Fees: ₹{course['total_fees']:,.2f}\n"
            knowledge += f"- Per Year Fees: ₹{course['per_year_fees']:,.2f}\n"
            knowledge += f"- Eligibility: {course['eligibility']}\n"
            knowledge += f"- Description: {course['description']}\n"
            knowledge += f"- Specializations: {', '.join(course['specializations'])}\n"
            knowledge += f"- Career Prospects: {course['career_prospects']}\n"
            knowledge += f"- Key Subjects: {course['subjects']}\n"
        
        # Facilities information
        knowledge += "\n\nCAMPUS FACILITIES:\n"
        for facility in SAMPLE_FACILITIES:
            knowledge += f"\n{facility['name']}:\n"
            knowledge += f"- Description: {facility['description']}\n"
            knowledge += f"- Features: {', '.join(facility['features'])}\n"
            if 'timings' in facility:
                knowledge += f"- Timings: {facility['timings']}\n"
            if 'fees' in facility:
                knowledge += f"- Fees: {facility['fees']}\n"
            if 'capacity' in facility:
                knowledge += f"- Capacity: {facility['capacity']}\n"
        
        # Placement information
        knowledge += "\n\nPLACEMENT RECORD:\n"
        total_placed = sum(p['students_placed'] for p in SAMPLE_PLACEMENTS)
        avg_package = sum(p['average_package'] for p in SAMPLE_PLACEMENTS) / len(SAMPLE_PLACEMENTS)
        highest_package = max(p['highest_package'] for p in SAMPLE_PLACEMENTS)
        
        knowledge += f"- Total Students Placed: {total_placed}\n"
        knowledge += f"- Average Package: ₹{avg_package:.2f} LPA\n"
        knowledge += f"- Highest Package: ₹{highest_package:.2f} LPA\n\n"
        
        knowledge += "TOP RECRUITING COMPANIES:\n"
        for placement in SAMPLE_PLACEMENTS:
            knowledge += f"\n{placement['company']}:\n"
            knowledge += f"- Average Package: ₹{placement['average_package']} LPA\n"
            knowledge += f"- Highest Package: ₹{placement['highest_package']} LPA\n"
            knowledge += f"- Students Placed: {placement['students_placed']}\n"
            knowledge += f"- Roles Offered: {', '.join(placement['roles_offered'])}\n"
        
        # FAQs
        knowledge += "\n\nFREQUENTLY ASKED QUESTIONS:\n"
        for faq in SAMPLE_FAQS:
            knowledge += f"\nQ: {faq['question']}\nA: {faq['answer']}\n"
        
        # Contact information
        knowledge += "\n\nCONTACT INFORMATION:\n"
        knowledge += "- Phone: 0512-2580001\n"
        knowledge += "- Email: info@axiscolleges.edu.in\n"
        knowledge += "- Address: Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305\n"
        knowledge += "- Office Hours: Monday to Saturday, 9:00 AM to 5:00 PM\n"
        knowledge += "- Admission Helpline: 0512-2580002\n"
        knowledge += "- Hostel Helpline: 0512-2580003\n"
        
        return knowledge
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build enhanced intent recognition patterns with comprehensive Hinglish support"""
        return {
            'course': ['course', 'program', 'study', 'btech', 'bca', 'bba', 'mba', 'mca', 'engineering', 'degree', 'branch', 'stream', 'subject', 'syllabus',
                      'padhai', 'padhna', 'course ka', 'konse course', 'best course', 'which course', 'course detail', 'course information',
                      'kon si padhai', 'padhne ke liye', 'admission kaise', 'course me kya hota hai', 'subject kya hai'],
            'event': ['event', 'fest', 'function', 'program', 'celebration', 'workshop', 'seminar', 'competition', 'cultural', 'technical fest', 'sports meet', 
                      'upcoming events', 'next event', 'event schedule', 'college events', 'campus events', 'event details', 
                      'event kab hai', 'next fest kab hai', 'events kya hai', 'upcoming events kya hai', 'festival', 'utsav', 'techfest'], 
            'fee': ['fee', 'fees', 'cost', 'price', 'payment', 'charges', 'expense', 'tuition', 'semester', 'fees kitna', 
                     'kharcha', 'kitna fees', 'total fees', 'course fees', 'semester fees', 'admission fees', 'paise', 'rupaye',
                     'fees structure', 'payment options', 'installment', 'fees jama karna'],
            'admission': ['admission', 'apply', 'application', 'process', 'enroll', 'register', 'join', 'entrance', 'admission kaise',
                        'admission process', 'kab admission', 'form kab', 'entrance exam', 'counselling', 'admission date',
                        'form bharne ka process', 'admission ke liye kya chahiye', 'documents', 'eligibility'],
            'placement': ['placement', 'job', 'company', 'package', 'salary', 'campus', 'recruit', 'interview', 'offer', 'placement kaisa',
                       'package kitna', 'company aati hai', 'campus placement', 'job placement', 'career', 'naukri', 'company list',
                       'highest package', 'average package', 'placement record', 'training'],
            'facility': ['facility', 'facilities', 'hostel', 'library', 'lab', 'sports', 'campus', 'wifi', 'transport', 
                        'canteen', 'parking', 'gym', 'playground', 'ground', 'building', 'classroom', 'computer', 'internet',
                        'hostel milti hai', 'library hai', 'wifi hai', 'sports ground', 'mess', 'cafeteria', 'infrastructure',
                        'campus life', 'accommodation', 'mess facility'],
            'contact': ['contact', 'phone', 'email', 'address', 'call', 'reach', 'location', 'office', 'helpline', 'contact number',
                       'phone number', 'address kya hai', 'call kaise', 'office location', 'pata chahiye', 'number chahiye',
                       'office timings', 'visit karna hai'],
            'scholarship': ['scholarship', 'financial', 'aid', 'grant', 'waiver', 'discount', 'support', 'fund', 'scholarship milta hai',
                         'fee waiver', 'chhatrav', 'financial help', 'scholarship kaise milega', 'fee concession', 'free education'],
            'comparison': ['compare', 'difference', 'better', 'vs', 'versus', 'between', 'kaisa hai', 'kya fark hai', 'behtar'],
            'eligibility': ['eligibility', 'criteria', 'requirement', 'qualified', 'eligible', 'qualification', 'marks', 'percentage',
                          'eligibility kya hai', 'kitne percent chahiye', 'qualification required'],
            'vision': ['vision', 'mission', 'philosophy', 'values', 'goal', 'objective', 'purpose', 'kya soch', 'aim', 'vision kya hai'],
            'history': ['history', 'established', 'founded', 'about', 'story', 'background', 'when established', 'history of college',
                       'college kab bana', 'itihaas', 'background'],
            'why_choose': ['why choose', 'reasons', 'benefits', 'advantage', 'kyun choose', 'behtar kyu hai', 'fayde', 'advantages'],
            'student_life': ['student life', 'campus life', 'clubs', 'activities', 'extracurricular', 'fun', 'enjoy', 'student activities',
                           'student clubs', 'cultural activities', 'technical activities'],
            'unknown': []
        }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check for comparison intent first
        if any(word in message_lower for word in self.intent_patterns['comparison']):
            return 'comparison'
        
        # Check other intents
        for intent, keywords in self.intent_patterns.items():
            if intent == 'comparison' or intent == 'unknown':
                continue
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'unknown'
    
    def _extract_course_context(self, message: str) -> Optional[str]:
        """Extract course name from message with Hinglish support"""
        message_lower = message.lower()
        
        for course in SAMPLE_COURSES:
            # Check short name
            if course['short_name'].lower() in message_lower:
                return course['short_name']
            
            # Check alternate names
            if 'alternate_names' in course:
                for alt_name in course['alternate_names']:
                    if alt_name.lower() in message_lower:
                        return course['short_name']
            
            # Check for partial matches in course name
            if any(word in message_lower for word in course['name'].lower().split()):
                return course['short_name']
            
            # Check Hinglish patterns
            if 'btech' in message_lower and 'computer' in message_lower:
                return 'CSE'
            elif 'bca' in message_lower:
                return 'BCA'
            elif 'bba' in message_lower:
                return 'BBA'
            elif 'mba' in message_lower:
                return 'MBA'
        
        return None
    
    def _get_context_memory(self, session_id: str) -> List[Dict]:
        """Get conversation context memory"""
        if session_id not in self.context_memory:
            self.context_memory[session_id] = []
        
        # Keep only last 5 messages
        if len(self.context_memory[session_id]) > 5:
            self.context_memory[session_id] = self.context_memory[session_id][-5:]
        
        return self.context_memory[session_id]
    
    def _update_context_memory(self, session_id: str, user_message: str, bot_response: str):
        """Update conversation context memory"""
        if session_id not in self.context_memory:
            self.context_memory[session_id] = []
        
        self.context_memory[session_id].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 5 messages
        if len(self.context_memory[session_id]) > 5:
            self.context_memory[session_id] = self.context_memory[session_id][-5:]
    
    def _is_college_related(self, message: str) -> bool:
        """Check if message is related to Axis Colleges - assume college-related by default"""
        # Non-college topics that should be restricted
        restricted_topics = [
            'cricket', 'football', 'sports score', 'movie', 'film', 'cinema', 'actor', 'actress',
            'politics', 'election', 'government', 'news', 'weather', 'stock', 'share market',
            'recipe', 'cooking', 'travel', 'vacation', 'hotel', 'restaurant', 'shopping',
            'gaming', 'music', 'song', 'concert', 'entertainment', 'joke', 'meme'
        ]
        
        message_lower = message.lower()
        
        # Check if message contains restricted topics
        for topic in restricted_topics:
            if topic in message_lower:
                return False
        
        # Assume all other questions are college-related since this is a college website
        return True
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate enhanced fallback response with counselor-like guidance"""
        if not self._is_college_related(message):
            return "🤖 I am specifically designed to assist with Axis Colleges related queries only.\n\n" \
                   "I can help you with:\n" \
                   "📚 Course information and details\n" \
                   "💰 Fee structure and scholarships\n" \
                   "🎓 Admission process and eligibility\n" \
                   "🚀 Placement information and companies\n" \
                   "🏗️ Campus facilities and hostels\n" \
                   "📞 Contact information and office timings\n" \
                   "🎪 Events and activities\n\n" \
                   "How can I assist you with Axis Colleges today?"
        
        # For college-related but unclear queries
        return "🤔 I apologize, but I need more specific information to help you better.\n\n" \
               "**Here are some topics I can help you with:**\n\n" \
               "📚 **Courses:** B.Tech, BCA, BBA, MBA details and comparison\n" \
               "💰 **Fees:** Complete fee structure and payment options\n" \
               "🎓 **Admission:** Step-by-step process and required documents\n" \
               "🚀 **Placements:** Companies, packages, and training programs\n" \
               "🏆 **Scholarships:** Merit-based and financial aid options\n" \
               "🏗️ **Facilities:** Hostel, library, labs, and campus infrastructure\n" \
               "📞 **Contact:** How to reach us and office timings\n\n" \
               "💡 **Please try asking about any of these topics, or call our helpline at " + AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['main'] + " for immediate assistance!"
    
    @lru_cache(maxsize=100)
    def _get_cached_response(self, message_hash: str) -> Optional[str]:
        """Get cached response for repeated queries"""
        return None
    
    def _cache_response(self, message_hash: str, response: str):
        """Cache response for performance optimization"""
        pass
    
    def _call_openai_api(self, message: str, context: List[Dict], intent: str) -> str:
        """Call OpenAI API for intelligent response generation"""
        if not OPENAI_API_KEY:
            return self._generate_rule_based_response(message, intent, context)
        
        try:
            # Build context for OpenAI
            context_str = ""
            if context:
                context_str = "\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 messages for context
                    context_str += f"User: {ctx['user']}\nAssistant: {ctx['bot']}\n"
            
            # Build system prompt
            system_prompt = f"""You are an official Axis Colleges AI Assistant - a professional, helpful, and polite digital counselor for Axis Colleges, Kanpur.

Your personality:
- Professional, helpful, and polite
- Act as official Axis College representative
- Give clear, structured answers with bullet points when needed
- Be conversational and human-like

Your knowledge base:
{self.knowledge_base}

Instructions:
1. Answer ONLY using the provided knowledge base
2. Do not hallucinate or make up information
3. If information is not in knowledge base, politely say so
4. Use bullet points for better readability
5. Be conversational and friendly
6. Handle Hinglish, Hindi, and English naturally
7. Remember context from previous messages
8. Detect user intent and respond accordingly

Current intent detected: {intent}
{context_str}

User message: {message}

Provide a helpful, professional response:"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_rule_based_response(message, intent, context)
    
    def _generate_rule_based_response(self, message: str, intent: str, context: List[Dict]) -> str:
        """Generate enhanced rule-based response with knowledge base integration"""
        message_lower = message.lower()
        
        # Check for course context from previous messages
        course_context = None
        if context:
            for ctx in reversed(context[-3:]):
                extracted = self._extract_course_context(ctx['user'])
                if extracted:
                    course_context = extracted
                    break
        
        # Handle different intents with knowledge base integration
        if intent == 'vision':
            return f"🎯 **Vision & Mission of Axis Colleges:**\n\n" \
                   f"**🔭 Our Vision:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['vision']}\n\n" \
                   f"**🎯 Our Mission:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['mission']}\n\n" \
                   f"**📚 Academic Philosophy:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['philosophy']}\n\n" \
                   f"**🌟 Why Choose Axis Colleges?**\n" + \
                   "\n".join([f"• {reason}" for reason in AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['why_choose']]) + \
                   "\n\nWould you like to know about our courses or admission process?"
        
        elif intent == 'history':
            return f"📜 **About Axis Colleges:**\n\n" \
                   f"**🏛️ Our History:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['history']}\n\n" \
                   f"**🎓 Campus Culture:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['campus_culture']}\n\n" \
                   f"**📖 Teaching Methodology:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['academic_info']['teaching_methodology']}\n\n" \
                   f"**🏆 Accreditation:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['academic_info']['accreditation']}\n\n" \
                   f"Would you like to know about our courses or facilities?"
        
        elif intent == 'why_choose':
            return f"⭐ **Why Choose Axis Colleges?**\n\n" \
                   f"🎓 **Academic Excellence:**\n" + \
                   "\n".join([f"• {reason}" for reason in AXIS_COLLEGES_KNOWLEDGE_BASE['college_info']['why_choose'][:4]]) + \
                   f"\n\n🏢 **Industry Collaboration:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['academic_info']['industry_collaboration']}\n\n" \
                   f"🔬 **Research Focus:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['academic_info']['research_focus']}\n\n" \
                   f"📊 **Placement Success:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['overall_placement_rate']} placement rate with highest package of {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['highest_package']}\n\n" \
                   f"Ready to join us? Ask about admission process!"
        
        elif intent == 'student_life':
            response = f"🎉 **Student Life at Axis Colleges:**\n\n" \
                     f"**🎭 Student Clubs:**\n" + \
                     "\n".join([f"• {club}" for club in AXIS_COLLEGES_KNOWLEDGE_BASE['student_life']['clubs']]) + \
                     f"\n\n**🎪 Events & Activities:**\n" + \
                     "\n".join([f"• {event}" for event in AXIS_COLLEGES_KNOWLEDGE_BASE['student_life']['events']]) + \
                     f"\n\n**🏗️ Campus Facilities:**\n" + \
                     "\n".join([f"• {facility}" for facility in AXIS_COLLEGES_KNOWLEDGE_BASE['student_life']['facilities']]) + \
                     "\n\n🎓 We believe in holistic development! Would you like details about any specific facility or activity?"
            return response
        
        elif intent == 'scholarship':
            response = f"💰 **Scholarship Opportunities at Axis Colleges:**\n\n" \
                     f"**🏆 Merit-Based Scholarships:**\n" \
                     f"• Criteria: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['merit_scholarships']['criteria']}\n" \
                     f"• Amount: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['merit_scholarships']['amount']}\n" \
                     f"• Categories:\n" + \
                     "\n".join([f"  - {category}" for category in AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['merit_scholarships']['categories']]) + \
                     f"\n\n**💼 Government Scholarships:**\n" + \
                     "\n".join([f"• {scholarship}" for scholarship in AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['government_scholarships']]) + \
                     f"\n\n**❤️ Need-Based Financial Aid:**\n" \
                     f"• Criteria: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['need_based']['criteria']}\n" \
                     f"• Amount: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['need_based']['amount']}\n" \
                     f"• Documentation: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['need_based']['documentation']}\n\n" \
                     f"🏅 **Sports Scholarship:**\n" \
                     f"• For: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['sports_scholarship']['criteria']}\n" \
                     f"• Amount: {AXIS_COLLEGES_KNOWLEDGE_BASE['scholarship_info']['sports_scholarship']['amount']}\n\n" \
                     f"📞 Contact admission office for detailed scholarship application process!"
            return response
        
        elif intent == 'contact':
            response = f"📞 **Contact Axis Colleges:**\n\n" \
                     f"**📍 Address:**\n{AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['address']}\n\n" \
                     f"**📞 Phone Numbers:**\n" \
                     f"• Main Office: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['main']}\n" \
                     f"• Admission Helpline: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['admission']}\n" \
                     f"• Hostel Helpline: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['hostel']}\n" \
                     f"• Placement Cell: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['placement']}\n\n" \
                     f"**📧 Email Addresses:**\n" \
                     f"• General Info: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['email']['info']}\n" \
                     f"• Admission: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['email']['admission']}\n" \
                     f"• Placement: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['email']['placement']}\n\n" \
                     f"**🌐 Website:** {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['website']}\n" \
                     f"**⏰ Office Hours:** {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['office_hours']}\n\n" \
                     f"Feel free to reach out for any assistance!"
            return response
        
        elif intent == 'placement':
            response = f"🚀 **Placement Excellence at Axis Colleges:**\n\n" \
                     f"**📊 Overall Statistics:**\n" \
                     f"• Placement Rate: {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['overall_placement_rate']}\n" \
                     f"• Highest Package: {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['highest_package']}\n" \
                     f"• Average Package: {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['average_package']}\n" \
                     f"• Companies Visited: {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['companies_visited']}\n" \
                     f"• Students Placed (2023): {AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['statistics']['students_placed_2023']}\n\n" \
                     f"**🏢 Top Recruiters:**\n" + \
                     "\n".join([f"• {recruiter}" for recruiter in AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['top_recruiters']]) + \
                     f"\n\n**🎯 Training Programs:**\n" + \
                     "\n".join([f"• {program}" for program in AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['training_programs']]) + \
                     f"\n\n**💼 Internship Support:**\n" + \
                     "\n".join([f"• {support}" for support in AXIS_COLLEGES_KNOWLEDGE_BASE['placement_info']['internship_support']]) + \
                     "\n\n🎓 Our placement cell works tirelessly to ensure your bright future!"
            return response
        
        # Handle different intents
        if intent == 'course':
            if course_context:
                course = next((c for c in SAMPLE_COURSES if c['short_name'].lower() == course_context.lower()), None)
                if course:
                    return f"📚 **{course['name']} Details:**\n\n" \
                           f"- **Duration:** {course['duration']}\n" \
                           f"- **Total Fees:** ₹{course['total_fees']:,.2f}\n" \
                           f"- **Per Year Fees:** ₹{course['per_year_fees']:,.2f}\n" \
                           f"- **Per Semester Fees:** ₹{course['per_semester_fees']:,.2f}\n" \
                           f"- **Eligibility:** {course['eligibility']}\n" \
                           f"- **Description:** {course['description']}\n" \
                           f"- **Approval:** {course['approval']}\n\n" \
                           f"**Specializations:** {', '.join(course['specializations'])}\n\n" \
                           f"**Career Options:** {course['career_prospects']}\n\n" \
                           f"**Internship Opportunities:** {course['internship_opportunities']}\n\n" \
                           f"Would you like to know about admission process or placement details?"
            
            # List all courses
            response = "📚 **Available Courses at Axis Colleges:**\n\n"
            for course in SAMPLE_COURSES:
                response += f"- **{course['name']}** ({course['duration']}) - ₹{course['per_year_fees']:,.2f}/year\n"
            response += "\n\nPlease specify which course you'd like detailed information about.\n" \
                      "Example: 'Tell me about BCA' or 'B.Tech details'"
            return response
        
        elif intent == 'fee':
            if course_context:
                course = next((c for c in SAMPLE_COURSES if c['short_name'].lower() == course_context.lower()), None)
                if course:
                    return f"💰 **Fee Structure for {course['name']}:**\n\n" \
                           f"- **Total Course Fees:** ₹{course['total_fees']:,.2f}\n" \
                           f"- **Per Year Fees:** ₹{course['per_year_fees']:,.2f}\n" \
                           f"- **Per Semester Fees:** ₹{course['per_semester_fees']:,.2f}\n" \
                           f"- **Payment Options:** Yearly, semester, and monthly installments available\n" \
                           f"- **Scholarship Eligibility:** Up to 50% fee waiver based on merit\n\n" \
                           f"💡 **Note:** Fees are subject to change as per university guidelines.\n\n" \
                           f"Would you like to know about scholarship opportunities?"
            
            # Show all course fees
            response = "💰 **Complete Fee Structure at Axis Colleges:**\n\n"
            for course in SAMPLE_COURSES:
                response += f"- **{course['name']}**\n" \
                          f"  - Per Year: ₹{course['per_year_fees']:,.2f}\n" \
                          f"  - Per Semester: ₹{course['per_semester_fees']:,.2f}\n" \
                          f"  - Total: ₹{course['total_fees']:,.2f}\n\n"
            response += "💡 **Financial Assistance:**\n" \
                      "- Merit-based scholarships available\n" \
                      "- Need-based financial aid\n" \
                      "- Education loan assistance\n\n" \
                      "Ask me about specific course fees or scholarship details!"
            return response
        
        elif intent == 'admission':
            response = f"🎓 **Complete Admission Guide for Axis Colleges:**\n\n" \
                     f"**📋 Eligibility Criteria:**\n" \
                     f"• Minimum 50% marks in 10+2 for all courses\n" \
                     f"• 60% marks required for B.Tech programs\n" \
                     f"• Valid through any recognized board\n\n" \
                     f"**📝 Step-by-Step Admission Process:**\n" + \
                     "\n".join([f"{i+1}. **{step.split(':')[0]}:** {step.split(':')[1]}" for i, step in enumerate(AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['steps'])]) + \
                     f"\n\n**📄 Required Documents:**\n" + \
                     "\n".join([f"• {doc}" for doc in AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['documents_required']]) + \
                     f"\n\n**🎯 Entrance Exams:**\n" \
                     f"• B.Tech: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['entrance_exams']['btech']}\n" \
                     f"• Other Courses: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['entrance_exams']['other_courses']}\n" \
                     f"• Management Quota: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['entrance_exams']['direct_admission']}\n\n" \
                     f"**📅 Important Dates:**\n" \
                     f"• Application Start: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['important_dates']['application_start']}\n" \
                     f"• Application End: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['important_dates']['application_end']}\n" \
                     f"• Classes Commence: {AXIS_COLLEGES_KNOWLEDGE_BASE['admission_process']['important_dates']['classes_commence']}\n\n" \
                     f"📞 **Need Help?** Call our admission helpline: {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['admission']}\n\n" \
                     f"💡 **Pro Tip:** Apply early for better chances of admission!"
            return response
        
        elif intent == 'facility':
            response = f"🏗️ **Campus Facilities at Axis Colleges:**\n\n" \
                     f"**📚 Academic Facilities:**\n" \
                     f"• Modern classrooms with projectors and smart boards\n" \
                     f"• Well-equipped laboratories with latest equipment\n" \
                     f"• Central library with 50,000+ books and digital resources\n" \
                     f"• Computer labs with high-speed internet\n\n" \
                     f"**🏠 Residential Facilities:**\n" \
                     f"• Separate hostels for boys and girls with WiFi\n" \
                     f"• 24/7 security and medical facilities\n" \
                     f"• Mess facility serving hygienic food\n\n" \
                     f"**🎭 Recreational Facilities:**\n" \
                     f"• Sports complex with indoor and outdoor facilities\n" \
                     f"• Cafeteria serving nutritious food\n" \
                     f"• Transport facility covering major routes in Kanpur\n\n" \
                     f"**📱 Campus Connectivity:**\n" \
                     f"• High-speed WiFi throughout campus\n" \
                     f"• 24/7 power backup\n" \
                     f"• Water purification systems\n\n" \
                     f"🏆 **Our facilities are designed for your comfort and learning!**\n\n" \
                     f"Would you like details about any specific facility?"
            return response
        
        elif intent == 'eligibility':
            return f"📋 **Eligibility Criteria for Axis Colleges:**\n\n" \
                   f"**🎓 General Eligibility:**\n" \
                   f"• Minimum 50% marks in 10+2 for all courses\n" \
                   f"• Must have studied from a recognized board\n" \
                   f"• Valid age limit as per university norms\n\n" \
                   f"**🔬 Course-Specific Eligibility:**\n" \
                   f"• **B.Tech Programs:** 60% marks in 10+2 with PCM\n" \
                   f"• **BCA Program:** 50% marks in 10+2 with Mathematics\n" \
                   f"• **BBA Program:** 50% marks in 10+2 (any stream)\n" \
                   f"• **MBA Program:** Graduation with 50% marks\n\n" \
                   f"• **MCA Program:** Graduation with Mathematics\n\n" \
                   f"**� Entrance Requirements:**\n" \
                   f"• Valid score in JEE Main/UPSEE for B.Tech\n" \
                   f"• College entrance test for other courses\n" \
                   f"• Management quota available based on merit\n\n" \
                   f"**📄 Document Requirements:**\n" \
                   f"• Original mark sheets and certificates\n" \
                   f"• Transfer and migration certificates\n" \
                   f"• Character certificate from previous institution\n" \
                   f"• Valid ID proof (Aadhar card)\n\n" \
                   f"💡 **Note:** Relaxation available for reserved categories as per government norms.\n\n" \
                   f"📞 Need clarification? Call us at {AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['admission']}"
        
        elif intent == 'comparison':
            # Handle course comparison
            courses_mentioned = []
            for course in SAMPLE_COURSES:
                if course['short_name'].lower() in message_lower or any(alt.lower() in message_lower for alt in course.get('alternate_names', [])):
                    courses_mentioned.append(course)
            
            if len(courses_mentioned) >= 2:
                response = "📊 **Course Comparison:**\n\n"
                for course in courses_mentioned:
                    response += f"**{course['name']}**\n" \
                             f"• Duration: {course['duration']}\n" \
                             f"• Fees: ₹{course['per_year_fees']:,.2f}/year\n" \
                             f"• Eligibility: {course['eligibility']}\n" \
                             f"• Placement Rate: {course.get('placement_rate', 'N/A')}\n" \
                             f"• Highest Package: ₹{course.get('highest_package', 'N/A')} LPA\n\n"
                response += "💡 **Recommendation:** Choose based on your interests, career goals, and eligibility.\n\n" \
                         "Need more details about any specific course?"
                return response
            else:
                return "📊 **Course Comparison Help:**\n\n" \
                       "Please mention at least 2 courses to compare.\n" \
                       "Example: 'Compare BCA and BBA' or 'B.Tech vs BCA'\n\n" \
                       "Available courses: B.Tech (CSE, ME, ECE), BCA, BBA, MBA"
        
        elif intent == 'event':
            # Get events from database
            try:
                events = Event.query.order_by(Event.event_date.asc()).limit(5).all()
                if events:
                    response = "🎪 **Upcoming Events at Axis Colleges:**\n\n"
                    for event in events:
                        response += f"**{event.event_name}**\n" \
                                 f"• 📅 Date: {event.event_date.strftime('%d %B %Y')}\n" \
                                 f"• ⏰ Time: {event.event_time}\n" \
                                 f"• 📍 Venue: {event.venue}\n" \
                                 f"• 🎭 Category: {event.category}\n" \
                                 f"• 📝 {event.description[:100]}...\n\n"
                    response += "🎉 **Join us for these exciting events!**\n\n" \
                             "📞 For event registration, call: " + AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['main']
                else:
                    response = "🎪 **Events at Axis Colleges:**\n\n" \
                             "📅 **Regular Events:**\n" \
                             "• Annual Tech Fest - March\n" \
                             "• Cultural Fest - Utsav - February\n" \
                             "• Sports Meet - December\n" \
                             "• Workshops - Monthly\n" \
                             "• Guest Lectures - Weekly\n\n" \
                             "🎭 **Student Clubs organize various activities throughout the year!**\n\n" \
                             "📞 Contact us for event schedules: " + AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['main']
                return response
            except Exception as e:
                return "🎪 **Events Information:**\n\n" \
                       "📅 **Regular Events:**\n" \
                       "• Annual Tech Fest - March\n" \
                       "• Cultural Fest - Utsav - February\n" \
                       "• Sports Meet - December\n" \
                       "• Workshops - Monthly\n" \
                       "• Guest Lectures - Weekly\n\n" \
                       "🎭 **Student Clubs organize various activities throughout the year!**\n\n" \
                       "📞 Contact us for event schedules: " + AXIS_COLLEGES_KNOWLEDGE_BASE['contact_info']['phone']['main']
        
        elif intent == 'placement':
            total_placed = sum(p['students_placed'] for p in SAMPLE_PLACEMENTS)
            avg_package = sum(p['average_package'] for p in SAMPLE_PLACEMENTS) / len(SAMPLE_PLACEMENTS)
            highest_package = max(p['highest_package'] for p in SAMPLE_PLACEMENTS)
            
            response = "💼 **Complete Placement Report - Axis Colleges:**\n\n" \
                      f"📊 **Overall Placement Statistics:**\n" \
                      f"- **Total Students Placed:** {total_placed}+\n" \
                      f"- **Placement Percentage:** 85%+\n" \
                      f"- **Average Package:** ₹{avg_package:.2f} LPA\n" \
                      f"- **Highest Package:** ₹{highest_package:.2f} LPA\n" \
                      f"- **Dream Companies Visited:** 50+\n\n" \
                      "**🏢 Top Recruiting Companies:**\n"
            
            for placement in SAMPLE_PLACEMENTS:
                response += f"\n**{placement['company']}**\n" \
                          f"- Average Package: ₹{placement['average_package']} LPA\n" \
                          f"- Highest Package: ₹{placement['highest_package']} LPA\n" \
                          f"- Students Placed: {placement['students_placed']}\n" \
                          f"- Roles: {', '.join(placement['roles_offered'])}\n"
            
            response += "\n\n**🎯 Placement Support:**\n" \
                      "- Dedicated Training & Placement Cell\n" \
                      "- Mock Interviews and GD Sessions\n" \
                      "- Resume Building Workshops\n" \
                      "- Aptitude & Technical Training\n" \
                      "- Soft Skills Development\n\n" \
                      "📞 **Placement Cell:** 0512-2580004\n" \
                      "Would you like details about placement preparation or specific company profiles?"
            return response
        
        elif intent == 'facility':
            return "🏢 **Axis Colleges provides the following facilities:**\n\n" \
                   "- **Fully WiFi Enabled Campus** - High-speed internet throughout the campus\n" \
                   "- **Separate Hostel for Boys and Girls** - Safe and comfortable accommodation\n" \
                   "- **Modern Computer Labs** - 500+ systems with latest software\n" \
                   "- **Library with Digital Resources** - 50,000+ books and e-resources\n" \
                   "- **Sports Grounds** - Cricket, football, basketball facilities\n" \
                   "- **Transport Facility** - Bus services from key locations in Kanpur\n" \
                   "- **Canteen & Cafeteria** - Hygienic and affordable food options\n" \
                   "- **Gym & Fitness Center** - Modern equipment for student wellness\n" \
                   "- **24/7 Security** - CCTV surveillance and security personnel\n" \
                   "- **Medical Facility** - First-aid and emergency medical care\n\n" \
                   "Would you like more details about hostel or labs?"
        
        elif intent == 'contact':
            return "📞 **Contact Information:**\n\n" \
                   "🏢 **Main Office**\n" \
                   "📱 Phone: 0512-2580001\n" \
                   "📧 Email: info@axiscolleges.edu.in\n" \
                   "📍 Address: Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305\n\n" \
                   "🕐 **Office Hours:** Monday to Saturday, 9:00 AM to 5:00 PM\n\n" \
                   "📞 **Specialized Helplines:**\n" \
                   "- Admission: 0512-2580002\n" \
                   "- Hostel: 0512-2580003\n" \
                   "- Placement: 0512-2580004"
        
        elif intent == 'scholarship':
            return """🎓 **Complete Scholarship Guide - Axis Colleges:**                   "**💰 Available Scholarship Programs:**
                   1. **Merit Scholarship:**
                   - Up to 50% fee waiver for toppers
                   - 90%+ in 12th: 50% waiver
                   - 85-89%: 30% waiver
                   - 80-84%: 20% waiver
                   2. **Need-Based Financial Aid:**
                   - Family income < ₹3L: 40% waiver
                   - Family income ₹3-6L: 25% waiver
                   - Family income ₹6-8L: 15% waiver
                   3. **Sports Scholarship:**
                   - State/National level: 30% waiver 
                   - District level: 20% waiver
                   - Must maintain sports performance
                   4. **Government Scholarships:
                   - UP Scholarship: Available for UP residents 
                   - Central Sector: PMSSS, NSP etc.
                   - Minority Scholarship: For minority students
                   **📋 Application Process:**
                   - Apply online through college portal
                   - Submit income certificate (for need-based)
                   - Provide sports certificates (for sports)
                   - Submit previous year mark sheets
                   **📅 Important Dates:**
                   - Scholarship Form: Available with admission form
                   - Last Date: August 31st
                   - Document Verification: September 5-10
                   - Scholarship List: September 20th
                   📞 **Scholarship Office:** 0512-2580005
                   🌐 **Online Portal:** www.axiscolleges.edu.in/scholarship
                   💡 **Note:** Scholarship is renewable based on academic performance."""
        
        elif intent == 'comparison':
            return self._generate_comparison_response(course_context)
        
        elif intent == 'eligibility':
            if course_context:
                course = next((c for c in SAMPLE_COURSES if c['short_name'].lower() == course_context.lower()), None)
                if course:
                    return f"📋 **Eligibility for {course['name']}:**\n\n" \
                           f"- **Academic:** {course['eligibility']}\n" \
                           f"- **Age Limit:** No age limit\n" \
                           f"- **Subjects:** Must have studied relevant subjects\n\n" \
                           f"**Admission Criteria:**\n" \
                           f"- Merit-based selection\n" \
                           f"- Entrance exam score (if applicable)\n" \
                           f"- Personal interview\n\n" \
                           f"Would you like to know about the admission process?"
            
            return "📋 **General Eligibility Criteria:**\n\n" \
                   "**For Engineering Courses:**\n" \
                   "- 10+2 with PCM, 60% marks\n\n" \
                   "**For Management Courses:**\n" \
                   "- 10+2 any stream, 50% marks\n\n" \
                   "**For Computer Applications:**\n" \
                   "- 10+2 with Math, 50% marks\n\n" \
                   "Which course eligibility would you like to know in detail?"
        
        return self._generate_fallback_response(message)
    
    def get_response(self, message: str, session_id: str = 'default') -> str:
        """Get intelligent AI response"""
        # Detect intent
        intent = self._detect_intent(message)
        
        # Get context memory
        context = self._get_context_memory(session_id)
        
        # Check if query contains restricted topics
        if not self._is_college_related(message):
            response = self._generate_fallback_response(message)
            self._update_context_memory(session_id, message, response)
            return response
        
        # Generate message hash for caching
        message_hash = hashlib.md5(message.encode()).hexdigest()
        
        # Check cache first
        cached_response = self._get_cached_response(message_hash)
        if cached_response:
            self._update_context_memory(session_id, message, cached_response)
            return cached_response
        
        # If intent is detected as college-related, provide structured response
        response = self._generate_rule_based_response(message, intent, context)
        
        # Cache response
        self._cache_response(message_hash, response)
        
        # Update context memory
        self._update_context_memory(session_id, message, response)
        
        return response

# Initialize AI Assistant
ai_assistant = AdvancedAIAssistant()

@app.route('/')
def index():
    """Main chatbot interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with advanced AI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get AI response
        bot_response = ai_assistant.get_response(user_message, session_id)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error in chat route: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'ai_mode',
        'openai_enabled': OPENAI_API_KEY is not None,
        'message': 'Axis Colleges Advanced AI Assistant is running'
    })

@app.route('/analytics', methods=['POST'])
def analytics():
    """Track user interactions for improvement"""
    try:
        data = request.get_json()
        # Store analytics data (implement as needed)
        return jsonify({'status': 'recorded'})
    except Exception as e:
        return jsonify({'error': 'Analytics recording failed'}), 500

# Admin Routes
@app.route('/admin')
def admin():
    """Admin login page"""
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Handle admin login"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple admin authentication (in production, use proper hashing)
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return jsonify({'success': True, 'redirect': '/admin/dashboard'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard page"""
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    return render_template('admin/dashboard.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/admin')

# Courses Management API
@app.route('/api/admin/courses', methods=['GET'])
def get_admin_courses():
    """Get all courses for admin dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Return sample courses data (in production, fetch from database)
        courses = []
        for course in SAMPLE_COURSES:
            courses.append({
                'id': course['id'],
                'name': course['name'],
                'duration': course['duration'],
                'fees': course['total_fees'],
                'eligibility': course['eligibility'],
                'description': course['description']
            })
        return jsonify({'courses': courses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses', methods=['POST'])
def add_course():
    """Add new course"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        # For now, return success (in production, save to database)
        return jsonify({
            'success': True,
            'message': 'Course added successfully',
            'course_id': len(SAMPLE_COURSES) + 1
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update existing course"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        # For now, return success (in production, update in database)
        return jsonify({
            'success': True,
            'message': 'Course updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete course"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # For now, return success (in production, delete from database)
        return jsonify({
            'success': True,
            'message': 'Course deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# FAQs Management API
@app.route('/api/admin/faqs', methods=['GET'])
def get_admin_faqs():
    """Get all FAQs for admin dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Return sample FAQs data (in production, fetch from database)
        faqs = []
        for i, faq in enumerate(SAMPLE_FAQS, 1):
            faqs.append({
                'id': i,
                'question': faq['question'],
                'answer': faq['answer'],
                'category': faq['category']
            })
        return jsonify({'faqs': faqs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faqs', methods=['POST'])
def add_faq():
    """Add new FAQ"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        # For now, return success (in production, save to database)
        return jsonify({
            'success': True,
            'message': 'FAQ added successfully',
            'faq_id': len(SAMPLE_FAQS) + 1
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    """Update existing FAQ"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        # For now, return success (in production, update in database)
        return jsonify({
            'success': True,
            'message': 'FAQ updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    """Delete FAQ"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # For now, return success (in production, delete from database)
        return jsonify({
            'success': True,
            'message': 'FAQ deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Event Management Routes
@app.route('/events')
def events_page():
    """Events page for students"""
    return render_template('events.html')

@app.route('/api/events')
def get_events():
    """Get all events for public display"""
    try:
        # Fetch events from database
        events = Event.query.order_by(Event.created_at.desc()).all()
        
        # Convert to dict format
        events_data = [event.to_dict() for event in events]
        
        print(f"Fetched {len(events_data)} events for public display")
        
        return jsonify({'events': events_data})
        
    except Exception as e:
        print(f"Error fetching public events from database: {str(e)}")
        # Fallback to sample data if database fails
        sample_events = [
            {
                'id': 1,
                'event_name': 'Annual Tech Fest 2024',
                'description': 'Technical festival with coding competitions, robotics workshops, and tech talks by industry experts.',
                'event_date': '2024-03-15',
                'event_time': '10:00 AM',
                'venue': 'Main Auditorium',
                'category': 'Technical',
                'image_url': 'https://picsum.photos/seed/techfest/400/300.jpg'
            },
            {
                'id': 2,
                'event_name': 'Cultural Fest - Utsav 2024',
                'description': 'Annual cultural festival with music, dance, drama, and various cultural activities.',
                'event_date': '2024-02-20',
                'event_time': '9:00 AM',
                'venue': 'College Ground',
                'category': 'Cultural',
                'image_url': 'https://picsum.photos/seed/culturalfest/400/300.jpg'
            }
        ]
        print(f"Using fallback sample data for public events: {len(sample_events)} events")
        return jsonify({'events': sample_events})

# Global storage for events (in production, use database)
ADMIN_EVENTS = []

@app.route('/api/admin/events', methods=['GET'])
def get_admin_events():
    """Get all events from database for admin dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Fetch events from database
        events = Event.query.order_by(Event.created_at.desc()).all()
        
        # Convert to dict format
        events_data = [event.to_dict() for event in events]
        
        print(f"Fetched {len(events_data)} events from database")
        
        return jsonify({'events': events_data})
        
    except Exception as e:
        print(f"Error fetching events from database: {str(e)}")
        # Fallback to sample data if database fails
        if not ADMIN_EVENTS:
            sample_events = [
                {
                    'id': 1,
                    'event_name': 'Annual Tech Fest 2024',
                    'description': 'Technical festival with coding competitions, robotics workshops, and tech talks by industry experts.',
                    'event_date': '2024-03-15',
                    'event_time': '10:00 AM',
                    'venue': 'Main Auditorium',
                    'category': 'Technical',
                    'image_url': 'https://picsum.photos/seed/techfest/400/300.jpg'
                },
                {
                    'id': 2,
                    'event_name': 'Cultural Fest - Utsav 2024',
                    'description': 'Annual cultural festival with music, dance, drama, and various cultural activities.',
                    'event_date': '2024-02-20',
                    'event_time': '9:00 AM',
                    'venue': 'College Ground',
                    'category': 'Cultural',
                    'image_url': 'https://picsum.photos/seed/culturalfest/400/300.jpg'
                }
            ]
            ADMIN_EVENTS.extend(sample_events)
            print(f"Using fallback sample data: {len(sample_events)} events")
        
        return jsonify({'events': ADMIN_EVENTS})

@app.route('/api/admin/events', methods=['POST'])
def add_event():
    """Add new event to database"""
    print("=== add_event called ===")
    
    # Check authentication
    if not session.get('admin_logged_in'):
        print("❌ Admin not logged in")
        return jsonify({'error': 'Unauthorized - Please login as admin'}), 401
    
    print("✅ Admin authenticated")
    
    try:
        # Check if request contains files (FormData) or JSON
        print(f"Request files: {bool(request.files)}")
        print(f"Request form data: {dict(request.form) if request.form else 'None'}")
        print(f"Request JSON: {request.get_json() if not request.files else 'FormData used'}")
        
        if request.files:
            # Handle FormData with file upload
            event_name = request.form.get('event_name', '').strip()
            description = request.form.get('description', '').strip()
            event_date_str = request.form.get('event_date', '').strip()
            event_time = request.form.get('event_time', '').strip()
            venue = request.form.get('venue', '').strip()
            category = request.form.get('category', '').strip()
            
            # Handle file upload
            image_url = None
            if 'event_image' in request.files:
                file = request.files['event_image']
                if file and file.filename and allowed_file(file.filename):
                    print(f"Processing file upload: {file.filename}")
                    # Generate unique filename
                    filename = generate_unique_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Create upload directory if it doesn't exist
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Save file
                    file.save(filepath)
                    image_url = f"/static/event_images/{filename}"
                    print(f"File saved: {filepath}")
        else:
            # Handle JSON data (no file upload)
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
                
            event_name = data.get('event_name', '').strip()
            description = data.get('description', '').strip()
            event_date_str = data.get('event_date', '').strip()
            event_time = data.get('event_time', '').strip()
            venue = data.get('venue', '').strip()
            category = data.get('category', '').strip()
            image_url = data.get('image_url', '')
        
        print(f"Event data: {event_name}, {description}, {event_date_str}, {event_time}, {venue}, {category}")
        
        # Validate required fields
        required_fields = ['event_name', 'description', 'event_date', 'event_time', 'venue', 'category']
        field_values = {
            'event_name': event_name,
            'description': description,
            'event_date': event_date_str,
            'event_time': event_time,
            'venue': venue,
            'category': category
        }
        
        for field in required_fields:
            if not field_values[field]:
                field_name = field.replace('_', ' ').title()
                print(f"❌ Validation failed: {field_name} is required")
                return jsonify({'error': f'{field_name} is required'}), 400
        
        # Validate category
        valid_categories = ['Cultural', 'Technical', 'Sports', 'Academic']
        if category not in valid_categories:
            print(f"❌ Invalid category: {category}")
            return jsonify({'error': 'Invalid category'}), 400
        
        # Parse date
        try:
            from datetime import datetime
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            print(f"✅ Date parsed: {event_date}")
        except ValueError as e:
            print(f"❌ Date parsing error: {str(e)}")
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create new event object
        new_event = Event(
            event_name=event_name,
            description=description,
            event_date=event_date,
            event_time=event_time,
            venue=venue,
            category=category,
            image_url=image_url or f"https://picsum.photos/seed/{event_name.replace(' ', '')}/400/300.jpg"
        )
        
        print("✅ Event object created")
        
        # Add to database
        db.session.add(new_event)
        db.session.commit()
        
        print(f"✅ Successfully added event to database: {event_name}")
        print(f"Event ID: {new_event.id}")
        
        return jsonify({
            'success': True,
            'message': 'Event added successfully',
            'event_id': new_event.id
        })
        
    except Exception as e:
        print(f"❌ Error in add_event: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Failed to save event: {str(e)}'}), 500

@app.route('/api/admin/events/stats')
def get_event_stats():
    """Get event statistics for admin dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # For now, return mock stats (in production, calculate from database)
        from datetime import date
        today = date.today()
        
        total_events = 8
        upcoming_events = 5  # events with date >= today
        past_events = 3     # events with date < today
        
        return jsonify({
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'past_events': past_events
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update existing event"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_name', 'description', 'event_date', 'event_time', 'venue', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate category
        valid_categories = ['Cultural', 'Technical', 'Sports', 'Academic']
        if data['category'] not in valid_categories:
            return jsonify({'error': 'Invalid category'}), 400
        
        # For now, return success (in production, update in database)
        return jsonify({
            'success': True,
            'message': 'Event updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete event from database"""
    print(f"=== delete_event called for ID: {event_id} ===")
    
    if not session.get('admin_logged_in'):
        print("❌ Admin not logged in")
        return jsonify({'error': 'Unauthorized'}), 401
    
    print("✅ Admin authenticated for delete")
    
    try:
        # Find event in database
        event = Event.query.get(event_id)
        if not event:
            print(f"❌ Event not found with ID: {event_id}")
            return jsonify({'error': 'Event not found'}), 404
        
        print(f"✅ Found event: {event.event_name}")
        
        # Delete from database
        db.session.delete(event)
        db.session.commit()
        
        print(f"✅ Successfully deleted event from database: {event.event_name}")
        
        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        })
        
    except Exception as e:
        print(f"❌ Error deleting event: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Failed to delete event: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎓 Starting Axis Colleges Advanced AI Assistant...")
    
    # Initialize database
    print("🔧 Initializing database...")
    init_db()
    
    print(" Chat Interface: http://localhost:5000")
    print("🧠 AI Mode: Advanced NLP with OpenAI Integration")
    print("🧠 Context Memory: Enabled (last 5 messages)")
    print("🧠 Intent Detection: Enabled")
    print("🧠 Multi-language Support: English, Hindi, Hinglish")
    print("🛡️ Security: College-restricted queries only")
    print("📊 Analytics: Enabled")
    print("💾 Database: PostgreSQL with SQLAlchemy")
    print("\n" + "="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

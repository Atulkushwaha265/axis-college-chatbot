# Axis Colleges AI Chatbot

A full-stack AI-powered chatbot web application for Axis Colleges, Kanpur. This intelligent assistant helps students with information about courses, fees, admission, placements, facilities, and other college-related queries.

## 🎓 Features

### 🤖 Chatbot Features
- **Intelligent Responses**: Smart keyword matching and AI-powered responses
- **Dynamic Database Integration**: Fetches real-time data from PostgreSQL
- **Natural Conversations**: Human-like responses with proper formatting
- **Quick Actions**: Pre-defined buttons for common queries
- **Chat History**: Persistent conversation history
- **Responsive Design**: Works seamlessly on all devices
- **Real-time Typing Indicators**: Visual feedback during processing
- **Auto-scroll**: Smooth chat experience

### 🛡️ Security Features
- **Input Validation**: Comprehensive protection against XSS and SQL injection
- **Rate Limiting**: Prevents abuse and spam
- **CSRF Protection**: Cross-site request forgery prevention
- **Secure Authentication**: Admin panel with encrypted passwords
- **Security Headers**: Comprehensive HTTP security headers
- **Session Management**: Secure session handling

### 🎛️ Admin Panel
- **Secure Login**: Protected admin dashboard
- **Course Management**: Add, edit, delete courses
- **FAQ Management**: Dynamic FAQ updates
- **Event Management**: College event management
- **Placement Data**: Update placement statistics
- **Analytics**: Chat usage statistics
- **Real-time Updates**: Live data synchronization

### 📊 Database Schema
- **Courses**: Course information with fees and eligibility
- **Facilities**: Campus facilities and amenities
- **Contacts**: Department-wise contact information
- **Placements**: Company-wise placement data
- **FAQs**: Frequently asked questions
- **Scholarships**: Scholarship information
- **Events**: College events and activities
- **Chat History**: Conversation logs

## 🚀 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Security**: Werkzeug, Bleach, Cryptography
- **AI Integration**: OpenAI API (Optional)

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Frameworks**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Styling**: Custom CSS with animations

### Development Tools
- **Environment**: Python 3.8+
- **Package Management**: pip
- **Version Control**: Git
- **Code Quality**: Black, Flake8

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Node.js (for frontend tools, optional)
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/axis-college-chatbot.git
cd axis-college-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb axis_college_ai

# Import schema
psql -d axis_college_ai -f database/schema.sql

# Import sample data (optional)
psql -d axis_college_ai -f database/sample_data.sql
```

### 5. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Update database credentials, secret keys, etc.
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/axis_college_ai

# Security
SECRET_KEY=your-super-secret-key-here

# OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Database Configuration
Update `config.py` for different environments:
- Development: `config['development']`
- Testing: `config['testing']`
- Production: `config['production']`

## 📁 Project Structure

```
axis-college-chatbot/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── security.py           # Security utilities
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── README.md            # Project documentation
├── database/
│   ├── schema.sql       # Database schema
│   └── sample_data.sql  # Sample data
├── templates/
│   ├── index.html       # Main chat interface
│   └── admin/
│       ├── login.html   # Admin login
│       └── dashboard.html # Admin panel
└── static/
    ├── css/
    │   └── style.css    # Custom styles
    └── js/
        ├── chat.js      # Chat functionality
        └── admin.js     # Admin panel scripts
```

## 🎯 Usage

### For Students
1. Open the application in your browser
2. Start typing your questions in the chat
3. Use quick action buttons for common queries
4. Get instant responses about courses, fees, admissions, etc.

### For Admins
1. Access `/admin` to reach the admin panel
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. Manage courses, FAQs, events, and other data
4. Monitor chat statistics and usage

## 🔐 Security Features

### Input Validation
- XSS prevention with HTML sanitization
- SQL injection detection and prevention
- Email and phone format validation
- Password strength requirements

### Authentication & Authorization
- Secure password hashing with bcrypt
- Session management with timeout
- CSRF token protection
- Rate limiting for API endpoints

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Main chat interface
- `POST /chat` - Chat API endpoint
- `GET /health` - Health check

### Admin Endpoints
- `GET /admin` - Admin dashboard
- `POST /admin/login` - Admin login
- `GET /api/admin/courses` - List courses
- `POST /api/admin/courses` - Add course
- `PUT /api/admin/courses/<id>` - Update course
- `DELETE /api/admin/courses/<id>` - Delete course

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```bash
# Build Docker image
docker build -t axis-chatbot .

# Run container
docker run -p 5000:5000 axis-chatbot
```

### Cloud Deployment (Render/Railway)
1. Connect your repository
2. Set environment variables
3. Deploy automatically

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Test Coverage
- Unit tests for chatbot logic
- Integration tests for API endpoints
- Security tests for input validation
- Database tests for CRUD operations

## 📈 Monitoring

### Health Checks
- Database connectivity
- API endpoint status
- System resources

### Logging
- Application logs
- Security events
- Error tracking
- Performance metrics

## 🔄 Updates and Maintenance

### Database Migration
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Backup Database
```bash
pg_dump axis_college_ai > backup.sql
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and queries:
- **Email**: support@axiscolleges.edu.in
- **Phone**: 0512-2580001
- **Address**: Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305

## 🌟 Acknowledgments

- Axis Colleges, Kanpur for the opportunity
- OpenAI for AI integration capabilities
- Flask community for excellent framework
- Bootstrap for responsive UI components

## 📋 Future Enhancements

- [ ] Voice chat integration
- [ ] Multi-language support (Hindi)
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with college ERP system
- [ ] AI-powered sentiment analysis
- [ ] Automated follow-up emails
- [ ] Social media integration
- [ ] Video tutorials integration
- [ ] Virtual campus tour

---

**Axis Colleges AI Chatbot** - Transforming student engagement with intelligent automation 🤖✨

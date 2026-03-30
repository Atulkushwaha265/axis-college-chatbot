-- Sample Data for Axis Colleges AI Chatbot
-- Insert sample data into all tables

-- Insert Courses
INSERT INTO courses (name, duration, fees, eligibility, description) VALUES
('B.Tech Computer Science Engineering', '4 Years', 85000.00, '10+2 with PCM, 60% marks', 'Comprehensive engineering program with focus on software development, AI, and machine learning.'),
('B.Tech Mechanical Engineering', '4 Years', 75000.00, '10+2 with PCM, 60% marks', 'Core mechanical engineering with modern manufacturing and design technologies.'),
('B.Tech Civil Engineering', '4 Years', 70000.00, '10+2 with PCM, 60% marks', 'Infrastructure development and construction management program.'),
('B.Tech Electronics & Communication', '4 Years', 80000.00, '10+2 with PCM, 60% marks', 'Communication systems and electronic device engineering.'),
('BCA (Bachelor of Computer Applications)', '3 Years', 55000.00, '10+2 with Math, 50% marks', 'Application development and software engineering program.'),
('BBA (Bachelor of Business Administration)', '3 Years', 50000.00, '10+2 any stream, 50% marks', 'Business management and entrepreneurship program.'),
('M.Tech Computer Science', '2 Years', 100000.00, 'B.Tech in CS/IT with 60% marks', 'Advanced computer science and research program.'),
('MBA', '2 Years', 120000.00, 'Graduation with 50% marks', 'Business administration and management program.'),
('Diploma in Engineering', '3 Years', 40000.00, '10th pass with 45% marks', 'Polytechnic program in various engineering branches.'),
('B.Sc. Computer Science', '3 Years', 45000.00, '10+2 with Math, 50% marks', 'Theoretical and practical computer science program.');

-- Insert Facilities
INSERT INTO facilities (name, description) VALUES
('Library', 'State-of-the-art library with over 50,000 books, digital resources, and 24/7 study areas.'),
('Computer Labs', 'Modern computer labs with 500+ systems, high-speed internet, and latest software.'),
('Sports Complex', 'Indoor and outdoor sports facilities including cricket ground, basketball courts, and gym.'),
('Hostel', 'Separate hostels for boys and girls with WiFi, mess, and 24/7 security.'),
('Cafeteria', 'Hygienic cafeteria serving nutritious meals and snacks at reasonable prices.'),
('Auditorium', '500-seat auditorium with modern audio-visual equipment for events and seminars.'),
('Transportation', 'Bus facility covering major routes in Kanpur and nearby areas.'),
('Medical Center', 'On-campus medical center with qualified doctors and emergency services.'),
('Placement Cell', 'Dedicated placement cell with industry connections and training programs.'),
('Research Labs', 'Advanced research laboratories for innovation and project development.');

-- Insert Contacts
INSERT INTO contacts (phone, email, address, department) VALUES
('0512-2580001', 'info@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Main Office'),
('0512-2580002', 'admission@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Admission Office'),
('0512-2580003', 'placement@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Placement Cell'),
('0512-2580004', 'hostel@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Hostel Office'),
('0512-2580005', 'examination@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Examination Cell'),
('9456789012', 'director@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Director Office'),
('9456789013', 'principal@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Principal Office'),
('9456789014', 'library@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Library'),
('9456789015', 'sports@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Sports Department'),
('9456789016', 'transport@axiscolleges.edu.in', 'Axis Colleges, Kanpur-Lucknow Highway, Kanpur, Uttar Pradesh - 209305', 'Transport Department');

-- Insert Placements
INSERT INTO placements (company_name, average_package, highest_package, students_placed, year) VALUES
('TCS', 4.50, 8.50, 120, 2023),
('Infosys', 4.20, 7.80, 95, 2023),
('Wipro', 4.00, 7.20, 85, 2023),
('HCL Technologies', 4.80, 9.00, 75, 2023),
('Tech Mahindra', 3.80, 6.50, 65, 2023),
('Amazon', 8.50, 15.00, 25, 2023),
('Microsoft', 12.00, 20.00, 15, 2023),
('Google', 15.00, 25.00, 8, 2023),
('IBM', 5.50, 10.00, 45, 2023),
('Accenture', 4.20, 8.00, 110, 2023),
('Capgemini', 3.90, 7.00, 90, 2023),
('Cognizant', 4.60, 8.50, 100, 2023),
('Deloitte', 6.00, 12.00, 35, 2023),
('KPMG', 5.80, 11.00, 30, 2023),
('Byju''s', 5.20, 9.00, 40, 2023);

-- Insert FAQs
INSERT INTO faqs (question, answer, category) VALUES
('What is the admission process?', 'Admission is based on merit and entrance exams. Apply online through our website or visit the admission office.', 'Admission'),
('What documents are required for admission?', '10th and 12th mark sheets, transfer certificate, migration certificate, passport size photos, and ID proof.', 'Admission'),
('Is there hostel facility available?', 'Yes, we provide separate hostel facilities for boys and girls with all modern amenities.', 'Hostel'),
('What is the fee structure?', 'Fee structure varies by course. Please check the courses section or contact admission office for details.', 'Fees'),
('Does the college provide placement?', 'Yes, we have a dedicated placement cell with 100% placement assistance and tie-ups with top companies.', 'Placement'),
('What are the library timings?', 'Library is open from 8:00 AM to 8:00 PM on weekdays and 9:00 AM to 5:00 PM on weekends.', 'Library'),
('Is transportation facility available?', 'Yes, we provide bus transportation covering major routes in Kanpur and nearby areas.', 'Transport'),
('What extracurricular activities are available?', 'We have sports, cultural events, technical clubs, and various student organizations.', 'General'),
('How can I apply for scholarships?', 'Scholarships are available based on merit and economic background. Contact the scholarship cell for details.', 'Scholarship'),
('What is the attendance requirement?', 'Minimum 75% attendance is required to appear in examinations.', 'Academic'),
('Does the college have Wi-Fi?', 'Yes, entire campus has high-speed Wi-Fi connectivity.', 'Facilities'),
('Are there any sports facilities?', 'Yes, we have cricket ground, football field, basketball courts, badminton courts, and a modern gym.', 'Sports'),
('What is the dress code?', 'Students are required to follow the dress code mentioned in the student handbook.', 'General'),
('How can I contact the faculty?', 'Faculty contact details are available on the website. You can also email respective departments.', 'General'),
('Is there any medical facility on campus?', 'Yes, we have a medical center with qualified doctors and emergency services.', 'Medical');

-- Insert Scholarships
INSERT INTO scholarships (name, eligibility, details, amount) VALUES
('Merit Scholarship', 'Students with 90%+ in 12th', 'Full tuition fee waiver for toppers', 85000.00),
('Economic Weaker Section', 'Family income below 2 lakhs', '50% fee concession for economically weaker students', 42500.00),
('Sports Scholarship', 'State/National level players', 'Fee concession for outstanding sports persons', 30000.00),
('Girls Scholarship', 'Female students', 'Special scholarship for girl students', 20000.00),
('Defense Wards Scholarship', 'Children of defense personnel', 'Fee concession for defense personnel children', 25000.00),
('Alumni Scholarship', 'Children of alumni', 'Special scholarship for alumni children', 15000.00),
('Minority Scholarship', 'Minority community students', 'Scholarship for minority community students', 18000.00),
('Differently Abled Scholarship', 'Physically challenged students', 'Full support for differently abled students', 50000.00);

-- Insert Events
INSERT INTO events (event_name, description, event_date, event_time, venue, category, image_url) VALUES
('Annual Tech Fest 2024', 'Technical festival with coding competitions, robotics workshops, and tech talks by industry experts. Join us for 3 days of innovation and learning.', '2024-03-15', '10:00 AM', 'Main Auditorium', 'Technical', 'https://picsum.photos/seed/techfest/400/300.jpg'),
('Cultural Fest - Utsav 2024', 'Annual cultural festival with music, dance, drama, and various cultural activities. Show your talent and celebrate diversity!', '2024-02-20', '9:00 AM', 'College Ground', 'Cultural', 'https://picsum.photos/seed/culturalfest/400/300.jpg'),
('Sports Meet 2024', 'Inter-college sports competition with various athletic events and games. Participate in cricket, football, basketball and more!', '2024-01-25', '8:00 AM', 'Sports Complex', 'Sports', 'https://picsum.photos/seed/sportsmeet/400/300.jpg'),
('Career Fair 2024', 'Job fair with top companies recruiting for various positions and internship opportunities. Bring your resume and dress professionally.', '2024-04-10', '10:00 AM', 'Placement Cell', 'Academic', 'https://picsum.photos/seed/careerfair/400/300.jpg'),
('Workshop on AI/ML', 'Hands-on workshop on Artificial Intelligence and Machine Learning technologies. Learn from industry experts and work on real projects.', '2024-03-05', '2:00 PM', 'Computer Lab', 'Technical', 'https://picsum.photos/seed/aiworkshop/400/300.jpg'),
('Alumni Meet 2024', 'Annual alumni reunion event for networking and sharing experiences. Connect with successful alumni and build your network.', '2024-02-10', '6:00 PM', 'Conference Hall', 'Cultural', 'https://picsum.photos/seed/alumni/400/300.jpg'),
('Hackathon 2024', '24-hour coding competition with exciting prizes and job opportunities. Form teams and build innovative solutions.', '2024-05-20', '10:00 AM', 'Innovation Lab', 'Technical', 'https://picsum.photos/seed/hackathon/400/300.jpg'),
('Music Concert', 'Live music concert featuring popular bands and artists. Enjoy an evening of great music and entertainment.', '2024-06-15', '7:00 PM', 'Open Air Theatre', 'Cultural', 'https://picsum.photos/seed/music/400/300.jpg'),
('Freshers Party', 'Welcome party for first-year students', '2024-08-15', 'Open Ground', 'General', ''),
('Farewell Party', 'Farewell event for final-year students', '2024-04-20', 'Auditorium', 'General', ''),
('Blood Donation Camp', 'Social service initiative for blood donation', '2024-02-10', 'Medical Center', 'General', ''),
('Tree Plantation Drive', 'Environmental initiative for campus greening', '2024-03-05', 'Campus Ground', 'General', '');

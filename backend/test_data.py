
# Centralized Test Data for Certificate Validator

TEST_CERTIFICATES = {
    'ganeeb': {
        'certificate_id': '21671A0517',
        'student_name': 'Ganeeb Shivasai',
        'roll_number': '21671A0517',
        'course': 'Bachelor of Technology in Computer Science & Engineering',
        'university': 'J.B Institute of Engineering and Technology',
        'year': '2025',
        'academic_data': {
            "tenth_certificate": {
                "name": "GANEEB SHIVASAI",
                "certificate_number": "259078",
                "roll_number": "191501796",
                "institution_name": "S P R SCHOOL OF EXCELLENCE, KAMAREDDY DISTRICT",
                "year_of_passing": "2019",
                "course_or_stream": "Board of Secondary Education",
                "cgpa_or_marks": "9.7"
            },
            "intermediate_certificate": {
                "name": "GANEEB SHIVASAI",
                "certificate_number": "G205923268",
                "roll_number": "2159234205",
                "institution_name": "SRI CHAITANYA JUNIOR KALASALA",
                "year_of_passing": "2021",
                "course_or_stream": "TELANGANA STATE BOARD OF INTERMEDIATE EDUCATION: HYDERABAD",
                "cgpa_or_marks": "943"
            },
            "degree_certificate": {
                "name": "Ganeeb Shivasai",
                "certificate_number": "21671A0517",
                "roll_number": "21671A0517",
                "institution_name": "J.B Institute of Engineering and Technology",
                "year_of_passing": "2025",
                "course_or_stream": "Bachelor of Technology in Computer Science & Engineering",
                "cgpa_or_marks": None
            }
        }
    },
    'rohit': {
        'certificate_id': 'RTU-2016-ECE-1001',
        'student_name': 'Rohit Kumar',
        'roll_number': '12ESKEC700',
        'course': 'Bachelor of Technology in Electronics & Communication Engineering',
        'university': 'Rajasthan Technical University (Shankara Institute of Technology)',
        'year': '2016'
    },
    'vidhya': {
        'certificate_id': '30906103052/RG', 
        'student_name': 'Vidhya Shree S',
        'roll_number': '30906103052',
        'course': 'Bachelor of Engineering in Civil Engineering',
        'university': 'Anna University', 
        'year': '2010'
    },
    'adarsh': {
        'certificate_id': '9215630', 
        'student_name': 'Adarsh',
        'roll_number': '1280387',
        'course': 'Electronics & Communication Engineering',
        'university': 'Punjab Technical University',
        'year': '2016'
    },
    'pal': {
        'certificate_id': '719', 
        'student_name': 'Pal Rohit Rajesh',
        'roll_number': '231TD6038489',
        'course': 'B.Sc. (Information Technology)',
        'university': 'Pillai College of Arts, Commerce & Science',
        'year': '2023',
        'cgpa': '8.30'
    },
    'yashaswini': {

        'certificate_id': 'CERT2026JNTU001245',
        'student_name': 'YASHASWINI GANEEB',
        'roll_number': '19CSE0458',
        'course': 'BACHELOR OF TECHNOLOGY IN COMPUTER SCIENCE AND ENGINEERING',
        'university': 'JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY',
        'year': '2026',
        'academic_data': {
            "tenth_certificate": {
                "name": "YASHASWINI GANEEB",
                "certificate_number": "SSC2020APF458921",
                "roll_number": "1623104589",
                "institution_name": "Secondary School Certificate",
                "year_of_passing": "2020",
                "course_or_stream": "SSC",
                "cgpa_or_marks": "TOTAL: 540, Grade: A1"
            },
            "intermediate_certificate": {
                "name": "YASHASWINI GANEEB",
                "certificate_number": "INTER2022AP774512",
                "roll_number": "2203107896",
                "institution_name": "Board of Intermediate Education, Andhra Pradesh",
                "year_of_passing": "2022",
                "course_or_stream": "Intermediate Public Examination",
                "cgpa_or_marks": "TOTAL MARKS 906 / 1000, DIVISION: FIRST"
            },
            "degree_certificate": {
                "name": "YASHASWINI GANEEB",
                "certificate_number": "CERT2026JNTU001245",
                "roll_number": "19CSE0458",
                "institution_name": "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY",
                "year_of_passing": "2026",
                "course_or_stream": "BACHELOR OF TECHNOLOGY IN COMPUTER SCIENCE AND ENGINEERING",
                "cgpa_or_marks": None
            }
        }
    }
}

def get_test_certificate(filename, force_genuine=False):
    """Return test data based on filename if applicable"""
    filename_lower = filename.lower()
    
    # Check for Yashaswini Ganeeb
    if "yashaswini" in filename_lower or "ganeeb" in filename_lower:
        import copy
        data = copy.deepcopy(TEST_CERTIFICATES['yashaswini'])
        if not force_genuine and ("fake" in filename_lower or "tampered" in filename_lower):
            data['year'] = '2025'
            data['academic_data']['degree_certificate']['year_of_passing'] = '2025'
        return data

    
    # Check for Ganeeb Shivasai
    if any(k in filename_lower for k in ["sai", "cert_sai", "21671"]):
        return TEST_CERTIFICATES['ganeeb']
        
    # Check for Rohit Kumar
    if any(k in filename_lower for k in ["rohit", "shankara", "cert6", "12esk"]):
        return TEST_CERTIFICATES['rohit']
        
    # Check for Vidhya Shree S
    if any(k in filename_lower for k in ["vidhya", "anna", "certt_a", "certt a", "30906"]):
        return TEST_CERTIFICATES['vidhya']
        
    # Check for Adarsh
    if any(k in filename_lower for k in ["punjab", "adarsh", "certt_c", "certt c", "92156"]):
        return TEST_CERTIFICATES['adarsh']
        
    # Check for Pal Rohit Rajesh
    if any(k in filename_lower for k in ["pillai", "pal", "certt_b", "certt b", "719", "23itd", "231td", "mumbai"]):
        data = TEST_CERTIFICATES['pal'].copy()
        if not force_genuine and ("fake" in filename_lower or "tampered" in filename_lower or "tampering" in filename_lower):
            data['cgpa'] = '9.47'
        return data
        
    return None

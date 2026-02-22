
# Centralized Test Data for Certificate Validator

TEST_CERTIFICATES = {
    'ganeeb': {
        'certificate_id': '21671A0517',
        'student_name': 'Ganeeb Shivasai',
        'roll_number': '21671A0517',
        'course': 'Bachelor of Technology in Computer Science & Engineering',
        'university': 'J.B Institute of Engineering and Technology',
        'year': '2025'
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
    }
}

def get_test_certificate(filename, force_genuine=False):
    """Return test data based on filename if applicable"""
    filename_lower = filename.lower()
    
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

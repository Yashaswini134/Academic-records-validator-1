
import sqlite3
import os
import json

class CertificateDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to certificates.db in the same directory as this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, 'certificates.db')
            # Ensure backend directory exists
            os.makedirs(base_dir, exist_ok=True)
        else:
            self.db_path = db_path
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                certificate_id TEXT PRIMARY KEY,
                student_name TEXT,
                university_name TEXT,
                roll_number TEXT,
                year TEXT,
                course TEXT,
                is_issued BOOLEAN DEFAULT 0,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash TEXT,
                issuer_email TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT,
                role TEXT,
                university_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Check if issuer_email column exists (migration for existing DBs)
        try:
            cursor.execute('ALTER TABLE certificates ADD COLUMN issuer_email TEXT')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        conn.commit()
        conn.close()

    def add_certificate(self, cert_data, is_issued=True, issuer_email=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO certificates 
                (certificate_id, student_name, university_name, roll_number, year, course, is_issued, hash, issuer_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cert_data.get('certificate_id'),
                cert_data.get('student_name'),
                cert_data.get('university') or cert_data.get('university_name'),
                cert_data.get('roll_number'),
                cert_data.get('year'),
                cert_data.get('course'),
                1 if is_issued else 0,
                cert_data.get('hash'),
                issuer_email or cert_data.get('issuer_email')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()

    def get_certificate(self, certificate_id, issuer_email=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if issuer_email:
            cursor.execute('SELECT * FROM certificates WHERE certificate_id = ? AND issuer_email = ?', (certificate_id, issuer_email))
        else:
            cursor.execute('SELECT * FROM certificates WHERE certificate_id = ?', (certificate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'certificate_id': row[0],
                'student_name': row[1],
                'university_name': row[2],
                'roll_number': row[3],
                'year': row[4],
                'course': row[5],
                'is_issued': bool(row[6]),
                'registration_date': row[7],
                'hash': row[8],
                'issuer_email': row[9]
            }
        return None

    def list_issued_certificates(self, issuer_email=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if issuer_email:
            cursor.execute('SELECT certificate_id, student_name, year, course, is_issued, university_name, issuer_email FROM certificates WHERE is_issued = 1 AND issuer_email = ? ORDER BY registration_date DESC', (issuer_email,))
        else:
            cursor.execute('SELECT certificate_id, student_name, year, course, is_issued, university_name, issuer_email FROM certificates WHERE is_issued = 1 ORDER BY registration_date DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'certificate_id': r[0],
                'student_name': r[1],
                'year': r[2],
                'course': r[3],
                'is_issued': bool(r[4]),
                'university_name': r[5],
                'issuer_email': r[6]
            } for r in rows
        ]

    def is_certificate_registered(self, certificate_id):
        cert = self.get_certificate(certificate_id)
        return cert is not None and cert['is_issued']

    # --- User Management ---
    
    def add_user(self, email, password, role, university_name=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, password, role, university_name)
                VALUES (?, ?, ?, ?)
            ''', (email, password, role, university_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # User already exists
        except Exception as e:
            print(f"Database error in add_user: {e}")
            return False
        finally:
            conn.close()

    def get_user(self, email):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT email, password, role, university_name FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'email': row[0],
                'password': row[1],
                'role': row[2],
                'university_name': row[3]
            }
        return None

# Global instance
db = CertificateDatabase()

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from mail1 import send_email
import random
import string

app = Flask(__name__)
CORS(app)

# Lưu tài khoản và OTP tạm thời
accounts = []
pending_registrations = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Kiểm tra email đã tồn tại
    if any(acc['email'] == email for acc in accounts):
        return 'Email đã được đăng ký!', 400
    
    # Tạo OTP và lưu tạm
    otp = generate_otp()
    pending_registrations[email] = {
        'name': name,
        'password': password,
        'otp': otp
    }
    
    # Gửi OTP qua email
    send_email(email, f'Mã OTP của bạn là: {otp}')
    return 'OTP đã được gửi đến email của bạn!'

@app.route('/verify', methods=['POST'])
def verify():
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    if email not in pending_registrations:
        return 'Không tìm thấy yêu cầu đăng ký!', 400
    
    if pending_registrations[email]['otp'] == otp:
        # Xác thực thành công, lưu tài khoản
        accounts.append({
            'name': pending_registrations[email]['name'],
            'email': email,
            'password': pending_registrations[email]['password']
        })
        del pending_registrations[email]
        return f'Đăng ký thành công! Tổng số tài khoản: {len(accounts)}'
    else:
        return 'OTP không đúng!', 400

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Tìm tài khoản
    account = next((acc for acc in accounts if acc['email'] == email), None)
    
    if not account:
        return 'Email chưa được đăng ký!', 400
    
    if account['password'] == password:
        return f'Đăng nhập thành công! Xin chào {account["name"]}'
    else:
        return 'Mật khẩu không đúng!', 400

@app.route('/accounts', methods=['GET'])
def get_accounts():
    return jsonify(accounts)

app.run(debug=True)
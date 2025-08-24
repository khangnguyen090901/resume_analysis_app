from flask import Flask
from routes.candidate import candidate_bp
from routes.hr import hr_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Cần cho session (đăng nhập HR)

# Đăng ký các blueprint (route chia module)
app.register_blueprint(candidate_bp)
app.register_blueprint(hr_bp)

# Trang mặc định sẽ redirect về form upload CV
@app.route("/")
def index():
    return candidate_bp.send_static_file("upload.html")

if __name__ == "__main__":
    app.run(debug=True)

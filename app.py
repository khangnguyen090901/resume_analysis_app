import os
from flask import Flask
from routes.candidate import candidate_bp
from routes.hr import hr_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")  # nên để trong biến môi trường khi deploy

# Đăng ký các blueprint (chia module route)
app.register_blueprint(candidate_bp)
app.register_blueprint(hr_bp)

# Trang mặc định redirect về form upload CV
@app.route("/")
def index():
    return candidate_bp.send_static_file("upload.html")


if __name__ == "__main__":
    # Render sẽ truyền PORT vào biến môi trường
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

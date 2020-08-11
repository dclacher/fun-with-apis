from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from weather import weather_page

app = Flask(__name__)
app.register_blueprint(weather_page)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

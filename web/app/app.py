from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/mydatabase'
db = SQLAlchemy(app)

# Define the Item model according to your table
class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    image_url = db.Column(db.String())

@app.route('/')
def index():
    items = Items.query.all()  # Fetch all items from the database
    return render_template('index.html', items=items)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Cigar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    purchase_location = db.Column(db.String(200))
    purchase_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=0)
    archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    cigars = Cigar.query.filter_by(archived=False).order_by(Cigar.brand).all()
    return render_template('index.html', cigars=cigars)

@app.route('/archive')
def archive():
    cigars = Cigar.query.filter_by(archived=True).order_by(Cigar.brand).all()
    return render_template('archive.html', cigars=cigars)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        brand = request.form['brand']
        model = request.form['model']
        location = request.form['purchase_location']
        date = request.form['purchase_date']
        quantity = int(request.form['quantity'])
        rating = int(request.form['rating'])
        new_cigar = Cigar(
            brand=brand,
            model=model,
            purchase_location=location,
            purchase_date=datetime.strptime(date, '%Y-%m-%d'),
            quantity=quantity,
            rating=rating
        )
        db.session.add(new_cigar)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/archive_toggle/<int:cigar_id>')
def archive_toggle(cigar_id):
    cigar = Cigar.query.get_or_404(cigar_id)
    cigar.archived = not cigar.archived
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<int:cigar_id>')
def delete(cigar_id):
    cigar = Cigar.query.get_or_404(cigar_id)
    db.session.delete(cigar)
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/smoke/<int:id>', methods=['POST'])
def smoke(id):
    cigar = Cigar.query.get_or_404(id)
    if cigar.quantity > 0:
        cigar.quantity -= 1
        db.session.commit()
    return redirect(url_for('index'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == os.environ.get('ADMIN_USER') and pw == os.environ.get('ADMIN_PASS'):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

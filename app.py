from flask import Flask, render_template, request, redirect
import sys
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi-clave-secreta'
db = SQLAlchemy(app)


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    regex = db.Column(db.String(50))
    text = db.Column(db.String(1024))
    result = db.Column(db.Boolean)


db.create_all()


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        regex = request.form.get('regex')
        text = request.form.get('text')
        result = re.match(regex, text) is not None
        loc_match = Record(
            regex=regex,
            text=text,
            result=result
        )
        db.session.add(loc_match)
        db.session.commit()
        record = Record.query.order_by(Record.id.desc()).first()
        return redirect(f"/result/{record.id}/")

    return render_template('index.html')


@app.route("/result/<id>/")
def results(id):
    record = Record.query.filter(Record.id == id).one()
    return render_template('results.html', record=record)


@app.route("/history/")
def history():
    records = Record.query.order_by(Record.id.desc()).all()
    return render_template('history.html', records=records)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

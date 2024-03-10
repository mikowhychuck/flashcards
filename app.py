from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards1.db'
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)



class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flashcards = db.relationship('Flashcard', backref='deck', lazy=True)

    def __repr__(self):
        return '<Deck %r>' % self.id

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_text = db.Column(db.String(200), nullable=False)
    back_text = db.Column(db.String(200), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'),nullable=False)

    def __repr__(self):
        return '<flashcard %r>' % self.id

@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
        deck_name = request.form['name']
        new_deck = Deck(name=deck_name)

        try:
            db.session.add(new_deck)
            db.session.commit()
            return redirect('/')
        except:
            return render_template("error.html")
    else:
        decks = Deck.query.order_by(Deck.created_at).all()
        return render_template("index.html", decks = decks)

@app.route("/delete/<int:deck_id>")
def delete_deck(deck_id):
    deck_to_delete = Deck.query.get_or_404(deck_id)

    try:
        db.session.delete(deck_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return render_template("error.html")

@app.route("/deck/<int:deck_id>", methods=['POST', 'GET'])
def deck(deck_id):
    
    if request.method == 'POST':
        front_text = request.form['front_text']
        back_text = request.form['back_text']
        new_flashcard = Flashcard(front_text=front_text, back_text=back_text, deck_id=deck_id)

        try:
            db.session.add(new_flashcard)
            db.session.commit()
            return redirect(f"/deck/{deck_id}")
        except:
            return render_template("error.html")
    else:
        deck_name = Deck.query.filter_by(id=deck_id).first().name
        flashcards = Flashcard.query.filter_by(deck_id=deck_id).all()
        return render_template("deck.html", flashcards=flashcards, deck_name = deck_name, deck_id=deck_id)
    
@app.route("/deck/<int:deck_id>/delete/<int:flashcard_id>")
def delete_flashcard(deck_id, flashcard_id):
    flashcard_to_delete = Flashcard.query.get_or_404(flashcard_id)
    
    try:
        db.session.delete(flashcard_to_delete)
        db.session.commit()
        return redirect("/deck/{}".format(deck_id))
    except:
        return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)
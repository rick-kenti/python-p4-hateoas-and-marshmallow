#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

# ---------------------------
# App Setup
# ---------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Marshmallow
ma = Marshmallow(app)

# Flask-RESTful API
api = Api(app)

# ---------------------------
# Marshmallow Schema
# ---------------------------
class NewsletterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Newsletter
        load_instance = True  # optional: allows JSON -> object

    title = ma.auto_field()
    published_at = ma.auto_field()

    url = ma.Hyperlinks({
        "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
        "collection": ma.URLFor("newsletters")
    })

# Schema instances
newsletter_schema = NewsletterSchema()          # single item
newsletters_schema = NewsletterSchema(many=True) # multiple items

# ---------------------------
# Resources
# ---------------------------
class Index(Resource):
    def get(self):
        response_dict = {
            "index": "Welcome to the Newsletter RESTful API"
        }
        return make_response(response_dict, 200)

# All newsletters
class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(newsletters_schema.dump(newsletters), 200)

    def post(self):
        new_newsletter = Newsletter(
            title=request.form['title'],
            body=request.form['body']
        )
        db.session.add(new_newsletter)
        db.session.commit()
        return make_response(newsletter_schema.dump(new_newsletter), 201)

# Single newsletter by ID
class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"message": "Newsletter not found"}, 404)
        return make_response(newsletter_schema.dump(newsletter), 200)

    def patch(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"message": "Newsletter not found"}, 404)

        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])
        db.session.commit()

        return make_response(newsletter_schema.dump(newsletter), 200)

    def delete(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if not newsletter:
            return make_response({"message": "Newsletter not found"}, 404)

        db.session.delete(newsletter)
        db.session.commit()
        return make_response({"message": "record successfully deleted"}, 200)

# ---------------------------
# Routes
# ---------------------------
api.add_resource(Index, '/')
api.add_resource(Newsletters, '/newsletters')
api.add_resource(NewsletterByID, '/newsletters/<int:id>')

# ---------------------------
# Run server
# ---------------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
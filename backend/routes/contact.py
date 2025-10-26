from flask import Blueprint, request, jsonify
from models.contact import Contact
from db import db

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def add_contact():
    data = request.get_json()
    contact = Contact(name=data['name'], email=data['email'], message=data['message'])
    db.session.add(contact)
    db.session.commit()
    return jsonify({"message": "Contact form submitted successfully"})

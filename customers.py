from flask import Blueprint, request, jsonify
from models import db, Customer

bp = Blueprint("customers", __name__, url_prefix="/api/customers")

@bp.get("/")
def list_customers():
    items = Customer.query.order_by(Customer.idCustomers.asc()).all()
    return jsonify([c.to_dict() for c in items])

@bp.get("/<int:cid>")
def get_customer(cid):
    c = Customer.query.get_or_404(cid)
    return jsonify(c.to_dict())

@bp.post("/")
def create_customer():
    data = request.get_json() or {}
    name = data.get("FirstName")
    if not name:
        return jsonify({"ok": False, "message": "FirstName required"}), 400
    c = Customer(FirstName=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"ok": True, "data": c.to_dict()}), 201

@bp.put("/<int:cid>")
def update_customer(cid):
    data = request.get_json() or {}
    c = Customer.query.get_or_404(cid)
    c.FirstName = data.get("FirstName", c.FirstName)
    db.session.commit()
    return jsonify({"ok": True, "data": c.to_dict()})

@bp.delete("/<int:cid>")
def delete_customer(cid):
    c = Customer.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True})

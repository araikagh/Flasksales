from flask import Blueprint, request, jsonify
from models import db, Category

bp = Blueprint("categories", __name__, url_prefix="/api/categories")

@bp.get("/")
def list_categories():
    items = Category.query.order_by(Category.CategoryName.asc()).all()
    return jsonify([c.to_dict() for c in items])

@bp.post("/")
def create_category():
    data = request.get_json() or {}
    name = data.get("CategoryName")
    if not name:
        return jsonify({"ok": False, "message": "CategoryName required"}), 400
    c = Category(CategoryName=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"ok": True, "data": c.to_dict()}), 201

@bp.put("/<int:cid>")
def update_category(cid):
    c = Category.query.get_or_404(cid)
    data = request.get_json() or {}
    c.CategoryName = data.get("CategoryName", c.CategoryName)
    db.session.commit()
    return jsonify({"ok": True, "data": c.to_dict()})

@bp.delete("/<int:cid>")
def delete_category(cid):
    c = Category.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True})

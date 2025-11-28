from flask import Blueprint, request, jsonify
from models import db, Product, Category

bp = Blueprint("products", __name__, url_prefix="/api/products")

@bp.get("/")
def list_products():
    q = request.args.get("q")
    cat = request.args.get("category")
    query = Product.query.join(Category, isouter=True)
    if cat:
        try:
            query = query.filter(Product.CategoryId == int(cat))
        except:
            pass
    if q:
        query = query.filter(Product.ProductName.ilike(f"%{q}%"))
    items = query.order_by(Product.id.asc()).all()
    return jsonify([p.to_dict() for p in items])

@bp.get("/<int:pid>")
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_dict())

@bp.post("/")
def create_product():
    data = request.get_json() or {}
    name = data.get("ProductName")
    if not name:
        return jsonify({"ok": False, "message": "ProductName required"}), 400
    try:
        p = Product(
            ProductName=name,
            Manufacturer=data.get("Manufacturer", "Не указано"),
            ProductCount=int(data.get("ProductCount", 0)),
            Price=float(data.get("Price", 0)),
            CategoryId=int(data.get("CategoryId"))
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({"ok": True, "data": p.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": str(e)}), 400

@bp.put("/<int:pid>")
def update_product(pid):
    data = request.get_json() or {}
    p = Product.query.get_or_404(pid)
    p.ProductName = data.get("ProductName", p.ProductName)
    p.Manufacturer = data.get("Manufacturer", p.Manufacturer)
    if "ProductCount" in data:
        p.ProductCount = int(data.get("ProductCount", p.ProductCount))
    if "Price" in data:
        p.Price = float(data.get("Price", p.Price))
    if "CategoryId" in data:
        p.CategoryId = int(data.get("CategoryId")) if data.get("CategoryId") else None
    db.session.commit()
    db.session.refresh(p)
    return jsonify({"ok": True, "data": p.to_dict()})

@bp.delete("/<int:pid>")
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})

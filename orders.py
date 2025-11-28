from flask import Blueprint, request, jsonify, session
from models import db, Order, Product, Customer
from datetime import datetime

bp = Blueprint("orders", __name__, url_prefix="/api/orders")

@bp.get("/")
def list_orders():
    items = Order.query.order_by(Order.idorders.desc()).all()
    return jsonify([o.to_dict() for o in items])

@bp.get("/<int:oid>")
def get_order(oid):
    o = Order.query.get_or_404(oid)
    return jsonify(o.to_dict())

@bp.post("/")
def create_order():
    data = request.get_json() or {}
    pid = data.get("ProductId") or data.get("pid")
    cnt = int(data.get("ProductCount") or data.get("cnt") or 1)
    cid = data.get("CustomerId") or session.get("customer_id")
    if not pid or not cid:
        return jsonify({"ok": False, "message": "ProductId and CustomerId required"}), 400
    product = Product.query.get(pid)
    if not product:
        return jsonify({"ok": False, "message": "Product not found"}), 404
    available = int(product.ProductCount or 0)
    if available < cnt:
        return jsonify({"ok": False, "message": "Not enough stock"}), 400
    customer = Customer.query.get(cid)
    if not customer:
        return jsonify({"ok": False, "message": "Customer not found"}), 404
    price = float(product.Price)
    order = Order(ProductId=product.id, CustomerId=customer.idCustomers,
                  ProductCount=cnt, Price=price, CreatedAt=datetime.now())
    product.ProductCount = available - cnt
    db.session.add(order)
    db.session.commit()
    return jsonify({"ok": True, "data": order.to_dict()}), 201

@bp.put("/<int:oid>")
def update_order(oid):
    o = Order.query.get_or_404(oid)
    data = request.get_json() or {}
    if "ProductCount" in data:
        new_cnt = int(data["ProductCount"])
        diff = new_cnt - o.ProductCount
        prod = Product.query.get(o.ProductId)
        if diff > 0:
            if prod.ProductCount < diff:
                return jsonify({"ok": False, "message": "Not enough stock to increase order"}), 400
            prod.ProductCount -= diff
        else:
            prod.ProductCount += (-diff)
        o.ProductCount = new_cnt
        o.totalpay = float(o.Price) * new_cnt
    if "ProductId" in data:
        new_pid = int(data["ProductId"])
        new_prod = Product.query.get(new_pid)
        if not new_prod:
            return jsonify({"ok": False, "message": "New product not found"}), 404
        # restore old product stock then deduct new product stock
        old_prod = Product.query.get(o.ProductId)
        if old_prod:
            old_prod.ProductCount += o.ProductCount
        if new_prod.ProductCount < o.ProductCount:
            return jsonify({"ok": False, "message": "Not enough stock in new product"}), 400
        new_prod.ProductCount -= o.ProductCount
        o.ProductId = new_pid
    db.session.commit()
    return jsonify({"ok": True, "data": o.to_dict()})

@bp.delete("/<int:oid>")
def delete_order(oid):
    o = Order.query.get_or_404(oid)
    # restore stock on delete
    p = Product.query.get(o.ProductId)
    if p:
        p.ProductCount = (p.ProductCount or 0) + (o.ProductCount or 0)
    db.session.delete(o)
    db.session.commit()
    return jsonify({"ok": True})

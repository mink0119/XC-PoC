#!/usr/bin/env python3
"""In-memory Pet Shop API. Legacy /pet routes plus a storefront-sized catalog.

BOLA lab pieces live in bola_model.py: operator JWT and owned private objects.
This server does not enforce ownership — defense is expected only from XC.
"""

import json
import os
import sys
import threading
from pathlib import Path

import bola_model

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "80"))
STATUSES = ("available", "pending", "sold")

_lock = threading.Lock()
_next_id = 1
_pets = {}


def _seed():
    global _next_id
    samples = [
        {"name": "Buddy", "status": "available", "category": "dog", "tags": ["friendly"]},
        {"name": "Milo", "status": "pending", "category": "cat", "tags": ["indoor"]},
        {"name": "Nemo", "status": "sold", "category": "fish", "tags": ["small"]},
    ]
    for pet in samples:
        pet = dict(pet)
        pet["id"] = _next_id
        _pets[_next_id] = pet
        _next_id += 1


def _error(message):
    return {"message": message}


def _parse_pet(body):
    if not isinstance(body, dict):
        return None, "JSON object 가 필요합니다"
    name = body.get("name")
    status = body.get("status")
    if not isinstance(name, str) or not name.strip():
        return None, "name 은 비어 있지 않은 문자열이어야 합니다"
    if status not in STATUSES:
        return None, "status 는 available, pending, sold 중 하나여야 합니다"
    if "category" in body and body["category"] is not None and not isinstance(body["category"], str):
        return None, "category 는 문자열이어야 합니다"
    tags = body.get("tags", [])
    if tags is None:
        tags = []
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        return None, "tags 는 문자열 배열이어야 합니다"
    return {
        "name": name.strip(),
        "status": status,
        "category": body.get("category") or "",
        "tags": tags,
    }, None


def _stamp(row):
    row.setdefault("createdAt", "2026-04-12T09:00:00Z")
    row.setdefault("updatedAt", "2026-10-01T03:12:00Z")
    return row


def _product(i):
    names = ["Salmon Kibble 2kg", "Feather Cat Teaser", "Adjustable Harness"]
    return _stamp({
        "id": i,
        "sku": f"PET-{i:04d}",
        "name": names[(i - 1) % len(names)],
        "price": round(8.5 + i * 3.25, 2),
        "currency": "USD",
        "status": "active",
        "categoryId": ((i - 1) % 4) + 1,
        "brandId": ((i - 1) % 3) + 1,
        "stock": 12 + i * 4,
        "rating": round(4.1 + (i % 5) * 0.1, 1),
    })


def _pet_record(i):
    names = ["Buddy", "Milo", "Nemo", "Coco", "Luna"]
    species = ["dog", "cat", "fish", "bird", "rabbit"]
    return _stamp({
        "id": i,
        "name": names[(i - 1) % len(names)],
        "species": species[(i - 1) % len(species)],
        "breedId": ((i - 1) % 6) + 1,
        "status": STATUSES[(i - 1) % len(STATUSES)],
        "customerId": ((i - 1) % 5) + 1,
        "weightKg": round(1.2 + i * 1.7, 1),
    })


def _customer(i):
    return _stamp({
        "id": i,
        "email": f"customer{i}@petshop.local",
        "firstName": ["Ada", "Jin", "Noah", "Mina", "Owen"][(i - 1) % 5],
        "lastName": ["Kim", "Park", "Cho", "Lee", "Song"][(i - 1) % 5],
        "phone": f"+1-415-555-01{i:02d}",
        "loyaltyTier": ["bronze", "silver", "gold"][(i - 1) % 3],
        "status": "active",
    })


def _order(i):
    return _stamp({
        "id": i,
        "number": f"PS-2026-{1000 + i}",
        "customerId": ((i - 1) % 5) + 1,
        "status": ["placed", "paid", "shipped", "delivered"][(i - 1) % 4],
        "currency": "USD",
        "subtotal": round(20 + i * 7.5, 2),
        "shipping": 4.5,
        "total": round(24.5 + i * 7.5, 2),
        "storeId": ((i - 1) % 3) + 1,
    })


def _store(i):
    return _stamp({
        "id": i,
        "name": ["Mission Store", "Soma Clinic", "Sunset Adoption"][(i - 1) % 3],
        "city": "San Francisco",
        "phone": f"+1-415-555-20{i:02d}",
        "timezone": "America/Los_Angeles",
        "status": "open",
    })


def _appointment(i):
    return _stamp({
        "id": i,
        "service": ["grooming", "boarding", "training", "veterinary"][(i - 1) % 4],
        "petId": ((i - 1) % 5) + 1,
        "customerId": ((i - 1) % 5) + 1,
        "storeId": ((i - 1) % 3) + 1,
        "veterinarianId": ((i - 1) % 4) + 1,
        "startsAt": f"2026-11-{(i % 27) + 1:02d}T15:00:00Z",
        "status": ["requested", "confirmed", "completed"][(i - 1) % 3],
    })


BUILDERS = {
    "categories": lambda i: _stamp({"id": i, "slug": ["dogs", "cats", "fish", "birds"][(i - 1) % 4], "name": ["Dogs", "Cats", "Fish", "Birds"][(i - 1) % 4], "parentId": None}),
    "products": _product,
    "brands": lambda i: _stamp({"id": i, "name": ["North Paw", "Harbor Pet", "Little Den"][(i - 1) % 3], "country": "US"}),
    "breeds": lambda i: _stamp({"id": i, "name": ["Labrador", "Siamese", "Holland Lop"][(i - 1) % 3], "species": ["dog", "cat", "rabbit"][(i - 1) % 3]}),
    "foods": lambda i: _stamp({"id": i, "name": ["Adult Salmon", "Kitten Chicken", "Pond Pellets"][(i - 1) % 3], "species": ["dog", "cat", "fish"][(i - 1) % 3], "kcalPer100g": 320 + i}),
    "toys": lambda i: _stamp({"id": i, "name": ["Rope Tug", "Feather Wand", "Bell Ball"][(i - 1) % 3], "species": ["dog", "cat", "cat"][(i - 1) % 3], "price": 6 + i}),
    "medications": lambda i: _stamp({"id": i, "name": ["Flea Tablet", "Joint Chew", "Ear Drops"][(i - 1) % 3], "requiresPrescription": i % 2 == 0}),
    "accessories": lambda i: _stamp({"id": i, "name": ["Nylon Collar", "Travel Crate", "Ceramic Bowl"][(i - 1) % 3], "price": 9 + i * 4}),
    "pets": _pet_record,
    "customers": _customer,
    "addresses": lambda i: _stamp({"id": i, "customerId": ((i - 1) % 5) + 1, "line1": f"{100 + i} Market St", "city": "San Francisco", "region": "CA", "postalCode": f"9410{i}", "country": "US", "kind": "shipping"}),
    "orders": _order,
    "payments": lambda i: _stamp({"id": i, "orderId": i, "method": ["card", "paypal", "gift_card"][(i - 1) % 3], "status": "captured", "amount": round(24.5 + i * 7.5, 2), "currency": "USD", "last4": f"{1000 + i}"[-4:]}),
    "refunds": lambda i: _stamp({"id": i, "paymentId": i, "amount": 5 + i, "currency": "USD", "status": "succeeded", "reason": "customer_request"}),
    "shipments": lambda i: _stamp({"id": i, "orderId": i, "carrier": "UPS", "service": "ground", "status": "in_transit", "trackingNumber": f"1Z{i:08d}"}),
    "returns": lambda i: _stamp({"id": i, "orderId": i, "status": "requested", "reason": "wrong_size"}),
    "coupons": lambda i: _stamp({"id": i, "code": ["WELCOME10", "PAW20", "CLINIC15"][(i - 1) % 3], "percentOff": [10, 20, 15][(i - 1) % 3], "status": "active"}),
    "gift-cards": lambda i: _stamp({"id": i, "code": f"GC-{i:04d}", "balance": 25 * i, "currency": "USD", "status": "active"}),
    "stores": _store,
    "services": lambda i: _stamp({"id": i, "code": ["grooming", "boarding", "training", "veterinary", "daycare"][(i - 1) % 5], "name": ["Grooming", "Boarding", "Training", "Veterinary", "Daycare"][(i - 1) % 5], "durationMinutes": 30 * i, "price": 25 * i}),
    "appointments": _appointment,
    "veterinarians": lambda i: _stamp({"id": i, "name": ["Dr. Han", "Dr. Brooks", "Dr. Ibarra", "Dr. Shah"][(i - 1) % 4], "specialty": ["general", "dental", "surgery", "dermatology"][(i - 1) % 4], "storeId": ((i - 1) % 3) + 1}),
    "shelters": lambda i: _stamp({"id": i, "name": ["Bay Shelter", "Sunset Rescue"][(i - 1) % 2], "city": "San Francisco", "capacity": 40 + i * 10}),
    "adoptions": lambda i: _stamp({"id": i, "petId": i, "shelterId": ((i - 1) % 2) + 1, "status": ["listed", "pending", "adopted"][(i - 1) % 3], "fee": 75 + i * 10}),
    "foster-homes": lambda i: _stamp({"id": i, "name": f"Foster Home {i}", "city": "Oakland", "capacity": 2}),
    "articles": lambda i: _stamp({"id": i, "slug": ["first-week-puppy", "cat-nutrition", "aquarium-basics"][(i - 1) % 3], "title": ["A puppy's first week", "Cat nutrition", "Aquarium basics"][(i - 1) % 3], "author": "Pet Shop Editors"}),
    "faq": lambda i: _stamp({"id": i, "question": ["Do you ship food?", "Can I book grooming online?", "What is the return window?"][(i - 1) % 3], "answer": "Yes. See the linked policy for the details that apply to this item."}),
    "promotions": lambda i: _stamp({"id": i, "name": ["Spring kits", "Clinic week", "Adopt and save"][(i - 1) % 3], "status": "active", "startsAt": "2026-10-01T00:00:00Z", "endsAt": "2026-12-31T00:00:00Z"}),
    "banners": lambda i: _stamp({"id": i, "title": ["New food", "Book grooming", "Adopt"][(i - 1) % 3], "href": ["/api/v1/foods", "/api/v1/services/grooming", "/api/v1/adoptions"][(i - 1) % 3], "active": True}),
    "pages": lambda i: _stamp({"id": i, "slug": ["about", "shipping", "privacy"][(i - 1) % 3], "title": ["About", "Shipping", "Privacy"][(i - 1) % 3]}),
    "reviews": lambda i: _stamp({"id": i, "productId": i, "customerId": i, "rating": 4 + (i % 2), "title": "Solid", "body": "Used it for two weeks."}),
    "subscriptions": lambda i: _stamp({"id": i, "customerId": i, "plan": ["food-monthly", "litter-monthly", "treats-biweekly"][(i - 1) % 3], "status": "active", "nextRenewalAt": "2026-11-12T00:00:00Z"}),
    "webhooks": lambda i: _stamp({"id": i, "url": f"https://example.local/hooks/{i}", "events": ["order.paid", "shipment.updated"], "status": "enabled"}),
    "notifications": lambda i: _stamp({"id": i, "customerId": i, "channel": "email", "title": "Order update", "read": False}),
    "inventory": lambda i: _stamp({"id": i, "sku": f"PET-{i:04d}", "storeId": ((i - 1) % 3) + 1, "onHand": 10 + i, "reserved": i % 3}),
    "carts": lambda i: _stamp({"id": i, "customerId": i, "currency": "USD", "itemCount": 2, "subtotal": 31.5}),
    "users": lambda i: _stamp({"id": i, "email": f"staff{i}@petshop.local", "role": ["clerk", "manager", "admin"][(i - 1) % 3], "status": "active"}),
}


def _item(resource, i):
    builder = BUILDERS.get(resource)
    if builder:
        return builder(int(i))
    return _stamp({"id": int(i), "name": f"{resource}-{i}", "status": "active"})


def _child(child, parent_id, i):
    row = _stamp({"id": i, "parentId": int(parent_id)})
    if child == "reviews":
        row.update(rating=5, title="Happy pet", body="Finished the bag.", author="Jamie")
    elif child == "images":
        row.update(url=f"https://cdn.petshop.local/{parent_id}/{i}.jpg", alt="product photo")
    elif child == "inventory":
        row.update(sku=f"PET-{int(parent_id):04d}", onHand=18, reserved=1, storeId=1)
    elif child == "variants":
        row.update(name=["Small", "Medium", "Large"][(i - 1) % 3], sku=f"PET-{int(parent_id):04d}-{i}", price=12 + i)
    elif child in ("related", "products"):
        row.update(_product(i))
        row["parentId"] = int(parent_id)
    elif child == "photos":
        row.update(url=f"https://cdn.petshop.local/pets/{parent_id}/{i}.jpg")
    elif child == "medical-records":
        row.update(visitAt="2026-09-02T16:00:00Z", diagnosis="healthy", veterinarianId=1)
    elif child == "vaccinations":
        row.update(name="rabies", givenAt="2026-05-01", dueAt="2027-05-01")
    elif child == "weight-history":
        row.update(kg=round(4 + i * 0.4, 1), recordedAt="2026-09-14")
    elif child == "allergies":
        row.update(name="chicken", severity="mild")
    elif child == "owners":
        row.update(_customer(i))
    elif child == "addresses":
        row.update(line1=f"{200 + i} Valencia St", city="San Francisco", postalCode="94110", country="US")
    elif child == "pets":
        row.update(_pet_record(i))
    elif child == "orders":
        row.update(_order(i))
    elif child == "payment-methods":
        row.update(brand="visa", last4=f"{4240 + i}"[-4:], expires="2028-08")
    elif child == "wishlist":
        row.update(productId=i)
    elif child == "notifications":
        row.update(title="Appointment tomorrow", channel="email", read=False)
    elif child == "subscriptions":
        row.update(plan="food-monthly", status="active")
    elif child == "items":
        row.update(sku=f"PET-{i:04d}", name="Salmon Kibble 2kg", quantity=1, unitPrice=18.0)
    elif child == "shipments":
        row.update(carrier="UPS", trackingNumber=f"1Z{i:08d}", status="label_created")
    elif child == "invoice":
        row.update(number=f"INV-{1000 + int(parent_id)}", total=42.0, currency="USD")
    elif child == "returns":
        row.update(status="requested", reason="changed_mind")
    elif child == "timeline":
        row.update(event="paid", at="2026-10-02T18:04:00Z")
    elif child == "refunds":
        row.update(amount=8.0, currency="USD", status="succeeded")
    elif child == "tracking":
        row.update(status="in_transit", location="Oakland, CA", at="2026-10-20T11:00:00Z")
    elif child == "events":
        row.update(status="arrived_at_facility", location="Richmond, CA")
    elif child == "balance":
        row.update(amount=40.0, currency="USD")
    elif child == "hours":
        row.update(day=["mon", "tue", "wed"][(i - 1) % 3], opens="09:00", closes="18:00")
    elif child == "staff":
        row.update(name=["Sam", "Riley", "Quinn"][(i - 1) % 3], role="associate")
    elif child == "services":
        row.update(code="grooming", name="Grooming", price=45)
    elif child == "slots":
        row.update(startsAt="2026-11-03T16:00:00Z", remaining=3)
    elif child == "notes":
        row.update(author="Dr. Han", body="No follow-up needed.")
    elif child == "schedule":
        row.update(weekday="tue", startsAt="09:00", endsAt="17:00")
    elif child == "patients":
        row.update(petId=i, lastVisit="2026-09-02")
    elif child == "animals":
        row.update(_pet_record(i))
        row["status"] = "adoptable"
    elif child == "applications":
        row.update(customerId=i, status="in_review", submittedAt="2026-10-11T00:00:00Z")
    elif child == "documents":
        row.update(name="adoption-agreement.pdf", url=f"https://cdn.petshop.local/docs/{parent_id}/{i}.pdf")
    elif child == "comments":
        row.update(author="Nora", body="Helpful article.")
    elif child == "nutrition":
        row.update(protein=28, fat=14, fiber=4)
    elif child == "dosage":
        row.update(amount="1 tablet", frequency="monthly", species="dog")
    elif child in ("invoices",):
        row.update(number=f"SUB-{i:04d}", total=29.0, currency="USD", status="paid")
    elif child == "deliveries":
        row.update(event="order.paid", status="delivered", responseCode=200)
    elif child == "movements":
        row.update(delta=-1, reason="order_allocated")
    else:
        row.update(name=f"{child}-{i}", status="active")
    return row


def _page(items):
    return {"items": items, "page": 1, "pageSize": 20, "total": len(items)}


# path, resource key, tag, summary, child segments
RESOURCES = [
    ("/api/v1/categories", "categories", "catalog", "카테고리", ["products"]),
    ("/api/v1/products", "products", "catalog", "상품", ["reviews", "images", "inventory", "variants", "related"]),
    ("/api/v1/brands", "brands", "catalog", "브랜드", ["products"]),
    ("/api/v1/breeds", "breeds", "catalog", "품종", ["pets"]),
    ("/api/v1/foods", "foods", "catalog", "사료", ["nutrition", "reviews"]),
    ("/api/v1/toys", "toys", "catalog", "장난감", ["reviews", "images"]),
    ("/api/v1/medications", "medications", "catalog", "의약품", ["dosage"]),
    ("/api/v1/accessories", "accessories", "catalog", "용품", ["variants", "images"]),
    ("/api/v1/inventory", "inventory", "catalog", "재고", ["movements"]),
    ("/api/v1/pets", "pets", "pets", "반려동물", ["photos", "medical-records", "vaccinations", "weight-history", "allergies", "owners"]),
    ("/api/v1/customers", "customers", "customers", "고객", ["addresses", "pets", "orders", "payment-methods", "wishlist", "notifications", "subscriptions", "reviews"]),
    ("/api/v1/addresses", "addresses", "customers", "주소", []),
    ("/api/v1/carts", "carts", "checkout", "장바구니", ["items"]),
    ("/api/v1/orders", "orders", "checkout", "주문", ["items", "shipments", "invoice", "returns", "timeline"]),
    ("/api/v1/payments", "payments", "checkout", "결제", ["refunds"]),
    ("/api/v1/refunds", "refunds", "checkout", "환불", []),
    ("/api/v1/shipments", "shipments", "checkout", "배송", ["tracking", "events"]),
    ("/api/v1/returns", "returns", "checkout", "반품", ["items"]),
    ("/api/v1/coupons", "coupons", "checkout", "쿠폰", []),
    ("/api/v1/gift-cards", "gift-cards", "checkout", "기프트 카드", ["balance"]),
    ("/api/v1/stores", "stores", "stores", "매장", ["hours", "inventory", "staff", "services", "reviews"]),
    ("/api/v1/services", "services", "stores", "서비스", ["slots"]),
    ("/api/v1/appointments", "appointments", "stores", "예약", ["notes", "pets"]),
    ("/api/v1/veterinarians", "veterinarians", "stores", "수의사", ["schedule", "patients"]),
    ("/api/v1/shelters", "shelters", "adoption", "보호소", ["animals", "staff"]),
    ("/api/v1/adoptions", "adoptions", "adoption", "입양", ["applications", "documents"]),
    ("/api/v1/foster-homes", "foster-homes", "adoption", "임시 보호", ["animals"]),
    ("/api/v1/articles", "articles", "content", "아티클", ["comments"]),
    ("/api/v1/faq", "faq", "content", "FAQ", []),
    ("/api/v1/promotions", "promotions", "content", "프로모션", ["products"]),
    ("/api/v1/banners", "banners", "content", "배너", []),
    ("/api/v1/pages", "pages", "content", "페이지", []),
    ("/api/v1/reviews", "reviews", "content", "리뷰", ["comments"]),
    ("/api/v1/subscriptions", "subscriptions", "loyalty", "구독", ["invoices", "items"]),
    ("/api/v1/notifications", "notifications", "customers", "알림", []),
    ("/api/v1/webhooks", "webhooks", "admin", "웹훅", ["deliveries"]),
    ("/api/v1/admin/users", "users", "admin", "운영 사용자", ["notifications"]),
    ("/api/v2/pets", "pets", "v2", "반려동물 v2", ["photos", "owners"]),
    ("/api/v2/products", "products", "v2", "상품 v2", ["variants", "inventory"]),
    ("/api/v2/orders", "orders", "v2", "주문 v2", ["items", "shipments"]),
    ("/api/v2/customers", "customers", "v2", "고객 v2", ["addresses", "orders"]),
    ("/api/v2/stores", "stores", "v2", "매장 v2", ["hours", "services"]),
]


def _singleton(path, summary, tag, payload, methods=("GET",)):
    return [(method, path, summary, tag, "singleton", None, None, payload) for method in methods]


def _build_routes():
    routes = []
    for path, resource, tag, summary, children in RESOURCES:
        routes.append(("GET", path, f"{summary} 목록", tag, "list", resource, None, None))
        routes.append(("POST", path, f"{summary} 추가", tag, "create", resource, None, None))
        item = path + "/{id}"
        routes.append(("GET", item, f"{summary} 조회", tag, "item", resource, None, None))
        routes.append(("PUT", item, f"{summary} 수정", tag, "update", resource, None, None))
        routes.append(("PATCH", item, f"{summary} 일부 수정", tag, "update", resource, None, None))
        routes.append(("DELETE", item, f"{summary} 삭제", tag, "delete", resource, None, None))
        for child in children:
            routes.append(("GET", item + "/" + child, f"{summary} {child}", tag, "child", resource, child, None))
            routes.append(("POST", item + "/" + child, f"{summary} {child} 추가", tag, "child-create", resource, child, None))

    routes.extend(_singleton("/api", "API 입구", "meta", {
        "name": "Pet Shop API",
        "versions": ["/api/v1", "/api/v2"],
        "docs": "/docs",
        "swagger": "/swagger.json",
    }))
    routes.extend(_singleton("/api/v1", "API v1 입구", "meta", {
        "version": "v1",
        "resources": [row[0] for row in RESOURCES if row[0].startswith("/api/v1/")],
    }))
    routes.extend(_singleton("/api/v2", "API v2 입구", "meta", {
        "version": "v2",
        "resources": [row[0] for row in RESOURCES if row[0].startswith("/api/v2/")],
    }))
    routes.extend(_singleton("/ready", "ready", "meta", {"status": "ready"}))
    routes.extend(_singleton("/live", "live", "meta", {"status": "live"}))
    routes.extend(_singleton("/version", "버전", "meta", {"name": "petshop", "version": "1.1.0", "api": ["v1", "v2"]}))
    routes.extend(_singleton("/metrics", "메트릭", "meta", {
        "httpRequestsTotal": 12840,
        "pets": 3,
        "ordersOpen": 6,
    }))
    routes.extend(_singleton("/api/v1/products/search", "상품 검색", "catalog", {
        "query": "salmon",
        "items": [_product(1), _product(2)],
        "total": 2,
    }))
    routes.extend(_singleton("/api/v1/pets/findByStatus", "상태별 pet", "pets", {
        "status": ["available"],
        "items": [_pet_record(1)],
        "total": 1,
    }))
    routes.extend(_singleton("/api/v1/pets/findByTags", "태그별 pet", "pets", {
        "tags": ["friendly"],
        "items": [_pet_record(1)],
        "total": 1,
    }))
    routes.extend(_singleton("/api/v1/search", "통합 검색", "catalog", {
        "query": "buddy",
        "products": [_product(1)],
        "pets": [_pet_record(1)],
        "articles": [_item("articles", 1)],
    }))
    routes.extend(_singleton("/api/v1/recommendations", "추천", "catalog", {
        "customerId": 1,
        "items": [_product(2), _product(3)],
    }))
    routes.extend(_singleton("/api/v1/sitemap", "사이트맵", "content", {
        "urls": ["/api/v1/products", "/api/v1/pets", "/api/v1/stores", "/api/v1/articles", "/api/v1/adoptions"],
    }))
    routes.extend(_singleton("/api/v1/cart", "현재 장바구니", "checkout", {
        "id": 1, "currency": "USD", "itemCount": 2, "subtotal": 31.5,
        "items": [_child("items", 1, 1), _child("items", 1, 2)],
    }, methods=("GET", "DELETE")))
    routes.extend(_singleton("/api/v1/cart/items", "장바구니 상품", "checkout", _page([_child("items", 1, 1), _child("items", 1, 2)]), methods=("GET", "POST")))
    routes.extend(_singleton("/api/v1/cart/coupon", "장바구니 쿠폰", "checkout", {"code": "WELCOME10", "percentOff": 10, "applied": True}, methods=("PUT", "DELETE")))
    routes.extend(_singleton("/api/v1/checkout", "체크아웃", "checkout", {"status": "ready", "cartId": 1, "total": 36.0, "currency": "USD"}, methods=("GET", "POST")))
    routes.extend(_singleton("/api/v1/checkout/shipping-rates", "배송비", "checkout", {"items": [{"service": "ground", "amount": 4.5, "currency": "USD", "etaDays": 4}, {"service": "express", "amount": 14.0, "currency": "USD", "etaDays": 1}]}))
    routes.extend(_singleton("/api/v1/checkout/payment-intent", "결제 의도", "checkout", {"id": "pi_test_1001", "amount": 36.0, "currency": "USD", "status": "requires_confirmation"}, methods=("POST",)))
    for path, summary, payload in (
        ("/api/v1/me", "내 계정", _customer(1)),
        ("/api/v1/me/profile", "내 프로필", {"customerId": 1, "displayName": "Ada Kim", "bio": "Two dogs and a tank."}),
        ("/api/v1/me/preferences", "내 설정", {"marketingEmail": True, "sms": False, "locale": "ko-KR"}),
        ("/api/v1/me/payment-methods", "내 결제 수단", _page([_child("payment-methods", 1, 1)])),
        ("/api/v1/me/addresses", "내 주소", _page([_item("addresses", 1)])),
        ("/api/v1/me/orders", "내 주문", _page([_order(1), _order(2)])),
        ("/api/v1/me/pets", "내 반려동물", _page([_pet_record(1), _pet_record(2)])),
        ("/api/v1/me/wishlist", "내 위시리스트", _page([_child("wishlist", 1, 1), _child("wishlist", 1, 2)])),
        ("/api/v1/me/notifications", "내 알림", _page([_item("notifications", 1)])),
        ("/api/v1/me/sessions", "내 세션", _page([{"id": 1, "userAgent": "curl", "current": True, "lastSeenAt": "2026-10-28T05:00:00Z"}])),
    ):
        routes.extend(_singleton(path, summary, "account", payload))
    token = {"accessToken": "test-token", "tokenType": "Bearer", "expiresIn": 3600}
    routes.extend(_singleton("/api/v1/auth/login", "로그인", "auth", token, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/token", "운영사/고객 JWT 발급", "auth", {
        "accessToken": "<jwt>",
        "tokenType": "Bearer",
        "expiresIn": 86400,
    }, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/logout", "로그아웃", "auth", {"status": "signed_out"}, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/register", "가입", "auth", {"customer": _customer(9), "accessToken": "test-token", "tokenType": "Bearer"}, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/refresh", "토큰 갱신", "auth", token, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/forgot-password", "비밀번호 찾기", "auth", {"status": "sent"}, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/reset-password", "비밀번호 재설정", "auth", {"status": "updated"}, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/verify-email", "이메일 인증", "auth", {"status": "verified"}, methods=("POST",)))
    routes.extend(_singleton("/api/v1/auth/sessions", "인증 세션", "auth", _page([{"id": 1, "current": True}])))
    routes.extend(_singleton("/api/v1/loyalty", "멤버십", "loyalty", {"customerId": 1, "tier": "silver", "points": 420}))
    routes.extend(_singleton("/api/v1/loyalty/points", "포인트", "loyalty", {"balance": 420, "pending": 20, "expiring": 0}))
    routes.extend(_singleton("/api/v1/loyalty/rewards", "리워드", "loyalty", _page([{"id": 1, "name": "$5 coupon", "points": 500, "available": False}])))
    routes.extend(_singleton("/api/v1/services/grooming", "그루밍", "stores", {"code": "grooming", "name": "Grooming", "price": 45, "durationMinutes": 60}))
    routes.extend(_singleton("/api/v1/services/boarding", "호텔링", "stores", {"code": "boarding", "name": "Boarding", "price": 55, "durationMinutes": 1440}))
    routes.extend(_singleton("/api/v1/services/training", "훈련", "stores", {"code": "training", "name": "Training", "price": 80, "durationMinutes": 50}))
    routes.extend(_singleton("/api/v1/services/veterinary", "진료", "stores", {"code": "veterinary", "name": "Veterinary", "price": 70, "durationMinutes": 30}))
    routes.extend(_singleton("/api/v1/services/daycare", "데이케어", "stores", {"code": "daycare", "name": "Daycare", "price": 40, "durationMinutes": 480}))
    routes.extend(_singleton("/api/v1/admin/dashboard", "관리자 대시보드", "admin", {"ordersToday": 18, "revenueToday": 1460.25, "lowStock": 4, "appointmentsToday": 11}))
    routes.extend(_singleton("/api/v1/admin/reports/sales", "매출 리포트", "admin", {"range": "2026-10", "orders": 420, "revenue": 28640.15, "currency": "USD"}))
    routes.extend(_singleton("/api/v1/admin/reports/inventory", "재고 리포트", "admin", {"lowStock": [_item("inventory", 2)], "skus": 86}))
    routes.extend(_singleton("/api/v1/admin/reports/customers", "고객 리포트", "admin", {"newCustomers": 36, "returning": 210, "range": "2026-10"}))
    routes.extend(_singleton("/api/v1/admin/roles", "역할", "admin", _page([{"id": 1, "name": "admin"}, {"id": 2, "name": "clerk"}])))
    routes.extend(_singleton("/api/v1/admin/audit-logs", "감사 로그", "admin", _page([{"id": 1, "actor": "staff1", "action": "order.refund", "at": "2026-10-21T04:12:00Z"}])))
    routes.extend(_singleton("/api/v1/admin/settings", "설정", "admin", {"storeName": "Pet Shop", "currency": "USD", "timezone": "America/Los_Angeles"}))
    routes.extend(_singleton("/api/v1/inventory/low-stock", "부족 재고", "catalog", _page([_item("inventory", 2)])))
    return routes


ROUTES = _build_routes()


def _match(method, path):
    exact = [route for route in ROUTES if route[0] == method and "{" not in route[1] and route[1] == path]
    if exact:
        return exact[0], {}
    parts = [part for part in path.split("/") if part]
    for route in ROUTES:
        if route[0] != method or "{" not in route[1]:
            continue
        template = [part for part in route[1].split("/") if part]
        if len(template) != len(parts):
            continue
        ids = {}
        matched = True
        for expected, actual in zip(template, parts):
            if expected.startswith("{") and expected.endswith("}"):
                if not actual.isdigit() or int(actual) < 1:
                    matched = False
                    break
                ids[expected[1:-1]] = int(actual)
            elif expected != actual:
                matched = False
                break
        if matched:
            return route, ids
    return None, {}


def _render(route, ids, body):
    _method, _path, _summary, _tag, kind, resource, child, payload = route
    parent = ids.get("id", 1)
    if kind == "singleton":
        data = payload() if callable(payload) else payload
        status = 201 if _method == "POST" else 200
        if isinstance(body, dict) and _method in ("POST", "PUT", "PATCH"):
            if isinstance(data, dict):
                data = dict(data)
                data.update({key: value for key, value in body.items() if key != "items"})
        if _method == "DELETE":
            return 204, None
        return status, data
    if kind == "list":
        return 200, _page([_item(resource, n) for n in (1, 2, 3)])
    if kind == "item":
        return 200, _item(resource, parent)
    if kind == "create":
        created = _item(resource, 1000)
        if isinstance(body, dict):
            created.update({key: value for key, value in body.items() if key != "id"})
            created["id"] = 1000
        return 201, created
    if kind == "update":
        updated = _item(resource, parent)
        if isinstance(body, dict):
            updated.update(body)
            updated["id"] = parent
        return 200, updated
    if kind == "delete":
        return 204, None
    if kind == "child":
        return 200, _page([_child(child, parent, n) for n in (1, 2)])
    if kind == "child-create":
        created = _child(child, parent, 1000)
        if isinstance(body, dict):
            created.update({key: value for key, value in body.items() if key != "id"})
            created["id"] = 1000
        return 201, created
    return 404, _error("없는 경로입니다")


def _openapi():
    paths = {}
    for method, template, summary, tag, kind, _resource, _child, _payload in ROUTES:
        operation = {
            "tags": [tag],
            "summary": summary,
            "operationId": f"{method.lower()}_{template.strip('/').replace('/', '_').replace('{', '').replace('}', '')}",
            "responses": {},
        }
        if "{id}" in template:
            operation["parameters"] = [{
                "name": "id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer", "minimum": 1},
            }]
        if method in ("POST", "PUT", "PATCH"):
            operation["requestBody"] = {
                "required": False,
                "content": {"application/json": {"schema": {"type": "object"}}},
            }
        if kind == "delete" or method == "DELETE":
            operation["responses"]["204"] = {"description": "삭제됨"}
        elif method == "POST":
            operation["responses"]["201"] = {"description": "생성됨"}
        else:
            operation["responses"]["200"] = {"description": "성공"}
        paths.setdefault(template, {})[method.lower()] = operation
    paths["/health"] = {"get": {"tags": ["meta"], "summary": "헬스 체크", "operationId": "health", "responses": {"200": {"description": "ok"}}}}
    paths["/swagger.json"] = {"get": {"tags": ["meta"], "summary": "OpenAPI 스펙", "operationId": "swagger", "responses": {"200": {"description": "이 파일"}}}}
    paths["/docs"] = {"get": {"tags": ["meta"], "summary": "Swagger UI", "operationId": "docs", "responses": {"200": {"description": "HTML"}}}}
    paths["/"] = {"get": {"tags": ["meta"], "summary": "서비스 인덱스", "operationId": "index", "responses": {"200": {"description": "링크 목록"}}}}
    paths["/pet"] = {
        "get": {"tags": ["legacy"], "summary": "레거시 pet 목록", "operationId": "legacy_list_pets", "responses": {"200": {"description": "목록"}}},
        "post": {"tags": ["legacy"], "summary": "레거시 pet 추가", "operationId": "legacy_create_pet", "responses": {"201": {"description": "생성됨"}, "400": {"description": "잘못된 요청"}}},
    }
    paths["/pet/findByStatus"] = {"get": {"tags": ["legacy"], "summary": "레거시 상태별 pet", "operationId": "legacy_find_by_status", "parameters": [{"name": "status", "in": "query", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "목록"}}}}
    paths["/pet/{petId}"] = {
        "get": {"tags": ["legacy"], "summary": "레거시 pet 조회", "operationId": "legacy_get_pet", "parameters": [{"name": "petId", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "조회"}, "404": {"description": "없음"}}},
        "put": {"tags": ["legacy"], "summary": "레거시 pet 수정", "operationId": "legacy_update_pet", "parameters": [{"name": "petId", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "수정"}, "404": {"description": "없음"}}},
        "delete": {"tags": ["legacy"], "summary": "레거시 pet 삭제", "operationId": "legacy_delete_pet", "parameters": [{"name": "petId", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"204": {"description": "삭제"}, "404": {"description": "없음"}}},
    }
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Pet Shop API",
            "description": (
                "스토어프론트, 주문, 계정 API. "
                "POST /api/v1/auth/token 으로 customer_id·operator_code JWT를 발급한다. "
                "비공개 객체 조회는 소유권을 검사하지 않는다."
            ),
            "version": "1.3.0",
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "servers": [{"url": "/", "description": "이 문서를 연 호스트의 포트 80"}],
        "tags": [
            {"name": "meta", "description": "스펙과 상태"},
            {"name": "legacy", "description": "기존 /pet 경로"},
            {"name": "catalog", "description": "상품 카탈로그"},
            {"name": "pets", "description": "반려동물"},
            {"name": "customers", "description": "고객"},
            {"name": "account", "description": "로그인 사용자"},
            {"name": "auth", "description": "인증"},
            {"name": "checkout", "description": "장바구니, 주문, 결제"},
            {"name": "stores", "description": "매장과 예약"},
            {"name": "adoption", "description": "입양"},
            {"name": "content", "description": "콘텐츠"},
            {"name": "loyalty", "description": "멤버십"},
            {"name": "admin", "description": "운영"},
            {"name": "v2", "description": "v2"},
        ],
        "paths": paths,
    }


def _example_path(template):
    return template.replace("{id}", "1").replace("{petId}", "1")


def _index():
    links = [{"method": "GET", "href": "/"}]
    seen = {"/"}
    for method, template, _summary, _tag, _kind, _resource, _child, _payload in ROUTES:
        if method != "GET":
            continue
        href = _example_path(template)
        if href in seen:
            continue
        seen.add(href)
        links.append({"method": "GET", "href": href})
    for href in ("/health", "/swagger.json", "/docs", "/pet", "/pet/findByStatus?status=available", "/pet/1"):
        if href not in seen:
            links.append({"method": "GET", "href": href})
    return {
        "name": "Pet Shop API",
        "docs": "/docs",
        "swagger": "/swagger.json",
        "api": "/api",
        "links": links,
    }


def _write_discover(spec):
    lines = [
        "#!/bin/sh",
        "# Pet Shop API discovery. 외부 Host 를 ncurity-test.local 로 두고 192.168.41.68:80 으로 보낸다.",
        "#",
        "#   sh /root/nginx/petshop/discover.sh",
        "",
        'RESOLVE="ncurity-test.local:80:192.168.41.68"',
        'BASE="http://ncurity-test.local"',
        'CREATED="/tmp/petshop-create.json"',
        "",
        "call() {",
        "  label=$1",
        "  shift",
        "  printf '\\n======== %s ========\\n' \"$label\"",
        "  curl -v --resolve \"$RESOLVE\" \"$@\"",
        "  printf '\\n'",
        "}",
        "",
        "run() {",
        "  method=$1",
        "  path=$2",
        "  body=$3",
        "  if [ -n \"$body\" ]; then",
        "    call \"$method $path\" -X \"$method\" -H \"Content-Type: application/json\" -d \"$body\" \"$BASE$path\"",
        "  elif [ \"$method\" = \"GET\" ]; then",
        "    call \"$method $path\" \"$BASE$path\"",
        "  else",
        "    call \"$method $path\" -X \"$method\" \"$BASE$path\"",
        "  fi",
        "}",
        "",
        'call "GET /" "$BASE/"',
        'call "GET /health" "$BASE/health"',
        'call "GET /swagger.json" "$BASE/swagger.json"',
        'call "GET /docs" "$BASE/docs"',
        'call "GET /static/swagger-ui.css" -o /dev/null "$BASE/static/swagger-ui.css"',
        'call "GET /static/swagger-ui-bundle.js" -o /dev/null "$BASE/static/swagger-ui-bundle.js"',
        "",
    ]
    body = '{"name":"sample","status":"active"}'
    for method, template, _summary, _tag, kind, _resource, _child, _payload in ROUTES:
        path = _example_path(template)
        if method == "GET" and template in ("/api/v1/products/search", "/api/v1/search"):
            path += "?q=salmon"
        elif method == "GET" and template == "/api/v1/pets/findByStatus":
            path += "?status=available"
        elif method == "GET" and template == "/api/v1/pets/findByTags":
            path += "?tags=friendly"
        payload = body if method in ("POST", "PUT", "PATCH") else ""
        if method == "POST" and "auth/login" in template:
            payload = '{"email":"ada@petshop.local","password":"secret"}'
        elif method == "POST" and "auth/register" in template:
            payload = '{"email":"new@petshop.local","password":"secret","firstName":"Ada"}'
        lines.append(f"run {method} '{path}' '{payload}'")
    lines.extend([
        "",
        'call "GET /pet" "$BASE/pet"',
        'call "GET /pet/findByStatus?status=available" "$BASE/pet/findByStatus?status=available"',
        'call "GET /pet/findByStatus?status=available&status=pending" "$BASE/pet/findByStatus?status=available&status=pending"',
        'call "GET /pet/1" "$BASE/pet/1"',
        "call \"POST /pet\" -o \"$CREATED\" -X POST \"$BASE/pet\" -H \"Content-Type: application/json\" -d '{\"name\":\"Coco\",\"status\":\"available\",\"category\":\"bird\",\"tags\":[\"small\"]}'",
        "printf '%s\\n' \"$(cat \"$CREATED\")\"",
        "id=$(sed -n 's/.*\"id\"[[:space:]]*:[[:space:]]*\\([0-9][0-9]*\\).*/\\1/p' \"$CREATED\")",
        "if [ -n \"$id\" ]; then",
        "  call \"PUT /pet/$id\" -X PUT \"$BASE/pet/$id\" -H \"Content-Type: application/json\" -d '{\"name\":\"Coco\",\"status\":\"sold\",\"category\":\"bird\",\"tags\":[\"small\"]}'",
        "  call \"DELETE /pet/$id\" -X DELETE \"$BASE/pet/$id\"",
        "else",
        "  printf 'POST 응답에서 id 를 찾지 못해 PUT/DELETE 는 건너뜀\\n'",
        "fi",
        "",
    ])
    path = ROOT / "discover.sh"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def _write_flask_routes():
    """Literal @app.route decorators so a static code scan can see every path."""
    lines = [
        "from flask import Flask",
        "",
        'app = Flask("petshop")',
        "app.url_map.strict_slashes = False",
        "",
        "@app.after_request",
        "def _cors(response):",
        '    response.headers["Access-Control-Allow-Origin"] = "*"',
        '    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"',
        '    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"',
        "    return response",
        "",
    ]
    seen = set()

    def add(method, template):
        flask_path = template.replace("{id}", "<int:id>").replace("{petId}", "<int:petId>")
        raw = template.strip("/") or "root"
        fname = method.lower() + "_" + raw.replace("/", "_").replace("{", "").replace("}", "").replace("-", "_").replace(".", "_")
        if fname in seen:
            fname = fname + "_2"
        seen.add(fname)
        params = []
        if "{id}" in template:
            params.append("id")
        if "{petId}" in template:
            params.append("petId")
        signature = ", ".join(params)
        extra = "".join(f", {name}={name}" for name in params)
        lines.append(f'@app.route("{flask_path}", methods=["{method}"])')
        lines.append(f"def {fname}({signature}):")
        lines.append("    from app import invoke")
        lines.append(f'    return invoke("{method}", "{template}"{extra})')
        lines.append("")

    for method, template, *_rest in ROUTES:
        add(method, template)
    for method, template in (
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/swagger.json"),
        ("GET", "/docs"),
        ("GET", "/static/swagger-ui.css"),
        ("GET", "/static/swagger-ui-bundle.js"),
        ("GET", "/pet"),
        ("POST", "/pet"),
        ("GET", "/pet/findByStatus"),
        ("GET", "/pet/{petId}"),
        ("PUT", "/pet/{petId}"),
        ("DELETE", "/pet/{petId}"),
    ):
        add(method, template)
    path = ROOT / "flask_routes.py"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_artifacts():
    spec = _openapi()
    (ROOT / "swagger.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    discover = _write_discover(spec)
    flask_routes = _write_flask_routes()
    paths = sorted({_example_path(route[1]) for route in ROUTES})
    print(f"routes={len(ROUTES)} paths={len(paths)} swagger={ROOT / 'swagger.json'} discover={discover} flask={flask_routes}")


def _response(status, body):
    from flask import Response
    if status == 204:
        return Response(status=204)
    payload = json.dumps(body, ensure_ascii=False)
    return Response(payload, status=status, mimetype="application/json")


def _request_json(required):
    from flask import request
    raw = request.get_data()
    if not raw:
        if required:
            return None, "JSON body 가 필요합니다"
        return {}, None
    try:
        return json.loads(raw.decode("utf-8")), None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "JSON 형식이 아닙니다"


def _pet_id(path):
    prefix = "/pet/"
    if not path.startswith(prefix) or path == "/pet/findByStatus":
        return None
    raw = path[len(prefix):]
    if not raw.isdigit() or int(raw) < 1:
        return None
    return int(raw)


def _legacy(method, path, query):
    if method == "GET" and path == "/pet":
        with _lock:
            body = list(_pets.values())
        return _response(200, body)
    if method == "GET" and path == "/pet/findByStatus":
        statuses = query.get("status", [])
        if not statuses:
            return _response(400, _error("status 쿼리가 필요합니다"))
        if any(item not in STATUSES for item in statuses):
            return _response(400, _error("status 는 available, pending, sold 중 하나여야 합니다"))
        with _lock:
            body = [pet for pet in _pets.values() if pet["status"] in statuses]
        return _response(200, body)
    if method == "POST" and path == "/pet":
        payload, err = _request_json(required=True)
        if err:
            return _response(400, _error(err))
        pet, err = _parse_pet(payload)
        if err:
            return _response(400, _error(err))
        global _next_id
        with _lock:
            pet["id"] = _next_id
            _pets[_next_id] = pet
            _next_id += 1
        return _response(201, pet)
    pet_id = _pet_id(path)
    if pet_id is None:
        return _response(400, _error("petId 는 양의 정수여야 합니다"))
    if method == "GET":
        with _lock:
            pet = _pets.get(pet_id)
        if pet is None:
            return _response(404, _error("pet 을 찾을 수 없습니다"))
        return _response(200, pet)
    if method == "PUT":
        payload, err = _request_json(required=True)
        if err:
            return _response(400, _error(err))
        pet, err = _parse_pet(payload)
        if err:
            return _response(400, _error(err))
        with _lock:
            if pet_id not in _pets:
                return _response(404, _error("pet 을 찾을 수 없습니다"))
            pet["id"] = pet_id
            _pets[pet_id] = pet
        return _response(200, pet)
    if method == "DELETE":
        with _lock:
            if pet_id not in _pets:
                return _response(404, _error("pet 을 찾을 수 없습니다"))
            del _pets[pet_id]
        return _response(204, None)
    return _response(404, _error("없는 경로입니다"))


def _handle_auth_token(body):
    if not isinstance(body, dict):
        return _response(400, _error("JSON object 가 필요합니다"))
    customer_id = body.get("customer_id")
    operator_code = body.get("operator_code")
    token_day = body.get("token_day")
    if not isinstance(customer_id, int) or customer_id < 1:
        return _response(400, _error("customer_id 는 양의 정수여야 합니다"))
    if operator_code is not None and not isinstance(operator_code, str):
        return _response(400, _error("operator_code 는 문자열이어야 합니다"))
    if token_day is not None and not isinstance(token_day, str):
        return _response(400, _error("token_day 는 YYYY-MM-DD 문자열이어야 합니다"))
    try:
        issued = bola_model.issue_token(
            customer_id=customer_id,
            operator_code=operator_code,
            token_day=token_day,
        )
    except ValueError as exc:
        return _response(400, _error(str(exc)))
    return _response(200, issued)


def _handle_private_get(path):
    """Return private objects without ownership checks (vulnerable by design)."""
    parts = [part for part in path.split("/") if part]
    # /api/v1/{orders|payments|customers|pets}/{id}
    if len(parts) == 4 and parts[0] == "api" and parts[1] == "v1" and parts[3].isdigit():
        resource, oid = parts[2], int(parts[3])
        if resource == "orders" and 1 <= oid <= bola_model.CUSTOMER_COUNT * bola_model.ORDERS_PER_CUSTOMER:
            return _response(200, bola_model.order_record(oid))
        if resource == "payments" and 1 <= oid <= bola_model.CUSTOMER_COUNT * bola_model.PAYMENTS_PER_CUSTOMER:
            return _response(200, bola_model.payment_record(oid))
        if resource == "customers" and 1 <= oid <= bola_model.CUSTOMER_COUNT:
            return _response(200, bola_model.customer_record(oid))
        if resource == "pets" and 1 <= oid <= bola_model.CUSTOMER_COUNT:
            return _response(200, bola_model.pet_record(oid))
    # /api/v1/pets/{id}/medical-records
    if (
        len(parts) == 5
        and parts[0] == "api"
        and parts[1] == "v1"
        and parts[2] == "pets"
        and parts[3].isdigit()
        and parts[4] == "medical-records"
    ):
        pet_id = int(parts[3])
        if pet_id < 1 or pet_id > bola_model.CUSTOMER_COUNT:
            return None
        items = [
            bola_model.medical_record(bola_model.medical_record_id_for(pet_id, slot))
            for slot in range(bola_model.MEDICAL_PER_PET)
        ]
        return _response(200, {
            "items": items,
            "total": len(items),
            "petId": pet_id,
            "customerId": bola_model.customer_id_for_pet(pet_id),
        })
    # /api/v1/customers/{id}/orders|payment-methods
    if (
        len(parts) == 5
        and parts[0] == "api"
        and parts[1] == "v1"
        and parts[2] == "customers"
        and parts[3].isdigit()
        and parts[4] in ("orders", "payment-methods")
    ):
        customer_id = int(parts[3])
        if customer_id < 1 or customer_id > bola_model.CUSTOMER_COUNT:
            return None
        if parts[4] == "orders":
            items = [
                bola_model.order_record(bola_model.order_id_for(customer_id, slot))
                for slot in range(bola_model.ORDERS_PER_CUSTOMER)
            ]
        else:
            items = [bola_model.payment_method_record(customer_id, 1)]
        return _response(200, {
            "items": items,
            "total": len(items),
            "customerId": customer_id,
        })
    return None


def invoke(method, template, **ids):
    from flask import request, send_file
    path = template
    for key, value in ids.items():
        path = path.replace("{" + key + "}", str(value))
    path = path.rstrip("/") or "/"
    query = request.args.to_dict(flat=False)
    if path == "/health":
        return _response(200, {"status": "ok"})
    if path == "/swagger.json":
        return _response(200, _openapi())
    if path == "/docs":
        return send_file(ROOT / "static" / "index.html", mimetype="text/html")
    if path == "/static/swagger-ui.css":
        return send_file(ROOT / "static" / "swagger-ui.css", mimetype="text/css")
    if path == "/static/swagger-ui-bundle.js":
        return send_file(ROOT / "static" / "swagger-ui-bundle.js", mimetype="application/javascript")
    if path == "/":
        return _response(200, _index())
    if path == "/pet" or path == "/pet/findByStatus" or path.startswith("/pet/"):
        return _legacy(method, path, query)
    body = None
    if method in ("POST", "PUT", "PATCH"):
        body, err = _request_json(required=False)
        if err:
            return _response(400, _error(err))
    if method == "POST" and path == "/api/v1/auth/token":
        return _handle_auth_token(body or {})
    if method == "GET":
        private = _handle_private_get(path)
        if private is not None:
            return private
    route, matched = _match(method, path)
    if route is None:
        return _response(404, _error("없는 경로입니다"))
    status, payload = _render(route, matched, body)
    return _response(status, payload)


_seed()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--write-artifacts":
        write_artifacts()
        return
    from flask_routes import app
    print(f"Pet Shop API listening on 0.0.0.0:{PORT}  routes={len(ROUTES)}  docs=/docs")
    app.run(host="0.0.0.0", port=PORT, threaded=True)


if __name__ == "__main__":
    main()

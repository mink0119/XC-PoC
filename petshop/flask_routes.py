from flask import Flask

app = Flask("petshop")
app.url_map.strict_slashes = False

@app.before_request
def _cors_preflight():
    from flask import request
    if request.method == "OPTIONS":
        return ("", 204)

@app.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Forwarded-For, X-Real-IP, X-Enforce-Ownership"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

@app.route("/api/v1/categories", methods=["GET"])
def get_api_v1_categories():
    from app import invoke
    return invoke("GET", "/api/v1/categories")

@app.route("/api/v1/categories", methods=["POST"])
def post_api_v1_categories():
    from app import invoke
    return invoke("POST", "/api/v1/categories")

@app.route("/api/v1/categories/<int:id>", methods=["GET"])
def get_api_v1_categories_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/categories/{id}", id=id)

@app.route("/api/v1/categories/<int:id>", methods=["PUT"])
def put_api_v1_categories_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/categories/{id}", id=id)

@app.route("/api/v1/categories/<int:id>", methods=["PATCH"])
def patch_api_v1_categories_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/categories/{id}", id=id)

@app.route("/api/v1/categories/<int:id>", methods=["DELETE"])
def delete_api_v1_categories_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/categories/{id}", id=id)

@app.route("/api/v1/categories/<int:id>/products", methods=["GET"])
def get_api_v1_categories_id_products(id):
    from app import invoke
    return invoke("GET", "/api/v1/categories/{id}/products", id=id)

@app.route("/api/v1/categories/<int:id>/products", methods=["POST"])
def post_api_v1_categories_id_products(id):
    from app import invoke
    return invoke("POST", "/api/v1/categories/{id}/products", id=id)

@app.route("/api/v1/products", methods=["GET"])
def get_api_v1_products():
    from app import invoke
    return invoke("GET", "/api/v1/products")

@app.route("/api/v1/products", methods=["POST"])
def post_api_v1_products():
    from app import invoke
    return invoke("POST", "/api/v1/products")

@app.route("/api/v1/products/<int:id>", methods=["GET"])
def get_api_v1_products_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}", id=id)

@app.route("/api/v1/products/<int:id>", methods=["PUT"])
def put_api_v1_products_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/products/{id}", id=id)

@app.route("/api/v1/products/<int:id>", methods=["PATCH"])
def patch_api_v1_products_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/products/{id}", id=id)

@app.route("/api/v1/products/<int:id>", methods=["DELETE"])
def delete_api_v1_products_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/products/{id}", id=id)

@app.route("/api/v1/products/<int:id>/reviews", methods=["GET"])
def get_api_v1_products_id_reviews(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}/reviews", id=id)

@app.route("/api/v1/products/<int:id>/reviews", methods=["POST"])
def post_api_v1_products_id_reviews(id):
    from app import invoke
    return invoke("POST", "/api/v1/products/{id}/reviews", id=id)

@app.route("/api/v1/products/<int:id>/images", methods=["GET"])
def get_api_v1_products_id_images(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}/images", id=id)

@app.route("/api/v1/products/<int:id>/images", methods=["POST"])
def post_api_v1_products_id_images(id):
    from app import invoke
    return invoke("POST", "/api/v1/products/{id}/images", id=id)

@app.route("/api/v1/products/<int:id>/inventory", methods=["GET"])
def get_api_v1_products_id_inventory(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}/inventory", id=id)

@app.route("/api/v1/products/<int:id>/inventory", methods=["POST"])
def post_api_v1_products_id_inventory(id):
    from app import invoke
    return invoke("POST", "/api/v1/products/{id}/inventory", id=id)

@app.route("/api/v1/products/<int:id>/variants", methods=["GET"])
def get_api_v1_products_id_variants(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}/variants", id=id)

@app.route("/api/v1/products/<int:id>/variants", methods=["POST"])
def post_api_v1_products_id_variants(id):
    from app import invoke
    return invoke("POST", "/api/v1/products/{id}/variants", id=id)

@app.route("/api/v1/products/<int:id>/related", methods=["GET"])
def get_api_v1_products_id_related(id):
    from app import invoke
    return invoke("GET", "/api/v1/products/{id}/related", id=id)

@app.route("/api/v1/products/<int:id>/related", methods=["POST"])
def post_api_v1_products_id_related(id):
    from app import invoke
    return invoke("POST", "/api/v1/products/{id}/related", id=id)

@app.route("/api/v1/brands", methods=["GET"])
def get_api_v1_brands():
    from app import invoke
    return invoke("GET", "/api/v1/brands")

@app.route("/api/v1/brands", methods=["POST"])
def post_api_v1_brands():
    from app import invoke
    return invoke("POST", "/api/v1/brands")

@app.route("/api/v1/brands/<int:id>", methods=["GET"])
def get_api_v1_brands_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/brands/{id}", id=id)

@app.route("/api/v1/brands/<int:id>", methods=["PUT"])
def put_api_v1_brands_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/brands/{id}", id=id)

@app.route("/api/v1/brands/<int:id>", methods=["PATCH"])
def patch_api_v1_brands_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/brands/{id}", id=id)

@app.route("/api/v1/brands/<int:id>", methods=["DELETE"])
def delete_api_v1_brands_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/brands/{id}", id=id)

@app.route("/api/v1/brands/<int:id>/products", methods=["GET"])
def get_api_v1_brands_id_products(id):
    from app import invoke
    return invoke("GET", "/api/v1/brands/{id}/products", id=id)

@app.route("/api/v1/brands/<int:id>/products", methods=["POST"])
def post_api_v1_brands_id_products(id):
    from app import invoke
    return invoke("POST", "/api/v1/brands/{id}/products", id=id)

@app.route("/api/v1/breeds", methods=["GET"])
def get_api_v1_breeds():
    from app import invoke
    return invoke("GET", "/api/v1/breeds")

@app.route("/api/v1/breeds", methods=["POST"])
def post_api_v1_breeds():
    from app import invoke
    return invoke("POST", "/api/v1/breeds")

@app.route("/api/v1/breeds/<int:id>", methods=["GET"])
def get_api_v1_breeds_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/breeds/{id}", id=id)

@app.route("/api/v1/breeds/<int:id>", methods=["PUT"])
def put_api_v1_breeds_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/breeds/{id}", id=id)

@app.route("/api/v1/breeds/<int:id>", methods=["PATCH"])
def patch_api_v1_breeds_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/breeds/{id}", id=id)

@app.route("/api/v1/breeds/<int:id>", methods=["DELETE"])
def delete_api_v1_breeds_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/breeds/{id}", id=id)

@app.route("/api/v1/breeds/<int:id>/pets", methods=["GET"])
def get_api_v1_breeds_id_pets(id):
    from app import invoke
    return invoke("GET", "/api/v1/breeds/{id}/pets", id=id)

@app.route("/api/v1/breeds/<int:id>/pets", methods=["POST"])
def post_api_v1_breeds_id_pets(id):
    from app import invoke
    return invoke("POST", "/api/v1/breeds/{id}/pets", id=id)

@app.route("/api/v1/foods", methods=["GET"])
def get_api_v1_foods():
    from app import invoke
    return invoke("GET", "/api/v1/foods")

@app.route("/api/v1/foods", methods=["POST"])
def post_api_v1_foods():
    from app import invoke
    return invoke("POST", "/api/v1/foods")

@app.route("/api/v1/foods/<int:id>", methods=["GET"])
def get_api_v1_foods_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/foods/{id}", id=id)

@app.route("/api/v1/foods/<int:id>", methods=["PUT"])
def put_api_v1_foods_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/foods/{id}", id=id)

@app.route("/api/v1/foods/<int:id>", methods=["PATCH"])
def patch_api_v1_foods_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/foods/{id}", id=id)

@app.route("/api/v1/foods/<int:id>", methods=["DELETE"])
def delete_api_v1_foods_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/foods/{id}", id=id)

@app.route("/api/v1/foods/<int:id>/nutrition", methods=["GET"])
def get_api_v1_foods_id_nutrition(id):
    from app import invoke
    return invoke("GET", "/api/v1/foods/{id}/nutrition", id=id)

@app.route("/api/v1/foods/<int:id>/nutrition", methods=["POST"])
def post_api_v1_foods_id_nutrition(id):
    from app import invoke
    return invoke("POST", "/api/v1/foods/{id}/nutrition", id=id)

@app.route("/api/v1/foods/<int:id>/reviews", methods=["GET"])
def get_api_v1_foods_id_reviews(id):
    from app import invoke
    return invoke("GET", "/api/v1/foods/{id}/reviews", id=id)

@app.route("/api/v1/foods/<int:id>/reviews", methods=["POST"])
def post_api_v1_foods_id_reviews(id):
    from app import invoke
    return invoke("POST", "/api/v1/foods/{id}/reviews", id=id)

@app.route("/api/v1/toys", methods=["GET"])
def get_api_v1_toys():
    from app import invoke
    return invoke("GET", "/api/v1/toys")

@app.route("/api/v1/toys", methods=["POST"])
def post_api_v1_toys():
    from app import invoke
    return invoke("POST", "/api/v1/toys")

@app.route("/api/v1/toys/<int:id>", methods=["GET"])
def get_api_v1_toys_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/toys/{id}", id=id)

@app.route("/api/v1/toys/<int:id>", methods=["PUT"])
def put_api_v1_toys_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/toys/{id}", id=id)

@app.route("/api/v1/toys/<int:id>", methods=["PATCH"])
def patch_api_v1_toys_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/toys/{id}", id=id)

@app.route("/api/v1/toys/<int:id>", methods=["DELETE"])
def delete_api_v1_toys_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/toys/{id}", id=id)

@app.route("/api/v1/toys/<int:id>/reviews", methods=["GET"])
def get_api_v1_toys_id_reviews(id):
    from app import invoke
    return invoke("GET", "/api/v1/toys/{id}/reviews", id=id)

@app.route("/api/v1/toys/<int:id>/reviews", methods=["POST"])
def post_api_v1_toys_id_reviews(id):
    from app import invoke
    return invoke("POST", "/api/v1/toys/{id}/reviews", id=id)

@app.route("/api/v1/toys/<int:id>/images", methods=["GET"])
def get_api_v1_toys_id_images(id):
    from app import invoke
    return invoke("GET", "/api/v1/toys/{id}/images", id=id)

@app.route("/api/v1/toys/<int:id>/images", methods=["POST"])
def post_api_v1_toys_id_images(id):
    from app import invoke
    return invoke("POST", "/api/v1/toys/{id}/images", id=id)

@app.route("/api/v1/medications", methods=["GET"])
def get_api_v1_medications():
    from app import invoke
    return invoke("GET", "/api/v1/medications")

@app.route("/api/v1/medications", methods=["POST"])
def post_api_v1_medications():
    from app import invoke
    return invoke("POST", "/api/v1/medications")

@app.route("/api/v1/medications/<int:id>", methods=["GET"])
def get_api_v1_medications_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/medications/{id}", id=id)

@app.route("/api/v1/medications/<int:id>", methods=["PUT"])
def put_api_v1_medications_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/medications/{id}", id=id)

@app.route("/api/v1/medications/<int:id>", methods=["PATCH"])
def patch_api_v1_medications_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/medications/{id}", id=id)

@app.route("/api/v1/medications/<int:id>", methods=["DELETE"])
def delete_api_v1_medications_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/medications/{id}", id=id)

@app.route("/api/v1/medications/<int:id>/dosage", methods=["GET"])
def get_api_v1_medications_id_dosage(id):
    from app import invoke
    return invoke("GET", "/api/v1/medications/{id}/dosage", id=id)

@app.route("/api/v1/medications/<int:id>/dosage", methods=["POST"])
def post_api_v1_medications_id_dosage(id):
    from app import invoke
    return invoke("POST", "/api/v1/medications/{id}/dosage", id=id)

@app.route("/api/v1/accessories", methods=["GET"])
def get_api_v1_accessories():
    from app import invoke
    return invoke("GET", "/api/v1/accessories")

@app.route("/api/v1/accessories", methods=["POST"])
def post_api_v1_accessories():
    from app import invoke
    return invoke("POST", "/api/v1/accessories")

@app.route("/api/v1/accessories/<int:id>", methods=["GET"])
def get_api_v1_accessories_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/accessories/{id}", id=id)

@app.route("/api/v1/accessories/<int:id>", methods=["PUT"])
def put_api_v1_accessories_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/accessories/{id}", id=id)

@app.route("/api/v1/accessories/<int:id>", methods=["PATCH"])
def patch_api_v1_accessories_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/accessories/{id}", id=id)

@app.route("/api/v1/accessories/<int:id>", methods=["DELETE"])
def delete_api_v1_accessories_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/accessories/{id}", id=id)

@app.route("/api/v1/accessories/<int:id>/variants", methods=["GET"])
def get_api_v1_accessories_id_variants(id):
    from app import invoke
    return invoke("GET", "/api/v1/accessories/{id}/variants", id=id)

@app.route("/api/v1/accessories/<int:id>/variants", methods=["POST"])
def post_api_v1_accessories_id_variants(id):
    from app import invoke
    return invoke("POST", "/api/v1/accessories/{id}/variants", id=id)

@app.route("/api/v1/accessories/<int:id>/images", methods=["GET"])
def get_api_v1_accessories_id_images(id):
    from app import invoke
    return invoke("GET", "/api/v1/accessories/{id}/images", id=id)

@app.route("/api/v1/accessories/<int:id>/images", methods=["POST"])
def post_api_v1_accessories_id_images(id):
    from app import invoke
    return invoke("POST", "/api/v1/accessories/{id}/images", id=id)

@app.route("/api/v1/inventory", methods=["GET"])
def get_api_v1_inventory():
    from app import invoke
    return invoke("GET", "/api/v1/inventory")

@app.route("/api/v1/inventory", methods=["POST"])
def post_api_v1_inventory():
    from app import invoke
    return invoke("POST", "/api/v1/inventory")

@app.route("/api/v1/inventory/<int:id>", methods=["GET"])
def get_api_v1_inventory_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/inventory/{id}", id=id)

@app.route("/api/v1/inventory/<int:id>", methods=["PUT"])
def put_api_v1_inventory_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/inventory/{id}", id=id)

@app.route("/api/v1/inventory/<int:id>", methods=["PATCH"])
def patch_api_v1_inventory_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/inventory/{id}", id=id)

@app.route("/api/v1/inventory/<int:id>", methods=["DELETE"])
def delete_api_v1_inventory_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/inventory/{id}", id=id)

@app.route("/api/v1/inventory/<int:id>/movements", methods=["GET"])
def get_api_v1_inventory_id_movements(id):
    from app import invoke
    return invoke("GET", "/api/v1/inventory/{id}/movements", id=id)

@app.route("/api/v1/inventory/<int:id>/movements", methods=["POST"])
def post_api_v1_inventory_id_movements(id):
    from app import invoke
    return invoke("POST", "/api/v1/inventory/{id}/movements", id=id)

@app.route("/api/v1/pets", methods=["GET"])
def get_api_v1_pets():
    from app import invoke
    return invoke("GET", "/api/v1/pets")

@app.route("/api/v1/pets", methods=["POST"])
def post_api_v1_pets():
    from app import invoke
    return invoke("POST", "/api/v1/pets")

@app.route("/api/v1/pets/<int:id>", methods=["GET"])
def get_api_v1_pets_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}", id=id)

@app.route("/api/v1/pets/<int:id>", methods=["PUT"])
def put_api_v1_pets_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/pets/{id}", id=id)

@app.route("/api/v1/pets/<int:id>", methods=["PATCH"])
def patch_api_v1_pets_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/pets/{id}", id=id)

@app.route("/api/v1/pets/<int:id>", methods=["DELETE"])
def delete_api_v1_pets_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/pets/{id}", id=id)

@app.route("/api/v1/pets/<int:id>/photos", methods=["GET"])
def get_api_v1_pets_id_photos(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/photos", id=id)

@app.route("/api/v1/pets/<int:id>/photos", methods=["POST"])
def post_api_v1_pets_id_photos(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/photos", id=id)

@app.route("/api/v1/pets/<int:id>/medical-records", methods=["GET"])
def get_api_v1_pets_id_medical_records(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/medical-records", id=id)

@app.route("/api/v1/pets/<int:id>/medical-records", methods=["POST"])
def post_api_v1_pets_id_medical_records(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/medical-records", id=id)

@app.route("/api/v1/pets/<int:id>/vaccinations", methods=["GET"])
def get_api_v1_pets_id_vaccinations(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/vaccinations", id=id)

@app.route("/api/v1/pets/<int:id>/vaccinations", methods=["POST"])
def post_api_v1_pets_id_vaccinations(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/vaccinations", id=id)

@app.route("/api/v1/pets/<int:id>/weight-history", methods=["GET"])
def get_api_v1_pets_id_weight_history(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/weight-history", id=id)

@app.route("/api/v1/pets/<int:id>/weight-history", methods=["POST"])
def post_api_v1_pets_id_weight_history(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/weight-history", id=id)

@app.route("/api/v1/pets/<int:id>/allergies", methods=["GET"])
def get_api_v1_pets_id_allergies(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/allergies", id=id)

@app.route("/api/v1/pets/<int:id>/allergies", methods=["POST"])
def post_api_v1_pets_id_allergies(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/allergies", id=id)

@app.route("/api/v1/pets/<int:id>/owners", methods=["GET"])
def get_api_v1_pets_id_owners(id):
    from app import invoke
    return invoke("GET", "/api/v1/pets/{id}/owners", id=id)

@app.route("/api/v1/pets/<int:id>/owners", methods=["POST"])
def post_api_v1_pets_id_owners(id):
    from app import invoke
    return invoke("POST", "/api/v1/pets/{id}/owners", id=id)

@app.route("/api/v1/customers", methods=["GET"])
def get_api_v1_customers():
    from app import invoke
    return invoke("GET", "/api/v1/customers")

@app.route("/api/v1/customers", methods=["POST"])
def post_api_v1_customers():
    from app import invoke
    return invoke("POST", "/api/v1/customers")

@app.route("/api/v1/customers/<int:id>", methods=["GET"])
def get_api_v1_customers_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}", id=id)

@app.route("/api/v1/customers/<int:id>", methods=["PUT"])
def put_api_v1_customers_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/customers/{id}", id=id)

@app.route("/api/v1/customers/<int:id>", methods=["PATCH"])
def patch_api_v1_customers_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/customers/{id}", id=id)

@app.route("/api/v1/customers/<int:id>", methods=["DELETE"])
def delete_api_v1_customers_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/customers/{id}", id=id)

@app.route("/api/v1/customers/<int:id>/addresses", methods=["GET"])
def get_api_v1_customers_id_addresses(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/addresses", id=id)

@app.route("/api/v1/customers/<int:id>/addresses", methods=["POST"])
def post_api_v1_customers_id_addresses(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/addresses", id=id)

@app.route("/api/v1/customers/<int:id>/pets", methods=["GET"])
def get_api_v1_customers_id_pets(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/pets", id=id)

@app.route("/api/v1/customers/<int:id>/pets", methods=["POST"])
def post_api_v1_customers_id_pets(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/pets", id=id)

@app.route("/api/v1/customers/<int:id>/orders", methods=["GET"])
def get_api_v1_customers_id_orders(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/orders", id=id)

@app.route("/api/v1/customers/<int:id>/orders", methods=["POST"])
def post_api_v1_customers_id_orders(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/orders", id=id)

@app.route("/api/v1/customers/<int:id>/payment-methods", methods=["GET"])
def get_api_v1_customers_id_payment_methods(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/payment-methods", id=id)

@app.route("/api/v1/customers/<int:id>/payment-methods", methods=["POST"])
def post_api_v1_customers_id_payment_methods(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/payment-methods", id=id)

@app.route("/api/v1/customers/<int:id>/wishlist", methods=["GET"])
def get_api_v1_customers_id_wishlist(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/wishlist", id=id)

@app.route("/api/v1/customers/<int:id>/wishlist", methods=["POST"])
def post_api_v1_customers_id_wishlist(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/wishlist", id=id)

@app.route("/api/v1/customers/<int:id>/notifications", methods=["GET"])
def get_api_v1_customers_id_notifications(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/notifications", id=id)

@app.route("/api/v1/customers/<int:id>/notifications", methods=["POST"])
def post_api_v1_customers_id_notifications(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/notifications", id=id)

@app.route("/api/v1/customers/<int:id>/subscriptions", methods=["GET"])
def get_api_v1_customers_id_subscriptions(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/subscriptions", id=id)

@app.route("/api/v1/customers/<int:id>/subscriptions", methods=["POST"])
def post_api_v1_customers_id_subscriptions(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/subscriptions", id=id)

@app.route("/api/v1/customers/<int:id>/reviews", methods=["GET"])
def get_api_v1_customers_id_reviews(id):
    from app import invoke
    return invoke("GET", "/api/v1/customers/{id}/reviews", id=id)

@app.route("/api/v1/customers/<int:id>/reviews", methods=["POST"])
def post_api_v1_customers_id_reviews(id):
    from app import invoke
    return invoke("POST", "/api/v1/customers/{id}/reviews", id=id)

@app.route("/api/v1/addresses", methods=["GET"])
def get_api_v1_addresses():
    from app import invoke
    return invoke("GET", "/api/v1/addresses")

@app.route("/api/v1/addresses", methods=["POST"])
def post_api_v1_addresses():
    from app import invoke
    return invoke("POST", "/api/v1/addresses")

@app.route("/api/v1/addresses/<int:id>", methods=["GET"])
def get_api_v1_addresses_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/addresses/{id}", id=id)

@app.route("/api/v1/addresses/<int:id>", methods=["PUT"])
def put_api_v1_addresses_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/addresses/{id}", id=id)

@app.route("/api/v1/addresses/<int:id>", methods=["PATCH"])
def patch_api_v1_addresses_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/addresses/{id}", id=id)

@app.route("/api/v1/addresses/<int:id>", methods=["DELETE"])
def delete_api_v1_addresses_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/addresses/{id}", id=id)

@app.route("/api/v1/carts", methods=["GET"])
def get_api_v1_carts():
    from app import invoke
    return invoke("GET", "/api/v1/carts")

@app.route("/api/v1/carts", methods=["POST"])
def post_api_v1_carts():
    from app import invoke
    return invoke("POST", "/api/v1/carts")

@app.route("/api/v1/carts/<int:id>", methods=["GET"])
def get_api_v1_carts_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/carts/{id}", id=id)

@app.route("/api/v1/carts/<int:id>", methods=["PUT"])
def put_api_v1_carts_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/carts/{id}", id=id)

@app.route("/api/v1/carts/<int:id>", methods=["PATCH"])
def patch_api_v1_carts_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/carts/{id}", id=id)

@app.route("/api/v1/carts/<int:id>", methods=["DELETE"])
def delete_api_v1_carts_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/carts/{id}", id=id)

@app.route("/api/v1/carts/<int:id>/items", methods=["GET"])
def get_api_v1_carts_id_items(id):
    from app import invoke
    return invoke("GET", "/api/v1/carts/{id}/items", id=id)

@app.route("/api/v1/carts/<int:id>/items", methods=["POST"])
def post_api_v1_carts_id_items(id):
    from app import invoke
    return invoke("POST", "/api/v1/carts/{id}/items", id=id)

@app.route("/api/v1/orders", methods=["GET"])
def get_api_v1_orders():
    from app import invoke
    return invoke("GET", "/api/v1/orders")

@app.route("/api/v1/orders", methods=["POST"])
def post_api_v1_orders():
    from app import invoke
    return invoke("POST", "/api/v1/orders")

@app.route("/api/v1/orders/<int:id>", methods=["GET"])
def get_api_v1_orders_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}", id=id)

@app.route("/api/v1/orders/<int:id>", methods=["PUT"])
def put_api_v1_orders_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/orders/{id}", id=id)

@app.route("/api/v1/orders/<int:id>", methods=["PATCH"])
def patch_api_v1_orders_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/orders/{id}", id=id)

@app.route("/api/v1/orders/<int:id>", methods=["DELETE"])
def delete_api_v1_orders_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/orders/{id}", id=id)

@app.route("/api/v1/orders/<int:id>/items", methods=["GET"])
def get_api_v1_orders_id_items(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}/items", id=id)

@app.route("/api/v1/orders/<int:id>/items", methods=["POST"])
def post_api_v1_orders_id_items(id):
    from app import invoke
    return invoke("POST", "/api/v1/orders/{id}/items", id=id)

@app.route("/api/v1/orders/<int:id>/shipments", methods=["GET"])
def get_api_v1_orders_id_shipments(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}/shipments", id=id)

@app.route("/api/v1/orders/<int:id>/shipments", methods=["POST"])
def post_api_v1_orders_id_shipments(id):
    from app import invoke
    return invoke("POST", "/api/v1/orders/{id}/shipments", id=id)

@app.route("/api/v1/orders/<int:id>/invoice", methods=["GET"])
def get_api_v1_orders_id_invoice(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}/invoice", id=id)

@app.route("/api/v1/orders/<int:id>/invoice", methods=["POST"])
def post_api_v1_orders_id_invoice(id):
    from app import invoke
    return invoke("POST", "/api/v1/orders/{id}/invoice", id=id)

@app.route("/api/v1/orders/<int:id>/returns", methods=["GET"])
def get_api_v1_orders_id_returns(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}/returns", id=id)

@app.route("/api/v1/orders/<int:id>/returns", methods=["POST"])
def post_api_v1_orders_id_returns(id):
    from app import invoke
    return invoke("POST", "/api/v1/orders/{id}/returns", id=id)

@app.route("/api/v1/orders/<int:id>/timeline", methods=["GET"])
def get_api_v1_orders_id_timeline(id):
    from app import invoke
    return invoke("GET", "/api/v1/orders/{id}/timeline", id=id)

@app.route("/api/v1/orders/<int:id>/timeline", methods=["POST"])
def post_api_v1_orders_id_timeline(id):
    from app import invoke
    return invoke("POST", "/api/v1/orders/{id}/timeline", id=id)

@app.route("/api/v1/payments", methods=["GET"])
def get_api_v1_payments():
    from app import invoke
    return invoke("GET", "/api/v1/payments")

@app.route("/api/v1/payments", methods=["POST"])
def post_api_v1_payments():
    from app import invoke
    return invoke("POST", "/api/v1/payments")

@app.route("/api/v1/payments/<int:id>", methods=["GET"])
def get_api_v1_payments_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/payments/{id}", id=id)

@app.route("/api/v1/payments/<int:id>", methods=["PUT"])
def put_api_v1_payments_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/payments/{id}", id=id)

@app.route("/api/v1/payments/<int:id>", methods=["PATCH"])
def patch_api_v1_payments_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/payments/{id}", id=id)

@app.route("/api/v1/payments/<int:id>", methods=["DELETE"])
def delete_api_v1_payments_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/payments/{id}", id=id)

@app.route("/api/v1/payments/<int:id>/refunds", methods=["GET"])
def get_api_v1_payments_id_refunds(id):
    from app import invoke
    return invoke("GET", "/api/v1/payments/{id}/refunds", id=id)

@app.route("/api/v1/payments/<int:id>/refunds", methods=["POST"])
def post_api_v1_payments_id_refunds(id):
    from app import invoke
    return invoke("POST", "/api/v1/payments/{id}/refunds", id=id)

@app.route("/api/v1/refunds", methods=["GET"])
def get_api_v1_refunds():
    from app import invoke
    return invoke("GET", "/api/v1/refunds")

@app.route("/api/v1/refunds", methods=["POST"])
def post_api_v1_refunds():
    from app import invoke
    return invoke("POST", "/api/v1/refunds")

@app.route("/api/v1/refunds/<int:id>", methods=["GET"])
def get_api_v1_refunds_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/refunds/{id}", id=id)

@app.route("/api/v1/refunds/<int:id>", methods=["PUT"])
def put_api_v1_refunds_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/refunds/{id}", id=id)

@app.route("/api/v1/refunds/<int:id>", methods=["PATCH"])
def patch_api_v1_refunds_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/refunds/{id}", id=id)

@app.route("/api/v1/refunds/<int:id>", methods=["DELETE"])
def delete_api_v1_refunds_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/refunds/{id}", id=id)

@app.route("/api/v1/shipments", methods=["GET"])
def get_api_v1_shipments():
    from app import invoke
    return invoke("GET", "/api/v1/shipments")

@app.route("/api/v1/shipments", methods=["POST"])
def post_api_v1_shipments():
    from app import invoke
    return invoke("POST", "/api/v1/shipments")

@app.route("/api/v1/shipments/<int:id>", methods=["GET"])
def get_api_v1_shipments_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/shipments/{id}", id=id)

@app.route("/api/v1/shipments/<int:id>", methods=["PUT"])
def put_api_v1_shipments_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/shipments/{id}", id=id)

@app.route("/api/v1/shipments/<int:id>", methods=["PATCH"])
def patch_api_v1_shipments_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/shipments/{id}", id=id)

@app.route("/api/v1/shipments/<int:id>", methods=["DELETE"])
def delete_api_v1_shipments_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/shipments/{id}", id=id)

@app.route("/api/v1/shipments/<int:id>/tracking", methods=["GET"])
def get_api_v1_shipments_id_tracking(id):
    from app import invoke
    return invoke("GET", "/api/v1/shipments/{id}/tracking", id=id)

@app.route("/api/v1/shipments/<int:id>/tracking", methods=["POST"])
def post_api_v1_shipments_id_tracking(id):
    from app import invoke
    return invoke("POST", "/api/v1/shipments/{id}/tracking", id=id)

@app.route("/api/v1/shipments/<int:id>/events", methods=["GET"])
def get_api_v1_shipments_id_events(id):
    from app import invoke
    return invoke("GET", "/api/v1/shipments/{id}/events", id=id)

@app.route("/api/v1/shipments/<int:id>/events", methods=["POST"])
def post_api_v1_shipments_id_events(id):
    from app import invoke
    return invoke("POST", "/api/v1/shipments/{id}/events", id=id)

@app.route("/api/v1/returns", methods=["GET"])
def get_api_v1_returns():
    from app import invoke
    return invoke("GET", "/api/v1/returns")

@app.route("/api/v1/returns", methods=["POST"])
def post_api_v1_returns():
    from app import invoke
    return invoke("POST", "/api/v1/returns")

@app.route("/api/v1/returns/<int:id>", methods=["GET"])
def get_api_v1_returns_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/returns/{id}", id=id)

@app.route("/api/v1/returns/<int:id>", methods=["PUT"])
def put_api_v1_returns_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/returns/{id}", id=id)

@app.route("/api/v1/returns/<int:id>", methods=["PATCH"])
def patch_api_v1_returns_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/returns/{id}", id=id)

@app.route("/api/v1/returns/<int:id>", methods=["DELETE"])
def delete_api_v1_returns_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/returns/{id}", id=id)

@app.route("/api/v1/returns/<int:id>/items", methods=["GET"])
def get_api_v1_returns_id_items(id):
    from app import invoke
    return invoke("GET", "/api/v1/returns/{id}/items", id=id)

@app.route("/api/v1/returns/<int:id>/items", methods=["POST"])
def post_api_v1_returns_id_items(id):
    from app import invoke
    return invoke("POST", "/api/v1/returns/{id}/items", id=id)

@app.route("/api/v1/coupons", methods=["GET"])
def get_api_v1_coupons():
    from app import invoke
    return invoke("GET", "/api/v1/coupons")

@app.route("/api/v1/coupons", methods=["POST"])
def post_api_v1_coupons():
    from app import invoke
    return invoke("POST", "/api/v1/coupons")

@app.route("/api/v1/coupons/<int:id>", methods=["GET"])
def get_api_v1_coupons_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/coupons/{id}", id=id)

@app.route("/api/v1/coupons/<int:id>", methods=["PUT"])
def put_api_v1_coupons_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/coupons/{id}", id=id)

@app.route("/api/v1/coupons/<int:id>", methods=["PATCH"])
def patch_api_v1_coupons_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/coupons/{id}", id=id)

@app.route("/api/v1/coupons/<int:id>", methods=["DELETE"])
def delete_api_v1_coupons_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/coupons/{id}", id=id)

@app.route("/api/v1/gift-cards", methods=["GET"])
def get_api_v1_gift_cards():
    from app import invoke
    return invoke("GET", "/api/v1/gift-cards")

@app.route("/api/v1/gift-cards", methods=["POST"])
def post_api_v1_gift_cards():
    from app import invoke
    return invoke("POST", "/api/v1/gift-cards")

@app.route("/api/v1/gift-cards/<int:id>", methods=["GET"])
def get_api_v1_gift_cards_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/gift-cards/{id}", id=id)

@app.route("/api/v1/gift-cards/<int:id>", methods=["PUT"])
def put_api_v1_gift_cards_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/gift-cards/{id}", id=id)

@app.route("/api/v1/gift-cards/<int:id>", methods=["PATCH"])
def patch_api_v1_gift_cards_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/gift-cards/{id}", id=id)

@app.route("/api/v1/gift-cards/<int:id>", methods=["DELETE"])
def delete_api_v1_gift_cards_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/gift-cards/{id}", id=id)

@app.route("/api/v1/gift-cards/<int:id>/balance", methods=["GET"])
def get_api_v1_gift_cards_id_balance(id):
    from app import invoke
    return invoke("GET", "/api/v1/gift-cards/{id}/balance", id=id)

@app.route("/api/v1/gift-cards/<int:id>/balance", methods=["POST"])
def post_api_v1_gift_cards_id_balance(id):
    from app import invoke
    return invoke("POST", "/api/v1/gift-cards/{id}/balance", id=id)

@app.route("/api/v1/stores", methods=["GET"])
def get_api_v1_stores():
    from app import invoke
    return invoke("GET", "/api/v1/stores")

@app.route("/api/v1/stores", methods=["POST"])
def post_api_v1_stores():
    from app import invoke
    return invoke("POST", "/api/v1/stores")

@app.route("/api/v1/stores/<int:id>", methods=["GET"])
def get_api_v1_stores_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}", id=id)

@app.route("/api/v1/stores/<int:id>", methods=["PUT"])
def put_api_v1_stores_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/stores/{id}", id=id)

@app.route("/api/v1/stores/<int:id>", methods=["PATCH"])
def patch_api_v1_stores_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/stores/{id}", id=id)

@app.route("/api/v1/stores/<int:id>", methods=["DELETE"])
def delete_api_v1_stores_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/stores/{id}", id=id)

@app.route("/api/v1/stores/<int:id>/hours", methods=["GET"])
def get_api_v1_stores_id_hours(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}/hours", id=id)

@app.route("/api/v1/stores/<int:id>/hours", methods=["POST"])
def post_api_v1_stores_id_hours(id):
    from app import invoke
    return invoke("POST", "/api/v1/stores/{id}/hours", id=id)

@app.route("/api/v1/stores/<int:id>/inventory", methods=["GET"])
def get_api_v1_stores_id_inventory(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}/inventory", id=id)

@app.route("/api/v1/stores/<int:id>/inventory", methods=["POST"])
def post_api_v1_stores_id_inventory(id):
    from app import invoke
    return invoke("POST", "/api/v1/stores/{id}/inventory", id=id)

@app.route("/api/v1/stores/<int:id>/staff", methods=["GET"])
def get_api_v1_stores_id_staff(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}/staff", id=id)

@app.route("/api/v1/stores/<int:id>/staff", methods=["POST"])
def post_api_v1_stores_id_staff(id):
    from app import invoke
    return invoke("POST", "/api/v1/stores/{id}/staff", id=id)

@app.route("/api/v1/stores/<int:id>/services", methods=["GET"])
def get_api_v1_stores_id_services(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}/services", id=id)

@app.route("/api/v1/stores/<int:id>/services", methods=["POST"])
def post_api_v1_stores_id_services(id):
    from app import invoke
    return invoke("POST", "/api/v1/stores/{id}/services", id=id)

@app.route("/api/v1/stores/<int:id>/reviews", methods=["GET"])
def get_api_v1_stores_id_reviews(id):
    from app import invoke
    return invoke("GET", "/api/v1/stores/{id}/reviews", id=id)

@app.route("/api/v1/stores/<int:id>/reviews", methods=["POST"])
def post_api_v1_stores_id_reviews(id):
    from app import invoke
    return invoke("POST", "/api/v1/stores/{id}/reviews", id=id)

@app.route("/api/v1/services", methods=["GET"])
def get_api_v1_services():
    from app import invoke
    return invoke("GET", "/api/v1/services")

@app.route("/api/v1/services", methods=["POST"])
def post_api_v1_services():
    from app import invoke
    return invoke("POST", "/api/v1/services")

@app.route("/api/v1/services/<int:id>", methods=["GET"])
def get_api_v1_services_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/services/{id}", id=id)

@app.route("/api/v1/services/<int:id>", methods=["PUT"])
def put_api_v1_services_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/services/{id}", id=id)

@app.route("/api/v1/services/<int:id>", methods=["PATCH"])
def patch_api_v1_services_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/services/{id}", id=id)

@app.route("/api/v1/services/<int:id>", methods=["DELETE"])
def delete_api_v1_services_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/services/{id}", id=id)

@app.route("/api/v1/services/<int:id>/slots", methods=["GET"])
def get_api_v1_services_id_slots(id):
    from app import invoke
    return invoke("GET", "/api/v1/services/{id}/slots", id=id)

@app.route("/api/v1/services/<int:id>/slots", methods=["POST"])
def post_api_v1_services_id_slots(id):
    from app import invoke
    return invoke("POST", "/api/v1/services/{id}/slots", id=id)

@app.route("/api/v1/appointments", methods=["GET"])
def get_api_v1_appointments():
    from app import invoke
    return invoke("GET", "/api/v1/appointments")

@app.route("/api/v1/appointments", methods=["POST"])
def post_api_v1_appointments():
    from app import invoke
    return invoke("POST", "/api/v1/appointments")

@app.route("/api/v1/appointments/<int:id>", methods=["GET"])
def get_api_v1_appointments_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/appointments/{id}", id=id)

@app.route("/api/v1/appointments/<int:id>", methods=["PUT"])
def put_api_v1_appointments_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/appointments/{id}", id=id)

@app.route("/api/v1/appointments/<int:id>", methods=["PATCH"])
def patch_api_v1_appointments_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/appointments/{id}", id=id)

@app.route("/api/v1/appointments/<int:id>", methods=["DELETE"])
def delete_api_v1_appointments_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/appointments/{id}", id=id)

@app.route("/api/v1/appointments/<int:id>/notes", methods=["GET"])
def get_api_v1_appointments_id_notes(id):
    from app import invoke
    return invoke("GET", "/api/v1/appointments/{id}/notes", id=id)

@app.route("/api/v1/appointments/<int:id>/notes", methods=["POST"])
def post_api_v1_appointments_id_notes(id):
    from app import invoke
    return invoke("POST", "/api/v1/appointments/{id}/notes", id=id)

@app.route("/api/v1/appointments/<int:id>/pets", methods=["GET"])
def get_api_v1_appointments_id_pets(id):
    from app import invoke
    return invoke("GET", "/api/v1/appointments/{id}/pets", id=id)

@app.route("/api/v1/appointments/<int:id>/pets", methods=["POST"])
def post_api_v1_appointments_id_pets(id):
    from app import invoke
    return invoke("POST", "/api/v1/appointments/{id}/pets", id=id)

@app.route("/api/v1/veterinarians", methods=["GET"])
def get_api_v1_veterinarians():
    from app import invoke
    return invoke("GET", "/api/v1/veterinarians")

@app.route("/api/v1/veterinarians", methods=["POST"])
def post_api_v1_veterinarians():
    from app import invoke
    return invoke("POST", "/api/v1/veterinarians")

@app.route("/api/v1/veterinarians/<int:id>", methods=["GET"])
def get_api_v1_veterinarians_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/veterinarians/{id}", id=id)

@app.route("/api/v1/veterinarians/<int:id>", methods=["PUT"])
def put_api_v1_veterinarians_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/veterinarians/{id}", id=id)

@app.route("/api/v1/veterinarians/<int:id>", methods=["PATCH"])
def patch_api_v1_veterinarians_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/veterinarians/{id}", id=id)

@app.route("/api/v1/veterinarians/<int:id>", methods=["DELETE"])
def delete_api_v1_veterinarians_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/veterinarians/{id}", id=id)

@app.route("/api/v1/veterinarians/<int:id>/schedule", methods=["GET"])
def get_api_v1_veterinarians_id_schedule(id):
    from app import invoke
    return invoke("GET", "/api/v1/veterinarians/{id}/schedule", id=id)

@app.route("/api/v1/veterinarians/<int:id>/schedule", methods=["POST"])
def post_api_v1_veterinarians_id_schedule(id):
    from app import invoke
    return invoke("POST", "/api/v1/veterinarians/{id}/schedule", id=id)

@app.route("/api/v1/veterinarians/<int:id>/patients", methods=["GET"])
def get_api_v1_veterinarians_id_patients(id):
    from app import invoke
    return invoke("GET", "/api/v1/veterinarians/{id}/patients", id=id)

@app.route("/api/v1/veterinarians/<int:id>/patients", methods=["POST"])
def post_api_v1_veterinarians_id_patients(id):
    from app import invoke
    return invoke("POST", "/api/v1/veterinarians/{id}/patients", id=id)

@app.route("/api/v1/shelters", methods=["GET"])
def get_api_v1_shelters():
    from app import invoke
    return invoke("GET", "/api/v1/shelters")

@app.route("/api/v1/shelters", methods=["POST"])
def post_api_v1_shelters():
    from app import invoke
    return invoke("POST", "/api/v1/shelters")

@app.route("/api/v1/shelters/<int:id>", methods=["GET"])
def get_api_v1_shelters_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/shelters/{id}", id=id)

@app.route("/api/v1/shelters/<int:id>", methods=["PUT"])
def put_api_v1_shelters_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/shelters/{id}", id=id)

@app.route("/api/v1/shelters/<int:id>", methods=["PATCH"])
def patch_api_v1_shelters_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/shelters/{id}", id=id)

@app.route("/api/v1/shelters/<int:id>", methods=["DELETE"])
def delete_api_v1_shelters_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/shelters/{id}", id=id)

@app.route("/api/v1/shelters/<int:id>/animals", methods=["GET"])
def get_api_v1_shelters_id_animals(id):
    from app import invoke
    return invoke("GET", "/api/v1/shelters/{id}/animals", id=id)

@app.route("/api/v1/shelters/<int:id>/animals", methods=["POST"])
def post_api_v1_shelters_id_animals(id):
    from app import invoke
    return invoke("POST", "/api/v1/shelters/{id}/animals", id=id)

@app.route("/api/v1/shelters/<int:id>/staff", methods=["GET"])
def get_api_v1_shelters_id_staff(id):
    from app import invoke
    return invoke("GET", "/api/v1/shelters/{id}/staff", id=id)

@app.route("/api/v1/shelters/<int:id>/staff", methods=["POST"])
def post_api_v1_shelters_id_staff(id):
    from app import invoke
    return invoke("POST", "/api/v1/shelters/{id}/staff", id=id)

@app.route("/api/v1/adoptions", methods=["GET"])
def get_api_v1_adoptions():
    from app import invoke
    return invoke("GET", "/api/v1/adoptions")

@app.route("/api/v1/adoptions", methods=["POST"])
def post_api_v1_adoptions():
    from app import invoke
    return invoke("POST", "/api/v1/adoptions")

@app.route("/api/v1/adoptions/<int:id>", methods=["GET"])
def get_api_v1_adoptions_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/adoptions/{id}", id=id)

@app.route("/api/v1/adoptions/<int:id>", methods=["PUT"])
def put_api_v1_adoptions_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/adoptions/{id}", id=id)

@app.route("/api/v1/adoptions/<int:id>", methods=["PATCH"])
def patch_api_v1_adoptions_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/adoptions/{id}", id=id)

@app.route("/api/v1/adoptions/<int:id>", methods=["DELETE"])
def delete_api_v1_adoptions_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/adoptions/{id}", id=id)

@app.route("/api/v1/adoptions/<int:id>/applications", methods=["GET"])
def get_api_v1_adoptions_id_applications(id):
    from app import invoke
    return invoke("GET", "/api/v1/adoptions/{id}/applications", id=id)

@app.route("/api/v1/adoptions/<int:id>/applications", methods=["POST"])
def post_api_v1_adoptions_id_applications(id):
    from app import invoke
    return invoke("POST", "/api/v1/adoptions/{id}/applications", id=id)

@app.route("/api/v1/adoptions/<int:id>/documents", methods=["GET"])
def get_api_v1_adoptions_id_documents(id):
    from app import invoke
    return invoke("GET", "/api/v1/adoptions/{id}/documents", id=id)

@app.route("/api/v1/adoptions/<int:id>/documents", methods=["POST"])
def post_api_v1_adoptions_id_documents(id):
    from app import invoke
    return invoke("POST", "/api/v1/adoptions/{id}/documents", id=id)

@app.route("/api/v1/foster-homes", methods=["GET"])
def get_api_v1_foster_homes():
    from app import invoke
    return invoke("GET", "/api/v1/foster-homes")

@app.route("/api/v1/foster-homes", methods=["POST"])
def post_api_v1_foster_homes():
    from app import invoke
    return invoke("POST", "/api/v1/foster-homes")

@app.route("/api/v1/foster-homes/<int:id>", methods=["GET"])
def get_api_v1_foster_homes_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/foster-homes/{id}", id=id)

@app.route("/api/v1/foster-homes/<int:id>", methods=["PUT"])
def put_api_v1_foster_homes_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/foster-homes/{id}", id=id)

@app.route("/api/v1/foster-homes/<int:id>", methods=["PATCH"])
def patch_api_v1_foster_homes_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/foster-homes/{id}", id=id)

@app.route("/api/v1/foster-homes/<int:id>", methods=["DELETE"])
def delete_api_v1_foster_homes_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/foster-homes/{id}", id=id)

@app.route("/api/v1/foster-homes/<int:id>/animals", methods=["GET"])
def get_api_v1_foster_homes_id_animals(id):
    from app import invoke
    return invoke("GET", "/api/v1/foster-homes/{id}/animals", id=id)

@app.route("/api/v1/foster-homes/<int:id>/animals", methods=["POST"])
def post_api_v1_foster_homes_id_animals(id):
    from app import invoke
    return invoke("POST", "/api/v1/foster-homes/{id}/animals", id=id)

@app.route("/api/v1/articles", methods=["GET"])
def get_api_v1_articles():
    from app import invoke
    return invoke("GET", "/api/v1/articles")

@app.route("/api/v1/articles", methods=["POST"])
def post_api_v1_articles():
    from app import invoke
    return invoke("POST", "/api/v1/articles")

@app.route("/api/v1/articles/<int:id>", methods=["GET"])
def get_api_v1_articles_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/articles/{id}", id=id)

@app.route("/api/v1/articles/<int:id>", methods=["PUT"])
def put_api_v1_articles_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/articles/{id}", id=id)

@app.route("/api/v1/articles/<int:id>", methods=["PATCH"])
def patch_api_v1_articles_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/articles/{id}", id=id)

@app.route("/api/v1/articles/<int:id>", methods=["DELETE"])
def delete_api_v1_articles_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/articles/{id}", id=id)

@app.route("/api/v1/articles/<int:id>/comments", methods=["GET"])
def get_api_v1_articles_id_comments(id):
    from app import invoke
    return invoke("GET", "/api/v1/articles/{id}/comments", id=id)

@app.route("/api/v1/articles/<int:id>/comments", methods=["POST"])
def post_api_v1_articles_id_comments(id):
    from app import invoke
    return invoke("POST", "/api/v1/articles/{id}/comments", id=id)

@app.route("/api/v1/faq", methods=["GET"])
def get_api_v1_faq():
    from app import invoke
    return invoke("GET", "/api/v1/faq")

@app.route("/api/v1/faq", methods=["POST"])
def post_api_v1_faq():
    from app import invoke
    return invoke("POST", "/api/v1/faq")

@app.route("/api/v1/faq/<int:id>", methods=["GET"])
def get_api_v1_faq_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/faq/{id}", id=id)

@app.route("/api/v1/faq/<int:id>", methods=["PUT"])
def put_api_v1_faq_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/faq/{id}", id=id)

@app.route("/api/v1/faq/<int:id>", methods=["PATCH"])
def patch_api_v1_faq_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/faq/{id}", id=id)

@app.route("/api/v1/faq/<int:id>", methods=["DELETE"])
def delete_api_v1_faq_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/faq/{id}", id=id)

@app.route("/api/v1/promotions", methods=["GET"])
def get_api_v1_promotions():
    from app import invoke
    return invoke("GET", "/api/v1/promotions")

@app.route("/api/v1/promotions", methods=["POST"])
def post_api_v1_promotions():
    from app import invoke
    return invoke("POST", "/api/v1/promotions")

@app.route("/api/v1/promotions/<int:id>", methods=["GET"])
def get_api_v1_promotions_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/promotions/{id}", id=id)

@app.route("/api/v1/promotions/<int:id>", methods=["PUT"])
def put_api_v1_promotions_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/promotions/{id}", id=id)

@app.route("/api/v1/promotions/<int:id>", methods=["PATCH"])
def patch_api_v1_promotions_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/promotions/{id}", id=id)

@app.route("/api/v1/promotions/<int:id>", methods=["DELETE"])
def delete_api_v1_promotions_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/promotions/{id}", id=id)

@app.route("/api/v1/promotions/<int:id>/products", methods=["GET"])
def get_api_v1_promotions_id_products(id):
    from app import invoke
    return invoke("GET", "/api/v1/promotions/{id}/products", id=id)

@app.route("/api/v1/promotions/<int:id>/products", methods=["POST"])
def post_api_v1_promotions_id_products(id):
    from app import invoke
    return invoke("POST", "/api/v1/promotions/{id}/products", id=id)

@app.route("/api/v1/banners", methods=["GET"])
def get_api_v1_banners():
    from app import invoke
    return invoke("GET", "/api/v1/banners")

@app.route("/api/v1/banners", methods=["POST"])
def post_api_v1_banners():
    from app import invoke
    return invoke("POST", "/api/v1/banners")

@app.route("/api/v1/banners/<int:id>", methods=["GET"])
def get_api_v1_banners_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/banners/{id}", id=id)

@app.route("/api/v1/banners/<int:id>", methods=["PUT"])
def put_api_v1_banners_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/banners/{id}", id=id)

@app.route("/api/v1/banners/<int:id>", methods=["PATCH"])
def patch_api_v1_banners_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/banners/{id}", id=id)

@app.route("/api/v1/banners/<int:id>", methods=["DELETE"])
def delete_api_v1_banners_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/banners/{id}", id=id)

@app.route("/api/v1/pages", methods=["GET"])
def get_api_v1_pages():
    from app import invoke
    return invoke("GET", "/api/v1/pages")

@app.route("/api/v1/pages", methods=["POST"])
def post_api_v1_pages():
    from app import invoke
    return invoke("POST", "/api/v1/pages")

@app.route("/api/v1/pages/<int:id>", methods=["GET"])
def get_api_v1_pages_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/pages/{id}", id=id)

@app.route("/api/v1/pages/<int:id>", methods=["PUT"])
def put_api_v1_pages_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/pages/{id}", id=id)

@app.route("/api/v1/pages/<int:id>", methods=["PATCH"])
def patch_api_v1_pages_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/pages/{id}", id=id)

@app.route("/api/v1/pages/<int:id>", methods=["DELETE"])
def delete_api_v1_pages_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/pages/{id}", id=id)

@app.route("/api/v1/reviews", methods=["GET"])
def get_api_v1_reviews():
    from app import invoke
    return invoke("GET", "/api/v1/reviews")

@app.route("/api/v1/reviews", methods=["POST"])
def post_api_v1_reviews():
    from app import invoke
    return invoke("POST", "/api/v1/reviews")

@app.route("/api/v1/reviews/<int:id>", methods=["GET"])
def get_api_v1_reviews_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/reviews/{id}", id=id)

@app.route("/api/v1/reviews/<int:id>", methods=["PUT"])
def put_api_v1_reviews_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/reviews/{id}", id=id)

@app.route("/api/v1/reviews/<int:id>", methods=["PATCH"])
def patch_api_v1_reviews_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/reviews/{id}", id=id)

@app.route("/api/v1/reviews/<int:id>", methods=["DELETE"])
def delete_api_v1_reviews_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/reviews/{id}", id=id)

@app.route("/api/v1/reviews/<int:id>/comments", methods=["GET"])
def get_api_v1_reviews_id_comments(id):
    from app import invoke
    return invoke("GET", "/api/v1/reviews/{id}/comments", id=id)

@app.route("/api/v1/reviews/<int:id>/comments", methods=["POST"])
def post_api_v1_reviews_id_comments(id):
    from app import invoke
    return invoke("POST", "/api/v1/reviews/{id}/comments", id=id)

@app.route("/api/v1/subscriptions", methods=["GET"])
def get_api_v1_subscriptions():
    from app import invoke
    return invoke("GET", "/api/v1/subscriptions")

@app.route("/api/v1/subscriptions", methods=["POST"])
def post_api_v1_subscriptions():
    from app import invoke
    return invoke("POST", "/api/v1/subscriptions")

@app.route("/api/v1/subscriptions/<int:id>", methods=["GET"])
def get_api_v1_subscriptions_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/subscriptions/{id}", id=id)

@app.route("/api/v1/subscriptions/<int:id>", methods=["PUT"])
def put_api_v1_subscriptions_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/subscriptions/{id}", id=id)

@app.route("/api/v1/subscriptions/<int:id>", methods=["PATCH"])
def patch_api_v1_subscriptions_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/subscriptions/{id}", id=id)

@app.route("/api/v1/subscriptions/<int:id>", methods=["DELETE"])
def delete_api_v1_subscriptions_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/subscriptions/{id}", id=id)

@app.route("/api/v1/subscriptions/<int:id>/invoices", methods=["GET"])
def get_api_v1_subscriptions_id_invoices(id):
    from app import invoke
    return invoke("GET", "/api/v1/subscriptions/{id}/invoices", id=id)

@app.route("/api/v1/subscriptions/<int:id>/invoices", methods=["POST"])
def post_api_v1_subscriptions_id_invoices(id):
    from app import invoke
    return invoke("POST", "/api/v1/subscriptions/{id}/invoices", id=id)

@app.route("/api/v1/subscriptions/<int:id>/items", methods=["GET"])
def get_api_v1_subscriptions_id_items(id):
    from app import invoke
    return invoke("GET", "/api/v1/subscriptions/{id}/items", id=id)

@app.route("/api/v1/subscriptions/<int:id>/items", methods=["POST"])
def post_api_v1_subscriptions_id_items(id):
    from app import invoke
    return invoke("POST", "/api/v1/subscriptions/{id}/items", id=id)

@app.route("/api/v1/notifications", methods=["GET"])
def get_api_v1_notifications():
    from app import invoke
    return invoke("GET", "/api/v1/notifications")

@app.route("/api/v1/notifications", methods=["POST"])
def post_api_v1_notifications():
    from app import invoke
    return invoke("POST", "/api/v1/notifications")

@app.route("/api/v1/notifications/<int:id>", methods=["GET"])
def get_api_v1_notifications_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/notifications/{id}", id=id)

@app.route("/api/v1/notifications/<int:id>", methods=["PUT"])
def put_api_v1_notifications_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/notifications/{id}", id=id)

@app.route("/api/v1/notifications/<int:id>", methods=["PATCH"])
def patch_api_v1_notifications_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/notifications/{id}", id=id)

@app.route("/api/v1/notifications/<int:id>", methods=["DELETE"])
def delete_api_v1_notifications_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/notifications/{id}", id=id)

@app.route("/api/v1/webhooks", methods=["GET"])
def get_api_v1_webhooks():
    from app import invoke
    return invoke("GET", "/api/v1/webhooks")

@app.route("/api/v1/webhooks", methods=["POST"])
def post_api_v1_webhooks():
    from app import invoke
    return invoke("POST", "/api/v1/webhooks")

@app.route("/api/v1/webhooks/<int:id>", methods=["GET"])
def get_api_v1_webhooks_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/webhooks/{id}", id=id)

@app.route("/api/v1/webhooks/<int:id>", methods=["PUT"])
def put_api_v1_webhooks_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/webhooks/{id}", id=id)

@app.route("/api/v1/webhooks/<int:id>", methods=["PATCH"])
def patch_api_v1_webhooks_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/webhooks/{id}", id=id)

@app.route("/api/v1/webhooks/<int:id>", methods=["DELETE"])
def delete_api_v1_webhooks_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/webhooks/{id}", id=id)

@app.route("/api/v1/webhooks/<int:id>/deliveries", methods=["GET"])
def get_api_v1_webhooks_id_deliveries(id):
    from app import invoke
    return invoke("GET", "/api/v1/webhooks/{id}/deliveries", id=id)

@app.route("/api/v1/webhooks/<int:id>/deliveries", methods=["POST"])
def post_api_v1_webhooks_id_deliveries(id):
    from app import invoke
    return invoke("POST", "/api/v1/webhooks/{id}/deliveries", id=id)

@app.route("/api/v1/admin/users", methods=["GET"])
def get_api_v1_admin_users():
    from app import invoke
    return invoke("GET", "/api/v1/admin/users")

@app.route("/api/v1/admin/users", methods=["POST"])
def post_api_v1_admin_users():
    from app import invoke
    return invoke("POST", "/api/v1/admin/users")

@app.route("/api/v1/admin/users/<int:id>", methods=["GET"])
def get_api_v1_admin_users_id(id):
    from app import invoke
    return invoke("GET", "/api/v1/admin/users/{id}", id=id)

@app.route("/api/v1/admin/users/<int:id>", methods=["PUT"])
def put_api_v1_admin_users_id(id):
    from app import invoke
    return invoke("PUT", "/api/v1/admin/users/{id}", id=id)

@app.route("/api/v1/admin/users/<int:id>", methods=["PATCH"])
def patch_api_v1_admin_users_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v1/admin/users/{id}", id=id)

@app.route("/api/v1/admin/users/<int:id>", methods=["DELETE"])
def delete_api_v1_admin_users_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v1/admin/users/{id}", id=id)

@app.route("/api/v1/admin/users/<int:id>/notifications", methods=["GET"])
def get_api_v1_admin_users_id_notifications(id):
    from app import invoke
    return invoke("GET", "/api/v1/admin/users/{id}/notifications", id=id)

@app.route("/api/v1/admin/users/<int:id>/notifications", methods=["POST"])
def post_api_v1_admin_users_id_notifications(id):
    from app import invoke
    return invoke("POST", "/api/v1/admin/users/{id}/notifications", id=id)

@app.route("/api/v2/pets", methods=["GET"])
def get_api_v2_pets():
    from app import invoke
    return invoke("GET", "/api/v2/pets")

@app.route("/api/v2/pets", methods=["POST"])
def post_api_v2_pets():
    from app import invoke
    return invoke("POST", "/api/v2/pets")

@app.route("/api/v2/pets/<int:id>", methods=["GET"])
def get_api_v2_pets_id(id):
    from app import invoke
    return invoke("GET", "/api/v2/pets/{id}", id=id)

@app.route("/api/v2/pets/<int:id>", methods=["PUT"])
def put_api_v2_pets_id(id):
    from app import invoke
    return invoke("PUT", "/api/v2/pets/{id}", id=id)

@app.route("/api/v2/pets/<int:id>", methods=["PATCH"])
def patch_api_v2_pets_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v2/pets/{id}", id=id)

@app.route("/api/v2/pets/<int:id>", methods=["DELETE"])
def delete_api_v2_pets_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v2/pets/{id}", id=id)

@app.route("/api/v2/pets/<int:id>/photos", methods=["GET"])
def get_api_v2_pets_id_photos(id):
    from app import invoke
    return invoke("GET", "/api/v2/pets/{id}/photos", id=id)

@app.route("/api/v2/pets/<int:id>/photos", methods=["POST"])
def post_api_v2_pets_id_photos(id):
    from app import invoke
    return invoke("POST", "/api/v2/pets/{id}/photos", id=id)

@app.route("/api/v2/pets/<int:id>/owners", methods=["GET"])
def get_api_v2_pets_id_owners(id):
    from app import invoke
    return invoke("GET", "/api/v2/pets/{id}/owners", id=id)

@app.route("/api/v2/pets/<int:id>/owners", methods=["POST"])
def post_api_v2_pets_id_owners(id):
    from app import invoke
    return invoke("POST", "/api/v2/pets/{id}/owners", id=id)

@app.route("/api/v2/products", methods=["GET"])
def get_api_v2_products():
    from app import invoke
    return invoke("GET", "/api/v2/products")

@app.route("/api/v2/products", methods=["POST"])
def post_api_v2_products():
    from app import invoke
    return invoke("POST", "/api/v2/products")

@app.route("/api/v2/products/<int:id>", methods=["GET"])
def get_api_v2_products_id(id):
    from app import invoke
    return invoke("GET", "/api/v2/products/{id}", id=id)

@app.route("/api/v2/products/<int:id>", methods=["PUT"])
def put_api_v2_products_id(id):
    from app import invoke
    return invoke("PUT", "/api/v2/products/{id}", id=id)

@app.route("/api/v2/products/<int:id>", methods=["PATCH"])
def patch_api_v2_products_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v2/products/{id}", id=id)

@app.route("/api/v2/products/<int:id>", methods=["DELETE"])
def delete_api_v2_products_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v2/products/{id}", id=id)

@app.route("/api/v2/products/<int:id>/variants", methods=["GET"])
def get_api_v2_products_id_variants(id):
    from app import invoke
    return invoke("GET", "/api/v2/products/{id}/variants", id=id)

@app.route("/api/v2/products/<int:id>/variants", methods=["POST"])
def post_api_v2_products_id_variants(id):
    from app import invoke
    return invoke("POST", "/api/v2/products/{id}/variants", id=id)

@app.route("/api/v2/products/<int:id>/inventory", methods=["GET"])
def get_api_v2_products_id_inventory(id):
    from app import invoke
    return invoke("GET", "/api/v2/products/{id}/inventory", id=id)

@app.route("/api/v2/products/<int:id>/inventory", methods=["POST"])
def post_api_v2_products_id_inventory(id):
    from app import invoke
    return invoke("POST", "/api/v2/products/{id}/inventory", id=id)

@app.route("/api/v2/orders", methods=["GET"])
def get_api_v2_orders():
    from app import invoke
    return invoke("GET", "/api/v2/orders")

@app.route("/api/v2/orders", methods=["POST"])
def post_api_v2_orders():
    from app import invoke
    return invoke("POST", "/api/v2/orders")

@app.route("/api/v2/orders/<int:id>", methods=["GET"])
def get_api_v2_orders_id(id):
    from app import invoke
    return invoke("GET", "/api/v2/orders/{id}", id=id)

@app.route("/api/v2/orders/<int:id>", methods=["PUT"])
def put_api_v2_orders_id(id):
    from app import invoke
    return invoke("PUT", "/api/v2/orders/{id}", id=id)

@app.route("/api/v2/orders/<int:id>", methods=["PATCH"])
def patch_api_v2_orders_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v2/orders/{id}", id=id)

@app.route("/api/v2/orders/<int:id>", methods=["DELETE"])
def delete_api_v2_orders_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v2/orders/{id}", id=id)

@app.route("/api/v2/orders/<int:id>/items", methods=["GET"])
def get_api_v2_orders_id_items(id):
    from app import invoke
    return invoke("GET", "/api/v2/orders/{id}/items", id=id)

@app.route("/api/v2/orders/<int:id>/items", methods=["POST"])
def post_api_v2_orders_id_items(id):
    from app import invoke
    return invoke("POST", "/api/v2/orders/{id}/items", id=id)

@app.route("/api/v2/orders/<int:id>/shipments", methods=["GET"])
def get_api_v2_orders_id_shipments(id):
    from app import invoke
    return invoke("GET", "/api/v2/orders/{id}/shipments", id=id)

@app.route("/api/v2/orders/<int:id>/shipments", methods=["POST"])
def post_api_v2_orders_id_shipments(id):
    from app import invoke
    return invoke("POST", "/api/v2/orders/{id}/shipments", id=id)

@app.route("/api/v2/customers", methods=["GET"])
def get_api_v2_customers():
    from app import invoke
    return invoke("GET", "/api/v2/customers")

@app.route("/api/v2/customers", methods=["POST"])
def post_api_v2_customers():
    from app import invoke
    return invoke("POST", "/api/v2/customers")

@app.route("/api/v2/customers/<int:id>", methods=["GET"])
def get_api_v2_customers_id(id):
    from app import invoke
    return invoke("GET", "/api/v2/customers/{id}", id=id)

@app.route("/api/v2/customers/<int:id>", methods=["PUT"])
def put_api_v2_customers_id(id):
    from app import invoke
    return invoke("PUT", "/api/v2/customers/{id}", id=id)

@app.route("/api/v2/customers/<int:id>", methods=["PATCH"])
def patch_api_v2_customers_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v2/customers/{id}", id=id)

@app.route("/api/v2/customers/<int:id>", methods=["DELETE"])
def delete_api_v2_customers_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v2/customers/{id}", id=id)

@app.route("/api/v2/customers/<int:id>/addresses", methods=["GET"])
def get_api_v2_customers_id_addresses(id):
    from app import invoke
    return invoke("GET", "/api/v2/customers/{id}/addresses", id=id)

@app.route("/api/v2/customers/<int:id>/addresses", methods=["POST"])
def post_api_v2_customers_id_addresses(id):
    from app import invoke
    return invoke("POST", "/api/v2/customers/{id}/addresses", id=id)

@app.route("/api/v2/customers/<int:id>/orders", methods=["GET"])
def get_api_v2_customers_id_orders(id):
    from app import invoke
    return invoke("GET", "/api/v2/customers/{id}/orders", id=id)

@app.route("/api/v2/customers/<int:id>/orders", methods=["POST"])
def post_api_v2_customers_id_orders(id):
    from app import invoke
    return invoke("POST", "/api/v2/customers/{id}/orders", id=id)

@app.route("/api/v2/stores", methods=["GET"])
def get_api_v2_stores():
    from app import invoke
    return invoke("GET", "/api/v2/stores")

@app.route("/api/v2/stores", methods=["POST"])
def post_api_v2_stores():
    from app import invoke
    return invoke("POST", "/api/v2/stores")

@app.route("/api/v2/stores/<int:id>", methods=["GET"])
def get_api_v2_stores_id(id):
    from app import invoke
    return invoke("GET", "/api/v2/stores/{id}", id=id)

@app.route("/api/v2/stores/<int:id>", methods=["PUT"])
def put_api_v2_stores_id(id):
    from app import invoke
    return invoke("PUT", "/api/v2/stores/{id}", id=id)

@app.route("/api/v2/stores/<int:id>", methods=["PATCH"])
def patch_api_v2_stores_id(id):
    from app import invoke
    return invoke("PATCH", "/api/v2/stores/{id}", id=id)

@app.route("/api/v2/stores/<int:id>", methods=["DELETE"])
def delete_api_v2_stores_id(id):
    from app import invoke
    return invoke("DELETE", "/api/v2/stores/{id}", id=id)

@app.route("/api/v2/stores/<int:id>/hours", methods=["GET"])
def get_api_v2_stores_id_hours(id):
    from app import invoke
    return invoke("GET", "/api/v2/stores/{id}/hours", id=id)

@app.route("/api/v2/stores/<int:id>/hours", methods=["POST"])
def post_api_v2_stores_id_hours(id):
    from app import invoke
    return invoke("POST", "/api/v2/stores/{id}/hours", id=id)

@app.route("/api/v2/stores/<int:id>/services", methods=["GET"])
def get_api_v2_stores_id_services(id):
    from app import invoke
    return invoke("GET", "/api/v2/stores/{id}/services", id=id)

@app.route("/api/v2/stores/<int:id>/services", methods=["POST"])
def post_api_v2_stores_id_services(id):
    from app import invoke
    return invoke("POST", "/api/v2/stores/{id}/services", id=id)

@app.route("/api", methods=["GET"])
def get_api():
    from app import invoke
    return invoke("GET", "/api")

@app.route("/api/v1", methods=["GET"])
def get_api_v1():
    from app import invoke
    return invoke("GET", "/api/v1")

@app.route("/api/v2", methods=["GET"])
def get_api_v2():
    from app import invoke
    return invoke("GET", "/api/v2")

@app.route("/ready", methods=["GET"])
def get_ready():
    from app import invoke
    return invoke("GET", "/ready")

@app.route("/live", methods=["GET"])
def get_live():
    from app import invoke
    return invoke("GET", "/live")

@app.route("/version", methods=["GET"])
def get_version():
    from app import invoke
    return invoke("GET", "/version")

@app.route("/metrics", methods=["GET"])
def get_metrics():
    from app import invoke
    return invoke("GET", "/metrics")

@app.route("/api/v1/products/search", methods=["GET"])
def get_api_v1_products_search():
    from app import invoke
    return invoke("GET", "/api/v1/products/search")

@app.route("/api/v1/pets/findByStatus", methods=["GET"])
def get_api_v1_pets_findByStatus():
    from app import invoke
    return invoke("GET", "/api/v1/pets/findByStatus")

@app.route("/api/v1/pets/findByTags", methods=["GET"])
def get_api_v1_pets_findByTags():
    from app import invoke
    return invoke("GET", "/api/v1/pets/findByTags")

@app.route("/api/v1/search", methods=["GET"])
def get_api_v1_search():
    from app import invoke
    return invoke("GET", "/api/v1/search")

@app.route("/api/v1/recommendations", methods=["GET"])
def get_api_v1_recommendations():
    from app import invoke
    return invoke("GET", "/api/v1/recommendations")

@app.route("/api/v1/sitemap", methods=["GET"])
def get_api_v1_sitemap():
    from app import invoke
    return invoke("GET", "/api/v1/sitemap")

@app.route("/api/v1/cart", methods=["GET"])
def get_api_v1_cart():
    from app import invoke
    return invoke("GET", "/api/v1/cart")

@app.route("/api/v1/cart", methods=["DELETE"])
def delete_api_v1_cart():
    from app import invoke
    return invoke("DELETE", "/api/v1/cart")

@app.route("/api/v1/cart/items", methods=["GET"])
def get_api_v1_cart_items():
    from app import invoke
    return invoke("GET", "/api/v1/cart/items")

@app.route("/api/v1/cart/items", methods=["POST"])
def post_api_v1_cart_items():
    from app import invoke
    return invoke("POST", "/api/v1/cart/items")

@app.route("/api/v1/cart/coupon", methods=["PUT"])
def put_api_v1_cart_coupon():
    from app import invoke
    return invoke("PUT", "/api/v1/cart/coupon")

@app.route("/api/v1/cart/coupon", methods=["DELETE"])
def delete_api_v1_cart_coupon():
    from app import invoke
    return invoke("DELETE", "/api/v1/cart/coupon")

@app.route("/api/v1/checkout", methods=["GET"])
def get_api_v1_checkout():
    from app import invoke
    return invoke("GET", "/api/v1/checkout")

@app.route("/api/v1/checkout", methods=["POST"])
def post_api_v1_checkout():
    from app import invoke
    return invoke("POST", "/api/v1/checkout")

@app.route("/api/v1/checkout/shipping-rates", methods=["GET"])
def get_api_v1_checkout_shipping_rates():
    from app import invoke
    return invoke("GET", "/api/v1/checkout/shipping-rates")

@app.route("/api/v1/checkout/payment-intent", methods=["POST"])
def post_api_v1_checkout_payment_intent():
    from app import invoke
    return invoke("POST", "/api/v1/checkout/payment-intent")

@app.route("/api/v1/me", methods=["GET"])
def get_api_v1_me():
    from app import invoke
    return invoke("GET", "/api/v1/me")

@app.route("/api/v1/me/profile", methods=["GET"])
def get_api_v1_me_profile():
    from app import invoke
    return invoke("GET", "/api/v1/me/profile")

@app.route("/api/v1/me/preferences", methods=["GET"])
def get_api_v1_me_preferences():
    from app import invoke
    return invoke("GET", "/api/v1/me/preferences")

@app.route("/api/v1/me/payment-methods", methods=["GET"])
def get_api_v1_me_payment_methods():
    from app import invoke
    return invoke("GET", "/api/v1/me/payment-methods")

@app.route("/api/v1/me/addresses", methods=["GET"])
def get_api_v1_me_addresses():
    from app import invoke
    return invoke("GET", "/api/v1/me/addresses")

@app.route("/api/v1/me/orders", methods=["GET"])
def get_api_v1_me_orders():
    from app import invoke
    return invoke("GET", "/api/v1/me/orders")

@app.route("/api/v1/me/pets", methods=["GET"])
def get_api_v1_me_pets():
    from app import invoke
    return invoke("GET", "/api/v1/me/pets")

@app.route("/api/v1/me/wishlist", methods=["GET"])
def get_api_v1_me_wishlist():
    from app import invoke
    return invoke("GET", "/api/v1/me/wishlist")

@app.route("/api/v1/me/notifications", methods=["GET"])
def get_api_v1_me_notifications():
    from app import invoke
    return invoke("GET", "/api/v1/me/notifications")

@app.route("/api/v1/me/sessions", methods=["GET"])
def get_api_v1_me_sessions():
    from app import invoke
    return invoke("GET", "/api/v1/me/sessions")

@app.route("/api/v1/auth/login", methods=["POST"])
def post_api_v1_auth_login():
    from app import invoke
    return invoke("POST", "/api/v1/auth/login")

@app.route("/api/v1/auth/token", methods=["POST"])
def post_api_v1_auth_token():
    from app import invoke
    return invoke("POST", "/api/v1/auth/token")

@app.route("/api/v1/auth/logout", methods=["POST"])
def post_api_v1_auth_logout():
    from app import invoke
    return invoke("POST", "/api/v1/auth/logout")

@app.route("/api/v1/auth/register", methods=["POST"])
def post_api_v1_auth_register():
    from app import invoke
    return invoke("POST", "/api/v1/auth/register")

@app.route("/api/v1/auth/refresh", methods=["POST"])
def post_api_v1_auth_refresh():
    from app import invoke
    return invoke("POST", "/api/v1/auth/refresh")

@app.route("/api/v1/auth/forgot-password", methods=["POST"])
def post_api_v1_auth_forgot_password():
    from app import invoke
    return invoke("POST", "/api/v1/auth/forgot-password")

@app.route("/api/v1/auth/reset-password", methods=["POST"])
def post_api_v1_auth_reset_password():
    from app import invoke
    return invoke("POST", "/api/v1/auth/reset-password")

@app.route("/api/v1/auth/verify-email", methods=["POST"])
def post_api_v1_auth_verify_email():
    from app import invoke
    return invoke("POST", "/api/v1/auth/verify-email")

@app.route("/api/v1/auth/sessions", methods=["GET"])
def get_api_v1_auth_sessions():
    from app import invoke
    return invoke("GET", "/api/v1/auth/sessions")

@app.route("/api/v1/loyalty", methods=["GET"])
def get_api_v1_loyalty():
    from app import invoke
    return invoke("GET", "/api/v1/loyalty")

@app.route("/api/v1/loyalty/points", methods=["GET"])
def get_api_v1_loyalty_points():
    from app import invoke
    return invoke("GET", "/api/v1/loyalty/points")

@app.route("/api/v1/loyalty/rewards", methods=["GET"])
def get_api_v1_loyalty_rewards():
    from app import invoke
    return invoke("GET", "/api/v1/loyalty/rewards")

@app.route("/api/v1/services/grooming", methods=["GET"])
def get_api_v1_services_grooming():
    from app import invoke
    return invoke("GET", "/api/v1/services/grooming")

@app.route("/api/v1/services/boarding", methods=["GET"])
def get_api_v1_services_boarding():
    from app import invoke
    return invoke("GET", "/api/v1/services/boarding")

@app.route("/api/v1/services/training", methods=["GET"])
def get_api_v1_services_training():
    from app import invoke
    return invoke("GET", "/api/v1/services/training")

@app.route("/api/v1/services/veterinary", methods=["GET"])
def get_api_v1_services_veterinary():
    from app import invoke
    return invoke("GET", "/api/v1/services/veterinary")

@app.route("/api/v1/services/daycare", methods=["GET"])
def get_api_v1_services_daycare():
    from app import invoke
    return invoke("GET", "/api/v1/services/daycare")

@app.route("/api/v1/admin/dashboard", methods=["GET"])
def get_api_v1_admin_dashboard():
    from app import invoke
    return invoke("GET", "/api/v1/admin/dashboard")

@app.route("/api/v1/admin/reports/sales", methods=["GET"])
def get_api_v1_admin_reports_sales():
    from app import invoke
    return invoke("GET", "/api/v1/admin/reports/sales")

@app.route("/api/v1/admin/reports/inventory", methods=["GET"])
def get_api_v1_admin_reports_inventory():
    from app import invoke
    return invoke("GET", "/api/v1/admin/reports/inventory")

@app.route("/api/v1/admin/reports/customers", methods=["GET"])
def get_api_v1_admin_reports_customers():
    from app import invoke
    return invoke("GET", "/api/v1/admin/reports/customers")

@app.route("/api/v1/admin/roles", methods=["GET"])
def get_api_v1_admin_roles():
    from app import invoke
    return invoke("GET", "/api/v1/admin/roles")

@app.route("/api/v1/admin/audit-logs", methods=["GET"])
def get_api_v1_admin_audit_logs():
    from app import invoke
    return invoke("GET", "/api/v1/admin/audit-logs")

@app.route("/api/v1/admin/settings", methods=["GET"])
def get_api_v1_admin_settings():
    from app import invoke
    return invoke("GET", "/api/v1/admin/settings")

@app.route("/api/v1/inventory/low-stock", methods=["GET"])
def get_api_v1_inventory_low_stock():
    from app import invoke
    return invoke("GET", "/api/v1/inventory/low-stock")

@app.route("/", methods=["GET"])
def get_root():
    from app import invoke
    return invoke("GET", "/")

@app.route("/health", methods=["GET"])
def get_health():
    from app import invoke
    return invoke("GET", "/health")

@app.route("/swagger.json", methods=["GET"])
def get_swagger_json():
    from app import invoke
    return invoke("GET", "/swagger.json")

@app.route("/docs", methods=["GET"])
def get_docs():
    from app import invoke
    return invoke("GET", "/docs")

@app.route("/lab", methods=["GET"])
def get_lab():
    from app import invoke
    return invoke("GET", "/lab")

@app.route("/static/swagger-ui.css", methods=["GET"])
def get_static_swagger_ui_css():
    from app import invoke
    return invoke("GET", "/static/swagger-ui.css")

@app.route("/static/swagger-ui-bundle.js", methods=["GET"])
def get_static_swagger_ui_bundle_js():
    from app import invoke
    return invoke("GET", "/static/swagger-ui-bundle.js")

@app.route("/static/lab.html", methods=["GET"])
def get_static_lab_html():
    from app import invoke
    return invoke("GET", "/static/lab.html")

@app.route("/api/v1/accounts/inquire", methods=["POST"])
def post_api_v1_accounts_inquire():
    from app import invoke
    return invoke("POST", "/api/v1/accounts/inquire")

@app.route("/api/v1/trading/order", methods=["POST"])
def post_api_v1_trading_order():
    from app import invoke
    return invoke("POST", "/api/v1/trading/order")

@app.route("/pet", methods=["GET"])
def get_pet():
    from app import invoke
    return invoke("GET", "/pet")

@app.route("/pet", methods=["POST"])
def post_pet():
    from app import invoke
    return invoke("POST", "/pet")

@app.route("/pet/findByStatus", methods=["GET"])
def get_pet_findByStatus():
    from app import invoke
    return invoke("GET", "/pet/findByStatus")

@app.route("/pet/<int:petId>", methods=["GET"])
def get_pet_petId(petId):
    from app import invoke
    return invoke("GET", "/pet/{petId}", petId=petId)

@app.route("/pet/<int:petId>", methods=["PUT"])
def put_pet_petId(petId):
    from app import invoke
    return invoke("PUT", "/pet/{petId}", petId=petId)

@app.route("/pet/<int:petId>", methods=["DELETE"])
def delete_pet_petId(petId):
    from app import invoke
    return invoke("DELETE", "/pet/{petId}", petId=petId)


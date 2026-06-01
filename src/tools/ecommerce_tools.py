PRODUCTS = {
    "standing desk": {"price": 320, "stock": 4, "weight": 28.0, "category": "furniture"},
    "ergonomic chair": {"price": 180, "stock": 6, "weight": 18.5, "category": "furniture"},
    "conference table": {"price": 540, "stock": 2, "weight": 45.0, "category": "furniture"},
    "filing cabinet": {"price": 210, "stock": 5, "weight": 24.0, "category": "furniture"},
    "whiteboard": {"price": 85, "stock": 7, "weight": 6.5, "category": "office supplies"},
    "conference webcam": {"price": 95, "stock": 3, "weight": 0.8, "category": "meeting equipment"},
    "noise cancelling headset": {"price": 140, "stock": 8, "weight": 0.4, "category": "communication equipment"},
    "business smartphone": {"price": 620, "stock": 9, "weight": 0.22, "category": "communication equipment"},
    "voip desk phone": {"price": 75, "stock": 12, "weight": 0.9, "category": "communication equipment"},
    "portable projector": {"price": 420, "stock": 1, "weight": 2.6, "category": "presentation equipment"},
    "4k monitor": {"price": 260, "stock": 10, "weight": 5.2, "category": "computer equipment"},
    "usb-c docking station": {"price": 130, "stock": 15, "weight": 0.6, "category": "computer equipment"},
    "wireless keyboard": {"price": 55, "stock": 20, "weight": 0.7, "category": "computer equipment"},
    "wireless mouse": {"price": 35, "stock": 25, "weight": 0.2, "category": "computer equipment"},
    "laser printer": {"price": 310, "stock": 4, "weight": 12.0, "category": "office equipment"},
    "document scanner": {"price": 240, "stock": 5, "weight": 3.4, "category": "office equipment"},
    "mesh wifi router": {"price": 170, "stock": 6, "weight": 1.1, "category": "network equipment"},
    "ups battery backup": {"price": 190, "stock": 3, "weight": 9.8, "category": "power equipment"}
}
COUPONS = {
    "OFFICE10": 10,
    "BULK15": 15,
    "WELCOME5": 5,
    "TECH20": 20,
    "FURNI12": 12,
    "SHIP5": 5,
    "NONE": 0
}
SHIPPING_RATE = {
    "hanoi": 4,
    "danang": 6,
    "hcmc": 5,
    "can tho": 7,
    "hai phong": 5,
    "hue": 6,
    "nha trang": 8,
    "da lat": 8
}
SYNONYMS = {
    "phone": ["business smartphone", "voip desk phone", "noise cancelling headset"],
    "phones": ["business smartphone", "voip desk phone", "noise cancelling headset"],
    "smartphone": ["business smartphone"],
    "telephone": ["voip desk phone", "business smartphone"],
    "call": ["voip desk phone", "noise cancelling headset", "conference webcam"],
    "meeting": ["conference webcam", "noise cancelling headset", "portable projector", "conference table"],
    "camera": ["conference webcam"],
    "webcam": ["conference webcam"],
    "desk": ["standing desk", "voip desk phone"],
    "chair": ["ergonomic chair"],
    "projector": ["portable projector"],
    "headset": ["noise cancelling headset"],
    "monitor": ["4k monitor"],
    "screen": ["4k monitor"],
    "keyboard": ["wireless keyboard"],
    "mouse": ["wireless mouse"],
    "dock": ["usb-c docking station"],
    "printer": ["laser printer"],
    "scanner": ["document scanner"],
    "wifi": ["mesh wifi router"],
    "router": ["mesh wifi router"],
    "power": ["ups battery backup"],
    "battery": ["ups battery backup"],
    "board": ["whiteboard"]
}

def _normalize(text: str) -> str:
    return text.lower().strip().strip('"').strip("'")


def _product_line(name: str) -> str:
    product = PRODUCTS[name]
    return (
        f"{name}: price {product['price']} USD, stock {product['stock']} units, "
        f"weight {product['weight']} kg, category {product['category']}"
    )


def check_stock(item_name: str) -> str:
    item = _normalize(item_name)

    if item not in PRODUCTS:
        return f"Product {item_name} not found. Use search_catalog or list_products to find available products."

    return f"{item_name} stock: {PRODUCTS[item]['stock']} units."


def get_price(item_name: str) -> str:
    item = _normalize(item_name)

    if item not in PRODUCTS:
        return f"Product {item_name} not found. Use search_catalog or list_products to find available products."

    return f"{item_name} price: {PRODUCTS[item]['price']} USD."


def get_weight(item_name: str) -> str:
    item = _normalize(item_name)

    if item not in PRODUCTS:
        return f"Product {item_name} not found. Use search_catalog or list_products to find available products."

    return f"{item_name} weight: {PRODUCTS[item]['weight']} kg."


def get_discount(coupon_code: str) -> str:
    code = coupon_code.upper().strip()

    if code not in COUPONS:
        return f"Coupon {coupon_code} not found. Available coupons: {', '.join(COUPONS.keys())}."

    return f"{code} discount: {COUPONS[code]}%."


def calc_shipping(destination: str) -> str:
    city = _normalize(destination)

    if city not in SHIPPING_RATE:
        return f"Shipping destination {destination} not supported. Available destinations: {', '.join(SHIPPING_RATE.keys())}."

    return f"Shipping rate to {destination}: {SHIPPING_RATE[city]} USD per kg."


def calculator(expression: str) -> str:
    allowed = "0123456789+-*/(). "

    if not all(ch in allowed for ch in expression):
        raise ValueError("Expression contains unsupported characters.")

    return str(eval(expression, {"__builtins__": {}}))


def list_products(_: str = "") -> str:
    lines = ["Available products:"]
    for name in sorted(PRODUCTS):
        lines.append(f"- {_product_line(name)}")
    return "\n".join(lines)


def search_catalog(query: str) -> str:
    q = _normalize(query)
    if not q:
        return list_products()

    matches = []
    for name, product in PRODUCTS.items():
        searchable = f"{name} {product['category']}"
        if q in searchable or any(part in searchable for part in q.split()):
            matches.append(name)

    for keyword, product_names in SYNONYMS.items():
        if keyword in q:
            matches.extend(product_names)

    unique_matches = []
    for name in matches:
        if name in PRODUCTS and name not in unique_matches:
            unique_matches.append(name)

    if not unique_matches:
        return (
            f"No exact catalog match for '{query}'.\n"
            f"Available categories: furniture, office supplies, meeting equipment, communication equipment, presentation equipment, computer equipment, office equipment, network equipment, power equipment.\n"
            f"Use list_products to see all available products."
        )

    lines = [f"Catalog search results for '{query}':"]
    for name in unique_matches:
        lines.append(f"- {_product_line(name)}")
    return "\n".join(lines)


def suggest_alternatives(query: str) -> str:
    q = _normalize(query)
    suggestions = []

    for keyword, product_names in SYNONYMS.items():
        if keyword in q:
            suggestions.extend(product_names)

    if not suggestions:
        suggestions = ["standing desk", "ergonomic chair", "business smartphone", "4k monitor", "laser printer", "mesh wifi router"]

    unique_suggestions = []
    for name in suggestions:
        if name in PRODUCTS and name not in unique_suggestions:
            unique_suggestions.append(name)

    lines = [f"Suggested alternatives for '{query}':"]
    for name in unique_suggestions[:3]:
        lines.append(f"- {_product_line(name)}")
    return "\n".join(lines)


def draw_order_flow(_: str = "") -> str:
    return """Order reasoning flow:
User request
  -> search/list product if product is unclear
  -> check_stock(product)
  -> get_price(product)
  -> get_weight(product)
  -> get_discount(coupon)
  -> calc_shipping(destination)
  -> calculator(quantity * price - discount + quantity * weight * shipping_rate)
  -> Final Answer"""


def get_tools_v1():
    return [
        {"name": "check_stock", "description": "Checks stock.", "func": check_stock},
        {"name": "get_price", "description": "Gets price.", "func": get_price},
        {"name": "get_weight", "description": "Gets weight.", "func": get_weight},
        {"name": "get_discount", "description": "Gets discount.", "func": get_discount},
        {"name": "calc_shipping", "description": "Gets shipping.", "func": calc_shipping},
        {"name": "calculator", "description": "Calculates math.", "func": calculator},
        {"name": "search_catalog", "description": "Searches products.", "func": search_catalog},
        {"name": "draw_order_flow", "description": "Draws order flow.", "func": draw_order_flow},
    ]


def get_tools_v2():
    return [
        {
            "name": "list_products",
            "description": (
                "List all products currently available in the catalog, including price, stock, weight, and category. "
                "Use this when the user asks what can be purchased or when a requested product is unknown."
            ),
            "func": list_products,
        },
        {
            "name": "search_catalog",
            "description": (
                "Search the product catalog by product name, category, or related keyword. "
                "Input can be a user term such as phone, camera, desk, chair, meeting, or projector. "
                "Use this before saying a product is unavailable."
            ),
            "func": search_catalog,
        },
        {
            "name": "suggest_alternatives",
            "description": (
                "Suggest available alternative products when the requested product is missing or not exact. "
                "Input should be the user's requested item or need, for example: suggest_alternatives(phone)."
            ),
            "func": suggest_alternatives,
        },
        {
            "name": "draw_order_flow",
            "description": (
                "Draw an ASCII flowchart of the order calculation process. "
                "Use this when the user asks to draw, visualize, show steps, or explain the workflow."
            ),
            "func": draw_order_flow,
        },
        {
            "name": "check_stock",
            "description": (
                "Check product inventory. Input must be only the exact product name from the catalog, "
                "for example: check_stock(standing desk), check_stock(portable projector)."
            ),
            "func": check_stock,
        },
        {
            "name": "get_price",
            "description": (
                "Get product unit price in USD. Input must be only the exact product name, "
                "for example: get_price(standing desk), get_price(ergonomic chair)."
            ),
            "func": get_price,
        },
        {
            "name": "get_weight",
            "description": (
                "Get product unit weight in kilograms. Input must be only the exact product name. "
                "Use this before calculating shipping cost."
            ),
            "func": get_weight,
        },
        {
            "name": "get_discount",
            "description": (
                "Get discount percentage for a coupon code. Input must be only the coupon code, "
                "for example: get_discount(OFFICE10), get_discount(BULK15)."
            ),
            "func": get_discount,
        },
        {
            "name": "calc_shipping",
            "description": (
                "Get shipping rate in USD per kg for a destination city. Input must be only one city name: "
                "Hanoi, Danang, HCMC, or Can Tho. Example: calc_shipping(Danang)."
            ),
            "func": calc_shipping,
        },
        {
            "name": "calculator",
            "description": (
                "Calculate arithmetic expressions using numbers and operators only. "
                "Example: calculator((2 * 320) * (1 - 0.10) + (2 * 28 * 6))."
            ),
            "func": calculator,
        },
    ]


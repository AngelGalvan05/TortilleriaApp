from datetime import datetime, timedelta

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"

def get_week_dates(selected_date):
    """Get all dates in the week containing the selected date"""
    # Find Monday of the week
    days_since_monday = selected_date.weekday()
    monday = selected_date - timedelta(days=days_since_monday)
    
    # Generate all 7 days of the week
    week_dates = []
    for i in range(7):
        week_dates.append(monday + timedelta(days=i))
    
    return week_dates

def validate_sale_data(sale_data):
    """Validate sale data before saving"""
    required_fields = [
        'date', 'time', 'username', 'tortilla_qty', 'totopos_qty', 
        'cacahuates_qty', 'mix_qty', 'salted_chips_qty', 'special_qty',
        'special_price', 'frequent_customer', 'supplier', 'total', 
        'payment', 'change'
    ]
    
    for field in required_fields:
        if field not in sale_data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric fields
    numeric_fields = [
        'tortilla_qty', 'totopos_qty', 'cacahuates_qty', 'mix_qty', 
        'salted_chips_qty', 'special_qty', 'special_price', 'total', 
        'payment', 'change'
    ]
    
    for field in numeric_fields:
        try:
            float(sale_data[field])
        except (ValueError, TypeError):
            return False, f"Invalid numeric value for field: {field}"
    
    # Validate quantities are non-negative
    quantity_fields = [
        'tortilla_qty', 'totopos_qty', 'cacahuates_qty', 'mix_qty', 
        'salted_chips_qty', 'special_qty'
    ]
    
    for field in quantity_fields:
        if float(sale_data[field]) < 0:
            return False, f"Quantity cannot be negative: {field}"
    
    return True, "Valid"

def calculate_product_total(product, quantity, is_supplier=False, special_price=0):
    """Calculate total for a specific product"""
    prices = {
        'Tortilla': 22.0 if is_supplier else 25.0,
        'Totopos': 25.0,
        'Cacahuates': 10.0,
        'Mix': 10.0,
        'Salted Chips': 15.0,
        'Special': special_price
    }
    
    return quantity * prices.get(product, 0)

def generate_receipt_text(sale_data):
    """Generate a formatted receipt text"""
    receipt_lines = []
    receipt_lines.append("=" * 30)
    receipt_lines.append("TORTILLA BUSINESS RECEIPT")
    receipt_lines.append("=" * 30)
    receipt_lines.append(f"Date: {sale_data['date']}")
    receipt_lines.append(f"Time: {sale_data['time']}")
    receipt_lines.append(f"Cashier: {sale_data['username']}")
    receipt_lines.append("-" * 30)
    
    # Products
    products = [
        ('Tortillas', sale_data['tortilla_qty'], 'kg'),
        ('Totopos', sale_data['totopos_qty'], 'units'),
        ('Cacahuates', sale_data['cacahuates_qty'], 'units'),
        ('Mix', sale_data['mix_qty'], 'units'),
        ('Salted Chips', sale_data['salted_chips_qty'], 'units'),
        ('Special', sale_data['special_qty'], 'units')
    ]
    
    for product, qty, unit in products:
        if qty > 0:
            if product == 'Tortillas':
                price = 22.0 if sale_data['supplier'] else 25.0
                total = qty * price
            elif product == 'Special':
                price = sale_data['special_price']
                total = qty * price
            else:
                prices = {'Totopos': 25.0, 'Cacahuates': 10.0, 'Mix': 10.0, 'Salted Chips': 15.0}
                price = prices[product]
                total = qty * price
            
            receipt_lines.append(f"{product}: {qty} {unit} @ ${price:.2f} = ${total:.2f}")
    
    receipt_lines.append("-" * 30)
    receipt_lines.append(f"TOTAL: ${sale_data['total']:.2f}")
    receipt_lines.append(f"PAYMENT: ${sale_data['payment']:.2f}")
    receipt_lines.append(f"CHANGE: ${sale_data['change']:.2f}")
    
    if sale_data['frequent_customer']:
        receipt_lines.append("* Frequent Customer")
    if sale_data['supplier']:
        receipt_lines.append("* Supplier Discount Applied")
    
    receipt_lines.append("=" * 30)
    receipt_lines.append("Thank you for your business!")
    receipt_lines.append("=" * 30)
    
    return "\n".join(receipt_lines)

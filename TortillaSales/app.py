import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from sales_manager import SalesManager
from utils import format_currency, get_week_dates
from auth import authenticate_user, is_admin, create_user, get_users, initialize_users_file

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "login"

# Initialize users file
initialize_users_file()

# Initialize sales manager (will be updated with username after login)
sales_manager = None

def login_screen():
    st.title("🔐 Secure Login")
    st.markdown("Welcome to the Tortilla Business Sales Management System")
    st.markdown("---")
    
    # Login Form
    with st.form("login_form"):
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("🔓 Login", type="primary")
        
        if submitted:
            if username and password:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.current_screen = "main_menu"
                    # Initialize sales manager with username
                    global sales_manager
                    sales_manager = SalesManager(username)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    st.markdown("---")
    st.info("💡 Default admin account: username='admin', password='admin123'")
    
    # First time setup info
    with st.expander("ℹ️ First Time Setup"):
        st.markdown("""
        **Default Admin Account:**
        - Username: `admin`
        - Password: `admin123`
        
        **After logging in as admin, you can:**
        - Change the admin password
        - Create new user accounts
        - Manage existing users
        """)

def user_management_screen():
    st.title("👥 User Management")
    st.markdown("Manage user accounts and permissions (Admin Only)")
    
    if not is_admin(st.session_state.username):
        st.error("❌ Access denied. Admin privileges required.")
        if st.button("🔙 Return to Main Menu"):
            st.session_state.current_screen = "main_menu"
            st.rerun()
        return
    
    # Get all users
    users_df = get_users()
    
    # Create new user section
    st.subheader("➕ Create New User")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
        
        with col2:
            confirm_password = st.text_input("Confirm Password", type="password")
            is_new_admin = st.checkbox("Admin Privileges")
        
        create_submitted = st.form_submit_button("✅ Create User", type="primary")
        
        if create_submitted:
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    if new_username not in users_df['username'].values:
                        if create_user(new_username, new_password, is_new_admin):
                            st.success(f"✅ User '{new_username}' created successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create user")
                    else:
                        st.error("❌ Username already exists")
                else:
                    st.error("❌ Passwords do not match")
            else:
                st.warning("⚠️ Please fill in all fields")
    
    st.markdown("---")
    
    # Display existing users
    st.subheader("👤 Existing Users")
    if not users_df.empty:
        for idx, user in users_df.iterrows():
            with st.expander(f"👤 {user['username']} {'(Admin)' if user['is_admin'] else '(User)'}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Role:** {'Administrator' if user['is_admin'] else 'Standard User'}")
                    st.write(f"**Account Status:** Active")
                
                with col2:
                    if user['username'] != st.session_state.username:
                        if st.button(f"🗑️ Delete", key=f"delete_{user['username']}"):
                            # Note: We don't implement user deletion for safety
                            st.warning("User deletion not implemented for security reasons")
    else:
        st.info("No users found")
    
    # Change password section
    st.markdown("---")
    st.subheader("🔑 Change Password")
    with st.form("change_password_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input("Current Password", type="password")
            new_user_password = st.text_input("New Password", type="password")
        
        with col2:
            confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        change_submitted = st.form_submit_button("🔄 Change Password")
        
        if change_submitted:
            if current_password and new_user_password and confirm_new_password:
                if authenticate_user(st.session_state.username, current_password):
                    if new_user_password == confirm_new_password:
                        if create_user(st.session_state.username, new_user_password, is_admin(st.session_state.username)):
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error("❌ Failed to change password")
                    else:
                        st.error("❌ New passwords do not match")
                else:
                    st.error("❌ Current password is incorrect")
            else:
                st.warning("⚠️ Please fill in all fields")
    
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def main_menu():
    st.title("🌮 Sales Management System")
    st.markdown(f"Welcome back, **{st.session_state.username}**! {'(Administrator)' if is_admin(st.session_state.username) else '(User)'}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Register Sale", use_container_width=True):
            st.session_state.current_screen = "register_sale"
            st.rerun()
        
        if st.button("📊 Daily Summary", use_container_width=True):
            st.session_state.current_screen = "daily_summary"
            st.rerun()
    
    with col2:
        if st.button("📈 Weekly Summary", use_container_width=True):
            st.session_state.current_screen = "weekly_summary"
            st.rerun()
        
        if st.button("📋 View Records", use_container_width=True):
            st.session_state.current_screen = "view_records"
            st.rerun()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Manage Excel Data", use_container_width=True):
            st.session_state.current_screen = "manage_excel_data"
            st.rerun()
    
    with col2:
        if st.button("📥 Download Reports", use_container_width=True):
            st.session_state.current_screen = "download_reports"
            st.rerun()
    
    # Admin-only features
    if is_admin(st.session_state.username):
        st.markdown("---")
        st.markdown("**🔧 Administrator Tools**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.current_screen = "user_management"
                st.rerun()
    
    # Logout section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.current_screen = "login"
            # Reset sales manager
            global sales_manager
            sales_manager = None
            st.success("Logged out successfully!")
            st.rerun()
    
    with col2:
        st.info(f"Logged in as: {st.session_state.username}")

def register_sale_screen():
    st.title("📝 Register Sale")
    
    # Initialize session state for sale
    if 'sale_products' not in st.session_state:
        st.session_state.sale_products = {
            'Tortilla': 0,
            'Totopos': 0,
            'Cacahuates': 0,
            'Mix': 0,
            'Salted Chips': 0,
            'Special': 0
        }
    if 'special_price' not in st.session_state:
        st.session_state.special_price = 0.0
    if 'frequent_customer' not in st.session_state:
        st.session_state.frequent_customer = False
    if 'supplier' not in st.session_state:
        st.session_state.supplier = False
    
    # Product prices
    base_prices = {
        'Tortilla': 25.0,
        'Totopos': 25.0,
        'Cacahuates': 10.0,
        'Mix': 10.0,
        'Salted Chips': 15.0,
        'Special': 0.0
    }
    
    # Product selection and quantity
    st.subheader("Product Selection")
    
    for product in st.session_state.sale_products.keys():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            st.write(f"**{product}**")
            if product == 'Tortilla':
                price = 22.0 if st.session_state.supplier else 25.0
                st.write(f"Price: ${price}/kg")
            elif product == 'Special':
                st.write("Manual price input")
            else:
                st.write(f"Price: ${base_prices[product]}")
        
        with col2:
            if st.button(f"➖", key=f"minus_{product}"):
                if product == 'Tortilla':
                    st.session_state.sale_products[product] = max(0, st.session_state.sale_products[product] - 0.5)
                else:
                    st.session_state.sale_products[product] = max(0, st.session_state.sale_products[product] - 1)
                st.rerun()
        
        with col3:
            if st.button(f"➕", key=f"plus_{product}"):
                if product == 'Tortilla':
                    st.session_state.sale_products[product] += 0.5
                else:
                    st.session_state.sale_products[product] += 1
                st.rerun()
        
        with col4:
            if product == 'Tortilla':
                st.write(f"Quantity: {st.session_state.sale_products[product]} kg")
            else:
                st.write(f"Quantity: {st.session_state.sale_products[product]}")
    
    # Special price input
    if st.session_state.sale_products['Special'] > 0:
        st.session_state.special_price = st.number_input("Special Product Price", min_value=0.0, value=st.session_state.special_price, step=0.1)
    
    # Checkboxes
    st.session_state.frequent_customer = st.checkbox("Frequent Customer", value=st.session_state.frequent_customer)
    st.session_state.supplier = st.checkbox("Supplier", value=st.session_state.supplier)
    
    # Calculate total
    total = 0
    for product, quantity in st.session_state.sale_products.items():
        if quantity > 0:
            if product == 'Tortilla':
                price = 22.0 if st.session_state.supplier else 25.0
                total += quantity * price
            elif product == 'Special':
                total += quantity * st.session_state.special_price
            else:
                total += quantity * base_prices[product]
    
    st.subheader("Sale Summary")
    st.write(f"**Total: {format_currency(total)}**")
    
    # Payment
    customer_payment = st.number_input("Customer Payment", min_value=0.0, step=0.1)
    
    if customer_payment > 0:
        change = customer_payment - total
        if change >= 0:
            st.success(f"Change: {format_currency(change)}")
        else:
            st.error(f"Insufficient payment. Missing: {format_currency(abs(change))}")
    
    # Register sale button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Register Sale", type="primary"):
            if total > 0 and customer_payment >= total:
                # Create sale record
                sale_data = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'username': st.session_state.username,
                    'tortilla_qty': st.session_state.sale_products['Tortilla'],
                    'totopos_qty': st.session_state.sale_products['Totopos'],
                    'cacahuates_qty': st.session_state.sale_products['Cacahuates'],
                    'mix_qty': st.session_state.sale_products['Mix'],
                    'salted_chips_qty': st.session_state.sale_products['Salted Chips'],
                    'special_qty': st.session_state.sale_products['Special'],
                    'special_price': st.session_state.special_price,
                    'frequent_customer': st.session_state.frequent_customer,
                    'supplier': st.session_state.supplier,
                    'total': total,
                    'payment': customer_payment,
                    'change': customer_payment - total
                }
                
                if sales_manager.add_sale(sale_data):
                    st.success("Sale registered successfully!")
                    # Reset form
                    st.session_state.sale_products = {
                        'Tortilla': 0,
                        'Totopos': 0,
                        'Cacahuates': 0,
                        'Mix': 0,
                        'Salted Chips': 0,
                        'Special': 0
                    }
                    st.session_state.special_price = 0.0
                    st.session_state.frequent_customer = False
                    st.session_state.supplier = False
                    st.rerun()
                else:
                    st.error("Failed to register sale")
            else:
                st.error("Please ensure all products have valid quantities and payment is sufficient")
    
    with col2:
        if st.button("🔙 Return to Main Menu"):
            st.session_state.current_screen = "main_menu"
            st.rerun()

def daily_summary_screen():
    st.title("📊 Daily Summary")
    
    # Date selector
    selected_date = st.date_input("Select Date", value=datetime.now().date())
    
    # Get daily sales
    daily_sales = sales_manager.get_daily_sales(selected_date.strftime('%Y-%m-%d'))
    
    if daily_sales.empty:
        st.info(f"No sales recorded for {selected_date.strftime('%B %d, %Y')}")
    else:
        st.subheader(f"Sales for {selected_date.strftime('%B %d, %Y')}")
        
        # Product totals
        st.markdown("### Product Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tortilla_total = daily_sales['tortilla_qty'].sum()
            totopos_total = daily_sales['totopos_qty'].sum()
            cacahuates_total = daily_sales['cacahuates_qty'].sum()
            
            st.metric("Tortillas", f"{tortilla_total} kg")
            st.metric("Totopos", f"{int(totopos_total)} units")
            st.metric("Cacahuates", f"{int(cacahuates_total)} units")
        
        with col2:
            mix_total = daily_sales['mix_qty'].sum()
            salted_chips_total = daily_sales['salted_chips_qty'].sum()
            special_total = daily_sales['special_qty'].sum()
            
            st.metric("Mix", f"{int(mix_total)} units")
            st.metric("Salted Chips", f"{int(salted_chips_total)} units")
            st.metric("Special", f"{int(special_total)} units")
        
        # Financial breakdown
        st.markdown("### Financial Summary")
        
        # Calculate subtotals
        tortilla_subtotal = 0
        supplier_tortilla_subtotal = 0
        other_subtotal = 0
        
        for _, sale in daily_sales.iterrows():
            if sale['tortilla_qty'] > 0:
                if sale['supplier']:
                    supplier_tortilla_subtotal += sale['tortilla_qty'] * 22.0
                else:
                    tortilla_subtotal += sale['tortilla_qty'] * 25.0
            
            other_subtotal += (
                sale['totopos_qty'] * 25.0 +
                sale['cacahuates_qty'] * 10.0 +
                sale['mix_qty'] * 10.0 +
                sale['salted_chips_qty'] * 15.0 +
                sale['special_qty'] * sale['special_price']
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Regular Tortilla Subtotal", format_currency(tortilla_subtotal))
            st.metric("Supplier Tortilla Subtotal", format_currency(supplier_tortilla_subtotal))
        
        with col2:
            st.metric("Other Products Subtotal", format_currency(other_subtotal))
            grand_total = tortilla_subtotal + supplier_tortilla_subtotal + other_subtotal
            st.metric("Grand Total", format_currency(grand_total))
        
        # Sales count
        st.metric("Total Sales Count", len(daily_sales))
        
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def weekly_summary_screen():
    st.title("📈 Weekly Summary")
    
    # Week selector
    selected_date = st.date_input("Select a date in the week", value=datetime.now().date())
    
    # Get week dates
    week_dates = get_week_dates(selected_date)
    
    st.subheader(f"Week of {week_dates[0].strftime('%B %d')} - {week_dates[6].strftime('%B %d, %Y')}")
    
    # Get weekly sales
    weekly_data = []
    total_weekly_earnings = 0
    
    for date in week_dates:
        date_str = date.strftime('%Y-%m-%d')
        daily_sales = sales_manager.get_daily_sales(date_str)
        daily_total = daily_sales['total'].sum() if not daily_sales.empty else 0
        
        weekly_data.append({
            'Day': date.strftime('%A'),
            'Date': date.strftime('%B %d'),
            'Sales': len(daily_sales),
            'Total': daily_total
        })
        
        total_weekly_earnings += daily_total
    
    # Display weekly breakdown
    df_weekly = pd.DataFrame(weekly_data)
    
    for _, row in df_weekly.iterrows():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{row['Day']}**")
        with col2:
            st.write(f"{row['Date']}")
        with col3:
            st.write(f"{row['Sales']} sales - {format_currency(row['Total'])}")
    
    st.markdown("---")
    st.metric("Total Weekly Earnings", format_currency(total_weekly_earnings))
    
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def view_records_screen():
    st.title("📋 View Records")
    
    # Get all sales
    all_sales = sales_manager.get_all_sales()
    
    if all_sales.empty:
        st.info("No sales records found")
    else:
        st.subheader(f"All Sales Records ({len(all_sales)} records)")
        
        # Display records
        for idx, sale in all_sales.iterrows():
            with st.expander(f"Sale {idx + 1} - {sale['date']} {sale['time']} - {format_currency(sale['total'])}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Date:** {sale['date']}")
                    st.write(f"**Time:** {sale['time']}")
                    st.write(f"**User:** {sale['username']}")
                    st.write(f"**Frequent Customer:** {'Yes' if sale['frequent_customer'] else 'No'}")
                    st.write(f"**Supplier:** {'Yes' if sale['supplier'] else 'No'}")
                
                with col2:
                    st.write("**Products:**")
                    if sale['tortilla_qty'] > 0:
                        st.write(f"- Tortillas: {sale['tortilla_qty']} kg")
                    if sale['totopos_qty'] > 0:
                        st.write(f"- Totopos: {int(sale['totopos_qty'])} units")
                    if sale['cacahuates_qty'] > 0:
                        st.write(f"- Cacahuates: {int(sale['cacahuates_qty'])} units")
                    if sale['mix_qty'] > 0:
                        st.write(f"- Mix: {int(sale['mix_qty'])} units")
                    if sale['salted_chips_qty'] > 0:
                        st.write(f"- Salted Chips: {int(sale['salted_chips_qty'])} units")
                    if sale['special_qty'] > 0:
                        st.write(f"- Special: {int(sale['special_qty'])} units @ {format_currency(sale['special_price'])}")
                
                st.write(f"**Total:** {format_currency(sale['total'])}")
                st.write(f"**Payment:** {format_currency(sale['payment'])}")
                st.write(f"**Change:** {format_currency(sale['change'])}")
                
                # Delete individual record button
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_sale_{idx}", type="secondary"):
                        if sales_manager.delete_sale_by_index(idx):
                            st.success(f"Record deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete record")
    
    # Delete all records button
    if not all_sales.empty:
        st.markdown("---")
        st.subheader("⚠️ Danger Zone")
        
        if st.button("🗑️ Delete All Records", type="secondary"):
            if sales_manager.delete_all_sales():
                st.success("All records deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete records")
    
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def manage_excel_data_screen():
    st.title("📊 Manage Excel Data")
    
    st.markdown("Import sales data from Excel files or export current data to Excel format.")
    
    # Create tabs for upload and download
    tab1, tab2 = st.tabs(["📤 Upload Excel Data", "📥 Download Excel Data"])
    
    # Upload Tab
    with tab1:
        st.markdown("Upload an Excel file to import sales data into the system.")
        st.warning("⚠️ This will add the uploaded data to your existing sales records.")
        
        uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                # Read the uploaded Excel file
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                
                # Display preview
                st.subheader("Preview of uploaded data:")
                st.dataframe(df.head())
                
                # Validate columns
                required_columns = ['date', 'time', 'username', 'tortilla_qty', 'totopos_qty', 
                                  'cacahuates_qty', 'mix_qty', 'salted_chips_qty', 'special_qty',
                                  'special_price', 'frequent_customer', 'supplier', 'total', 
                                  'payment', 'change']
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    st.info("Required columns: " + ", ".join(required_columns))
                else:
                    st.success("✅ All required columns found!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Import Data", type="primary"):
                            # Import each row
                            import_count = 0
                            for _, row in df.iterrows():
                                sale_data = {
                                    'date': str(row['date']),
                                    'time': str(row['time']),
                                    'username': str(row['username']),
                                    'tortilla_qty': float(row['tortilla_qty']),
                                    'totopos_qty': float(row['totopos_qty']),
                                    'cacahuates_qty': float(row['cacahuates_qty']),
                                    'mix_qty': float(row['mix_qty']),
                                    'salted_chips_qty': float(row['salted_chips_qty']),
                                    'special_qty': float(row['special_qty']),
                                    'special_price': float(row['special_price']),
                                    'frequent_customer': bool(row['frequent_customer']),
                                    'supplier': bool(row['supplier']),
                                    'total': float(row['total']),
                                    'payment': float(row['payment']),
                                    'change': float(row['change'])
                                }
                                
                                if sales_manager.add_sale(sale_data):
                                    import_count += 1
                            
                            st.success(f"Successfully imported {import_count} sales records!")
                            st.balloons()
                    
                    with col2:
                        st.info(f"Ready to import {len(df)} records")
            
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                st.info("Please make sure the file is a valid Excel file with the correct format.")
    
    # Download Tab
    with tab2:
        st.markdown("Export all current sales data to an Excel file.")
        
        # Get current sales data
        all_sales = sales_manager.get_all_sales()
        
        if all_sales.empty:
            st.info("No sales data available to export.")
        else:
            st.success(f"Ready to export {len(all_sales)} sales records")
            
            # Show preview of data
            st.subheader("Preview of current sales data:")
            st.dataframe(all_sales.head())
            
            if st.button("📥 Generate Excel File", type="primary"):
                try:
                    # Create Excel file in memory
                    import io
                    output = io.BytesIO()
                    
                    # Write data to Excel
                    all_sales.to_excel(output, index=False, engine='openpyxl')
                    output.seek(0)
                    
                    # Generate filename with current date
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    filename = f"sales_data_export_{current_date}.xlsx"
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output.getvalue(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success(f"Excel file ready for download: {filename}")
                    
                except Exception as e:
                    st.error(f"Error creating Excel file: {e}")
    
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def download_reports_screen():
    st.title("📥 Download Reports")
    
    st.markdown("Generate and download sales reports in TXT format.")
    
    # Daily Report Section
    st.subheader("📊 Daily Report")
    daily_date = st.date_input("Select Date for Daily Report", value=datetime.now().date())
    
    if st.button("📥 Generate Daily Report (TXT)"):
        try:
            daily_sales = sales_manager.get_daily_sales(daily_date.strftime('%Y-%m-%d'))
            
            # Generate TXT content
            report_lines = []
            report_lines.append("=" * 50)
            report_lines.append("TORTILLA BUSINESS - DAILY SALES REPORT")
            report_lines.append("=" * 50)
            report_lines.append(f"Date: {daily_date.strftime('%Y-%m-%d')}")
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 50)
            
            if daily_sales.empty:
                report_lines.append("No sales recorded for this date.")
            else:
                # Product summary
                report_lines.append("PRODUCT SUMMARY:")
                report_lines.append("-" * 30)
                report_lines.append(f"Tortillas: {daily_sales['tortilla_qty'].sum()} kg")
                report_lines.append(f"Totopos: {int(daily_sales['totopos_qty'].sum())} units")
                report_lines.append(f"Cacahuates: {int(daily_sales['cacahuates_qty'].sum())} units")
                report_lines.append(f"Mix: {int(daily_sales['mix_qty'].sum())} units")
                report_lines.append(f"Salted Chips: {int(daily_sales['salted_chips_qty'].sum())} units")
                report_lines.append(f"Special: {int(daily_sales['special_qty'].sum())} units")
                
                # Financial summary
                tortilla_subtotal = 0
                supplier_tortilla_subtotal = 0
                other_subtotal = 0
                
                for _, sale in daily_sales.iterrows():
                    if sale['tortilla_qty'] > 0:
                        if sale['supplier']:
                            supplier_tortilla_subtotal += sale['tortilla_qty'] * 22.0
                        else:
                            tortilla_subtotal += sale['tortilla_qty'] * 25.0
                    
                    other_subtotal += (
                        sale['totopos_qty'] * 25.0 +
                        sale['cacahuates_qty'] * 10.0 +
                        sale['mix_qty'] * 10.0 +
                        sale['salted_chips_qty'] * 15.0 +
                        sale['special_qty'] * sale['special_price']
                    )
                
                report_lines.append("")
                report_lines.append("FINANCIAL SUMMARY:")
                report_lines.append("-" * 30)
                report_lines.append(f"Regular Tortilla Subtotal: ${tortilla_subtotal:.2f}")
                report_lines.append(f"Supplier Tortilla Subtotal: ${supplier_tortilla_subtotal:.2f}")
                report_lines.append(f"Other Products Subtotal: ${other_subtotal:.2f}")
                report_lines.append(f"GRAND TOTAL: ${tortilla_subtotal + supplier_tortilla_subtotal + other_subtotal:.2f}")
                report_lines.append(f"Total Sales Count: {len(daily_sales)}")
                
                # Individual sales
                report_lines.append("")
                report_lines.append("INDIVIDUAL SALES:")
                report_lines.append("-" * 30)
                for idx, sale in daily_sales.iterrows():
                    report_lines.append(f"Sale {idx + 1} - {sale['time']} - ${sale['total']:.2f}")
                    if sale['tortilla_qty'] > 0:
                        report_lines.append(f"  Tortillas: {sale['tortilla_qty']} kg")
                    if sale['totopos_qty'] > 0:
                        report_lines.append(f"  Totopos: {int(sale['totopos_qty'])} units")
                    if sale['cacahuates_qty'] > 0:
                        report_lines.append(f"  Cacahuates: {int(sale['cacahuates_qty'])} units")
                    if sale['mix_qty'] > 0:
                        report_lines.append(f"  Mix: {int(sale['mix_qty'])} units")
                    if sale['salted_chips_qty'] > 0:
                        report_lines.append(f"  Salted Chips: {int(sale['salted_chips_qty'])} units")
                    if sale['special_qty'] > 0:
                        report_lines.append(f"  Special: {int(sale['special_qty'])} units @ ${sale['special_price']:.2f}")
                    if sale['frequent_customer']:
                        report_lines.append("  * Frequent Customer")
                    if sale['supplier']:
                        report_lines.append("  * Supplier Discount")
                    report_lines.append("")
            
            report_lines.append("=" * 50)
            
            report_content = "\n".join(report_lines)
            
            st.download_button(
                label="📥 Download Daily Report",
                data=report_content,
                file_name=f"daily_report_{daily_date.strftime('%Y-%m-%d')}.txt",
                mime="text/plain"
            )
            
            st.success(f"Daily report generated for {daily_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            st.error(f"Error generating daily report: {e}")
    
    st.markdown("---")
    
    # Weekly Report Section
    st.subheader("📈 Weekly Report")
    weekly_date = st.date_input("Select a date in the week for Weekly Report", value=datetime.now().date())
    
    if st.button("📥 Generate Weekly Report (TXT)"):
        try:
            week_dates = get_week_dates(weekly_date)
            
            # Generate TXT content
            report_lines = []
            report_lines.append("=" * 50)
            report_lines.append("TORTILLA BUSINESS - WEEKLY SALES REPORT")
            report_lines.append("=" * 50)
            report_lines.append(f"Week: {week_dates[0].strftime('%Y-%m-%d')} to {week_dates[6].strftime('%Y-%m-%d')}")
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 50)
            
            total_weekly_earnings = 0
            weekly_data = []
            
            for date in week_dates:
                date_str = date.strftime('%Y-%m-%d')
                daily_sales = sales_manager.get_daily_sales(date_str)
                daily_total = daily_sales['total'].sum() if not daily_sales.empty else 0
                
                weekly_data.append({
                    'day': date.strftime('%A'),
                    'date': date.strftime('%Y-%m-%d'),
                    'sales_count': len(daily_sales),
                    'total': daily_total
                })
                
                total_weekly_earnings += daily_total
            
            # Daily breakdown
            report_lines.append("DAILY BREAKDOWN:")
            report_lines.append("-" * 30)
            for data in weekly_data:
                report_lines.append(f"{data['day']:<10} {data['date']:<12} {data['sales_count']:>3} sales  ${data['total']:>8.2f}")
            
            report_lines.append("-" * 30)
            report_lines.append(f"TOTAL WEEKLY EARNINGS: ${total_weekly_earnings:.2f}")
            total_sales_count = sum(data['sales_count'] for data in weekly_data)
            report_lines.append(f"Total Sales Count: {total_sales_count}")
            days_with_sales = sum(1 for data in weekly_data if data['sales_count'] > 0)
            report_lines.append(f"Days with Sales: {days_with_sales}/7")
            
            report_lines.append("=" * 50)
            
            report_content = "\n".join(report_lines)
            
            st.download_button(
                label="📥 Download Weekly Report",
                data=report_content,
                file_name=f"weekly_report_{week_dates[0].strftime('%Y-%m-%d')}_to_{week_dates[6].strftime('%Y-%m-%d')}.txt",
                mime="text/plain"
            )
            
            st.success(f"Weekly report generated for {week_dates[0].strftime('%Y-%m-%d')} to {week_dates[6].strftime('%Y-%m-%d')}")
            
        except Exception as e:
            st.error(f"Error generating weekly report: {e}")
    
    if st.button("🔙 Return to Main Menu"):
        st.session_state.current_screen = "main_menu"
        st.rerun()

def main():
    global sales_manager
    
    # Check authentication
    if not st.session_state.authenticated:
        login_screen()
        return
    
    # Initialize sales manager if not already initialized
    if sales_manager is None and st.session_state.username:
        sales_manager = SalesManager(st.session_state.username)
    
    # Handle authenticated screens
    if st.session_state.current_screen == "main_menu":
        main_menu()
    elif st.session_state.current_screen == "register_sale":
        register_sale_screen()
    elif st.session_state.current_screen == "daily_summary":
        daily_summary_screen()
    elif st.session_state.current_screen == "weekly_summary":
        weekly_summary_screen()
    elif st.session_state.current_screen == "view_records":
        view_records_screen()
    elif st.session_state.current_screen == "manage_excel_data":
        manage_excel_data_screen()
    elif st.session_state.current_screen == "download_reports":
        download_reports_screen()
    elif st.session_state.current_screen == "user_management":
        user_management_screen()

if __name__ == "__main__":
    main()

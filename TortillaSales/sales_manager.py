import pandas as pd
import os
from datetime import datetime

class SalesManager:
    def __init__(self, username="default"):
        self.username = username
        self.sales_file = f"sales_data_{username}.xlsx"
        self.initialize_sales_file()
    
    def initialize_sales_file(self):
        """Initialize the sales Excel file with proper columns"""
        if not os.path.exists(self.sales_file):
            # Create empty DataFrame with all necessary columns
            columns = [
                'date', 'time', 'username', 'tortilla_qty', 'totopos_qty', 
                'cacahuates_qty', 'mix_qty', 'salted_chips_qty', 'special_qty',
                'special_price', 'frequent_customer', 'supplier', 'total', 
                'payment', 'change'
            ]
            empty_df = pd.DataFrame(columns=columns)
            try:
                empty_df.to_excel(self.sales_file, index=False, engine='openpyxl')
                print(f"Created new sales file: {self.sales_file}")
            except Exception as e:
                print(f"Error creating sales file: {e}")
    
    def add_sale(self, sale_data):
        """Add a new sale to the Excel file"""
        try:
            # Read existing data
            existing_df = pd.read_excel(self.sales_file, engine='openpyxl')
            
            # Create new sale DataFrame
            new_sale_df = pd.DataFrame([sale_data])
            
            # Combine and save
            updated_df = pd.concat([existing_df, new_sale_df], ignore_index=True)
            updated_df.to_excel(self.sales_file, index=False, engine='openpyxl')
            
            return True
        except Exception as e:
            print(f"Error adding sale: {e}")
            return False
    
    def get_all_sales(self):
        """Get all sales from the Excel file"""
        try:
            df = pd.read_excel(self.sales_file, engine='openpyxl')
            # Sort by date and time (most recent first)
            df = df.sort_values(['date', 'time'], ascending=[False, False])
            return df
        except Exception as e:
            print(f"Error reading sales: {e}")
            return pd.DataFrame()
    
    def get_daily_sales(self, date_str):
        """Get sales for a specific date"""
        try:
            df = pd.read_excel(self.sales_file, engine='openpyxl')
            daily_sales = df[df['date'] == date_str]
            return daily_sales.sort_values('time', ascending=False)
        except Exception as e:
            print(f"Error reading daily sales: {e}")
            return pd.DataFrame()
    
    def get_weekly_sales(self, start_date, end_date):
        """Get sales for a date range"""
        try:
            df = pd.read_excel(self.sales_file, engine='openpyxl')
            df['date'] = pd.to_datetime(df['date'])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            weekly_sales = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            return weekly_sales.sort_values(['date', 'time'], ascending=[False, False])
        except Exception as e:
            print(f"Error reading weekly sales: {e}")
            return pd.DataFrame()
    
    def delete_all_sales(self):
        """Delete all sales records"""
        try:
            # Create empty DataFrame with columns
            columns = [
                'date', 'time', 'username', 'tortilla_qty', 'totopos_qty', 
                'cacahuates_qty', 'mix_qty', 'salted_chips_qty', 'special_qty',
                'special_price', 'frequent_customer', 'supplier', 'total', 
                'payment', 'change'
            ]
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_excel(self.sales_file, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"Error deleting all sales: {e}")
            return False
    
    def delete_sale_by_index(self, index):
        """Delete a specific sale by its index"""
        try:
            # Read existing data
            if os.path.exists(self.sales_file):
                df = pd.read_excel(self.sales_file, engine='openpyxl')
                
                # Check if index is valid
                if 0 <= index < len(df):
                    # Remove the row at the specified index
                    df = df.drop(df.index[index])
                    
                    # Save the updated DataFrame
                    df.to_excel(self.sales_file, index=False, engine='openpyxl')
                    return True
                else:
                    print(f"Invalid index: {index}")
                    return False
            else:
                print("Sales file not found")
                return False
        except Exception as e:
            print(f"Error deleting sale: {e}")
            return False
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """Get summary statistics for sales"""
        try:
            if start_date and end_date:
                df = self.get_weekly_sales(start_date, end_date)
            else:
                df = self.get_all_sales()
            
            if df.empty:
                return {}
            
            summary = {
                'total_sales': len(df),
                'total_revenue': df['total'].sum(),
                'average_sale': df['total'].mean(),
                'tortilla_total': df['tortilla_qty'].sum(),
                'totopos_total': df['totopos_qty'].sum(),
                'cacahuates_total': df['cacahuates_qty'].sum(),
                'mix_total': df['mix_qty'].sum(),
                'salted_chips_total': df['salted_chips_qty'].sum(),
                'special_total': df['special_qty'].sum(),
                'frequent_customers': df['frequent_customer'].sum(),
                'supplier_sales': df['supplier'].sum()
            }
            
            return summary
        except Exception as e:
            print(f"Error generating sales summary: {e}")
            return {}

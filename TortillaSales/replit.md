# Tortilla Business Sales Management System

## Overview

This is a Streamlit-based web application for managing sales data for a tortilla business. The system provides direct access to sales recording and reporting functionality without authentication requirements. The application uses Excel files for data storage.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development and built-in UI components
- **Session Management**: Built-in Streamlit session state for screen navigation
- **UI Components**: Form-based inputs, data tables, and charts for sales visualization

### Backend Architecture
- **Data Storage**: Excel files (.xlsx) using pandas and openpyxl
- **Authentication**: Removed - direct access to application
- **Business Logic**: Modular design with separate classes for different functionalities

### Data Storage
- **Primary Storage**: Excel files for simplicity and business user familiarity
- **Files**:
  - `sales_data.xlsx`: Sales transactions and product data
- **Rationale**: Excel chosen for ease of backup, sharing, and direct business user access

## Key Components

### Authentication System (`auth.py`)
- **Status**: Secure login system with user management
- **Features**:
  - Password hashing using SHA-256
  - Admin privilege system
  - User creation and management
  - Password change functionality
- **Default Admin**: Username: 'admin', Password: 'admin123'
- **Rationale**: Provides secure access control and user accountability

### Sales Manager (`sales_manager.py`)
- **Purpose**: Core sales data management
- **Features**:
  - Sales recording and validation
  - Data retrieval and filtering
  - Excel file initialization and management
- **Product Types**: Tortilla, Totopos, Cacahuates, Mix, Salted Chips, Special items

### Utility Functions (`utils.py`)
- **Purpose**: Common helper functions
- **Features**:
  - Currency formatting
  - Date/week calculations
  - Data validation
- **Design Decision**: Centralized utilities for code reusability

### Main Application (`app.py`)
- **Purpose**: Primary application interface and routing
- **Features**:
  - Login screen management
  - Session state handling
  - Screen navigation
- **Architecture**: State-based navigation using Streamlit session state

## Data Flow

1. **User Authentication**: 
   - User credentials verified against `users.xlsx`
   - Session state updated on successful login
   - Admin privileges checked for user management features
   - User-specific sales manager initialized

2. **Sales Recording**:
   - Form input validation
   - Data processing and calculation
   - Append to user-specific Excel file: `sales_data_{username}.xlsx`
   - Immediate feedback to user

3. **Data Retrieval**:
   - Excel file reading with error handling from user-specific file
   - Data filtering and sorting
   - Display formatting for UI presentation
   - Individual record deletion capability

4. **Data Separation**:
   - Each user has their own Excel file to prevent data mixing
   - File naming convention: `sales_data_{username}.xlsx`
   - Users can only access their own sales data

## External Dependencies

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and Excel file operations
- **OpenPyXL**: Excel file reading/writing engine
- **OS/Datetime**: File operations and date handling (standard library)

## Deployment Strategy

- **Target Environment**: Local deployment or cloud platforms supporting Streamlit
- **File Storage**: Local file system (Excel files in application directory)
- **Considerations**: 
  - Files need to persist between deployments
  - Concurrent access limitations with Excel files
  - Backup strategy needed for data files

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 04, 2025. Initial setup
- July 04, 2025. Added secure login system with user management and individual record deletion
  - Implemented user authentication with admin privileges
  - Added user-specific Excel files to prevent data mixing
  - Created individual record deletion functionality in View Records section
  - Each user now has separate data file: sales_data_{username}.xlsx
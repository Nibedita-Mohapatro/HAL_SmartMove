# HAL SmartMove - User Guide

## 🎯 **Welcome to HAL SmartMove**

*"Hassle-Free Transport at Your Fingertips. From booking to tracking, manage your travel needs with speed, clarity, and control."*

HAL SmartMove is your comprehensive transport management solution designed to streamline all aspects of organizational transportation.

## 🔑 **Login Credentials**

### **Administrator Access**
- **Employee ID**: `HAL001`
- **Password**: `admin123`
- **Role**: Administrator
- **Access Level**: Full system control

### **Employee Access**
- **Employee ID**: `HAL003`
- **Password**: `employee123`
- **Role**: Employee
- **Access Level**: Request and track transport

### **Transport Manager Access**
- **Employee ID**: `HAL002`
- **Password**: `transport123`
- **Role**: Transport Manager
- **Access Level**: Manage trips and drivers

## 🚀 **Getting Started**

### **1. Accessing the System**
1. Open your web browser
2. Navigate to: `http://localhost:3000`
3. Enter your Employee ID and Password
4. Click "Sign In"

### **2. First Login**
- You'll be redirected to your role-specific dashboard
- Take a moment to explore the navigation menu
- Check your profile information in the top-right corner

## 👑 **Administrator Features**

### **Dashboard Overview**
- **System Statistics**: Total users, vehicles, drivers, and requests
- **Recent Activity**: Latest transport requests and assignments
- **Quick Actions**: Access to key management functions
- **GPS Tracking**: Monitor ongoing trips

### **User Management**
- **View Users**: See all system users with their roles
- **Add Users**: Create new employee, admin, or transport accounts
- **Edit Users**: Update user information and roles
- **Deactivate Users**: Disable user accounts when needed

### **Vehicle Management**
- **Vehicle Fleet**: View all vehicles with status and details
- **Add Vehicles**: Register new vehicles with specifications
- **Edit Vehicles**: Update vehicle information and status
- **Delete Vehicles**: Remove vehicles from the system
- **Maintenance Tracking**: Monitor vehicle maintenance schedules

### **Driver Management** ✅ **Recently Fixed**
- **Driver List**: View all active drivers with details
- **Add Drivers**: Register new drivers with license information
- **Edit Drivers**: Update driver information and status
- **Delete Drivers**: ✅ **Now Working Properly**
  - Smart deletion: Preserves historical data when needed
  - Safety checks: Prevents deletion of drivers with active assignments
  - Clear feedback: Shows success/error messages

### **Transport Request Management**
- **Approve Requests**: Review and approve pending transport requests
- **Assign Resources**: Assign vehicles and drivers to approved requests
- **Track Progress**: Monitor ongoing trips with status updates
- **View History**: Access completed trip records

### **Assignment Management**
- **Vehicle Assignment**: Assign vehicles to specific requests
- **Driver Assignment**: Assign drivers to trips
- **Safety Validation**: Automatic safety checks for assignments
- **Conflict Detection**: Prevent double-booking of resources

## 👥 **Employee Features**

### **Request Transport**
- **Create Request**: Submit new transport requests
- **Specify Details**: Origin, destination, date, time, passenger count
- **Set Priority**: Choose urgency level (low, medium, high)
- **Add Purpose**: Describe the reason for transport

### **My Requests**
- **View Status**: Track request approval and assignment status
- **Request History**: See all previous transport requests
- **Modify Requests**: Edit pending requests before approval
- **Cancel Requests**: Cancel requests that are no longer needed

### **Trip Tracking**
- **Live Updates**: Real-time status of assigned trips
- **Driver Information**: Contact details of assigned driver
- **Vehicle Details**: Information about assigned vehicle
- **Estimated Times**: Pickup and arrival time estimates

## 🚛 **Transport Manager Features**

### **Trip Management**
- **Active Trips**: Monitor all ongoing trips
- **Driver Coordination**: Communicate with drivers
- **Route Planning**: Optimize routes for efficiency
- **Status Updates**: Update trip progress and status

### **Resource Allocation**
- **Vehicle Availability**: Check vehicle status and availability
- **Driver Scheduling**: Manage driver schedules and assignments
- **Capacity Planning**: Optimize resource utilization

### **Operational Oversight**
- **Performance Metrics**: Track operational efficiency
- **Issue Resolution**: Handle trip-related issues
- **Reporting**: Generate operational reports

## 🎮 **How to Use Key Features**

### **Creating a Transport Request (Employee)**
1. Click "Request Transport" in the sidebar
2. Fill in the request form:
   - **Origin**: Starting location
   - **Destination**: End location
   - **Date & Time**: When you need transport
   - **Passengers**: Number of people
   - **Purpose**: Reason for travel
   - **Priority**: Urgency level
3. Click "Submit Request"
4. Wait for admin approval

### **Approving Requests (Admin)**
1. Go to "Transport Requests" tab
2. Find pending requests in the list
3. Click "Approve" for valid requests
4. Assign vehicle and driver:
   - Select available vehicle
   - Choose qualified driver
   - Confirm assignment
5. Request status changes to "Approved"

### **Managing Drivers (Admin)** ✅ **Enhanced**
1. Navigate to "Driver Management"
2. **Add New Driver**:
   - Click "Add Driver"
   - Fill in personal and license details
   - Submit form
3. **Edit Driver**:
   - Click "Edit" next to driver name
   - Update information
   - Save changes
4. **Delete Driver**: ✅ **Now Working**
   - Click "Delete" next to driver name
   - Confirm deletion in popup
   - System performs safety checks
   - Driver removed if no active assignments

### **GPS Tracking (Admin/Transport)**
1. Go to dashboard or transport requests
2. Find trips with "In Progress" status
3. Click "🛰️ Track GPS" button
4. View real-time location and route

## 🔧 **System Features**

### **Dashboard Enhancements** ✅ **Recently Streamlined**
- **Clean Interface**: Removed clutter from overview screen
- **Focused Monitoring**: Dashboard now focuses on monitoring, not actions
- **Preserved Functionality**: All approval features moved to dedicated tabs
- **GPS Access**: Easy access to track ongoing trips

### **Safety Features**
- **Assignment Validation**: Prevents invalid vehicle/driver assignments
- **Conflict Detection**: Avoids double-booking resources
- **Safety Checks**: Validates driver licenses and vehicle status
- **Data Integrity**: Protects against data corruption

### **User Experience**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Clear menu structure and breadcrumbs
- **Real-time Updates**: Live status updates without page refresh
- **Error Handling**: Clear error messages and guidance

## 📱 **Navigation Guide**

### **Sidebar Menu**
- **Dashboard**: System overview and statistics
- **Transport Requests**: Manage transport requests (Admin/Transport)
- **Vehicle Management**: Manage vehicle fleet (Admin)
- **Driver Management**: Manage drivers (Admin)
- **User Management**: Manage system users (Admin)
- **My Requests**: Personal transport requests (Employee)
- **Request Transport**: Create new request (Employee)

### **Top Navigation**
- **User Profile**: Access profile settings
- **Notifications**: System alerts and updates
- **Logout**: Sign out of the system

## 🛡️ **Security & Privacy**

### **Data Protection**
- All personal information is encrypted
- Access is role-based and restricted
- Audit trails track all system changes
- Regular security updates applied

### **Password Security**
- Use strong passwords
- Change default passwords in production
- Report suspicious activity immediately
- Log out when finished using the system

## 🆘 **Getting Help**

### **Common Issues**
- **Can't Login**: Check Employee ID and password
- **Page Not Loading**: Refresh browser or check internet connection
- **Feature Not Working**: Try logging out and back in
- **Data Not Updating**: Refresh the page

### **Contact Support**
- **Technical Issues**: Check TROUBLESHOOTING.md
- **Feature Requests**: Contact system administrator
- **Bug Reports**: Document steps to reproduce the issue

### **Training Resources**
- **Video Tutorials**: Available in the help section
- **User Manual**: This document
- **FAQ**: Frequently asked questions
- **Live Training**: Contact admin for group training sessions

## 📊 **Tips for Efficient Use**

### **For Employees**
- Submit requests early for better availability
- Provide accurate pickup/drop-off locations
- Keep contact information updated
- Cancel requests promptly if plans change

### **For Administrators**
- Review requests promptly for better service
- Keep vehicle and driver information updated
- Monitor system performance regularly
- Use GPS tracking for operational insights

### **For Transport Managers**
- Coordinate with drivers for smooth operations
- Update trip status in real-time
- Plan routes efficiently
- Communicate delays promptly

## 🎯 **Best Practices**

### **Request Management**
- Plan transport needs in advance
- Provide complete and accurate information
- Respect assigned pickup times
- Provide feedback after trips

### **Resource Management**
- Keep vehicle maintenance schedules updated
- Ensure driver information is current
- Monitor resource utilization
- Plan for peak demand periods

### **System Maintenance**
- Regular data backups
- Monitor system performance
- Update user information promptly
- Review and update security settings

**Welcome to HAL SmartMove - Your journey to efficient transport management starts here!** 🚀

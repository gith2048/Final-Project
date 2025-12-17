# Machine Management System

This system implements user-based machine management with approval workflow for the Predictive Maintenance Dashboard.

## Features

### For Regular Users:
- **Add New Machines**: Users can add machines with details like motor type, motor ID, purchase date, and purpose
- **Machine Approval**: Added machines require admin approval before appearing in the dashboard
- **Personal Dashboard**: Users only see their own approved machines
- **Conditional Access**: Dashboard features (charts, analysis, etc.) only appear after selecting a machine

### For Administrators:
- **Manual Approval**: Approve machines directly in phpMyAdmin database
- **Machine Verification**: Review machine details in database before approval
- **Simple Workflow**: Just change status from 'pending' to 'approved'

## Setup Instructions

### 1. Database Setup
The system uses MySQL/phpMyAdmin. Make sure your database connection is configured in `backend/app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/predictive_maintenance2'
```

### 2. Start the Backend
```bash
cd backend
python app.py
```

The database tables will be created automatically on first run.

### 3. Create Admin User
```bash
cd backend
python create_admin.py
```

This creates an admin user with:
- **Email**: admin@example.com
- **Password**: admin123
- **Role**: admin

### 4. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

## User Workflow

### New User Experience:
1. **Sign Up/Login**: User creates account and logs in
2. **Empty Dashboard**: Initially sees only "Add Machine" button
3. **Add Machine**: Fills out machine form with required details:
   - Machine Name
   - Motor Type (dropdown selection)
   - Motor ID (must be unique)
   - Date of Purchase
   - Purpose (description)
   - Location (optional)
4. **Pending Approval**: Machine is submitted and shows "pending" status
5. **Wait for Approval**: Admin must approve the machine
6. **Access Dashboard**: Once approved, machine appears and user can select it to access monitoring features

### Admin Workflow:
1. **Access phpMyAdmin**: Go to your phpMyAdmin interface
2. **Open Database**: Navigate to `predictive_maintenance2` database
3. **Review Machines**: Check `machines` table for entries with `status = 'pending'`
4. **Approve Machines**: Change `status` from `'pending'` to `'approved'`
5. **User Access**: Users immediately see approved machines in their dashboard

## API Endpoints

### Machine Management:
- `GET /api/machines?user_email={email}` - Get user's approved machines
- `POST /api/machines` - Add new machine (requires manual approval in database)

### User Authentication:
- `POST /api/signup` - Create new user account
- `POST /api/login` - Login and send OTP
- `POST /api/verify-login-otp` - Verify OTP and complete login

## Database Schema

### Updated Machine Model:
```sql
CREATE TABLE machines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    motor_type VARCHAR(100) NOT NULL,
    motor_id VARCHAR(100) UNIQUE NOT NULL,
    date_of_purchase DATE NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    location VARCHAR(100),
    status ENUM('pending', 'approved', 'rejected', 'active', 'inactive', 'maintenance') DEFAULT 'pending',
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    approved_by INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

## Security Features

- **User Isolation**: Users can only see their own machines
- **Admin Authorization**: Only admin users can approve machines
- **Unique Motor IDs**: Prevents duplicate machine identifiers
- **Input Validation**: All form fields are validated on both frontend and backend

## Testing

### Test User Flow:
1. Create a regular user account
2. Try to access dashboard (should only see "Add Machine")
3. Add a machine with valid details
4. Login as admin and approve the machine
5. Login back as regular user and verify machine appears
6. Select machine and verify dashboard features are now accessible

### Test Admin Flow:
1. User adds a machine (status = 'pending')
2. Open phpMyAdmin and navigate to machines table
3. Find the pending machine and change status to 'approved'
4. User refreshes dashboard and sees the approved machine

## Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Ensure MySQL is running
   - Check database credentials in `backend/app.py`
   - Verify database `predictive_maintenance2` exists

2. **Machine Not Appearing After Approval**:
   - Ensure status is exactly 'approved' (case-sensitive)
   - Check user_id matches the correct user

3. **Machine Not Appearing After Approval**:
   - Check machine status is 'approved' in database
   - Refresh the user's dashboard
   - Verify user_id matches in machines table

4. **Form Validation Errors**:
   - Ensure all required fields are filled
   - Motor ID must be unique across all machines
   - Date cannot be in the future

## Future Enhancements

- **Email Notifications**: Notify users when machines are approved/rejected
- **Machine Status Updates**: Allow users to update machine status (maintenance, etc.)
- **Bulk Operations**: Admin ability to approve multiple machines at once
- **Machine History**: Track machine modifications and status changes
- **Role-based Permissions**: Add engineer role with limited admin capabilities
# Manual Machine Approval Guide

This guide explains how to manually approve machines using phpMyAdmin instead of an admin panel.

## 🎯 **Approval Workflow**

1. **User adds machine** → Machine stored with `status = 'pending'`
2. **You approve in phpMyAdmin** → Change `status` to `'approved'`
3. **User sees machine** → Machine appears in their dashboard

## 📋 **Step-by-Step Approval Process**

### Step 1: Access phpMyAdmin
1. Open your web browser
2. Go to `http://localhost/phpmyadmin` (or your phpMyAdmin URL)
3. Login with your MySQL credentials

### Step 2: Navigate to the Database
1. Click on your database name: `predictive_maintenance2`
2. Click on the `machines` table

### Step 3: Review Pending Machines
1. Look for machines with `status = 'pending'`
2. Review the machine details:
   - `name` - Machine name
   - `motor_type` - Type of motor
   - `motor_id` - Unique motor identifier
   - `date_of_purchase` - When it was purchased
   - `purpose` - What it's used for
   - `location` - Where it's located
   - `user_id` - Which user owns it (you can check the `users` table)

### Step 4: Approve the Machine
1. Click the **Edit** button (pencil icon) for the machine you want to approve
2. Change the `status` field from `'pending'` to `'approved'`
3. Optionally, set the `approved_at` field to the current date/time
4. Click **Go** to save the changes

### Step 5: Verify Approval
1. The machine status should now show `'approved'`
2. The user will see this machine in their dashboard immediately
3. They can now select it and access all monitoring features

## 🔍 **Quick SQL Commands (Alternative)**

If you prefer using SQL commands in phpMyAdmin:

### View all pending machines:
```sql
SELECT 
    m.id,
    m.name,
    m.motor_type,
    m.motor_id,
    m.purpose,
    u.name as owner_name,
    u.email as owner_email,
    m.created_at
FROM machines m
JOIN users u ON m.user_id = u.id
WHERE m.status = 'pending'
ORDER BY m.created_at DESC;
```

### Approve a specific machine (replace `MACHINE_ID` with actual ID):
```sql
UPDATE machines 
SET status = 'approved', 
    approved_at = NOW() 
WHERE id = MACHINE_ID;
```

### Approve all pending machines:
```sql
UPDATE machines 
SET status = 'approved', 
    approved_at = NOW() 
WHERE status = 'pending';
```

### Reject a machine (optional):
```sql
UPDATE machines 
SET status = 'rejected' 
WHERE id = MACHINE_ID;
```

## 📊 **Database Table Structure**

The `machines` table contains these important fields:

| Field | Description | Values |
|-------|-------------|---------|
| `id` | Unique machine ID | Auto-increment number |
| `name` | Machine name | User-provided text |
| `motor_type` | Type of motor | AC Induction, DC Motor, etc. |
| `motor_id` | Unique motor identifier | User-provided (must be unique) |
| `date_of_purchase` | Purchase date | YYYY-MM-DD format |
| `purpose` | Machine purpose | User-provided description |
| `location` | Machine location | User-provided text |
| `status` | Approval status | `pending`, `approved`, `rejected` |
| `user_id` | Owner user ID | Links to `users.id` |
| `created_at` | When submitted | Auto-generated timestamp |
| `approved_at` | When approved | Set when you approve |

## ✅ **Status Values**

- **`pending`** - Newly submitted, waiting for approval
- **`approved`** - Approved and visible to user
- **`rejected`** - Rejected (user won't see it)
- **`active`** - Currently operational (same as approved)
- **`inactive`** - Temporarily offline
- **`maintenance`** - Under maintenance

## 🔄 **User Experience After Approval**

Once you approve a machine:

1. **User refreshes dashboard** → Machine appears in their machine list
2. **User selects machine** → All monitoring features become available:
   - Temperature, Vibration, Speed gauges
   - Real-time charts
   - AI analysis and recommendations
   - Report generation

## 🚨 **Important Notes**

- **Unique Motor IDs**: Each `motor_id` must be unique across all machines
- **User Ownership**: Each machine belongs to a specific user (`user_id`)
- **Immediate Effect**: Changes take effect immediately (user sees approved machines right away)
- **No Undo**: Once approved, you'd need to manually change status back to reject

## 🛠️ **Troubleshooting**

### Machine not appearing after approval:
1. Check that `status = 'approved'` (exactly, case-sensitive)
2. Verify the `user_id` matches an existing user
3. Ask user to refresh their browser

### Duplicate motor_id error:
1. Check if another machine has the same `motor_id`
2. Update one of them to have a unique identifier

### User can't see their machine:
1. Verify the `user_id` in machines table matches the user's ID in users table
2. Check that user is logged in with the correct email

## 📞 **Quick Reference**

**Most Common Task - Approve a machine:**
1. phpMyAdmin → `predictive_maintenance2` → `machines` table
2. Find machine with `status = 'pending'`
3. Edit → Change `status` to `'approved'` → Save
4. Done! User can now see and use the machine.

This manual approval process gives you full control over which machines are added to the system while keeping the user interface simple and clean.
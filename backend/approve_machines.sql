-- SQL Commands for Manual Machine Approval in phpMyAdmin
-- Copy and paste these commands in the SQL tab of phpMyAdmin

-- 1. VIEW ALL PENDING MACHINES
-- This shows all machines waiting for approval with user details
SELECT 
    m.id as machine_id,
    m.name as machine_name,
    m.motor_type,
    m.motor_id,
    m.purpose,
    m.location,
    m.date_of_purchase,
    u.name as owner_name,
    u.email as owner_email,
    m.created_at as submitted_on,
    m.status
FROM machines m
JOIN users u ON m.user_id = u.id
WHERE m.status = 'pending'
ORDER BY m.created_at DESC;

-- 2. APPROVE A SPECIFIC MACHINE
-- Replace 'MACHINE_ID' with the actual machine ID you want to approve
-- Example: UPDATE machines SET status = 'approved', approved_at = NOW() WHERE id = 1;
UPDATE machines 
SET status = 'approved', 
    approved_at = NOW() 
WHERE id = MACHINE_ID;

-- 3. APPROVE ALL PENDING MACHINES AT ONCE
-- Use this to approve all pending machines in one go
UPDATE machines 
SET status = 'approved', 
    approved_at = NOW() 
WHERE status = 'pending';

-- 4. REJECT A SPECIFIC MACHINE (OPTIONAL)
-- Replace 'MACHINE_ID' with the actual machine ID you want to reject
UPDATE machines 
SET status = 'rejected' 
WHERE id = MACHINE_ID;

-- 5. VIEW ALL APPROVED MACHINES
-- This shows all approved machines
SELECT 
    m.id,
    m.name,
    m.motor_id,
    u.name as owner,
    u.email,
    m.approved_at,
    m.status
FROM machines m
JOIN users u ON m.user_id = u.id
WHERE m.status = 'approved'
ORDER BY m.approved_at DESC;

-- 6. VIEW MACHINE STATISTICS
-- This gives you a summary of machine statuses
SELECT 
    status,
    COUNT(*) as count
FROM machines
GROUP BY status;

-- 7. FIND MACHINES BY USER EMAIL
-- Replace 'user@example.com' with the actual user email
SELECT 
    m.id,
    m.name,
    m.motor_id,
    m.status,
    m.created_at
FROM machines m
JOIN users u ON m.user_id = u.id
WHERE u.email = 'user@example.com';

-- QUICK APPROVAL WORKFLOW:
-- 1. Run query #1 to see pending machines
-- 2. Review the machine details
-- 3. Run query #2 with the specific machine ID to approve
-- 4. User will immediately see the machine in their dashboard
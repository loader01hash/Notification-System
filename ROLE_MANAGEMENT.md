# Role Management System

## Overview
This Django application now uses a flexible, database-driven role management system instead of hardcoded usernames. Administrators can be managed through the database, Django admin, or command-line tools.

## Role System Architecture

### UserRole Model
- Located: `apps/auth_system/models.py`
- Table: `user_roles`
- Fields:
  - `user`: OneToOneField to Django User
  - `role`: CharField with choices ['admin', 'user']
  - `created_at`: Timestamp
  - `updated_at`: Timestamp

### Permission System
- **IsAdminUser Class**: Centralized permission class supporting multiple admin methods:
  1. Django staff users (`user.is_staff = True`)
  2. UserRole model (`UserRole.objects.filter(user=user, role='admin')`)
  3. Backward compatibility with username 'krushnappan'

## Managing Admin Users

### 1. Command Line Interface
```bash
# Set up demo users (demo_admin as admin, demo_customer as regular user)
python manage.py manage_roles setup_demo

# Make a user admin
python manage.py manage_roles make_admin <username>

# Remove admin privileges  
python manage.py manage_roles remove_admin <username>

# Check user's role
python manage.py manage_roles check <username>

# List all admin users
python manage.py manage_roles list_admins
```

### 2. Database (SQL Commands)
```sql
-- Make user admin via UserRole table
INSERT INTO user_roles (user_id, role, created_at, updated_at) 
SELECT id, 'admin', NOW(), NOW() 
FROM auth_user WHERE username = 'username';

-- Or update existing role
UPDATE user_roles 
SET role = 'admin', updated_at = NOW() 
WHERE user_id = (SELECT id FROM auth_user WHERE username = 'username');

-- Make user admin via Django staff
UPDATE auth_user 
SET is_staff = 1 
WHERE username = 'username';

-- List all admins
SELECT u.username, u.email, ur.role, u.is_staff
FROM auth_user u
LEFT JOIN user_roles ur ON u.id = ur.user_id
WHERE ur.role = 'admin' OR u.is_staff = 1;
```

### 3. Django Admin Interface
1. Go to: `http://127.0.0.1:8000/admin/`
2. Navigate to: `Auth System → User roles`
3. Add/Edit user roles as needed

## Current Admin Users

### Active Admins
- **krushnappan**: Original admin (has staff privileges)
- **demo_admin**: Demo admin user (has UserRole admin + staff privileges)

### Demo Credentials
- **Admin**: username=`demo_admin`, password=`admin123`
- **User**: username=`demo_customer`, password=`user123`

## Permission Flow

```
API Request → IsAdminUser.has_permission() → Check:
1. Is Django staff user? (is_staff=True)
2. Has UserRole 'admin'?
3. Is username 'krushnappan'? (backward compatibility)
→ Grant/Deny access
```

## Files Modified

### Core Changes
- `apps/auth_system/models.py`: UserRole model + IsAdminUser permission class
- `apps/auth_system/management/commands/manage_roles.py`: Role management CLI
- `apps/auth_system/migrations/0001_initial.py`: Database migration

### Updated Imports
- `apps/customers/admin_views.py`: Uses centralized IsAdminUser
- `apps/orders/admin_views.py`: Uses centralized IsAdminUser  
- `apps/notifications/admin_views.py`: Uses centralized IsAdminUser
- `apps/orders/views.py`: Uses centralized IsAdminUser

## Migration Status
✅ Database migration applied successfully
✅ `user_roles` table created with proper foreign keys
✅ Demo users created with appropriate roles

## Testing

### Demo Validation
```bash
python demo_runner.py
```
Expected results:
- ✅ demo_admin can access all admin endpoints
- ✅ demo_customer blocked from admin endpoints  
- ✅ Authentication working for both users
- ✅ Permission controls enforced

### Manual Testing
```bash
# Test role assignments
python manage.py manage_roles check demo_admin
python manage.py manage_roles check demo_customer
python manage.py manage_roles list_admins
```

## Backward Compatibility
- Existing 'krushnappan' user retains admin access
- No breaking changes to existing functionality
- Both role-based and staff-based admin access supported

## Future Enhancements
- Role hierarchy (super_admin, admin, moderator, user)
- Permission-based access (instead of just admin/user)
- Group-based role management
- Role expiration/time-based access

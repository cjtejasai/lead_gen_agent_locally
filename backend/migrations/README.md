# Database Migrations

This directory contains database migration scripts for Lyncsea.

## Running Migrations on Server

### 1. Navigate to backend directory
```bash
cd /home/ec2-user/lead_gen_agent_locally/backend
```

### 2. Run migration script
```bash
python migrations/001_add_action_items_table.py
```

### 3. To rollback (if needed)
```bash
python migrations/001_add_action_items_table.py --rollback
```

## Migration List

- **001_add_action_items_table.py** - Adds action_items table for smart scheduling feature
  - Creates action_items table
  - Adds indexes for performance
  - Links to recordings table

## Safety Features

- ✅ Checks if table already exists before creating
- ✅ Requires confirmation for rollback
- ✅ Uses transactions for safety
- ✅ Detailed logging of all operations

## Notes

- Migrations are safe to run multiple times (idempotent)
- Always backup database before running migrations in production
- Test migrations in development environment first
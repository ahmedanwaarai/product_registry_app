# Secure Product Registration and Ownership Transfer (PHP + MySQL)

Requirements: PHP 8.0+, MySQL 5.7+/8.0, Apache with mod_php. Uses Bootstrap 5.

## Local Setup
1. Create a MySQL database, e.g., `anti_theft_app`.
2. Import schema:
   - `mysql -u root -p anti_theft_app < app/schema.sql`
3. Configure DB credentials via environment or edit `app/inc/config.php` constants `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`.
4. Set webroot to `app/public` or copy contents of `app/public` into your server document root and symlink `assets`:
   - Ensure `app/assets` is accessible at `/assets` relative to the webroot.

## Hostinger Deployment
- Upload the `app/public` directory contents into `public_html/`.
- Upload `app/assets` to `public_html/assets/`.
- Upload `app/inc`, `app/user`, `app/admin`, `app/templates` above or alongside and ensure PHP can include via relative paths. Alternatively, upload the entire `app` folder into `public_html/` and keep paths as is.
- Create a MySQL database and user in Hostinger control panel.
- Update environment variables in `.htaccess` or set in Hostinger:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`.
- Import `app/schema.sql` using phpMyAdmin.

## Default Admin
- Register a user, then use `Admin > Users` to promote to Admin and set role in `Admin > Admin Roles`.

## Modules
- Auth (login/register/logout)
- Dashboards (admin, user/shopkeeper)
- Product registration with limits and statuses
- Deals with admin approval and ownership transfer
- Verification by serial
- Product history (status + ownership + deals)

## Security
- Passwords hashed with bcrypt
- CSRF tokens for forms
- Role-based access control
- Prepared statements and basic validation

## Notes
- Modify `BASE_URL` auto-detection in `inc/config.php` if deploying under a subdirectory.
- Use `admin/products` to change product statuses with rule restrictions.
<?php
require_once __DIR__ . '/db.php';
require_once __DIR__ . '/util.php';
require_once __DIR__ . '/config.php';

function current_user(): ?array
{
    if (!empty($_SESSION['user_id'])) {
        static $cachedUser = null;
        if ($cachedUser === null) {
            $cachedUser = Database::fetchOne('SELECT * FROM users WHERE id = ?', [$_SESSION['user_id']]);
        }
        return $cachedUser ?: null;
    }
    return null;
}

function is_logged_in(): bool
{
    return current_user() !== null;
}

function is_admin(): bool
{
    $user = current_user();
    return $user && $user['user_type'] === ROLE_ADMIN;
}

function is_shopkeeper(): bool
{
    $user = current_user();
    return $user && $user['user_type'] === ROLE_SHOPKEEPER;
}

function is_user(): bool
{
    $user = current_user();
    return $user && $user['user_type'] === ROLE_USER;
}

function require_login(): void
{
    if (!is_logged_in()) {
        set_flash('warning', 'Please login to continue.');
        redirect(base_url('public/login.php'));
    }
}

function require_admin(?string $requiredAccess = null): void
{
    require_login();
    $user = current_user();
    if (!$user || $user['user_type'] !== ROLE_ADMIN) {
        http_response_code(403);
        die('Forbidden');
    }

    if ($requiredAccess) {
        $role = Database::fetchOne('SELECT access_level FROM admin_roles WHERE user_id = ?', [$user['id']]);
        $access = $role['access_level'] ?? ADMIN_ACCESS_LIMITED;
        if ($requiredAccess === ADMIN_ACCESS_FULL && $access !== ADMIN_ACCESS_FULL) {
            http_response_code(403);
            die('Insufficient admin privileges');
        }
    }
}

function require_shopkeeper_approved(): void
{
    require_login();
    $user = current_user();
    if (!$user || $user['user_type'] !== ROLE_SHOPKEEPER) {
        http_response_code(403);
        die('Forbidden');
    }
    if ($user['shopkeeper_status'] !== SHOPKEEPER_APPROVED) {
        set_flash('warning', 'Your shopkeeper account is pending approval by admin.');
        redirect(base_url('public/dashboard.php'));
    }
}

?>
<?php

// App configuration and constants

// Display errors in development only
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

// Start secure session
if (session_status() === PHP_SESSION_NONE) {
    $secure = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on';
    session_set_cookie_params([
        'lifetime' => 0,
        'path' => '/',
        'domain' => '',
        'secure' => $secure,
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    session_name('sprs_session');
    session_start();
}

// Base URL autodetection (works on Hostinger/Apache)
$scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
$host = $_SERVER['HTTP_HOST'] ?? 'localhost';
$scriptDir = rtrim(str_replace('public', '', dirname($_SERVER['SCRIPT_NAME'] ?? '/')), '/');
if ($scriptDir === '') { $scriptDir = '/'; }

define('BASE_URL', rtrim($scheme . '://' . $host . $scriptDir, '/') . '/');

define('ASSETS_URL', BASE_URL . 'assets/');

define('FREE_PRODUCT_LIMIT_USER', 3);
define('FREE_PRODUCT_LIMIT_SHOPKEEPER', 25);

// Database configuration (override via environment variables on Hostinger)

define('DB_HOST', getenv('DB_HOST') ?: 'localhost');
define('DB_NAME', getenv('DB_NAME') ?: 'anti_theft_app');
define('DB_USER', getenv('DB_USER') ?: 'root');
define('DB_PASS', getenv('DB_PASS') ?: '');

// Role constants
const ROLE_USER = 'user';
const ROLE_SHOPKEEPER = 'shopkeeper';
const ROLE_ADMIN = 'admin';

// Admin access levels
const ADMIN_ACCESS_FULL = 'full';
const ADMIN_ACCESS_LIMITED = 'limited';

// Product statuses
const STATUS_FOR_SALE = 'for_sale';
const STATUS_LOCKED = 'locked';
const STATUS_STOLEN = 'stolen';

// Deal statuses
const DEAL_PENDING = 'pending';
const DEAL_APPROVED = 'approved';
const DEAL_REJECTED = 'rejected';

// Shopkeeper approval statuses
const SHOPKEEPER_PENDING = 'pending';
const SHOPKEEPER_APPROVED = 'approved';

// CSRF token key
const CSRF_TOKEN_KEY = '_csrf_token';

?>
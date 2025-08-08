<?php
require_once __DIR__ . '/config.php';

function csrf_token(): string
{
    if (empty($_SESSION[CSRF_TOKEN_KEY])) {
        $_SESSION[CSRF_TOKEN_KEY] = bin2hex(random_bytes(32));
    }
    return $_SESSION[CSRF_TOKEN_KEY];
}

function csrf_field(): string
{
    $token = htmlspecialchars(csrf_token(), ENT_QUOTES, 'UTF-8');
    return '<input type="hidden" name="_token" value="' . $token . '">';
}

function verify_csrf_or_die(): void
{
    $token = $_POST['_token'] ?? '';
    if (!hash_equals($_SESSION[CSRF_TOKEN_KEY] ?? '', $token)) {
        http_response_code(400);
        die('Invalid CSRF token.');
    }
}

?>
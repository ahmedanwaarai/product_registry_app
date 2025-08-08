<?php
require_once __DIR__ . '/config.php';

function e(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function redirect(string $path): void
{
    header('Location: ' . $path);
    exit;
}

function base_url(string $path = ''): string
{
    return rtrim(BASE_URL, '/') . '/' . ltrim($path, '/');
}

function set_flash(string $type, string $message): void
{
    $_SESSION['flash'][$type][] = $message;
}

function get_flash(): array
{
    $flash = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $flash;
}

function random_cnic(): string
{
    // Pakistani CNIC format: 5-7-1 digits
    $part1 = str_pad((string)random_int(10000, 99999), 5, '0', STR_PAD_LEFT);
    $part2 = str_pad((string)random_int(1000000, 9999999), 7, '0', STR_PAD_LEFT);
    $part3 = (string)random_int(0, 9);
    return $part1 . '-' . $part2 . '-' . $part3;
}

function now(): string
{
    return date('Y-m-d H:i:s');
}

?>
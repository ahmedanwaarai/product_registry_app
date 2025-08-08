<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/util.php';
$flash = get_flash();
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Secure Product Registration</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="<?php echo e(ASSETS_URL); ?>css/style.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="<?php echo e(base_url('public/index.php')); ?>">SPRS</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="<?php echo e(base_url('public/index.php')); ?>">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="<?php echo e(base_url('public/index.php?page=about')); ?>">About</a></li>
        <li class="nav-item"><a class="nav-link" href="<?php echo e(base_url('public/index.php?page=services')); ?>">Services</a></li>
        <li class="nav-item"><a class="nav-link" href="<?php echo e(base_url('public/index.php?page=contact')); ?>">Contact</a></li>
        <li class="nav-item"><a class="nav-link" href="<?php echo e(base_url('public/index.php?page=terms')); ?>">Terms and Conditions</a></li>
      </ul>
      <ul class="navbar-nav">
        <?php if (!is_logged_in()): ?>
          <li class="nav-item"><a class="btn btn-outline-light me-2" href="<?php echo e(base_url('public/login.php')); ?>">Login</a></li>
          <li class="nav-item"><a class="btn btn-warning" href="<?php echo e(base_url('public/register.php')); ?>">Register</a></li>
        <?php else: ?>
          <li class="nav-item"><a class="btn btn-outline-light me-2" href="<?php echo e(base_url('public/dashboard.php')); ?>">Dashboard</a></li>
          <li class="nav-item"><a class="btn btn-danger" href="<?php echo e(base_url('public/logout.php')); ?>">Logout</a></li>
        <?php endif; ?>
      </ul>
    </div>
  </div>
</nav>
<div class="container py-3">
  <?php if ($flash): ?>
    <?php foreach ($flash as $type => $messages): ?>
      <?php foreach ($messages as $message): ?>
        <div class="alert alert-<?php echo e($type); ?> alert-dismissible fade show" role="alert">
          <?php echo e($message); ?>
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      <?php endforeach; ?>
    <?php endforeach; ?>
  <?php endif; ?>
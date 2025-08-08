<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/db.php';

require_admin();
$user = current_user();

$pendingShops = Database::fetchOne('SELECT COUNT(*) as c FROM users WHERE user_type = ? AND shopkeeper_status = ?', [ROLE_SHOPKEEPER, SHOPKEEPER_PENDING])['c'] ?? 0;
$pendingDeals = Database::fetchOne('SELECT COUNT(*) as c FROM sale_deals WHERE status = ?', [DEAL_PENDING])['c'] ?? 0;
$totalProducts = Database::fetchOne('SELECT COUNT(*) as c FROM products', [])['c'] ?? 0;

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Admin Dashboard</h3>
<div class="row">
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <div class="h6">Pending Shopkeepers</div>
    <div class="display-6"><?php echo e($pendingShops); ?></div>
    <a href="<?php echo e(base_url('admin/shopkeepers.php')); ?>" class="btn btn-sm btn-link p-0 mt-2">Review</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <div class="h6">Pending Deals</div>
    <div class="display-6"><?php echo e($pendingDeals); ?></div>
    <a href="<?php echo e(base_url('admin/deals.php')); ?>" class="btn btn-sm btn-link p-0 mt-2">Review</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <div class="h6">Total Products</div>
    <div class="display-6"><?php echo e($totalProducts); ?></div>
    <a href="<?php echo e(base_url('admin/products.php')); ?>" class="btn btn-sm btn-link p-0 mt-2">View</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <div class="h6">Users</div>
    <a href="<?php echo e(base_url('admin/users.php')); ?>" class="btn btn-sm btn-primary">Manage Users</a>
  </div></div></div>
</div>
<div class="row">
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <a href="<?php echo e(base_url('admin/categories.php')); ?>" class="btn btn-outline-secondary w-100">Manage Categories</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <a href="<?php echo e(base_url('admin/brands.php')); ?>" class="btn btn-outline-secondary w-100">Manage Brands</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <a href="<?php echo e(base_url('admin/roles.php')); ?>" class="btn btn-outline-secondary w-100">Admin Roles</a>
  </div></div></div>
  <div class="col-md-3"><div class="card mb-3"><div class="card-body">
    <a href="<?php echo e(base_url('admin/reports.php')); ?>" class="btn btn-outline-secondary w-100">Reports</a>
  </div></div></div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
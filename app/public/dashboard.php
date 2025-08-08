<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_login();
$user = current_user();

if ($user['user_type'] === ROLE_ADMIN) {
    redirect(base_url('admin/index.php'));
}

require_once __DIR__ . '/../templates/header.php';

// Counts
$productCount = Database::fetchOne('SELECT COUNT(*) as c FROM products WHERE owner_user_id = ?', [$user['id']])['c'] ?? 0;
$dealCount = Database::fetchOne('SELECT COUNT(*) as c FROM sale_deals WHERE buyer_user_id = ? OR seller_user_id = ?', [$user['id'], $user['id']])['c'] ?? 0;
?>
<div class="row">
  <div class="col-12">
    <div class="card mb-3">
      <div class="card-body d-flex justify-content-between align-items-center">
        <div>
          <h5 class="card-title mb-1">Welcome, <?php echo e($user['username']); ?>!</h5>
          <div class="text-muted">Account: <?php echo e(ucfirst($user['user_type'])); ?><?php if ($user['user_type'] === ROLE_SHOPKEEPER): ?> (<?php echo e($user['shopkeeper_status']); ?>)<?php endif; ?></div>
        </div>
        <div>
          <a href="<?php echo e(base_url('user/register_product.php')); ?>" class="btn btn-primary me-2">Register Product</a>
          <a href="<?php echo e(base_url('user/create_deal.php')); ?>" class="btn btn-success me-2">Create Deal</a>
          <a href="<?php echo e(base_url('user/verify.php')); ?>" class="btn btn-outline-secondary">Verify Product</a>
        </div>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card"><div class="card-body">
      <div class="d-flex justify-content-between"><span>My Products</span><span class="badge bg-primary"><?php echo e($productCount); ?></span></div>
      <a href="<?php echo e(base_url('user/my_products.php')); ?>" class="btn btn-link p-0 mt-2">View</a>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card"><div class="card-body">
      <div class="d-flex justify-content-between"><span>My Deals</span><span class="badge bg-success"><?php echo e($dealCount); ?></span></div>
      <a href="<?php echo e(base_url('user/my_deals.php')); ?>" class="btn btn-link p-0 mt-2">View</a>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card"><div class="card-body">
      <div class="d-flex justify-content-between"><span>Verify/Search Product</span><span class="badge bg-secondary">Go</span></div>
      <a href="<?php echo e(base_url('user/verify.php')); ?>" class="btn btn-link p-0 mt-2">Open</a>
    </div></div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
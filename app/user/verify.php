<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_login();
$querySerial = trim($_GET['serial'] ?? ($_POST['serial'] ?? ''));
$product = null;
if ($querySerial !== '') {
    $product = Database::fetchOne('SELECT p.*, u.username, u.mobile, u.cnic FROM products p LEFT JOIN users u ON u.id = p.owner_user_id WHERE p.serial = ?', [$querySerial]);
}
require_once __DIR__ . '/../templates/header.php';
?>
<h3>Verify/Search Product</h3>
<form class="row g-3 mb-3" method="post">
  <div class="col-auto">
    <input type="text" name="serial" class="form-control" placeholder="Enter Serial Number" value="<?php echo e($querySerial); ?>" required>
  </div>
  <div class="col-auto">
    <button class="btn btn-primary" type="submit">Search</button>
  </div>
</form>
<?php if ($product): ?>
  <div class="card"><div class="card-body">
    <div class="h5 mb-3"><?php echo e($product['name']); ?> <span class="badge bg-<?php echo e($product['status']==STATUS_FOR_SALE?'primary':($product['status']==STATUS_LOCKED?'warning text-dark':'danger')); ?>"><?php echo e(strtoupper($product['status'])); ?></span></div>
    <div><strong>Serial:</strong> <?php echo e($product['serial']); ?></div>
    <div><strong>Owner:</strong> <?php echo e($product['username']); ?> (<?php echo e($product['mobile']); ?>, <?php echo e($product['cnic']); ?>)</div>
    <div><strong>Registered at:</strong> <?php echo e($product['registered_at']); ?></div>
    <a class="btn btn-link" href="<?php echo e(base_url('user/product_history.php?id=' . $product['id'])); ?>">View History</a>
  </div></div>
<?php elseif ($querySerial !== ''): ?>
  <div class="alert alert-warning">No product found with that serial.</div>
<?php endif; ?>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
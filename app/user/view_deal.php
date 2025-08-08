<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_login();
$user = current_user();
$dealId = (int)($_GET['id'] ?? 0);
$deal = Database::fetchOne('SELECT d.*, bu.username AS buyer_name, su.username AS seller_name FROM sale_deals d LEFT JOIN users bu ON bu.id = d.buyer_user_id LEFT JOIN users su ON su.id = d.seller_user_id WHERE d.id = ?', [$dealId]);
if (!$deal || ($deal['buyer_user_id'] !== $user['id'] && $deal['seller_user_id'] !== $user['id'] && $user['user_type'] !== ROLE_ADMIN)) {
    http_response_code(404);
    die('Deal not found');
}
$items = Database::fetchAll('SELECT * FROM deal_products WHERE deal_id = ?', [$dealId]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Deal #<?php echo e($deal['id']); ?></h3>
<div class="card mb-3"><div class="card-body">
  <div><strong>Buyer:</strong> <?php echo e($deal['buyer_name']); ?></div>
  <div><strong>Seller:</strong> <?php echo e($deal['seller_name']); ?></div>
  <div><strong>Status:</strong> <span class="badge bg-<?php echo e($deal['status']===DEAL_APPROVED?'success':($deal['status']===DEAL_REJECTED?'danger':'warning text-dark')); ?>"><?php echo e(strtoupper($deal['status'])); ?></span></div>
  <div><strong>Seller Contact:</strong> <?php echo e($deal['seller_mobile']); ?>, <?php echo e($deal['seller_cnic']); ?>, <?php echo e($deal['seller_address']); ?></div>
  <div><strong>Created:</strong> <?php echo e($deal['created_at']); ?></div>
</div></div>
<div class="card"><div class="card-body">
  <h5>Products</h5>
  <ul class="list-group">
    <?php foreach ($items as $it): ?>
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <div><strong><?php echo e($it['product_name']); ?></strong> (<?php echo e($it['product_serial']); ?>)</div>
          <div class="text-muted small"><?php echo e(($it['category_name'] ?? '-') . ' / ' . ($it['brand_name'] ?? '-')); ?></div>
        </div>
        <a class="btn btn-sm btn-outline-secondary" href="<?php echo e(base_url('user/verify.php?serial=' . urlencode($it['product_serial']))); ?>">Verify</a>
      </li>
    <?php endforeach; ?>
  </ul>
</div></div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
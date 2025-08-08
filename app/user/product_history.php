<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_login();
$user = current_user();
$productId = (int)($_GET['id'] ?? 0);
$product = Database::fetchOne('SELECT p.*, u.username AS owner_name FROM products p LEFT JOIN users u ON u.id = p.owner_user_id WHERE p.id = ?', [$productId]);
if (!$product) { http_response_code(404); die('Not found'); }
// Authorization: owner or admin can view
if ($product['owner_user_id'] !== $user['id'] && $user['user_type'] !== ROLE_ADMIN) {
    http_response_code(403); die('Forbidden');
}
$statusLogs = Database::fetchAll('SELECT l.*, u.username FROM product_status_log l LEFT JOIN users u ON u.id = l.changed_by_user_id WHERE l.product_id = ? ORDER BY l.changed_at DESC', [$productId]);
$ownerships = Database::fetchAll('SELECT o.*, u.username FROM product_ownerships o LEFT JOIN users u ON u.id = o.user_id WHERE o.product_id = ? ORDER BY o.acquired_at DESC', [$productId]);
$deals = Database::fetchAll('SELECT d.* FROM sale_deals d JOIN deal_products dp ON dp.deal_id = d.id WHERE dp.product_id = ? ORDER BY d.created_at DESC', [$productId]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Product History: <?php echo e($product['name']); ?> (<?php echo e($product['serial']); ?>)</h3>
<div class="row">
  <div class="col-md-4">
    <div class="card mb-3"><div class="card-body">
      <h5>Current Owner</h5>
      <div><?php echo e($product['owner_name']); ?></div>
      <div>Status: <span class="badge bg-<?php echo e($product['status']==STATUS_FOR_SALE?'primary':($product['status']==STATUS_LOCKED?'warning text-dark':'danger')); ?>"><?php echo e(strtoupper($product['status'])); ?></span></div>
      <div>Registered: <?php echo e($product['registered_at']); ?></div>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card mb-3"><div class="card-body">
      <h5>Status Changes</h5>
      <ul class="list-group">
        <?php foreach ($statusLogs as $l): ?>
          <li class="list-group-item">
            <div><strong><?php echo e(strtoupper($l['status'])); ?></strong> by <?php echo e($l['username'] ?? 'System'); ?></div>
            <div class="text-muted small"><?php echo e($l['changed_at']); ?> - <?php echo e($l['note']); ?></div>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
  <div class="col-md-4">
    <div class="card mb-3"><div class="card-body">
      <h5>Ownership</h5>
      <ul class="list-group">
        <?php foreach ($ownerships as $o): ?>
          <li class="list-group-item">
            <div><strong><?php echo e($o['username'] ?? 'Unknown'); ?></strong> via <?php echo e($o['method']); ?></div>
            <div class="text-muted small"><?php echo e($o['acquired_at']); ?></div>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
</div>
<div class="card"><div class="card-body">
  <h5>Deals</h5>
  <ul class="list-group">
    <?php foreach ($deals as $d): ?>
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>Deal #<?php echo e($d['id']); ?> - <span class="badge bg-<?php echo e($d['status']===DEAL_APPROVED?'success':($d['status']===DEAL_REJECTED?'danger':'warning text-dark')); ?>"><?php echo e(strtoupper($d['status'])); ?></span></div>
        <a class="btn btn-sm btn-outline-secondary" href="<?php echo e(base_url('user/view_deal.php?id=' . $d['id'])); ?>">View</a>
      </li>
    <?php endforeach; ?>
  </ul>
</div></div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
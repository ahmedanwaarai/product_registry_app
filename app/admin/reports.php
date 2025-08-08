<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_admin(ADMIN_ACCESS_LIMITED);

$recentDeals = Database::fetchAll('SELECT d.*, bu.username AS buyer_name, su.username AS seller_name FROM sale_deals d LEFT JOIN users bu ON bu.id = d.buyer_user_id LEFT JOIN users su ON su.id = d.seller_user_id ORDER BY d.created_at DESC LIMIT 20');
$summary = Database::fetchOne('SELECT SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as for_sale, SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as locked, SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as stolen, COUNT(*) as total FROM products', [STATUS_FOR_SALE, STATUS_LOCKED, STATUS_STOLEN]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Reports</h3>
<div class="row">
  <div class="col-md-4">
    <div class="card mb-3"><div class="card-body">
      <h5>Products Summary</h5>
      <ul class="list-group">
        <li class="list-group-item d-flex justify-content-between align-items-center">For Sale <span class="badge bg-primary"><?php echo e($summary['for_sale']); ?></span></li>
        <li class="list-group-item d-flex justify-content-between align-items-center">Locked <span class="badge bg-warning text-dark"><?php echo e($summary['locked']); ?></span></li>
        <li class="list-group-item d-flex justify-content-between align-items-center">Stolen <span class="badge bg-danger"><?php echo e($summary['stolen']); ?></span></li>
        <li class="list-group-item d-flex justify-content-between align-items-center">Total <span class="badge bg-secondary"><?php echo e($summary['total']); ?></span></li>
      </ul>
    </div></div>
  </div>
  <div class="col-md-8">
    <div class="card mb-3"><div class="card-body">
      <h5>Recent Deals</h5>
      <ul class="list-group">
        <?php foreach ($recentDeals as $d): ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong>#<?php echo e($d['id']); ?></strong> Buyer: <?php echo e($d['buyer_name']); ?> | Seller: <?php echo e($d['seller_name']); ?></div>
              <div>Status: <span class="badge bg-<?php echo e($d['status']===DEAL_APPROVED?'success':($d['status']===DEAL_REJECTED?'danger':'warning text-dark')); ?>"><?php echo e(strtoupper($d['status'])); ?></span></div>
            </div>
            <a class="btn btn-sm btn-outline-secondary" href="<?php echo e(base_url('user/view_deal.php?id=' . $d['id'])); ?>">View</a>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_login();
$user = current_user();

$deals = Database::fetchAll('SELECT d.*, bu.username AS buyer_name, su.username AS seller_name FROM sale_deals d LEFT JOIN users bu ON bu.id = d.buyer_user_id LEFT JOIN users su ON su.id = d.seller_user_id WHERE d.buyer_user_id = ? OR d.seller_user_id = ? ORDER BY d.created_at DESC', [$user['id'], $user['id']]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>My Deals</h3>
<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>ID</th><th>Buyer</th><th>Seller</th><th>Status</th><th>Created</th><th>Details</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($deals as $d): ?>
      <tr>
        <td>#<?php echo e($d['id']); ?></td>
        <td><?php echo e($d['buyer_name']); ?></td>
        <td><?php echo e($d['seller_name']); ?></td>
        <td><span class="badge bg-<?php echo e($d['status']===DEAL_APPROVED?'success':($d['status']===DEAL_REJECTED?'danger':'warning text-dark')); ?>"><?php echo e(strtoupper($d['status'])); ?></span></td>
        <td><?php echo e($d['created_at']); ?></td>
        <td><a class="btn btn-sm btn-outline-secondary" href="<?php echo e(base_url('user/view_deal.php?id=' . $d['id'])); ?>">View</a></td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
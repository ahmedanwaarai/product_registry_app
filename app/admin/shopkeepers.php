<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_admin(ADMIN_ACCESS_LIMITED);

if (isset($_GET['approve'])) {
    $id = (int)$_GET['approve'];
    Database::execute('UPDATE users SET shopkeeper_status = ? WHERE id = ? AND user_type = ?', [SHOPKEEPER_APPROVED, $id, ROLE_SHOPKEEPER]);
    set_flash('success', 'Shopkeeper approved.');
    redirect(base_url('admin/shopkeepers.php'));
}

$pending = Database::fetchAll('SELECT * FROM users WHERE user_type = ? AND shopkeeper_status = ? ORDER BY created_at DESC', [ROLE_SHOPKEEPER, SHOPKEEPER_PENDING]);
$approved = Database::fetchAll('SELECT * FROM users WHERE user_type = ? AND shopkeeper_status = ? ORDER BY created_at DESC', [ROLE_SHOPKEEPER, SHOPKEEPER_APPROVED]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Shopkeepers</h3>
<div class="row">
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Pending Approval</h5>
      <ul class="list-group">
        <?php foreach ($pending as $u): ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong><?php echo e($u['username']); ?></strong> (<?php echo e($u['email']); ?>, <?php echo e($u['mobile']); ?>)</div>
              <div class="text-muted small">Shop: <?php echo e($u['shop_name']); ?> | CNIC: <?php echo e($u['cnic']); ?></div>
            </div>
            <a class="btn btn-sm btn-success" href="?approve=<?php echo e($u['id']); ?>">Approve</a>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Approved</h5>
      <ul class="list-group">
        <?php foreach ($approved as $u): ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong><?php echo e($u['username']); ?></strong> (<?php echo e($u['email']); ?>, <?php echo e($u['mobile']); ?>)</div>
              <div class="text-muted small">Shop: <?php echo e($u['shop_name']); ?> | CNIC: <?php echo e($u['cnic']); ?></div>
            </div>
            <span class="badge bg-success">Approved</span>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
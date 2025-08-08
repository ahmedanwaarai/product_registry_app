<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_admin(ADMIN_ACCESS_LIMITED);

if (isset($_GET['approve'])) {
    $dealId = (int)$_GET['approve'];
    $deal = Database::fetchOne('SELECT * FROM sale_deals WHERE id = ?', [$dealId]);
    if ($deal && $deal['status'] === DEAL_PENDING) {
        $items = Database::fetchAll('SELECT * FROM deal_products WHERE deal_id = ?', [$dealId]);
        $valid = true;
        foreach ($items as $it) {
            $p = Database::fetchOne('SELECT * FROM products WHERE id = ?', [$it['product_id']]);
            if (!$p || $p['status'] !== STATUS_FOR_SALE) { $valid = false; break; }
        }
        if ($valid) {
            // Transfer ownership to buyer, log history
            foreach ($items as $it) {
                $p = Database::fetchOne('SELECT * FROM products WHERE id = ?', [$it['product_id']]);
                Database::execute('UPDATE products SET owner_user_id = ?, last_status_change_at = ? WHERE id = ?', [$deal['buyer_user_id'], now(), $p['id']]);
                Database::execute('INSERT INTO product_ownerships (product_id, user_id, acquired_at, method) VALUES (?,?,?,?)', [$p['id'], $deal['buyer_user_id'], now(), 'deal_approved']);
                Database::execute('INSERT INTO product_status_log (product_id, status, changed_by_user_id, changed_at, note) VALUES (?,?,?,?,?)', [$p['id'], $p['status'], current_user()['id'], now(), 'Ownership transferred via deal #' . $dealId]);
            }
            Database::execute('UPDATE sale_deals SET status = ?, decided_at = ? WHERE id = ?', [DEAL_APPROVED, now(), $dealId]);
            set_flash('success', 'Deal approved and ownership transferred.');
        } else {
            set_flash('danger', 'Deal cannot be approved. One or more products are not eligible.');
        }
    }
    redirect(base_url('admin/deals.php'));
}

if (isset($_GET['reject'])) {
    $dealId = (int)$_GET['reject'];
    $deal = Database::fetchOne('SELECT * FROM sale_deals WHERE id = ?', [$dealId]);
    if ($deal && $deal['status'] === DEAL_PENDING) {
        Database::execute('UPDATE sale_deals SET status = ?, decided_at = ? WHERE id = ?', [DEAL_REJECTED, now(), $dealId]);
        set_flash('success', 'Deal rejected.');
    }
    redirect(base_url('admin/deals.php'));
}

$pending = Database::fetchAll('SELECT d.*, bu.username AS buyer_name, su.username AS seller_name FROM sale_deals d LEFT JOIN users bu ON bu.id = d.buyer_user_id LEFT JOIN users su ON su.id = d.seller_user_id WHERE d.status = ? ORDER BY d.created_at ASC', [DEAL_PENDING]);
$all = Database::fetchAll('SELECT d.*, bu.username AS buyer_name, su.username AS seller_name FROM sale_deals d LEFT JOIN users bu ON bu.id = d.buyer_user_id LEFT JOIN users su ON su.id = d.seller_user_id ORDER BY d.created_at DESC LIMIT 100', []);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Deals</h3>
<div class="row">
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Pending</h5>
      <ul class="list-group">
        <?php foreach ($pending as $d): ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong>#<?php echo e($d['id']); ?></strong> Buyer: <?php echo e($d['buyer_name']); ?> | Seller: <?php echo e($d['seller_name']); ?></div>
              <div class="text-muted small"><?php echo e($d['created_at']); ?></div>
            </div>
            <span>
              <a class="btn btn-sm btn-success" href="?approve=<?php echo e($d['id']); ?>">Approve</a>
              <a class="btn btn-sm btn-outline-danger" href="?reject=<?php echo e($d['id']); ?>">Reject</a>
              <a class="btn btn-sm btn-outline-secondary" href="<?php echo e(base_url('user/view_deal.php?id=' . $d['id'])); ?>">View</a>
            </span>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Recent</h5>
      <ul class="list-group">
        <?php foreach ($all as $d): ?>
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
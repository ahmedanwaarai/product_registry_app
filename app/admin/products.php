<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_admin(ADMIN_ACCESS_LIMITED);

// Filters
$q_serial = trim($_GET['serial'] ?? '');
$q_mobile = trim($_GET['mobile'] ?? '');
$q_name = trim($_GET['name'] ?? '');
$q_cnic = trim($_GET['cnic'] ?? '');

$where = [];$params = [];
if ($q_serial !== '') { $where[] = 'p.serial LIKE ?'; $params[] = "%$q_serial%"; }
if ($q_mobile !== '') { $where[] = 'u.mobile LIKE ?'; $params[] = "%$q_mobile%"; }
if ($q_name !== '') { $where[] = 'u.username LIKE ?'; $params[] = "%$q_name%"; }
if ($q_cnic !== '') { $where[] = 'u.cnic LIKE ?'; $params[] = "%$q_cnic%"; }
$sql = 'SELECT p.*, u.username, u.mobile, u.cnic, b.name AS brand_name, c.name AS category_name FROM products p LEFT JOIN users u ON u.id = p.owner_user_id LEFT JOIN brands b ON b.id = p.brand_id LEFT JOIN product_categories c ON c.id = p.category_id';
if ($where) { $sql .= ' WHERE ' . implode(' AND ', $where); }
$sql .= ' ORDER BY p.registered_at DESC LIMIT 200';
$products = Database::fetchAll($sql, $params);

// Admin status change with rule enforcement
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['product_id'], $_POST['new_status'])) {
    verify_csrf_or_die();
    $product = Database::fetchOne('SELECT * FROM products WHERE id = ?', [$_POST['product_id']]);
    $newStatus = $_POST['new_status'];
    if ($product && in_array($newStatus, [STATUS_FOR_SALE, STATUS_LOCKED, STATUS_STOLEN], true)) {
        // Admin rules: Can change For Sale -> Locked/Stolen; Locked -> Stolen; Cannot change Locked/Stolen -> For Sale
        $from = $product['status'];
        $allowed = false;
        if ($from === STATUS_FOR_SALE && in_array($newStatus, [STATUS_LOCKED, STATUS_STOLEN], true)) { $allowed = true; }
        if ($from === STATUS_LOCKED && $newStatus === STATUS_STOLEN) { $allowed = true; }
        if ($allowed) {
            Database::execute('UPDATE products SET status = ?, last_status_change_at = ? WHERE id = ?', [$newStatus, now(), $product['id']]);
            Database::execute('INSERT INTO product_status_log (product_id, status, changed_by_user_id, changed_at, note) VALUES (?,?,?,?,?)', [$product['id'], $newStatus, current_user()['id'], now(), 'Admin changed status']);
            set_flash('success', 'Status updated.');
        } else {
            set_flash('danger', 'Status change not permitted by rule.');
        }
    }
    redirect(base_url('admin/products.php'));
}

require_once __DIR__ . '/../templates/header.php';
?>
<h3>All Products</h3>
<form class="row g-2 mb-3">
  <div class="col-md-3"><input class="form-control" name="serial" placeholder="Serial" value="<?php echo e($q_serial); ?>"></div>
  <div class="col-md-3"><input class="form-control" name="mobile" placeholder="Mobile" value="<?php echo e($q_mobile); ?>"></div>
  <div class="col-md-3"><input class="form-control" name="name" placeholder="Owner Name" value="<?php echo e($q_name); ?>"></div>
  <div class="col-md-3"><input class="form-control" name="cnic" placeholder="CNIC" value="<?php echo e($q_cnic); ?>"></div>
  <div class="col-12"><button class="btn btn-primary" type="submit">Search</button></div>
</form>
<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Name</th><th>Serial</th><th>Category</th><th>Brand</th><th>Owner</th><th>Status</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($products as $p): ?>
      <tr>
        <td><?php echo e($p['name']); ?></td>
        <td><?php echo e($p['serial']); ?></td>
        <td><?php echo e($p['category_name'] ?? '-'); ?></td>
        <td><?php echo e($p['brand_name'] ?? '-'); ?></td>
        <td><?php echo e($p['username']); ?> (<?php echo e($p['mobile']); ?>)</td>
        <td><span class="badge bg-<?php echo e($p['status']==STATUS_FOR_SALE?'primary':($p['status']==STATUS_LOCKED?'warning text-dark':'danger')); ?>"><?php echo e(strtoupper($p['status'])); ?></span></td>
        <td>
          <form method="post" class="d-flex align-items-center">
            <?php echo csrf_field(); ?>
            <input type="hidden" name="product_id" value="<?php echo e($p['id']); ?>">
            <select name="new_status" class="form-select form-select-sm me-2">
              <option value="<?php echo e(STATUS_FOR_SALE); ?>">For Sale</option>
              <option value="<?php echo e(STATUS_LOCKED); ?>">Locked</option>
              <option value="<?php echo e(STATUS_STOLEN); ?>">Stolen</option>
            </select>
            <button class="btn btn-sm btn-outline-primary" type="submit">Set</button>
            <a class="btn btn-sm btn-link ms-2" href="<?php echo e(base_url('user/product_history.php?id=' . $p['id'])); ?>">History</a>
          </form>
        </td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
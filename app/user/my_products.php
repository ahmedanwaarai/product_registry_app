<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_login();
$user = current_user();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['product_id'], $_POST['new_status'])) {
    verify_csrf_or_die();
    $product = Database::fetchOne('SELECT * FROM products WHERE id = ? AND owner_user_id = ?', [$_POST['product_id'], $user['id']]);
    $newStatus = $_POST['new_status'];
    if ($product && in_array($newStatus, [STATUS_FOR_SALE, STATUS_LOCKED, STATUS_STOLEN], true)) {
        // Rule: cannot change Locked/Stolen back to For Sale
        if (in_array($product['status'], [STATUS_LOCKED, STATUS_STOLEN], true) && $newStatus === STATUS_FOR_SALE) {
            set_flash('danger', 'Cannot revert to For Sale from Locked/Stolen.');
        } else {
            Database::execute('UPDATE products SET status = ?, last_status_change_at = ? WHERE id = ?', [$newStatus, now(), $product['id']]);
            Database::execute('INSERT INTO product_status_log (product_id, status, changed_by_user_id, changed_at, note) VALUES (?,?,?,?,?)', [$product['id'], $newStatus, $user['id'], now(), 'User changed status']);
            set_flash('success', 'Status updated.');
        }
    }
    redirect(base_url('user/my_products.php'));
}

$products = Database::fetchAll('SELECT p.*, c.name AS category_name, b.name AS brand_name FROM products p LEFT JOIN product_categories c ON c.id = p.category_id LEFT JOIN brands b ON b.id = p.brand_id WHERE p.owner_user_id = ? ORDER BY p.registered_at DESC', [$user['id']]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>My Products</h3>
<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Name</th><th>Serial</th><th>Category</th><th>Brand</th><th>Status</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($products as $p): ?>
      <tr>
        <td><?php echo e($p['name']); ?></td>
        <td><?php echo e($p['serial']); ?></td>
        <td><?php echo e($p['category_name'] ?? '-'); ?></td>
        <td><?php echo e($p['brand_name'] ?? '-'); ?></td>
        <td><span class="badge bg-<?php echo e($p['status']==STATUS_FOR_SALE?'primary':($p['status']==STATUS_LOCKED?'warning text-dark':'danger')); ?>"><?php echo e(strtoupper($p['status'])); ?></span></td>
        <td>
          <form method="post" class="d-flex align-items-center">
            <?php echo csrf_field(); ?>
            <input type="hidden" name="product_id" value="<?php echo e($p['id']); ?>">
            <select name="new_status" class="form-select form-select-sm me-2" <?php echo in_array($p['status'], [STATUS_LOCKED, STATUS_STOLEN], true) ? '': ''; ?>>
              <option value="<?php echo e(STATUS_FOR_SALE); ?>" <?php echo $p['status']===STATUS_FOR_SALE?'selected':''; ?>>For Sale</option>
              <option value="<?php echo e(STATUS_LOCKED); ?>" <?php echo $p['status']===STATUS_LOCKED?'selected':''; ?>>Locked</option>
              <option value="<?php echo e(STATUS_STOLEN); ?>" <?php echo $p['status']===STATUS_STOLEN?'selected':''; ?>>Stolen</option>
            </select>
            <button class="btn btn-sm btn-outline-primary" type="submit">Update</button>
          </form>
        </td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
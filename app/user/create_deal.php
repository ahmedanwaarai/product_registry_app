<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_login();
$user = current_user();

$errors = [];
$seller_name = $_POST['seller_name'] ?? '';
$seller_mobile = $_POST['seller_mobile'] ?? '';
$seller_cnic = $_POST['seller_cnic'] ?? '';
$seller_address = $_POST['seller_address'] ?? '';
$serials_input = $_POST['serials'] ?? '';
$serials = array_filter(array_map('trim', preg_split('/[\s,\n]+/', $serials_input)));

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();
    if ($seller_name === '' || $seller_mobile === '' || $seller_cnic === '' || $seller_address === '') {
        $errors[] = 'All seller fields are required.';
    }
    if (!$serials) { $errors[] = 'Provide at least one product serial.'; }

    $products = [];
    if (!$errors) {
        foreach ($serials as $serial) {
            $p = Database::fetchOne('SELECT p.*, u.username AS owner_name, u.id AS owner_id, u.user_type AS owner_user_type, b.name AS brand_name, c.name AS category_name FROM products p LEFT JOIN users u ON u.id = p.owner_user_id LEFT JOIN brands b ON b.id = p.brand_id LEFT JOIN product_categories c ON c.id = p.category_id WHERE p.serial = ?', [$serial]);
            if (!$p) { $errors[] = "Serial $serial not found."; continue; }
            if ($p['status'] !== STATUS_FOR_SALE) { $errors[] = "Serial $serial is not For Sale."; continue; }
            // Resale rule: if current owner is a normal user, product must be at least 3 days since registration
            if (($p['owner_user_type'] ?? '') === ROLE_USER) {
                $registeredAt = new DateTime($p['registered_at']);
                $diffDays = $registeredAt->diff(new DateTime())->days;
                if ($diffDays < 3) { $errors[] = "Serial $serial cannot be resold within 3 days of registration."; continue; }
            }
            $products[] = $p;
        }
    }

    if (!$errors && $products) {
        Database::execute('INSERT INTO sale_deals (buyer_user_id, seller_user_id, seller_name, seller_mobile, seller_cnic, seller_address, status, created_at) VALUES (?,?,?,?,?,?,?,?)', [
            $user['id'], $products[0]['owner_id'], $seller_name, $seller_mobile, $seller_cnic, $seller_address, DEAL_PENDING, now()
        ]);
        $dealId = Database::lastInsertId();
        foreach ($products as $p) {
            Database::execute('INSERT INTO deal_products (deal_id, product_id, product_serial, product_name, brand_name, category_name) VALUES (?,?,?,?,?,?)', [
                $dealId, $p['id'], $p['serial'], $p['name'], $p['brand_name'], $p['category_name']
            ]);
        }
        set_flash('success', 'Deal submitted for admin approval.');
        redirect(base_url('user/my_deals.php'));
    }
}

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Create Deal</h3>
<div class="row">
  <div class="col-md-6">
    <?php if ($errors): ?><div class="alert alert-danger"><?php echo e(implode('<br>', $errors)); ?></div><?php endif; ?>
    <div class="card mb-3"><div class="card-body">
      <form method="post">
        <?php echo csrf_field(); ?>
        <div class="mb-2"><label class="form-label">Seller Name</label><input class="form-control" name="seller_name" value="<?php echo e($seller_name); ?>" required></div>
        <div class="mb-2"><label class="form-label">Seller Mobile</label><input class="form-control" name="seller_mobile" value="<?php echo e($seller_mobile); ?>" required></div>
        <div class="mb-2"><label class="form-label">Seller CNIC</label><input class="form-control" name="seller_cnic" value="<?php echo e($seller_cnic); ?>" required></div>
        <div class="mb-2"><label class="form-label">Seller Address</label><input class="form-control" name="seller_address" value="<?php echo e($seller_address); ?>" required></div>
        <div class="mb-3"><label class="form-label">Product Serials (comma or newline separated)</label><textarea class="form-control" rows="4" name="serials" placeholder="ABC123\nXYZ789"><?php echo e($serials_input); ?></textarea></div>
        <button class="btn btn-success" type="submit">Submit Deal</button>
        <a href="<?php echo e(base_url('public/dashboard.php')); ?>" class="btn btn-link">Back</a>
      </form>
    </div></div>
  </div>
  <div class="col-md-6">
    <?php if ($serials): ?>
      <div class="card"><div class="card-body">
        <h5>Products in Deal</h5>
        <ul class="list-group">
        <?php foreach ($serials as $serial): $p = Database::fetchOne('SELECT p.*, b.name AS brand_name, c.name AS category_name FROM products p LEFT JOIN brands b ON b.id = p.brand_id LEFT JOIN product_categories c ON c.id = p.category_id WHERE p.serial = ?', [$serial]); ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong><?php echo e($p['name'] ?? 'Unknown'); ?></strong> (<?php echo e($serial); ?>)</div>
              <div class="text-muted small"><?php echo e(($p['category_name'] ?? '-') . ' / ' . ($p['brand_name'] ?? '-')); ?></div>
            </div>
            <span class="badge bg-<?php echo e(($p['status'] ?? '')===STATUS_FOR_SALE?'primary':'secondary'); ?>"><?php echo e(strtoupper($p['status'] ?? 'N/A')); ?></span>
          </li>
        <?php endforeach; ?>
        </ul>
      </div></div>
    <?php endif; ?>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
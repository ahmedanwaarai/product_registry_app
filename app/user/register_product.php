<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_login();
$user = current_user();

$errors = [];
$name = $_POST['name'] ?? '';
$serial = $_POST['serial'] ?? '';
$category_id = $_POST['category_id'] ?? '';
$brand_id = $_POST['brand_id'] ?? '';
$status = $_POST['status'] ?? STATUS_FOR_SALE;

$categories = Database::fetchAll('SELECT id, name FROM product_categories ORDER BY name');
$brands = Database::fetchAll('SELECT id, name FROM brands ORDER BY name');

// Enforce limits
$limit = $user['user_type'] === ROLE_SHOPKEEPER ? FREE_PRODUCT_LIMIT_SHOPKEEPER : FREE_PRODUCT_LIMIT_USER;
$currentCount = Database::fetchOne('SELECT COUNT(*) as c FROM products WHERE owner_user_id = ?', [$user['id']])['c'] ?? 0;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();

    if (trim($name) === '') { $errors[] = 'Product name is required.'; }
    if (!preg_match('/^[A-Za-z0-9\-]{4,50}$/', $serial)) { $errors[] = 'Serial must be 4-50 chars, alphanumeric or dash.'; }
    if (!$category_id) { $errors[] = 'Category is required.'; }
    if (!$brand_id) { $errors[] = 'Brand is required.'; }
    if (!in_array($status, [STATUS_FOR_SALE, STATUS_LOCKED, STATUS_STOLEN], true)) { $errors[] = 'Invalid status.'; }
    if ((int)$currentCount >= (int)$limit) { $errors[] = 'You have reached your free product limit.'; }

    // Unique serial number
    $exists = Database::fetchOne('SELECT id FROM products WHERE serial = ?', [$serial]);
    if ($exists) { $errors[] = 'Serial number already registered.'; }

    if (!$errors) {
        Database::execute(
            'INSERT INTO products (name, serial, category_id, brand_id, status, owner_user_id, registered_at, last_status_change_at) VALUES (?,?,?,?,?,?,?,?)',
            [$name, $serial, $category_id, $brand_id, $status, $user['id'], now(), now()]
        );
        $productId = Database::lastInsertId();
        Database::execute('INSERT INTO product_status_log (product_id, status, changed_by_user_id, changed_at, note) VALUES (?,?,?,?,?)', [$productId, $status, $user['id'], now(), 'Registered']);
        Database::execute('INSERT INTO product_ownerships (product_id, user_id, acquired_at, method) VALUES (?,?,?,?)', [$productId, $user['id'], now(), 'registration']);
        set_flash('success', 'Product registered successfully.');
        redirect(base_url('user/my_products.php'));
    }
}

require_once __DIR__ . '/../templates/header.php';
?>
<div class="row justify-content-center">
  <div class="col-md-8">
    <div class="card">
      <div class="card-header">Register Product</div>
      <div class="card-body">
        <?php if ($errors): ?><div class="alert alert-danger"><?php echo e(implode('<br>', $errors)); ?></div><?php endif; ?>
        <form method="post">
          <?php echo csrf_field(); ?>
          <div class="mb-3">
            <label class="form-label">Product Name</label>
            <input type="text" name="name" class="form-control" value="<?php echo e($name); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Serial Number</label>
            <input type="text" name="serial" class="form-control" value="<?php echo e($serial); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Category</label>
            <select name="category_id" class="form-select" required>
              <option value="">Select</option>
              <?php foreach ($categories as $c): ?>
                <option value="<?php echo e($c['id']); ?>" <?php echo $category_id==$c['id']?'selected':''; ?>><?php echo e($c['name']); ?></option>
              <?php endforeach; ?>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Brand</label>
            <select name="brand_id" class="form-select" required>
              <option value="">Select</option>
              <?php foreach ($brands as $b): ?>
                <option value="<?php echo e($b['id']); ?>" <?php echo $brand_id==$b['id']?'selected':''; ?>><?php echo e($b['name']); ?></option>
              <?php endforeach; ?>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Status</label>
            <select name="status" class="form-select">
              <option value="<?php echo e(STATUS_FOR_SALE); ?>" <?php echo $status===STATUS_FOR_SALE?'selected':''; ?>>For Sale</option>
              <option value="<?php echo e(STATUS_LOCKED); ?>" <?php echo $status===STATUS_LOCKED?'selected':''; ?>>Locked</option>
              <option value="<?php echo e(STATUS_STOLEN); ?>" <?php echo $status===STATUS_STOLEN?'selected':''; ?>>Stolen</option>
            </select>
          </div>
          <button class="btn btn-primary" type="submit">Register</button>
          <a href="<?php echo e(base_url('public/dashboard.php')); ?>" class="btn btn-link">Back</a>
        </form>
      </div>
    </div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
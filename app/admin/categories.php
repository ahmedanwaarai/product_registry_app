<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_admin(ADMIN_ACCESS_LIMITED);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();
    $name = trim($_POST['name'] ?? '');
    if ($name !== '') {
        Database::execute('INSERT INTO product_categories (name) VALUES (?)', [$name]);
        set_flash('success', 'Category added');
    }
    redirect(base_url('admin/categories.php'));
}
if (isset($_GET['delete'])) {
    $id = (int)$_GET['delete'];
    // Only delete if no products
    $c = Database::fetchOne('SELECT COUNT(*) as c FROM products WHERE category_id = ?', [$id]);
    if (($c['c'] ?? 0) == 0) {
        Database::execute('DELETE FROM product_categories WHERE id = ?', [$id]);
        set_flash('success', 'Category deleted');
    } else {
        set_flash('danger', 'Cannot delete category with products.');
    }
    redirect(base_url('admin/categories.php'));
}
$categories = Database::fetchAll('SELECT * FROM product_categories ORDER BY name');
require_once __DIR__ . '/../templates/header.php';
?>
<h3>Manage Categories</h3>
<div class="row">
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <form method="post">
        <?php echo csrf_field(); ?>
        <div class="input-group">
          <input class="form-control" name="name" placeholder="New category name" required>
          <button class="btn btn-primary" type="submit">Add</button>
        </div>
      </form>
    </div></div>
    <div class="card"><div class="card-body">
      <ul class="list-group">
        <?php foreach ($categories as $cat): ?>
          <li class="list-group-item d-flex justify-content-between align-items-center">
            <span><?php echo e($cat['name']); ?></span>
            <a class="btn btn-sm btn-outline-danger" href="?delete=<?php echo e($cat['id']); ?>" onclick="return confirm('Delete?')">Delete</a>
          </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
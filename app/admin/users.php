<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';

require_admin(ADMIN_ACCESS_FULL);

if (isset($_GET['make_admin'])) {
    $id = (int)$_GET['make_admin'];
    Database::execute('UPDATE users SET user_type = ? WHERE id = ?', [ROLE_ADMIN, $id]);
    Database::execute('INSERT INTO admin_roles (user_id, access_level) VALUES (?, ?) ON DUPLICATE KEY UPDATE access_level = VALUES(access_level)', [$id, ADMIN_ACCESS_LIMITED]);
    set_flash('success', 'User elevated to admin.');
    redirect(base_url('admin/users.php'));
}
if (isset($_GET['remove_admin'])) {
    $id = (int)$_GET['remove_admin'];
    Database::execute('DELETE FROM admin_roles WHERE user_id = ?', [$id]);
    Database::execute('UPDATE users SET user_type = ? WHERE id = ?', [ROLE_USER, $id]);
    set_flash('success', 'Admin demoted to user.');
    redirect(base_url('admin/users.php'));
}

$users = Database::fetchAll('SELECT * FROM users ORDER BY created_at DESC LIMIT 200');
require_once __DIR__ . '/../templates/header.php';
?>
<h3>Manage Users</h3>
<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Email</th><th>Mobile</th><th>Type</th><th>Shop</th><th>Status</th><th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <?php foreach ($users as $u): ?>
      <tr>
        <td><?php echo e($u['id']); ?></td>
        <td><?php echo e($u['username']); ?></td>
        <td><?php echo e($u['email']); ?></td>
        <td><?php echo e($u['mobile']); ?></td>
        <td><?php echo e($u['user_type']); ?></td>
        <td><?php echo e($u['shop_name']); ?></td>
        <td><?php echo e($u['shopkeeper_status']); ?></td>
        <td>
          <?php if ($u['user_type'] !== ROLE_ADMIN): ?>
            <a class="btn btn-sm btn-outline-primary" href="?make_admin=<?php echo e($u['id']); ?>">Make Admin</a>
          <?php else: ?>
            <a class="btn btn-sm btn-outline-danger" href="?remove_admin=<?php echo e($u['id']); ?>">Remove Admin</a>
          <?php endif; ?>
        </td>
      </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
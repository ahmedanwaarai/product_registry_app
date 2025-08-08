<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/auth.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/csrf.php';

require_admin(ADMIN_ACCESS_FULL);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();
    $user_id = (int)($_POST['user_id'] ?? 0);
    $level = $_POST['level'] ?? ADMIN_ACCESS_LIMITED;
    if (in_array($level, [ADMIN_ACCESS_FULL, ADMIN_ACCESS_LIMITED], true)) {
        Database::execute('INSERT INTO admin_roles (user_id, access_level) VALUES (?, ?) ON DUPLICATE KEY UPDATE access_level = VALUES(access_level)', [$user_id, $level]);
        Database::execute('UPDATE users SET user_type = ? WHERE id = ?', [ROLE_ADMIN, $user_id]);
        set_flash('success', 'Role saved.');
    }
    redirect(base_url('admin/roles.php'));
}

$admins = Database::fetchAll('SELECT u.id, u.username, u.email, COALESCE(r.access_level, ?) AS access_level FROM users u LEFT JOIN admin_roles r ON r.user_id = u.id WHERE u.user_type = ? ORDER BY u.username', [ADMIN_ACCESS_LIMITED, ROLE_ADMIN]);
$users = Database::fetchAll('SELECT id, username FROM users WHERE user_type <> ? ORDER BY username', [ROLE_ADMIN]);

require_once __DIR__ . '/../templates/header.php';
?>
<h3>Admin Roles</h3>
<div class="row">
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Existing Admins</h5>
      <ul class="list-group">
        <?php foreach ($admins as $a): ?>
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <div><?php echo e($a['username']); ?> (<?php echo e($a['email']); ?>)</div>
            <div class="text-muted small">Access: <?php echo e($a['access_level']); ?></div>
          </div>
        </li>
        <?php endforeach; ?>
      </ul>
    </div></div>
  </div>
  <div class="col-md-6">
    <div class="card mb-3"><div class="card-body">
      <h5>Add/Update Admin</h5>
      <form method="post">
        <?php echo csrf_field(); ?>
        <div class="mb-2">
          <label class="form-label">Select User</label>
          <select class="form-select" name="user_id" required>
            <?php foreach ($users as $u): ?>
              <option value="<?php echo e($u['id']); ?>"><?php echo e($u['username']); ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="mb-2">
          <label class="form-label">Access Level</label>
          <select class="form-select" name="level">
            <option value="<?php echo e(ADMIN_ACCESS_LIMITED); ?>">Limited</option>
            <option value="<?php echo e(ADMIN_ACCESS_FULL); ?>">Full</option>
          </select>
        </div>
        <button class="btn btn-primary" type="submit">Save</button>
      </form>
    </div></div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
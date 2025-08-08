<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/csrf.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/auth.php';

if (is_logged_in()) { redirect(base_url('public/dashboard.php')); }

$errors = [];
$email_or_mobile = $_POST['email_or_mobile'] ?? '';
$password = $_POST['password'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();
    if ($email_or_mobile === '' || $password === '') {
        $errors[] = 'Email/Mobile and password are required.';
    } else {
        $user = Database::fetchOne('SELECT * FROM users WHERE email = ? OR mobile = ? LIMIT 1', [$email_or_mobile, $email_or_mobile]);
        if (!$user || !password_verify($password, $user['password_hash'])) {
            $errors[] = 'Invalid credentials.';
        } else {
            $_SESSION['user_id'] = $user['id'];
            set_flash('success', 'Welcome back, ' . e($user['username']) . '!');
            redirect(base_url('public/dashboard.php'));
        }
    }
}

require_once __DIR__ . '/../templates/header.php';
?>
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-4">
    <div class="card">
      <div class="card-header">Login</div>
      <div class="card-body">
        <?php if ($errors): ?><div class="alert alert-danger"><?php echo e(implode('<br>', $errors)); ?></div><?php endif; ?>
        <form method="post" action="">
          <?php echo csrf_field(); ?>
          <div class="mb-3">
            <label class="form-label">Email or Mobile</label>
            <input type="text" name="email_or_mobile" class="form-control" value="<?php echo e($email_or_mobile); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input type="password" name="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary w-100">Login</button>
          <a href="<?php echo e(base_url('public/register.php')); ?>" class="btn btn-link w-100 mt-2">Create an account</a>
        </form>
      </div>
    </div>
  </div>
</div>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
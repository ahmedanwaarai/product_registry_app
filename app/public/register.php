<?php
require_once __DIR__ . '/../inc/config.php';
require_once __DIR__ . '/../inc/db.php';
require_once __DIR__ . '/../inc/csrf.php';
require_once __DIR__ . '/../inc/util.php';
require_once __DIR__ . '/../inc/auth.php';

if (is_logged_in()) { redirect(base_url('public/dashboard.php')); }

$errors = [];
$username = $_POST['username'] ?? '';
$email = $_POST['email'] ?? '';
$mobile = $_POST['mobile'] ?? '';
$password = $_POST['password'] ?? '';
$confirm_password = $_POST['confirm_password'] ?? '';
$cnic = random_cnic();
$account_type = $_POST['account_type'] ?? ROLE_USER;
$shop_name = $_POST['shop_name'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf_or_die();

    // Validation
    if (trim($username) === '') { $errors[] = 'Username is required.'; }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) { $errors[] = 'Valid email is required.'; }
    if (!preg_match('/^[0-9]{10,15}$/', $mobile)) { $errors[] = 'Valid mobile number is required (10-15 digits).'; }
    if (strlen($password) < 6) { $errors[] = 'Password must be at least 6 characters.'; }
    if ($password !== $confirm_password) { $errors[] = 'Passwords do not match.'; }
    if (!in_array($account_type, [ROLE_USER, ROLE_SHOPKEEPER], true)) { $errors[] = 'Invalid account type.'; }
    if ($account_type === ROLE_SHOPKEEPER && trim($shop_name) === '') { $errors[] = 'Shop name is required for shopkeepers.'; }

    // Uniqueness
    $exists = Database::fetchOne('SELECT id FROM users WHERE email = ? OR mobile = ?', [$email, $mobile]);
    if ($exists) { $errors[] = 'Email or mobile already exists.'; }

    if (!$errors) {
        $password_hash = password_hash($password, PASSWORD_BCRYPT);
        $shopStatus = ($account_type === ROLE_SHOPKEEPER) ? SHOPKEEPER_PENDING : SHOPKEEPER_APPROVED;
        Database::execute(
            'INSERT INTO users (username, email, mobile, password_hash, cnic, user_type, shop_name, shopkeeper_status, created_at) VALUES (?,?,?,?,?,?,?,?,?)',
            [$username, $email, $mobile, $password_hash, $cnic, $account_type, $shop_name, $shopStatus, now()]
        );
        set_flash('success', 'Registration successful. ' . ($account_type === ROLE_SHOPKEEPER ? 'Await admin approval to activate your shopkeeper account.' : 'You can login now.'));
        redirect(base_url('public/login.php'));
    }
}

require_once __DIR__ . '/../templates/header.php';
?>
<div class="row justify-content-center">
  <div class="col-md-8 col-lg-6">
    <div class="card">
      <div class="card-header">Register</div>
      <div class="card-body">
        <?php if ($errors): ?><div class="alert alert-danger"><?php echo e(implode('<br>', $errors)); ?></div><?php endif; ?>
        <form method="post" action="">
          <?php echo csrf_field(); ?>

          <div class="mb-3">
            <label class="form-label">Username</label>
            <input type="text" name="username" class="form-control" value="<?php echo e($username); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" name="email" class="form-control" value="<?php echo e($email); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Mobile Number</label>
            <input type="text" name="mobile" class="form-control" value="<?php echo e($mobile); ?>" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input type="password" name="password" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Confirm Password</label>
            <input type="password" name="confirm_password" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">ID Card Number (Auto-generated)</label>
            <input type="text" class="form-control" value="<?php echo e($cnic); ?>" readonly>
          </div>
          <div class="mb-3">
            <label class="form-label">Account Type</label>
            <select name="account_type" id="account_type" class="form-select" required>
              <option value="<?php echo e(ROLE_USER); ?>" <?php echo $account_type===ROLE_USER?'selected':''; ?>>User</option>
              <option value="<?php echo e(ROLE_SHOPKEEPER); ?>" <?php echo $account_type===ROLE_SHOPKEEPER?'selected':''; ?>>Shopkeeper</option>
            </select>
          </div>
          <div class="mb-3" id="shop_name_group" style="display: none;">
            <label class="form-label">Shop Name</label>
            <input type="text" name="shop_name" id="shop_name" class="form-control" value="<?php echo e($shop_name); ?>">
          </div>

          <button type="submit" class="btn btn-primary">Create Account</button>
          <a href="<?php echo e(base_url('public/login.php')); ?>" class="btn btn-link">Already have an account? Login</a>
        </form>
      </div>
    </div>
  </div>
</div>
<script>
  const accountType = document.getElementById('account_type');
  const shopGroup = document.getElementById('shop_name_group');
  function toggleShop() {
    shopGroup.style.display = accountType.value === '<?php echo e(ROLE_SHOPKEEPER); ?>' ? 'block' : 'none';
    document.getElementById('shop_name').required = accountType.value === '<?php echo e(ROLE_SHOPKEEPER); ?>';
  }
  accountType.addEventListener('change', toggleShop);
  toggleShop();
</script>
<?php require_once __DIR__ . '/../templates/footer.php'; ?>
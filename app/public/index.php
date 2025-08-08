<?php require_once __DIR__ . '/../templates/header.php'; ?>

<?php $page = $_GET['page'] ?? 'home'; ?>

<?php if ($page === 'home'): ?>
  <div class="p-5 mb-4 bg-light rounded-3">
    <div class="container py-5">
      <h1 class="display-5 fw-bold">Secure Product Registration & Ownership Transfer</h1>
      <p class="col-md-8 fs-4">Register products, verify ownership, and transfer securely. Prevent unauthorized resale and fraud.</p>
      <a href="<?php echo e(base_url('public/register.php')); ?>" class="btn btn-primary btn-lg">Register Now</a>
      <a href="<?php echo e(base_url('public/login.php')); ?>" class="btn btn-outline-secondary btn-lg ms-2">Login</a>
      <a href="<?php echo e(base_url('user/verify.php')); ?>" class="btn btn-link btn-lg ms-2">Verify Product</a>
    </div>
  </div>
  <div class="row">
    <div class="col-md-4">
      <div class="card mb-3"><div class="card-body">
        <h5>Track Ownership</h5>
        <p>End-to-end visibility for every product including registration, deals, and admin actions.</p>
      </div></div>
    </div>
    <div class="col-md-4">
      <div class="card mb-3"><div class="card-body">
        <h5>Anti-Theft Protection</h5>
        <p>Mark products Locked or Stolen. Prevent them from being sold until resolved.</p>
      </div></div>
    </div>
    <div class="col-md-4">
      <div class="card mb-3"><div class="card-body">
        <h5>Deal Verification</h5>
        <p>Admin-verified ownership transfer to protect buyers and sellers.</p>
      </div></div>
    </div>
  </div>
<?php elseif ($page === 'about'): ?>
  <h2>About</h2>
  <p>This platform helps prevent unauthorized resale and ensures transparent product ownership history.</p>
<?php elseif ($page === 'services'): ?>
  <h2>Services</h2>
  <ul>
    <li>Product Registration</li>
    <li>Ownership Transfer via Deals</li>
    <li>Admin Verification & History Logs</li>
  </ul>
<?php elseif ($page === 'contact'): ?>
  <h2>Contact</h2>
  <p>For support, contact admin after login or email support@example.com.</p>
<?php elseif ($page === 'terms'): ?>
  <h2>Terms and Conditions</h2>
  <p>Use this system responsibly. Admin decisions are final for disputes and fraud prevention.</p>
<?php endif; ?>

<?php require_once __DIR__ . '/../templates/footer.php'; ?>
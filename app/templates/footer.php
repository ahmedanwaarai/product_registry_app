  </div> <!-- /container -->
  <footer class="bg-light border-top mt-auto py-3">
    <div class="container">
      <div class="d-flex justify-content-between">
        <span class="text-muted">&copy; <?php echo date('Y'); ?> Secure Product Registration System</span>
        <span>
          <a href="<?php echo e(base_url('public/index.php?page=terms')); ?>" class="text-muted me-3">Terms</a>
          <a href="<?php echo e(base_url('public/index.php?page=contact')); ?>" class="text-muted">Contact</a>
        </span>
      </div>
    </div>
  </footer>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="<?php echo e(ASSETS_URL); ?>js/app.js"></script>
</body>
</html>
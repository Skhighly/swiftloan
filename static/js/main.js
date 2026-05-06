/* SwiftLoan — Main JS */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss alerts after 5 seconds ──────────────────────────────────
  setTimeout(function () {
    document.querySelectorAll('.sl-alert').forEach(function (el) {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, 5000);

  // ── ID upload: click-to-browse + drag-and-drop + preview ─────────────────
  document.querySelectorAll('.id-upload-box').forEach(function (box) {
    var input   = box.querySelector('input[type=file]');
    var preview = box.querySelector('.upload-preview');
    var label   = box.querySelector('.upload-label');
    if (!input) return;

    box.addEventListener('click', function (e) {
      if (e.target !== input) input.click();
    });

    input.addEventListener('change', function () {
      if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
          if (preview) {
            preview.src = e.target.result;
            preview.style.display = 'block';
          }
          if (label) {
            var span = label.querySelector('span');
            if (span) span.textContent = input.files[0].name;
          }
        };
        reader.readAsDataURL(input.files[0]);
      }
    });

    box.addEventListener('dragover',  function (e) { e.preventDefault(); box.classList.add('dragging'); });
    box.addEventListener('dragleave', function ()  { box.classList.remove('dragging'); });
    box.addEventListener('drop', function (e) {
      e.preventDefault();
      box.classList.remove('dragging');
      if (e.dataTransfer.files[0]) {
        var dt = e.dataTransfer;
        // Assign files via DataTransfer if supported
        try { input.files = dt.files; } catch (_) {}
        input.dispatchEvent(new Event('change'));
      }
    });
  });

  // ── Loan amount selection: live deposit preview ───────────────────────────
  document.querySelectorAll('.loan-amount-radio').forEach(function (radio) {
    radio.addEventListener('change', function () {
      var amount          = parseInt(this.value);
      var depositDisplay  = document.getElementById('deposit-display');
      var depositAmount   = document.getElementById('deposit-amount');
      var totalAmount     = document.getElementById('total-amount');

      if (depositDisplay) depositDisplay.style.display = 'block';
      if (depositAmount)  depositAmount.textContent  = 'KES ' + (amount * 0.1).toLocaleString();
      if (totalAmount)    totalAmount.textContent    = 'KES ' + amount.toLocaleString();
    });
  });

  // ── Payment status polling on the awaiting page ───────────────────────────
  var statusUrlEl = document.getElementById('payment-status-url');
  if (statusUrlEl) {
    var url        = statusUrlEl.dataset.url;
    var statusMsg  = document.getElementById('payment-status-msg');
    var pollCount  = 0;
    var maxPolls   = 60; // stop after 4 minutes (60 × 4s)

    var interval = setInterval(function () {
      pollCount++;
      if (pollCount > maxPolls) {
        clearInterval(interval);
        if (statusMsg) statusMsg.textContent = 'Timed out. Please refresh the page.';
        return;
      }

      fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.status === 'completed') {
            clearInterval(interval);
            window.location.reload();
          } else if (data.status === 'failed') {
            clearInterval(interval);
            if (statusMsg) statusMsg.textContent = 'Payment failed. Please try again.';
          }
        })
        .catch(function () {
          // Silently ignore network errors during polling
        });
    }, 4000);
  }

  // ── Job info page: live qualification preview ─────────────────────────────
  var incomeInput = document.querySelector('input[name="monthly_income"]');
  var qualPreview = document.getElementById('qual-preview');
  var qualDisplay = document.getElementById('qual-amount-display');

  var tiers = [
    [50000, 20000],
    [25000, 10000],
    [10000,  5000],
    [0,      3000],
  ];

  if (incomeInput) {
    incomeInput.addEventListener('input', function () {
      var income    = parseFloat(this.value) || 0;
      var qualified = 3000;
      for (var i = 0; i < tiers.length; i++) {
        if (income >= tiers[i][0]) { qualified = tiers[i][1]; break; }
      }
      if (qualPreview) qualPreview.style.display = 'block';
      if (qualDisplay) qualDisplay.textContent = 'KES ' + qualified.toLocaleString();
    });
  }

});

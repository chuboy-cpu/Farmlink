// Show / hide password
document.querySelectorAll('[data-toggle-pw]').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.querySelector(btn.dataset.togglePw);
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.querySelector('i').className = show ? 'bi bi-eye-slash' : 'bi bi-eye';
  });
});

// Live estimate on the new-listing form
const qty = document.getElementById('qty'), price = document.getElementById('price'),
      est = document.getElementById('estimate');
function updateEstimate() {
  if (!est) return;
  const v = (parseInt(qty.value) || 0) * (parseInt(price.value) || 0);
  est.textContent = '₦' + v.toLocaleString('en-NG');
}
if (qty && price) { qty.addEventListener('input', updateEstimate); price.addEventListener('input', updateEstimate); }

// Live payout on the sign-off form
document.querySelectorAll('[data-weigh]').forEach(input => {
  input.addEventListener('input', () => {
    const out = document.getElementById(input.dataset.weigh);
    out.textContent = '₦' + ((parseInt(input.value) || 0) * parseInt(input.dataset.rate)).toLocaleString('en-NG');
  });
});

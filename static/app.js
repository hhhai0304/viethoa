/* Shared page interactions. No dependencies. */
(function () {
  "use strict";

  const theme = document.querySelector('.theme select');
  theme.value = document.documentElement.dataset.theme || 'auto';
  theme.parentElement.hidden = false;
  theme.addEventListener('change', () => {
    document.documentElement.dataset.theme = theme.value;
    try { localStorage.setItem('viethoa-theme', theme.value); } catch { /* Storage is optional. */ }
  });

  document.querySelectorAll(".tabs").forEach(function (box) {
    var buttons = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) {
          var pane = document.getElementById(b.getAttribute("aria-controls"));
          var on = b === btn;
          b.setAttribute("aria-selected", on ? "true" : "false");
          if (pane) pane.hidden = !on;
        });
      });
    });
  });

  var dlg = document.getElementById("moi-cafe");
  if (dlg) {
    document.querySelectorAll("[data-open=moi-cafe]").forEach(function (b) {
      b.addEventListener("click", function () { dlg.showModal(); });
    });
    var close = dlg.querySelector(".close");
    if (close) close.addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelectorAll("button.copy").forEach(function (b) {
      b.addEventListener("click", async function () {
        const status = dlg.querySelector('.copy-status');
        try {
          await navigator.clipboard.writeText(b.dataset.copy);
          status.textContent = b.getAttribute('aria-label').replace('Chép', 'Đã chép') + '.';
        } catch {
          status.textContent = 'Không thể chép tự động. Hãy chọn và sao chép dòng bên trên.';
        }
      });
    });
    if (location.hash === "#moi-cafe") dlg.showModal();
  }
})();

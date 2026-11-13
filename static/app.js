/* Tabs, donate dialog, copy buttons. No dependencies. */
(function () {
  "use strict";

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
      b.addEventListener("click", function () {
        navigator.clipboard.writeText(b.dataset.copy).then(function () {
          var old = b.textContent;
          b.textContent = "Đã chép";
          setTimeout(function () { b.textContent = old; }, 1500);
        });
      });
    });
    if (location.hash === "#moi-cafe") dlg.showModal();
  }
})();

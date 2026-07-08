document.addEventListener('DOMContentLoaded', function () {

    var spinner = document.getElementById('loadingSpinner');

    function showSpinner() {
        if (spinner) spinner.classList.add('show');
    }

    document.querySelectorAll('a:not([data-bs-toggle]):not([data-no-spinner])').forEach(function (link) {
        link.addEventListener('click', function (e) {
            var href = this.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript:') && !href.startsWith('tel:') && !href.startsWith('mailto:')) {
                showSpinner();
            }
        });
    });

    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            showSpinner();
        });
    });

    document.querySelectorAll('.toast').forEach(function (toastEl) {
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    });

    var tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length) {
        [...tooltipTriggerList].map(function (el) { return new bootstrap.Tooltip(el); });
    }

    var qtyInputs = document.querySelectorAll('.input-group input[type="number"]');
    qtyInputs.forEach(function (input) {
        if (input.closest('.qty-update-form')) return;
        var parent = input.closest('.input-group');
        if (!parent) return;
        var decBtn = parent.querySelector('button:first-child');
        var incBtn = parent.querySelector('button:last-child');
        var max = parseInt(input.max) || 999;
        if (decBtn) {
            decBtn.addEventListener('click', function () {
                var val = parseInt(input.value) || 1;
                if (val > 1) input.value = val - 1;
                input.dispatchEvent(new Event('change'));
            });
        }
        if (incBtn) {
            incBtn.addEventListener('click', function () {
                var val = parseInt(input.value) || 1;
                if (val < max) input.value = val + 1;
                input.dispatchEvent(new Event('change'));
            });
        }
    });

    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrfToken = getCookie('csrftoken');

    document.querySelectorAll('.product-card[data-href]').forEach(function (card) {
        card.addEventListener('click', function (e) {
            if (e.target.closest('a') || e.target.closest('button')) return;
            var href = this.getAttribute('data-href');
            if (href && href !== '#') {
                showSpinner();
                window.location.href = href;
            }
        });
    });

    document.querySelectorAll('.gallery-thumb').forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            var src = this.getAttribute('data-src');
            var mainImage = document.getElementById('mainImage');
            if (src && mainImage) {
                mainImage.src = src;
                document.querySelectorAll('.gallery-thumb').forEach(function (t) {
                    t.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });

    document.querySelectorAll('.wishlist-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            var form = this.closest('form');
            if (form) return;

            e.preventDefault();
            var productId = this.getAttribute('data-product-id');
            if (!productId) {
                var card = this.closest('[data-product-id]');
                if (card) productId = card.getAttribute('data-product-id');
            }
            if (!productId) return;

            var icon = this.querySelector('i');

            if (!csrfToken) {
                window.location.href = '/accounts/login/';
                return;
            }

            fetch('/accounts/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: 'product_id=' + productId,
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status === 'added') {
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                    btn.style.background = '#dc3545';
                    btn.style.color = '#fff';
                } else {
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                    btn.style.background = '';
                    btn.style.color = '';
                }
                var badge = document.querySelector('.wishlist-count');
                if (badge) badge.textContent = data.count;
            })
            .catch(function () {
                window.location.reload();
            });
        });
    });

});

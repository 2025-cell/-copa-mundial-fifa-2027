// Auto-ocultar alertas después de unos segundos
document.addEventListener("DOMContentLoaded", function () {
    const alertas = document.querySelectorAll(".alerta");
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            alerta.style.transition = "opacity 0.5s";
            alerta.style.opacity = "0";
            setTimeout(function () { alerta.remove(); }, 500);
        }, 4000);
    });
});

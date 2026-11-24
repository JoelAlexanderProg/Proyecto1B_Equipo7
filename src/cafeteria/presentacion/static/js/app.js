// Mejoras progresivas de CaféPoli. La aplicación funciona sin JavaScript: el servidor
// valida y calcula todo. Aquí solo se actualiza el total en vivo, se manejan los botones
// de cantidad y se recargan las pantallas de seguimiento.
(function () {
  "use strict";

  function formatearDinero(centavos) {
    return "$" + (centavos / 100).toFixed(2).replace(".", ",");
  }

  function actualizarCarrito(formulario) {
    let centavos = 0;
    let articulos = 0;
    formulario.querySelectorAll(".cantidad").forEach(function (caja) {
      const cantidad = Math.max(0, Number.parseInt(caja.querySelector("input").value, 10) || 0);
      articulos += cantidad;
      centavos += cantidad * Math.round(Number.parseFloat(caja.dataset.precio) * 100);
    });
    const total = document.getElementById("carrito-total");
    const resumen = document.getElementById("carrito-articulos");
    if (total) total.textContent = formatearDinero(centavos);
    if (resumen) resumen.textContent = articulos === 1 ? "1 artículo" : articulos + " artículos";
  }

  const formulario = document.getElementById("form-pedido");
  if (formulario) {
    const maximo = Number.parseInt(formulario.dataset.maximo, 10) || 20;
    formulario.addEventListener("click", function (evento) {
      const boton = evento.target.closest(".paso");
      if (!boton) return;
      const entrada = boton.parentElement.querySelector("input");
      const valor = (Number.parseInt(entrada.value, 10) || 0) + Number.parseInt(boton.dataset.paso, 10);
      entrada.value = Math.min(maximo, Math.max(0, valor));
      actualizarCarrito(formulario);
    });
    formulario.addEventListener("input", function () {
      actualizarCarrito(formulario);
    });
    actualizarCarrito(formulario);
  }

  // Recarga periódica sin interrumpir a quien está escribiendo un código.
  const segundos = Number.parseInt(document.body.dataset.recargar, 10);
  if (segundos > 0) {
    setInterval(function () {
      const activo = document.activeElement;
      const escribiendo = activo && activo.matches("input, select, textarea");
      const conTexto = Array.prototype.some.call(
        document.querySelectorAll("input[type=text]"),
        function (entrada) { return entrada.value !== ""; }
      );
      if (!escribiendo && !conTexto && document.visibilityState === "visible") {
        window.location.reload();
      }
    }, segundos * 1000);
  }
})();

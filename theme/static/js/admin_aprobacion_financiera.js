/**
 * Admin Aprobación Financiera - Lógica condicional para campos
 *
 * - Fecha de Pago: Solo disponible cuando estado_financiero = "PAGADA"
 * - Validación en tiempo real del número de factura
 */
(function () {
  "use strict";

  function init() {
    const estadoSelect = document.querySelector("#id_estado_financiero");
    const fechaPagoInput = document.querySelector("#id_fecha_pago");
    const numeroFacturaInput = document.querySelector("#id_numero_factura");

    if (!estadoSelect) {
      console.log(
        "[AprobacionFinanciera] Select estado_financiero no encontrado"
      );
      return;
    }

    console.log("[AprobacionFinanciera] Iniciando lógica condicional");

    // Función para actualizar estado de fecha_pago
    function updateFechaPago() {
      const estado = estadoSelect.value;
      const fechaPagoRow = document.querySelector(".field-fecha_pago");

      if (estado === "PAGADA") {
        // Habilitar fecha de pago
        if (fechaPagoInput) {
          fechaPagoInput.disabled = false;
          fechaPagoInput.style.backgroundColor = "";
        }
        if (fechaPagoRow) {
          fechaPagoRow.style.opacity = "1";
          const label = fechaPagoRow.querySelector("label");
          if (label && !label.innerHTML.includes("*")) {
            label.innerHTML =
              label.innerHTML.replace(":", "") +
              ' <span style="color: red;">*</span>:';
          }
        }
      } else {
        // Deshabilitar y limpiar fecha de pago
        if (fechaPagoInput) {
          fechaPagoInput.disabled = true;
          fechaPagoInput.value = "";
          fechaPagoInput.style.backgroundColor = "#f0f0f0";
        }
        if (fechaPagoRow) {
          fechaPagoRow.style.opacity = "0.5";
          const label = fechaPagoRow.querySelector("label");
          if (label) {
            label.innerHTML = label.innerHTML
              .replace(/<span style="color: red;">\*<\/span>/g, "")
              .replace(/\s+:/g, ":");
            if (!label.innerHTML.endsWith(":")) {
              label.innerHTML = label.innerHTML.trim() + ":";
            }
          }
        }
      }

      // Mostrar mensaje según estado
      updateEstadoMessage(estado);
    }

    function updateEstadoMessage(estado) {
      const estadoRow = document.querySelector(".field-estado_financiero");
      if (!estadoRow) return;

      // Remover mensaje anterior si existe
      const oldMessage = estadoRow.querySelector(".estado-help-message");
      if (oldMessage) {
        oldMessage.remove();
      }

      const mensajes = {
        PENDIENTE:
          '<div class="estado-help-message" style="margin-top: 5px; padding: 8px; background: #fff3cd; border-radius: 4px; color: #856404;">' +
          "⚠️ <strong>Pendiente:</strong> El Gate Pass está BLOQUEADO hasta que se pague o apruebe crédito.</div>",
        PAGADA:
          '<div class="estado-help-message" style="margin-top: 5px; padding: 8px; background: #d4edda; border-radius: 4px; color: #155724;">' +
          "✅ <strong>Pagada:</strong> El Gate Pass está LIBERADO. Debe especificar la fecha de pago.</div>",
        CREDITO:
          '<div class="estado-help-message" style="margin-top: 5px; padding: 8px; background: #cce5ff; border-radius: 4px; color: #004085;">' +
          "💳 <strong>Crédito Aprobado:</strong> El Gate Pass está LIBERADO. Cliente con línea de crédito.</div>",
        ANULADA:
          '<div class="estado-help-message" style="margin-top: 5px; padding: 8px; background: #f8d7da; border-radius: 4px; color: #721c24;">' +
          "❌ <strong>Anulada:</strong> Factura inválida. No se considera para el proceso.</div>",
      };

      if (mensajes[estado]) {
        estadoRow.insertAdjacentHTML("beforeend", mensajes[estado]);
      }
    }

    // Escuchar cambios en el estado
    estadoSelect.addEventListener("change", updateFechaPago);

    // Ejecutar al cargar
    updateFechaPago();

    // === Validación del Número de Factura en tiempo real ===
    if (numeroFacturaInput) {
      numeroFacturaInput.addEventListener("input", function (e) {
        let value = e.target.value.trim().toUpperCase();
        e.target.value = value;

        const patron = /^[FB]\d{3}-\d{8}$/;

        if (value.length > 0) {
          if (patron.test(value)) {
            e.target.style.borderColor = "#28a745";
            e.target.style.boxShadow = "0 0 0 2px rgba(40, 167, 69, 0.25)";
          } else {
            e.target.style.borderColor = "#dc3545";
            e.target.style.boxShadow = "0 0 0 2px rgba(220, 53, 69, 0.25)";
          }
        } else {
          e.target.style.borderColor = "";
          e.target.style.boxShadow = "";
        }
      });

      // Auto-formateo: insertar guión después del 4to carácter
      numeroFacturaInput.addEventListener("keyup", function (e) {
        if (e.key === "Backspace" || e.key === "Delete" || e.ctrlKey) {
          return;
        }

        let value = e.target.value.toUpperCase();
        // Remover caracteres no válidos
        value = value.replace(/[^FB0-9-]/g, "");

        // Auto-insertar guión después de F001 o B001
        if (value.length === 4 && !value.includes("-")) {
          value = value + "-";
        }

        // Limitar longitud total
        if (value.length > 13) {
          value = value.substring(0, 13);
        }

        e.target.value = value;
      });
    }
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 300);
  }
})();

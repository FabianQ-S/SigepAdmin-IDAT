/**
 * Admin Aprobación Aduanera - Lógica condicional para campos
 *
 * Cuando el checkbox "Aprobado" está marcado:
 *   - Fecha de Levante: OBLIGATORIO (se habilita)
 *   - Documento Adjunto: OBLIGATORIO
 *   - Observaciones: Opcional
 *
 * Cuando el checkbox "Aprobado" está desmarcado:
 *   - Fecha de Levante: Se deshabilita y limpia
 *   - Observaciones: OBLIGATORIO
 */
(function () {
  "use strict";

  function init() {
    const aprobadoCheckbox = document.querySelector("#id_aprobado");
    const fechaLevanteInput = document.querySelector("#id_fecha_levante_0");
    const fechaLevanteTimeInput = document.querySelector("#id_fecha_levante_1");
    const observacionesInput = document.querySelector("#id_observaciones");
    const documentoInput = document.querySelector("#id_documento_adjunto");

    if (!aprobadoCheckbox) {
      console.log("[AprobacionAduanera] Checkbox aprobado no encontrado");
      return;
    }

    console.log("[AprobacionAduanera] Iniciando lógica condicional");

    // Función para actualizar el estado de los campos
    function updateFieldStates() {
      const isAprobado = aprobadoCheckbox.checked;

      // Encontrar las filas de los campos para agregar indicadores visuales
      const fechaLevanteRow = document.querySelector(".field-fecha_levante");
      const observacionesRow = document.querySelector(".field-observaciones");
      const documentoRow = document.querySelector(".field-documento_adjunto");

      if (isAprobado) {
        // === APROBADO ===
        console.log("[AprobacionAduanera] Estado: APROBADO");

        // Habilitar fecha de levante
        if (fechaLevanteInput) {
          fechaLevanteInput.disabled = false;
          fechaLevanteInput.style.backgroundColor = "";
        }
        if (fechaLevanteTimeInput) {
          fechaLevanteTimeInput.disabled = false;
          fechaLevanteTimeInput.style.backgroundColor = "";
        }

        // Marcar fecha de levante como obligatorio visualmente
        if (fechaLevanteRow) {
          const label = fechaLevanteRow.querySelector("label");
          if (label && !label.innerHTML.includes("*")) {
            label.innerHTML =
              label.innerHTML.replace(":", "") +
              ' <span style="color: red;">*</span>:';
          }
          fechaLevanteRow.style.opacity = "1";
        }

        // Marcar documento como obligatorio visualmente
        if (documentoRow) {
          const label = documentoRow.querySelector("label");
          if (label && !label.innerHTML.includes("*")) {
            label.innerHTML =
              label.innerHTML.replace(":", "") +
              ' <span style="color: red;">*</span>:';
          }
        }

        // Quitar obligatorio de observaciones
        if (observacionesRow) {
          const label = observacionesRow.querySelector("label");
          if (label) {
            label.innerHTML = label.innerHTML
              .replace(/<span style="color: red;">\*<\/span>/g, "")
              .replace(/\s+:/g, ":");
            if (!label.innerHTML.endsWith(":")) {
              label.innerHTML = label.innerHTML.trim() + ":";
            }
          }
        }
      } else {
        // === NO APROBADO (Pendiente/Rechazado) ===
        console.log("[AprobacionAduanera] Estado: PENDIENTE/RECHAZADO");

        // Deshabilitar y limpiar fecha de levante
        if (fechaLevanteInput) {
          fechaLevanteInput.disabled = true;
          fechaLevanteInput.value = "";
          fechaLevanteInput.style.backgroundColor = "#f0f0f0";
        }
        if (fechaLevanteTimeInput) {
          fechaLevanteTimeInput.disabled = true;
          fechaLevanteTimeInput.value = "";
          fechaLevanteTimeInput.style.backgroundColor = "#f0f0f0";
        }

        // Quitar obligatorio de fecha de levante visualmente
        if (fechaLevanteRow) {
          const label = fechaLevanteRow.querySelector("label");
          if (label) {
            label.innerHTML = label.innerHTML
              .replace(/<span style="color: red;">\*<\/span>/g, "")
              .replace(/\s+:/g, ":");
            if (!label.innerHTML.endsWith(":")) {
              label.innerHTML = label.innerHTML.trim() + ":";
            }
          }
          fechaLevanteRow.style.opacity = "0.6";
        }

        // Quitar obligatorio de documento visualmente
        if (documentoRow) {
          const label = documentoRow.querySelector("label");
          if (label) {
            label.innerHTML = label.innerHTML
              .replace(/<span style="color: red;">\*<\/span>/g, "")
              .replace(/\s+:/g, ":");
            if (!label.innerHTML.endsWith(":")) {
              label.innerHTML = label.innerHTML.trim() + ":";
            }
          }
        }

        // Marcar observaciones como obligatorio
        if (observacionesRow) {
          const label = observacionesRow.querySelector("label");
          if (label && !label.innerHTML.includes("*")) {
            label.innerHTML =
              label.innerHTML.replace(":", "") +
              ' <span style="color: red;">*</span>:';
          }
        }
      }
    }

    // Escuchar cambios en el checkbox
    aprobadoCheckbox.addEventListener("change", updateFieldStates);

    // Ejecutar al cargar la página
    updateFieldStates();

    // === Validación del Número de Despacho en tiempo real ===
    const numeroDespachoInput = document.querySelector("#id_numero_despacho");
    if (numeroDespachoInput) {
      numeroDespachoInput.addEventListener("input", function (e) {
        const value = e.target.value.trim();
        const patron = /^\d{3}-\d{4}-\d{2}-\d{6}(-\d{2})?$/;

        // Remover clases previas
        e.target.classList.remove("is-valid", "is-invalid");

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

      // Formateo automático: insertar guiones mientras escribe
      numeroDespachoInput.addEventListener("keyup", function (e) {
        // Solo formatear si no es tecla de borrar o control
        if (e.key === "Backspace" || e.key === "Delete" || e.ctrlKey) {
          return;
        }

        let value = e.target.value.replace(/[^0-9-]/g, ""); // Solo números y guiones
        let digits = value.replace(/-/g, ""); // Solo números

        // Auto-insertar guiones en las posiciones correctas
        let formatted = "";
        for (let i = 0; i < digits.length && i < 20; i++) {
          if (i === 3 || i === 7 || i === 9 || i === 15) {
            formatted += "-";
          }
          formatted += digits[i];
        }

        if (formatted !== value) {
          e.target.value = formatted;
        }
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

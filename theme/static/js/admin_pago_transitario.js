/**
 * Admin Pago Transitario - Auto-completar transitario desde contenedor
 *
 * Cuando se selecciona un contenedor, automáticamente muestra el transitario asociado
 * y actualiza el campo hidden del transitario.
 */
(function () {
  "use strict";

  function init() {
    const contenedorSelect = document.querySelector("#id_contenedor");
    const transitarioHidden = document.querySelector("#id_transitario");

    if (!contenedorSelect) {
      console.log("[PagoTransitario] Campo contenedor no encontrado");
      return;
    }

    console.log("[PagoTransitario] Iniciando auto-completado de transitario");
    console.log(
      "[PagoTransitario] Campo transitario hidden:",
      transitarioHidden ? "encontrado" : "no encontrado"
    );

    // Función para obtener el transitario del contenedor seleccionado
    async function updateTransitario() {
      const contenedorId = contenedorSelect.value;

      if (!contenedorId) {
        updateTransitarioDisplay(
          "📋 Se seleccionará automáticamente el transitario del contenedor",
          false,
          null
        );
        return;
      }

      try {
        // Obtener datos del contenedor via API
        const response = await fetch(`/api/contenedor/${contenedorId}/`);
        if (response.ok) {
          const data = await response.json();
          console.log("[PagoTransitario] Datos recibidos:", data);

          if (data.transitario) {
            updateTransitarioDisplay(
              `🏢 ${data.transitario.nombre}`,
              true,
              data.transitario.id
            );
          } else {
            updateTransitarioDisplay(
              "⚠️ El contenedor no tiene transitario asignado",
              false,
              null
            );
          }
        } else {
          console.log("[PagoTransitario] Error en respuesta:", response.status);
        }
      } catch (error) {
        console.log("[PagoTransitario] Error obteniendo transitario:", error);
        updateTransitarioDisplay(
          "❌ Error al obtener transitario",
          false,
          null
        );
      }
    }

    function updateTransitarioDisplay(text, isSuccess, transitarioId) {
      // Actualizar el campo hidden del transitario
      if (transitarioHidden && transitarioId !== undefined) {
        transitarioHidden.value = transitarioId || "";
        console.log(
          "[PagoTransitario] Transitario ID actualizado a:",
          transitarioId
        );
      }

      // Buscar el elemento de display del transitario (readonly field)
      const transitarioRow = document.querySelector(
        ".field-transitario_display"
      );
      if (transitarioRow) {
        const readonlyDiv = transitarioRow.querySelector(".readonly");
        if (readonlyDiv) {
          if (isSuccess) {
            readonlyDiv.innerHTML = `<span id="transitario-display" style="font-weight: bold; color: #4CAF50;">${text}</span>`;
          } else {
            readonlyDiv.innerHTML = `<span id="transitario-display" style="color: #999; font-style: italic;">${text}</span>`;
          }
        }
      }

      // También buscar por ID si existe
      const displaySpan = document.querySelector("#transitario-display");
      if (displaySpan) {
        if (isSuccess) {
          displaySpan.outerHTML = `<span id="transitario-display" style="font-weight: bold; color: #4CAF50;">${text}</span>`;
        } else {
          displaySpan.outerHTML = `<span id="transitario-display" style="color: #999; font-style: italic;">${text}</span>`;
        }
      }
    }

    // Escuchar cambios en el select de contenedor
    // Para Select2
    if (window.jQuery) {
      jQuery(contenedorSelect).on("change", updateTransitario);
    } else {
      contenedorSelect.addEventListener("change", updateTransitario);
    }

    // También actualizar cuando se carga la página si ya hay un contenedor seleccionado
    if (contenedorSelect.value) {
      setTimeout(updateTransitario, 500);
    }
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 300);
  }
})();

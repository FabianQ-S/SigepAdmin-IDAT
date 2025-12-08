/**
 * Script para consultar RUC en SUNAT desde el panel de administración.
 *
 * Este script agrega un botón de consulta al campo "identificador_tributario"
 * en el formulario de Transitarios. Al hacer clic, consulta la API de SUNAT
 * y rellena automáticamente los campos relacionados.
 */

(function () {
  "use strict";

  // Esperar a que el DOM esté listo
  document.addEventListener("DOMContentLoaded", function () {
    // Buscar el campo de RUC (identificador_tributario)
    const rucInput = document.getElementById("id_identificador_tributario");

    if (!rucInput) {
      return; // No estamos en el formulario de Transitarios
    }

    // Crear el contenedor para el botón
    const wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.gap = "10px";

    // Insertar el wrapper
    rucInput.parentNode.insertBefore(wrapper, rucInput);
    wrapper.appendChild(rucInput);

    // Crear el botón de consulta SUNAT
    const btnConsultar = document.createElement("button");
    btnConsultar.type = "button";
    btnConsultar.innerHTML = "🔍 Consultar SUNAT";
    btnConsultar.className = "button";
    btnConsultar.style.cssText = `
            background: linear-gradient(90deg, #417690, #5a9bb5);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            white-space: nowrap;
            transition: all 0.3s ease;
        `;

    btnConsultar.addEventListener("mouseenter", function () {
      this.style.background = "linear-gradient(90deg, #5a9bb5, #417690)";
      this.style.transform = "scale(1.02)";
    });

    btnConsultar.addEventListener("mouseleave", function () {
      this.style.background = "linear-gradient(90deg, #417690, #5a9bb5)";
      this.style.transform = "scale(1)";
    });

    wrapper.appendChild(btnConsultar);

    // Crear indicador de estado
    const statusIndicator = document.createElement("span");
    statusIndicator.id = "sunat-status";
    statusIndicator.style.cssText = `
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
        `;
    wrapper.appendChild(statusIndicator);

    // Función para mostrar estado
    function showStatus(message, type) {
      statusIndicator.textContent = message;
      statusIndicator.style.display = "inline-block";

      const colors = {
        loading: { bg: "#fff3cd", color: "#856404" },
        success: { bg: "#d4edda", color: "#155724" },
        error: { bg: "#f8d7da", color: "#721c24" },
        info: { bg: "#cce5ff", color: "#004085" },
      };

      const style = colors[type] || colors["info"];
      statusIndicator.style.backgroundColor = style.bg;
      statusIndicator.style.color = style.color;

      // Auto-ocultar después de 5 segundos para éxito
      if (type === "success") {
        setTimeout(() => {
          statusIndicator.style.display = "none";
        }, 5000);
      }
    }

    // Función para consultar SUNAT
    async function consultarSunat() {
      const ruc = rucInput.value.trim();

      // Validar RUC
      if (!ruc) {
        showStatus("⚠️ Ingrese un RUC", "error");
        rucInput.focus();
        return;
      }

      if (!/^\d{11}$/.test(ruc)) {
        showStatus("⚠️ El RUC debe tener 11 dígitos", "error");
        rucInput.focus();
        return;
      }

      // Mostrar loading
      btnConsultar.disabled = true;
      btnConsultar.innerHTML = "⏳ Consultando...";
      showStatus("Consultando SUNAT...", "loading");

      try {
        const response = await fetch(`/api/sunat/ruc/${ruc}/`);

        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
          showStatus(`❌ ${data.error}`, "error");
          if (data.instrucciones) {
            console.log("Instrucciones para configurar:", data.instrucciones);
          }
          return;
        }

        // Rellenar campos automáticamente
        rellenarCampos(data);

        // Mostrar mensaje de éxito
        const modoDemo = data._modo ? " (DEMO)" : "";
        showStatus(`✅ Datos obtenidos${modoDemo}`, "success");
      } catch (error) {
        console.error("Error al consultar SUNAT:", error);
        showStatus("❌ Error de conexión", "error");
      } finally {
        btnConsultar.disabled = false;
        btnConsultar.innerHTML = "🔍 Consultar SUNAT";
      }
    }

    // Función para rellenar los campos del formulario
    function rellenarCampos(data) {
      // Mapeo de campos SUNAT a campos del formulario
      const fieldMappings = {
        razon_social: "id_razon_social",
        nombre_comercial: "id_nombre_comercial",
        direccion: "id_direccion",
      };

      for (const [sunatField, formFieldId] of Object.entries(fieldMappings)) {
        const value = data[sunatField];
        const field = document.getElementById(formFieldId);

        if (field && value) {
          // Solo rellenar si el campo está vacío o preguntar
          if (!field.value || field.value === value) {
            field.value = value;
            highlightField(field);
          } else {
            // El campo ya tiene un valor diferente
            if (confirm(`¿Desea reemplazar "${field.value}" por "${value}"?`)) {
              field.value = value;
              highlightField(field);
            }
          }
        }
      }

      // Campos especiales de ubicación (solo si están vacíos)
      const paisField = document.getElementById("id_pais");
      if (paisField && !paisField.value && data.departamento) {
        paisField.value = "Perú";
        highlightField(paisField);
      }

      const ciudadField = document.getElementById("id_ciudad");
      if (ciudadField && !ciudadField.value && data.provincia) {
        ciudadField.value = `${data.distrito}, ${data.provincia}`;
        highlightField(ciudadField);
      }

      // Mostrar información adicional en consola
      console.log("Datos SUNAT recibidos:", data);
      if (data.estado) {
        console.log(`Estado del contribuyente: ${data.estado}`);
      }
      if (data.condicion) {
        console.log(`Condición: ${data.condicion}`);
      }
    }

    // Función para resaltar campos actualizados
    function highlightField(field) {
      const originalBg = field.style.backgroundColor;
      field.style.backgroundColor = "#d4edda";
      field.style.transition = "background-color 0.5s ease";

      setTimeout(() => {
        field.style.backgroundColor = originalBg || "";
      }, 2000);
    }

    // Event listener para el botón
    btnConsultar.addEventListener("click", consultarSunat);

    // También permitir consultar con Enter en el campo RUC
    rucInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        consultarSunat();
      }
    });

    // Agregar tooltip al pasar el mouse sobre el botón
    btnConsultar.title =
      "Consultar datos del contribuyente en SUNAT usando el RUC ingresado";
  });
})();

/**
 * Script para consultar RUC en SUNAT desde el panel de administración.
 *
 * Funcionalidades:
 * - Consulta API SUNAT al hacer clic en la flecha
 * - Autocompleta campos del formulario
 * - Botón X para limpiar datos autocompletados
 * - Campos de solo lectura para datos SUNAT
 * - Validaciones y formateos especiales
 */

(function () {
  "use strict";

  // Estado global para saber si hay datos de SUNAT cargados
  let sunatDataLoaded = false;
  let originalRuc = null;

  // Campos que se autocompletarán desde SUNAT (no editables)
  const SUNAT_READONLY_FIELDS = [
    "id_razon_social",
    "id_pais",
    "id_ciudad",
    "id_direccion",
    "id_estado_operacion",
  ];

  // Campos que se autocompletarán pero son editables
  const SUNAT_EDITABLE_FIELDS = ["id_nombre_comercial", "id_observaciones"];

  document.addEventListener("DOMContentLoaded", function () {
    // Buscar el campo de RUC
    const rucInput = document.getElementById("id_identificador_tributario");

    if (!rucInput) {
      return; // No estamos en el formulario de Transitarios
    }

    // Inicializar todas las mejoras
    initRucField(rucInput);
    initPhoneValidation();
    initSitioWebPrefix();
    initLicenciaPlaceholder();
    initFechaVencimientoValidation();
    initLimiteCreditoFormat();
    hideEsActivoField();
    checkExistingData(rucInput);
  });

  /**
   * Inicializa el campo RUC con botón de consulta/limpiar
   */
  function initRucField(rucInput) {
    // Cambiar el label del campo
    const label = document.querySelector(
      'label[for="id_identificador_tributario"]'
    );
    if (label) {
      label.textContent = "RUC:";
    }

    // Crear contenedor
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "display: flex; align-items: center; gap: 8px;";

    rucInput.parentNode.insertBefore(wrapper, rucInput);
    wrapper.appendChild(rucInput);

    // Botón de consulta (flecha)
    const btnConsultar = document.createElement("button");
    btnConsultar.type = "button";
    btnConsultar.id = "btn-sunat-action";
    btnConsultar.innerHTML = "➡️ Consultar";
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
    wrapper.appendChild(btnConsultar);

    // Indicador de estado
    const statusIndicator = document.createElement("span");
    statusIndicator.id = "sunat-status";
    statusIndicator.style.cssText = `
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
            display: none;
        `;
    wrapper.appendChild(statusIndicator);

    // Event listeners
    btnConsultar.addEventListener("click", function () {
      if (sunatDataLoaded) {
        limpiarDatosSunat(rucInput, btnConsultar);
      } else {
        consultarSunat(rucInput, btnConsultar, statusIndicator);
      }
    });

    rucInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        if (!sunatDataLoaded) {
          consultarSunat(rucInput, btnConsultar, statusIndicator);
        }
      }
    });

    // Solo permitir números en el campo RUC
    rucInput.addEventListener("input", function (e) {
      this.value = this.value.replace(/\D/g, "").slice(0, 11);
    });
  }

  /**
   * Verifica si ya hay datos cargados (edición de registro existente)
   */
  function checkExistingData(rucInput) {
    const razonSocial = document.getElementById("id_razon_social");
    if (razonSocial && razonSocial.value && rucInput.value) {
      // Hay datos existentes, establecer estado como cargado
      sunatDataLoaded = true;
      originalRuc = rucInput.value;
      updateButtonState(document.getElementById("btn-sunat-action"), true);
      setFieldsReadonly(true);

      // Bloquear el campo RUC con estilos de tema oscuro
      rucInput.readOnly = true;
      rucInput.style.backgroundColor = "#2d3748";
      rucInput.style.color = "#a0aec0";
      rucInput.style.border = "1px solid #4a5568";
      rucInput.style.cursor = "not-allowed";
    }
  }

  /**
   * Consulta la API de SUNAT
   */
  async function consultarSunat(rucInput, btnConsultar, statusIndicator) {
    const ruc = rucInput.value.trim();

    if (!ruc) {
      showStatus(statusIndicator, "⚠️ Ingrese un RUC", "error");
      rucInput.focus();
      return;
    }

    if (!/^\d{11}$/.test(ruc)) {
      showStatus(statusIndicator, "⚠️ El RUC debe tener 11 dígitos", "error");
      rucInput.focus();
      return;
    }

    btnConsultar.disabled = true;
    btnConsultar.innerHTML = "⏳ Consultando...";
    showStatus(statusIndicator, "Consultando SUNAT...", "loading");

    try {
      const response = await fetch(`/api/sunat/ruc/${ruc}/`);

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        showStatus(statusIndicator, `❌ ${data.error}`, "error");
        btnConsultar.disabled = false;
        btnConsultar.innerHTML = "➡️ Consultar";
        return;
      }

      // Rellenar campos
      rellenarCampos(data);

      // Actualizar estado
      sunatDataLoaded = true;
      originalRuc = ruc;
      updateButtonState(btnConsultar, true);
      setFieldsReadonly(true);

      // Bloquear el campo RUC con estilos de tema oscuro
      rucInput.readOnly = true;
      rucInput.style.backgroundColor = "#2d3748";
      rucInput.style.color = "#a0aec0";
      rucInput.style.border = "1px solid #4a5568";
      rucInput.style.cursor = "not-allowed";

      showStatus(statusIndicator, "✅ Datos cargados desde SUNAT", "success");
    } catch (error) {
      console.error("Error al consultar SUNAT:", error);
      showStatus(statusIndicator, "❌ Error de conexión", "error");
      btnConsultar.disabled = false;
      btnConsultar.innerHTML = "➡️ Consultar";
    }
  }

  /**
   * Limpia los datos autocompletados de SUNAT
   */
  function limpiarDatosSunat(rucInput, btnConsultar) {
    if (
      !confirm(
        "¿Está seguro de eliminar los datos de SUNAT? Podrá ingresar otro RUC."
      )
    ) {
      return;
    }

    // Limpiar campos de solo lectura
    SUNAT_READONLY_FIELDS.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        if (field.tagName === "SELECT") {
          field.disabled = false;
        } else {
          field.value = "";
          field.readOnly = false;
        }
        field.style.backgroundColor = "";
        field.style.color = "";
        field.style.cursor = "";
        field.style.border = "";
      }
    });

    // Limpiar campos editables excepto observaciones (punto 23)
    const nombreComercial = document.getElementById("id_nombre_comercial");
    if (nombreComercial) {
      nombreComercial.value = "";
    }

    // Resetear estado de operación a ACTIVO y quitar alerta roja
    const estadoOperacion = document.getElementById("id_estado_operacion");
    if (estadoOperacion) {
      estadoOperacion.value = "ACTIVO";
      estadoOperacion.style.backgroundColor = "";
      estadoOperacion.style.color = "";
      estadoOperacion.style.pointerEvents = "";
      const parentRow =
        estadoOperacion.closest(".form-row") || estadoOperacion.parentElement;
      if (parentRow) {
        parentRow.style.backgroundColor = "";
        parentRow.style.borderLeft = "";
        parentRow.style.paddingLeft = "";
      }
    }

    // Limpiar RUC y habilitarlo
    rucInput.value = "";
    rucInput.readOnly = false;
    rucInput.style.backgroundColor = "";
    rucInput.style.color = "";
    rucInput.style.border = "";
    rucInput.style.cursor = "";
    rucInput.focus();

    // Actualizar estado
    sunatDataLoaded = false;
    originalRuc = null;
    updateButtonState(btnConsultar, false);
    setFieldsReadonly(false);

    // Ocultar status
    const statusIndicator = document.getElementById("sunat-status");
    if (statusIndicator) {
      statusIndicator.style.display = "none";
    }
  }

  /**
   * Actualiza el estado visual del botón
   */
  function updateButtonState(btn, isLoaded) {
    if (isLoaded) {
      btn.innerHTML = "❌ Limpiar";
      btn.style.background = "linear-gradient(90deg, #dc3545, #c82333)";
      btn.disabled = false;
    } else {
      btn.innerHTML = "➡️ Consultar";
      btn.style.background = "linear-gradient(90deg, #417690, #5a9bb5)";
      btn.disabled = false;
    }
  }

  /**
   * Establece los campos como solo lectura o editables
   */
  function setFieldsReadonly(readonly) {
    SUNAT_READONLY_FIELDS.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        if (readonly) {
          // Estilos para tema oscuro - fondo oscuro con texto visible
          field.style.backgroundColor = "#2d3748";
          field.style.color = "#a0aec0";
          field.style.cursor = "not-allowed";
          field.style.border = "1px solid #4a5568";
          field.style.pointerEvents = "none";

          // Para inputs de texto
          if (field.tagName === "INPUT" || field.tagName === "TEXTAREA") {
            field.readOnly = true;
          }
          // Para select: NO usar disabled, solo bloquear visualmente con pointerEvents
          // El valor aún se enviará al servidor
        } else {
          field.style.backgroundColor = "";
          field.style.color = "";
          field.style.cursor = "";
          field.style.border = "";
          field.style.pointerEvents = "";

          if (field.tagName === "INPUT" || field.tagName === "TEXTAREA") {
            field.readOnly = false;
          }
        }
      }
    });
  }

  /**
   * Rellena los campos del formulario con datos de SUNAT
   */
  function rellenarCampos(data) {
    // 1. Razón Social (no editable)
    setFieldValue("id_razon_social", data.razon_social);

    // 2. Nombre Comercial (editable, copia razón social si no hay)
    const nombreComercial = data.nombre_comercial || data.razon_social;
    setFieldValue("id_nombre_comercial", nombreComercial);

    // 7. País (no editable)
    setFieldValue("id_pais", "Perú");

    // 8. Ciudad (no editable)
    const ciudad = `${data.distrito || ""}, ${data.provincia || ""}`.trim();
    setFieldValue("id_ciudad", ciudad);

    // 9. Dirección
    setFieldValue("id_direccion", data.direccion);

    // 16. Estado de Operación
    const estadoOperacion = document.getElementById("id_estado_operacion");
    if (estadoOperacion) {
      const estado = data.estado ? data.estado.toUpperCase() : "";
      const condicion = data.condicion ? data.condicion.toUpperCase() : "";

      // Limpiar alerta previa si existe
      const parentRow =
        estadoOperacion.closest(".form-row") || estadoOperacion.parentElement;
      if (parentRow) {
        parentRow.style.backgroundColor = "";
        parentRow.style.borderLeft = "";
        parentRow.style.paddingLeft = "";
      }

      if (estado === "ACTIVO" && condicion === "HABIDO") {
        estadoOperacion.value = "ACTIVO";
      } else if (
        estado === "BAJA" ||
        condicion === "NO HABIDO" ||
        condicion === "NO HALLADO"
      ) {
        estadoOperacion.value = "BLOQUEADO";
        highlightFieldRed(estadoOperacion);
      } else {
        estadoOperacion.value = "SUSPENDIDO";
        highlightFieldRed(estadoOperacion);
      }
      highlightField(estadoOperacion);
    }

    // 23. Observaciones - Agregar datos adicionales
    const observaciones = document.getElementById("id_observaciones");
    if (observaciones) {
      const datosAdicionales = [];
      datosAdicionales.push(
        `--- Datos SUNAT (RUC: ${data.ruc || data.numero_documento || ""}) ---`
      );
      datosAdicionales.push(`Estado: ${data.estado || "N/A"}`);
      datosAdicionales.push(`Condición: ${data.condicion || "N/A"}`);
      datosAdicionales.push(
        `Es Agente de Retención: ${data.es_agente_retencion ? "Sí" : "No"}`
      );
      datosAdicionales.push(
        `Es Buen Contribuyente: ${data.es_buen_contribuyente ? "Sí" : "No"}`
      );
      if (data.ubigeo) datosAdicionales.push(`Ubigeo: ${data.ubigeo}`);
      if (data.departamento)
        datosAdicionales.push(`Departamento: ${data.departamento}`);
      datosAdicionales.push(
        `Fecha consulta: ${new Date().toLocaleString("es-PE")}`
      );

      // Agregar al final del contenido existente
      const nuevoContenido = datosAdicionales.join("\n");
      if (observaciones.value) {
        observaciones.value = observaciones.value + "\n\n" + nuevoContenido;
      } else {
        observaciones.value = nuevoContenido;
      }
      highlightField(observaciones);
    }
  }

  /**
   * Establece el valor de un campo y lo resalta
   */
  function setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && value) {
      field.value = value;
      highlightField(field);
    }
  }

  /**
   * Resalta un campo temporalmente (verde)
   */
  function highlightField(field) {
    const originalBg = field.style.backgroundColor;
    const originalColor = field.style.color;
    field.style.backgroundColor = "#276749";
    field.style.color = "#c6f6d5";
    field.style.transition = "background-color 0.5s ease, color 0.5s ease";

    setTimeout(() => {
      // Solo restaurar si no es un campo readonly
      if (!SUNAT_READONLY_FIELDS.includes(field.id)) {
        field.style.backgroundColor = originalBg || "";
        field.style.color = originalColor || "";
      } else {
        // Campos readonly - tema oscuro
        field.style.backgroundColor = "#2d3748";
        field.style.color = "#a0aec0";
      }
    }, 2000);
  }

  /**
   * Resalta un campo en rojo (alerta)
   */
  function highlightFieldRed(field) {
    const parentRow = field.closest(".form-row") || field.parentElement;
    if (parentRow) {
      parentRow.style.backgroundColor = "#f8d7da";
      parentRow.style.borderLeft = "4px solid #dc3545";
      parentRow.style.paddingLeft = "10px";
    }
  }

  /**
   * Muestra el indicador de estado
   */
  function showStatus(statusIndicator, message, type) {
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

    if (type === "success") {
      setTimeout(() => {
        statusIndicator.style.display = "none";
      }, 5000);
    }
  }

  /**
   * 11-12. Validación de teléfonos (solo números)
   */
  function initPhoneValidation() {
    const phoneFields = ["id_telefono_contacto", "id_telefono_emergencia"];

    phoneFields.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.addEventListener("input", function (e) {
          // Permitir solo números, +, -, espacios y paréntesis
          this.value = this.value.replace(/[^\d\s\+\-\(\)]/g, "");
        });
        field.setAttribute("placeholder", "Ej: +51 999 999 999");
      }
    });
  }

  /**
   * 15. Prefijo https:// en Sitio Web
   */
  function initSitioWebPrefix() {
    const sitioWeb = document.getElementById("id_sitio_web");
    if (!sitioWeb) return;

    // Crear wrapper
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "display: flex; align-items: center;";

    const prefix = document.createElement("span");
    prefix.textContent = "https://";
    prefix.style.cssText = `
            background: #e9ecef;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-right: none;
            border-radius: 4px 0 0 4px;
            color: #495057;
            font-size: 13px;
        `;

    sitioWeb.style.borderRadius = "0 4px 4px 0";
    sitioWeb.setAttribute("placeholder", "www.ejemplo.com");

    sitioWeb.parentNode.insertBefore(wrapper, sitioWeb);
    wrapper.appendChild(prefix);
    wrapper.appendChild(sitioWeb);

    // Limpiar https:// si el usuario lo ingresa
    sitioWeb.addEventListener("input", function () {
      this.value = this.value.replace(/^https?:\/\//i, "");
    });

    // Al guardar, asegurar que tenga https://
    const form = sitioWeb.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        if (sitioWeb.value && !sitioWeb.value.startsWith("http")) {
          sitioWeb.value = "https://" + sitioWeb.value;
        }
      });
    }
  }

  /**
   * 17. Placeholder para Licencia de Operador
   */
  function initLicenciaPlaceholder() {
    const licencia = document.getElementById("id_licencia_operador");
    if (licencia) {
      licencia.setAttribute("placeholder", "EJ: MTC-202X-XXXX");
    }
  }

  /**
   * 18. Validación de fecha de vencimiento (no anterior a hoy)
   */
  function initFechaVencimientoValidation() {
    const fechaField = document.getElementById("id_fecha_vencimiento_licencia");
    if (!fechaField) return;

    // Establecer fecha mínima como hoy
    const today = new Date().toISOString().split("T")[0];
    fechaField.setAttribute("min", today);

    // Agregar mensaje de ayuda
    const helpText = document.createElement("span");
    helpText.style.cssText =
      "font-size: 11px; color: #6c757d; margin-left: 10px;";
    helpText.textContent = "(No puede ser anterior a hoy)";
    fechaField.parentNode.appendChild(helpText);

    // Validación al cambiar
    fechaField.addEventListener("change", function () {
      const selectedDate = new Date(this.value);
      const todayDate = new Date();
      todayDate.setHours(0, 0, 0, 0);

      if (selectedDate < todayDate) {
        alert("⚠️ La fecha de vencimiento no puede ser anterior a hoy.");
        this.value = "";
      }
    });
  }

  /**
   * 20. Formato de dólares para Límite de Crédito
   */
  function initLimiteCreditoFormat() {
    const limiteCredito = document.getElementById("id_limite_credito");
    if (!limiteCredito) return;

    // Crear wrapper con símbolo de dólar
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "display: flex; align-items: center;";

    const prefix = document.createElement("span");
    prefix.textContent = "$";
    prefix.style.cssText = `
            background: #e9ecef;
            padding: 6px 12px;
            border: 1px solid #ced4da;
            border-right: none;
            border-radius: 4px 0 0 4px;
            color: #495057;
            font-size: 14px;
            font-weight: bold;
        `;

    limiteCredito.style.borderRadius = "0 4px 4px 0";

    limiteCredito.parentNode.insertBefore(wrapper, limiteCredito);
    wrapper.appendChild(prefix);
    wrapper.appendChild(limiteCredito);
  }

  /**
   * 22. Ocultar campo es_activo de la interfaz
   */
  function hideEsActivoField() {
    const esActivo = document.getElementById("id_es_activo");
    if (!esActivo) return;

    // Buscar la fila contenedora y ocultarla
    const fieldRow = esActivo.closest(".form-row");
    if (fieldRow) {
      fieldRow.style.display = "none";
    } else {
      // Intentar ocultar el contenedor padre
      const parent = esActivo.parentElement;
      if (parent) {
        parent.style.display = "none";
      }
    }
  }
})();

/**
 * Admin Arribo - Validaciones y mejoras UX para el panel de Arribos
 *
 * Funcionalidades:
 * 1. Búsqueda en dropdown de Buque (autocomplete)
 * 2. Estado: deshabilitar fecha arribo real si es "Programado" o "En Ruta"
 * 3. Tipo de Operación: deshabilitar campos según selección
 * 4. Validación ETA < ETD
 * 5. Fecha Arribo Real no puede ser futura
 */
(function () {
  "use strict";

  // ====== CONFIGURACIÓN ======
  const CONFIG = {
    // Selectores de campos
    estadoSelector: "#id_estado",
    tipoOperacionSelector: "#id_tipo_operacion",
    fechaEtaSelector:
      '#id_fecha_eta_0, #id_fecha_eta, input[name="fecha_eta_0"], input[name="fecha_eta"]',
    fechaEtdSelector:
      '#id_fecha_etd_0, #id_fecha_etd, input[name="fecha_etd_0"], input[name="fecha_etd"]',
    fechaArriboRealSelector:
      '#id_fecha_arribo_real_0, #id_fecha_arribo_real, input[name="fecha_arribo_real_0"], input[name="fecha_arribo_real"]',
    contenedoresDescargaSelector: "#id_contenedores_descarga",
    contenedoresCargaSelector: "#id_contenedores_carga",

    // Estados que deshabilitan fecha arribo real
    estadosSinArriboReal: ["PROGRAMADO", "EN_RUTA"],

    // Tipos de operación (simplificado - solo Carga o Descarga)
    tipoDescarga: "DESCARGA",
    tipoCarga: "CARGA",
  };

  // ====== UTILIDADES ======
  function log(message) {
    console.log(`[ArriboAdmin] ${message}`);
  }

  function getField(selector) {
    return document.querySelector(selector);
  }

  function getAllFields(selector) {
    return document.querySelectorAll(selector);
  }

  function setFieldDisabled(selector, disabled, grayValue = null) {
    const fields = getAllFields(selector);
    fields.forEach((field) => {
      field.disabled = disabled;
      if (disabled) {
        field.style.backgroundColor = "#3a3a3a";
        field.style.color = "#888";
        field.style.cursor = "not-allowed";
        if (grayValue !== null && field.type !== "hidden") {
          field.value = grayValue;
        }
      } else {
        field.style.backgroundColor = "";
        field.style.color = "";
        field.style.cursor = "";
      }
    });
  }

  function showFieldMessage(fieldSelector, message, type = "warning") {
    const field = getField(fieldSelector);
    if (!field) return;

    // Eliminar mensaje anterior si existe
    const existingMsg = field.parentNode.querySelector(".field-validation-msg");
    if (existingMsg) existingMsg.remove();

    if (!message) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = "field-validation-msg";
    msgDiv.style.cssText = `
            font-size: 11px;
            margin-top: 4px;
            padding: 4px 8px;
            border-radius: 4px;
            ${
              type === "error"
                ? "background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;"
                : "background: #fff3cd; color: #856404; border: 1px solid #ffeeba;"
            }
        `;
    msgDiv.textContent = message;
    field.parentNode.appendChild(msgDiv);
  }

  // ====== VALIDACIÓN 2: Estado y Fecha Arribo Real ======
  function setupEstadoValidation() {
    const estadoField = getField(CONFIG.estadoSelector);
    if (!estadoField) {
      log("Campo estado no encontrado");
      return;
    }

    function validateEstado() {
      const estado = estadoField.value;
      const shouldDisable = CONFIG.estadosSinArriboReal.includes(estado);

      // Deshabilitar fecha arribo real
      const arriboRealFields = getAllFields(CONFIG.fechaArriboRealSelector);
      arriboRealFields.forEach((field) => {
        field.disabled = shouldDisable;
        field.style.backgroundColor = shouldDisable ? "#3a3a3a" : "";
        field.style.color = shouldDisable ? "#666" : "";

        if (shouldDisable) {
          field.value = "";
        }
      });

      // También buscar campos de hora asociados
      const horaFields = document.querySelectorAll(
        '#id_fecha_arribo_real_1, input[name="fecha_arribo_real_1"]'
      );
      horaFields.forEach((field) => {
        field.disabled = shouldDisable;
        field.style.backgroundColor = shouldDisable ? "#3a3a3a" : "";
        field.style.color = shouldDisable ? "#666" : "";
        if (shouldDisable) field.value = "";
      });

      // Mostrar mensaje
      if (shouldDisable) {
        showFieldMessage(
          CONFIG.fechaArriboRealSelector,
          '⚠️ No disponible para estado "Programado" o "En Ruta"',
          "warning"
        );
      } else {
        showFieldMessage(CONFIG.fechaArriboRealSelector, null);
      }
    }

    estadoField.addEventListener("change", validateEstado);
    // Ejecutar al cargar
    validateEstado();
    log("Validación de estado configurada");
  }

  // ====== VALIDACIÓN 3: Tipo de Operación ======
  function setupTipoOperacionValidation() {
    const tipoOpField = getField(CONFIG.tipoOperacionSelector);
    if (!tipoOpField) {
      log("Campo tipo_operacion no encontrado");
      return;
    }

    function validateTipoOperacion() {
      const tipoOp = tipoOpField.value;

      const descargaField = getField(CONFIG.contenedoresDescargaSelector);
      const cargaField = getField(CONFIG.contenedoresCargaSelector);

      // Resetear ambos campos primero
      if (descargaField) {
        descargaField.disabled = false;
        descargaField.style.backgroundColor = "";
        descargaField.style.color = "";
        showFieldMessage(CONFIG.contenedoresDescargaSelector, null);
      }
      if (cargaField) {
        cargaField.disabled = false;
        cargaField.style.backgroundColor = "";
        cargaField.style.color = "";
        showFieldMessage(CONFIG.contenedoresCargaSelector, null);
      }

      if (tipoOp === CONFIG.tipoDescarga) {
        // Solo descarga: deshabilitar carga
        if (cargaField) {
          cargaField.disabled = true;
          cargaField.value = "0";
          cargaField.style.backgroundColor = "#3a3a3a";
          cargaField.style.color = "#666";
          showFieldMessage(
            CONFIG.contenedoresCargaSelector,
            "⚠️ No aplica para operación de Descarga",
            "warning"
          );
        }
      } else if (tipoOp === CONFIG.tipoCarga) {
        // Solo carga: deshabilitar descarga
        if (descargaField) {
          descargaField.disabled = true;
          descargaField.value = "0";
          descargaField.style.backgroundColor = "#3a3a3a";
          descargaField.style.color = "#666";
          showFieldMessage(
            CONFIG.contenedoresDescargaSelector,
            "⚠️ No aplica para operación de Carga",
            "warning"
          );
        }
      }
      // Solo hay dos opciones: DESCARGA o CARGA
    }

    tipoOpField.addEventListener("change", validateTipoOperacion);
    // Ejecutar al cargar
    validateTipoOperacion();
    log("Validación de tipo de operación configurada");
  }

  // ====== VALIDACIÓN 5 y 6: ETA < ETD ======
  function setupFechasValidation() {
    const etaField = getField(CONFIG.fechaEtaSelector);
    const etdField = getField(CONFIG.fechaEtdSelector);

    if (!etaField || !etdField) {
      log("Campos de fecha ETA/ETD no encontrados");
      return;
    }

    function getDateValue(dateField, timeFieldId) {
      const dateValue = dateField.value;
      if (!dateValue) return null;

      // Buscar campo de hora asociado
      const timeField = document.querySelector(timeFieldId);
      const timeValue = timeField ? timeField.value : "00:00:00";

      try {
        return new Date(`${dateValue}T${timeValue}`);
      } catch (e) {
        return new Date(dateValue);
      }
    }

    function validateFechas() {
      const etaDate = getDateValue(etaField, "#id_fecha_eta_1");
      const etdDate = getDateValue(etdField, "#id_fecha_etd_1");

      if (etaDate && etdDate) {
        if (etdDate < etaDate) {
          showFieldMessage(
            CONFIG.fechaEtdSelector,
            "❌ ETD no puede ser anterior a ETA",
            "error"
          );
          etdField.style.borderColor = "#dc3545";
        } else {
          showFieldMessage(CONFIG.fechaEtdSelector, null);
          etdField.style.borderColor = "";
        }
      }

      // Establecer min date en ETD basado en ETA
      if (etaDate && etdField.type === "date") {
        const etaDateStr = etaField.value;
        etdField.min = etaDateStr;
      }
    }

    etaField.addEventListener("change", validateFechas);
    etdField.addEventListener("change", validateFechas);

    // También para los campos de hora
    const etaTimeField = document.querySelector("#id_fecha_eta_1");
    const etdTimeField = document.querySelector("#id_fecha_etd_1");
    if (etaTimeField) etaTimeField.addEventListener("change", validateFechas);
    if (etdTimeField) etdTimeField.addEventListener("change", validateFechas);

    // Ejecutar al cargar
    validateFechas();
    log("Validación de fechas ETA/ETD configurada");
  }

  // ====== VALIDACIÓN 7: Fecha Arribo Real no puede ser futura ======
  function setupFechaArriboRealValidation() {
    const arriboRealFields = getAllFields(CONFIG.fechaArriboRealSelector);

    arriboRealFields.forEach((field) => {
      if (field.type === "date") {
        // Establecer max date como hoy
        const today = new Date().toISOString().split("T")[0];
        field.max = today;
      }

      field.addEventListener("change", function () {
        const value = this.value;
        if (!value) return;

        const selectedDate = new Date(value);
        const now = new Date();

        // Comparar solo fechas si es campo de fecha
        if (this.type === "date") {
          now.setHours(23, 59, 59, 999);
        }

        if (selectedDate > now) {
          showFieldMessage(
            CONFIG.fechaArriboRealSelector,
            "❌ La fecha de arribo real no puede ser futura",
            "error"
          );
          this.style.borderColor = "#dc3545";
        } else {
          showFieldMessage(CONFIG.fechaArriboRealSelector, null);
          this.style.borderColor = "";
        }
      });
    });

    log("Validación de fecha arribo real configurada");
  }

  // ====== MEJORA: Indicadores visuales para campos deshabilitados ======
  function setupVisualIndicators() {
    // Agregar estilos CSS para campos deshabilitados
    const style = document.createElement("style");
    style.textContent = `
            .field-validation-msg {
                animation: fadeIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-5px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Estilos para campos deshabilitados */
            input:disabled, select:disabled, textarea:disabled {
                background-color: #3a3a3a !important;
                color: #888 !important;
                cursor: not-allowed !important;
            }
            
            /* Tooltip para campos con advertencias */
            .field-with-warning {
                position: relative;
            }
        `;
    document.head.appendChild(style);
  }

  // ====== VALIDACIÓN EN SUBMIT ======
  function setupFormValidation() {
    const form = document.querySelector("#arribo_form, form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      let hasErrors = false;
      const errors = [];

      // Validar ETA < ETD
      const etaField = getField(CONFIG.fechaEtaSelector);
      const etdField = getField(CONFIG.fechaEtdSelector);

      if (etaField && etdField && etaField.value && etdField.value) {
        const etaDate = new Date(etaField.value);
        const etdDate = new Date(etdField.value);

        if (etdDate < etaDate) {
          errors.push("ETD no puede ser anterior a ETA");
          hasErrors = true;
        }
      }

      // Validar fecha arribo real no futura
      const arriboRealField = getField(CONFIG.fechaArriboRealSelector);
      if (
        arriboRealField &&
        arriboRealField.value &&
        !arriboRealField.disabled
      ) {
        const arriboDate = new Date(arriboRealField.value);
        const now = new Date();

        if (arriboDate > now) {
          errors.push("La fecha de arribo real no puede ser futura");
          hasErrors = true;
        }
      }

      // Validar coherencia estado/fecha arribo real
      const estadoField = getField(CONFIG.estadoSelector);
      if (estadoField && arriboRealField) {
        const estado = estadoField.value;
        if (
          CONFIG.estadosSinArriboReal.includes(estado) &&
          arriboRealField.value
        ) {
          errors.push(
            `No puede haber fecha de arribo real con estado "${estado}"`
          );
          hasErrors = true;
        }
      }

      if (hasErrors) {
        e.preventDefault();
        alert("⚠️ Errores de validación:\n\n• " + errors.join("\n• "));
      }
    });

    log("Validación de formulario configurada");
  }

  // ====== INICIALIZACIÓN ======
  function init() {
    log("Inicializando validaciones de Arribo...");

    // Verificar que estamos en la página de Arribo
    if (!window.location.pathname.includes("/arribo/")) {
      log("No estamos en la página de Arribo, saliendo");
      return;
    }

    // Esperar a que el DOM esté listo
    setTimeout(() => {
      setupVisualIndicators();
      setupEstadoValidation();
      setupTipoOperacionValidation();
      setupFechasValidation();
      setupFechaArriboRealValidation();
      setupFormValidation();

      log("Todas las validaciones configuradas");
    }, 100);
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

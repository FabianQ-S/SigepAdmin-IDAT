/**
 * Script para consultar IMO en la API de barcos desde el panel de administración.
 *
 * Funcionalidades:
 * - Consulta API IMO al hacer clic en la flecha
 * - Autocompleta campos del formulario
 * - Botón X para limpiar datos autocompletados
 * - Campos de solo lectura para datos de la API
 * - Manejo especial de campos híbridos (calado, TEU)
 */

(function () {
  "use strict";

  // Estado global para saber si hay datos de IMO cargados
  let imoDataLoaded = false;
  let originalImo = null;

  // Campos que se autocompletarán desde IMO (no editables)
  const IMO_READONLY_FIELDS = [
    "id_nombre",
    "id_eslora_metros",
    "id_manga_metros",
    "id_callsign",
  ];

  // Campo de bandera (especial - readonly si viene de API, dropdown si es manual)
  const FIELD_BANDERA = "id_pabellon_bandera";

  // Campos híbridos (se autocompletan pero son editables)
  const IMO_HYBRID_FIELDS = ["id_calado_metros", "id_teu_capacidad"];

  // Lista de países para el dropdown de bandera (manual)
  const PAISES_BANDERA = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brazil",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Colombia",
    "Comoros",
    "Congo",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "France",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Israel",
    "Italy",
    "Ivory Coast",
    "Jamaica",
    "Japan",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Kuwait",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Mexico",
    "Micronesia",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Korea",
    "North Macedonia",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Poland",
    "Portugal",
    "Qatar",
    "Romania",
    "Russia",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Korea",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Taiwan",
    "Tajikistan",
    "Tanzania",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Vatican City",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Zambia",
    "Zimbabwe",
  ];

  document.addEventListener("DOMContentLoaded", function () {
    // Buscar el campo de IMO
    const imoInput = document.getElementById("id_imo_number");

    if (!imoInput) {
      return; // No estamos en el formulario de Buques
    }

    // Inicializar todas las mejoras
    initImoField(imoInput);
    initBanderaDropdown();
    initPuertoRegistroHelper();
    initCaladoHelper();
    initTeuHelper();
    checkExistingData(imoInput);
  });

  /**
   * Inicializa el campo IMO con botón de consulta/limpiar
   */
  function initImoField(imoInput) {
    // Crear contenedor
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "display: flex; align-items: center; gap: 8px;";

    imoInput.parentNode.insertBefore(wrapper, imoInput);
    wrapper.appendChild(imoInput);

    // Botón de consulta (flecha)
    const btnConsultar = document.createElement("button");
    btnConsultar.type = "button";
    btnConsultar.id = "btn-imo-action";
    btnConsultar.innerHTML = "🚢 Consultar";
    btnConsultar.className = "button";
    btnConsultar.style.cssText = `
            background: linear-gradient(90deg, #0c4a6e, #0369a1);
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
    statusIndicator.id = "imo-status";
    statusIndicator.style.cssText = `
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
            display: none;
        `;
    wrapper.appendChild(statusIndicator);

    // Event listeners
    btnConsultar.addEventListener("click", function () {
      if (imoDataLoaded) {
        limpiarDatosImo(imoInput, btnConsultar);
      } else {
        consultarImo(imoInput, btnConsultar, statusIndicator);
      }
    });

    imoInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        if (!imoDataLoaded) {
          consultarImo(imoInput, btnConsultar, statusIndicator);
        }
      }
    });

    // Solo permitir números en el campo IMO (7 dígitos)
    imoInput.addEventListener("input", function (e) {
      this.value = this.value.replace(/\D/g, "").slice(0, 7);
    });
  }

  /**
   * Verifica si ya hay datos cargados (edición de registro existente)
   */
  function checkExistingData(imoInput) {
    const nombre = document.getElementById("id_nombre");
    if (nombre && nombre.value && imoInput.value) {
      // Hay datos existentes, establecer estado como cargado
      imoDataLoaded = true;
      originalImo = imoInput.value;
      updateButtonState(document.getElementById("btn-imo-action"), true);
      setFieldsReadonly(true);

      // Bloquear el campo IMO con estilos de tema oscuro
      imoInput.readOnly = true;
      imoInput.style.backgroundColor = "#2d3748";
      imoInput.style.color = "#a0aec0";
      imoInput.style.border = "1px solid #4a5568";
      imoInput.style.cursor = "not-allowed";
    }
  }

  /**
   * Consulta la API de IMO
   */
  async function consultarImo(imoInput, btnConsultar, statusIndicator) {
    const imo = imoInput.value.trim();

    if (!imo) {
      showStatus(statusIndicator, "⚠️ Ingrese un IMO", "error");
      imoInput.focus();
      return;
    }

    if (!/^\d{7}$/.test(imo)) {
      showStatus(statusIndicator, "⚠️ El IMO debe tener 7 dígitos", "error");
      imoInput.focus();
      return;
    }

    btnConsultar.disabled = true;
    btnConsultar.innerHTML = "⏳ Consultando...";
    showStatus(statusIndicator, "Consultando API de barcos...", "loading");

    try {
      const response = await fetch(`/api/imo/ship/${imo}/`);

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        showStatus(statusIndicator, `❌ ${data.error}`, "error");
        btnConsultar.disabled = false;
        btnConsultar.innerHTML = "🚢 Consultar";
        return;
      }

      // Rellenar campos
      rellenarCampos(data);

      // Actualizar estado
      imoDataLoaded = true;
      originalImo = imo;
      updateButtonState(btnConsultar, true);
      setFieldsReadonly(true);

      // Bloquear el campo IMO con estilos de tema oscuro
      imoInput.readOnly = true;
      imoInput.style.backgroundColor = "#2d3748";
      imoInput.style.color = "#a0aec0";
      imoInput.style.border = "1px solid #4a5568";
      imoInput.style.cursor = "not-allowed";

      showStatus(statusIndicator, "✅ Datos cargados desde API", "success");
    } catch (error) {
      console.error("Error al consultar IMO:", error);
      showStatus(statusIndicator, "❌ Error de conexión", "error");
      btnConsultar.disabled = false;
      btnConsultar.innerHTML = "🚢 Consultar";
    }
  }

  /**
   * Limpia los datos autocompletados de IMO
   */
  function limpiarDatosImo(imoInput, btnConsultar) {
    if (
      !confirm(
        "¿Está seguro de eliminar los datos de la API? Podrá ingresar otro IMO."
      )
    ) {
      return;
    }

    // Limpiar campos de solo lectura
    IMO_READONLY_FIELDS.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.value = "";
        field.readOnly = false;
        field.style.backgroundColor = "";
        field.style.color = "";
        field.style.cursor = "";
        field.style.border = "";
        field.style.pointerEvents = "";
      }
    });

    // Limpiar campo bandera y restaurar dropdown
    const bandera = document.getElementById(FIELD_BANDERA);
    if (bandera) {
      // Restaurar a input con datalist
      bandera.value = "";
      bandera.style.backgroundColor = "";
      bandera.style.color = "";
      bandera.style.pointerEvents = "";
      bandera.style.cursor = "";
      bandera.style.border = "";
    }

    // Limpiar campos híbridos
    IMO_HYBRID_FIELDS.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.value = "";
        // Quitar alertas de TEU
        const alert = field.parentElement.querySelector(".teu-alert");
        if (alert) alert.remove();
      }
    });

    // Limpiar puerto de registro
    const puerto = document.getElementById("id_puerto_registro");
    if (puerto) {
      puerto.value = "";
    }

    // Limpiar IMO y habilitarlo
    imoInput.value = "";
    imoInput.readOnly = false;
    imoInput.style.backgroundColor = "";
    imoInput.style.color = "";
    imoInput.style.border = "";
    imoInput.style.cursor = "";
    imoInput.focus();

    // Actualizar estado
    imoDataLoaded = false;
    originalImo = null;
    updateButtonState(btnConsultar, false);
    setFieldsReadonly(false);

    // Ocultar status
    const statusIndicator = document.getElementById("imo-status");
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
      btn.innerHTML = "🚢 Consultar";
      btn.style.background = "linear-gradient(90deg, #0c4a6e, #0369a1)";
      btn.disabled = false;
    }
  }

  /**
   * Establece los campos como solo lectura o editables
   */
  function setFieldsReadonly(readonly) {
    IMO_READONLY_FIELDS.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        if (readonly) {
          // Estilos para tema oscuro - fondo oscuro con texto visible
          field.style.backgroundColor = "#2d3748";
          field.style.color = "#a0aec0";
          field.style.cursor = "not-allowed";
          field.style.border = "1px solid #4a5568";
          field.style.pointerEvents = "none";

          if (field.tagName === "INPUT" || field.tagName === "TEXTAREA") {
            field.readOnly = true;
          }
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

    // Campo bandera - bloquear si viene de API
    const bandera = document.getElementById(FIELD_BANDERA);
    if (bandera && readonly) {
      bandera.style.backgroundColor = "#2d3748";
      bandera.style.color = "#a0aec0";
      bandera.style.cursor = "not-allowed";
      bandera.style.border = "1px solid #4a5568";
      bandera.style.pointerEvents = "none";
    }
  }

  /**
   * Rellena los campos del formulario con datos de la API
   */
  function rellenarCampos(data) {
    // 1. Nombre del Buque (no editable)
    setFieldValue("id_nombre", data.nombre);

    // 3. Pabellón/Bandera (no editable si viene de API)
    if (data.bandera) {
      setFieldValue(FIELD_BANDERA, data.bandera);
    }

    // 5. Eslora (no editable)
    if (data.eslora) {
      setFieldValue("id_eslora_metros", data.eslora);
    }

    // 6. Manga (no editable)
    if (data.manga) {
      setFieldValue("id_manga_metros", data.manga);
    }

    // 7. Calado (híbrido - editable con nota)
    if (data.calado) {
      setFieldValue("id_calado_metros", data.calado);
      addCaladoNote();
    }

    // 8. Capacidad TEU (híbrido - alerta si es 0)
    const teu = data.teu || 0;
    if (teu > 0) {
      setFieldValue("id_teu_capacidad", teu);
    } else {
      // TEU es 0, mostrar alerta
      showTeuAlert();
    }

    // 9. Puerto de Registro - prellenar con país
    if (data.bandera) {
      const puerto = document.getElementById("id_puerto_registro");
      if (puerto && !puerto.value) {
        puerto.value = data.bandera + ", ";
        puerto.focus();
        // Mover cursor al final
        puerto.setSelectionRange(puerto.value.length, puerto.value.length);
      }
    }

    // 10. Call Sign (no editable)
    if (data.call_sign) {
      setFieldValue("id_callsign", data.call_sign);
    }
  }

  /**
   * Establece el valor de un campo y lo resalta
   */
  function setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && value !== undefined && value !== null && value !== "") {
      field.value = value;
      highlightField(field);
    }
  }

  /**
   * Resalta un campo temporalmente (verde para tema oscuro)
   */
  function highlightField(field) {
    const originalBg = field.style.backgroundColor;
    const originalColor = field.style.color;
    field.style.backgroundColor = "#276749";
    field.style.color = "#c6f6d5";
    field.style.transition = "background-color 0.5s ease, color 0.5s ease";

    setTimeout(() => {
      // Solo restaurar si no es un campo readonly
      if (
        !IMO_READONLY_FIELDS.includes(field.id) &&
        field.id !== FIELD_BANDERA
      ) {
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
   * Inicializa el dropdown de países para bandera (modo manual)
   */
  function initBanderaDropdown() {
    const bandera = document.getElementById(FIELD_BANDERA);
    if (!bandera) return;

    // Crear datalist con países
    const datalistId = "paises-bandera-list";
    let datalist = document.getElementById(datalistId);

    if (!datalist) {
      datalist = document.createElement("datalist");
      datalist.id = datalistId;

      PAISES_BANDERA.forEach((pais) => {
        const option = document.createElement("option");
        option.value = pais;
        datalist.appendChild(option);
      });

      document.body.appendChild(datalist);
    }

    bandera.setAttribute("list", datalistId);
    bandera.setAttribute("autocomplete", "off");
  }

  /**
   * Inicializa helper para Puerto de Registro
   */
  function initPuertoRegistroHelper() {
    const puerto = document.getElementById("id_puerto_registro");
    if (!puerto) return;

    const helpText = document.createElement("span");
    helpText.style.cssText =
      "font-size: 11px; color: #a0aec0; margin-left: 10px;";
    helpText.textContent =
      "(El país se prellenará automáticamente si usa la API)";
    puerto.parentNode.appendChild(helpText);
  }

  /**
   * Agrega nota al campo de calado
   */
  function initCaladoHelper() {
    const calado = document.getElementById("id_calado_metros");
    if (!calado) return;

    // Agregar nota sobre dato híbrido
    const existingNote = calado.parentElement.querySelector(".calado-note");
    if (!existingNote) {
      const note = document.createElement("div");
      note.className = "calado-note";
      note.style.cssText = `
                font-size: 11px;
                color: #fbbf24;
                margin-top: 4px;
                display: none;
            `;
      note.innerHTML =
        "⚠️ Dato sugerido por AIS (Calado actual). Puede editarlo si necesita el Calado de Diseño.";
      calado.parentNode.appendChild(note);
    }
  }

  /**
   * Muestra la nota de calado
   */
  function addCaladoNote() {
    const note = document.querySelector(".calado-note");
    if (note) {
      note.style.display = "block";
    }
  }

  /**
   * Inicializa helper para TEU
   */
  function initTeuHelper() {
    const teu = document.getElementById("id_teu_capacidad");
    if (!teu) return;

    // Placeholder
    teu.setAttribute("placeholder", "Ingrese capacidad TEU");
  }

  /**
   * Muestra alerta de TEU faltante
   */
  function showTeuAlert() {
    const teu = document.getElementById("id_teu_capacidad");
    if (!teu) return;

    // Verificar si ya existe la alerta
    let alert = teu.parentElement.querySelector(".teu-alert");
    if (!alert) {
      alert = document.createElement("div");
      alert.className = "teu-alert";
      alert.style.cssText = `
                background: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 4px;
                padding: 8px;
                margin-top: 8px;
                font-size: 12px;
                color: #92400e;
            `;
      alert.innerHTML =
        "⚠️ <strong>Atención:</strong> La API no proporcionó la capacidad TEU. Por favor ingrese este dato manualmente.";
      teu.parentNode.appendChild(alert);
    }

    // Enfocar el campo
    teu.focus();
    teu.style.border = "2px solid #f59e0b";
  }
})();

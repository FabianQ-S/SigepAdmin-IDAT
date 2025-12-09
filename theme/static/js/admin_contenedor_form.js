/**
 * Lógica de auto-llenado para el formulario de Contenedor
 *
 * Sistema de botones ➡️ para auto-completar campos relacionados:
 * 1. Código ISO ➡️ BIC Propietario
 * 2. Arribo ➡️ Dirección, Carrier, Origen/Destino, Ubicación
 * 3. Tipo/Tamaño ➡️ Tara (kg)
 * 4. Transitario ➡️ Consignatario
 */

(function () {
  "use strict";

  // ====== CONSTANTES ======

  const TIPOS_CONTENEDOR = {
    "22G1": { nombre: "20' Dry Standard", tara_kg: 2200 },
    "22G0": { nombre: "20' Dry Standard (ventilado)", tara_kg: 2300 },
    "22R1": { nombre: "20' Reefer", tara_kg: 3100 },
    "22U1": { nombre: "20' Open Top", tara_kg: 2300 },
    "22P1": { nombre: "20' Flat Rack", tara_kg: 2500 },
    "22T1": { nombre: "20' Tank", tara_kg: 3600 },
    "42G1": { nombre: "40' Dry Standard", tara_kg: 3800 },
    "42G0": { nombre: "40' Dry Standard (ventilado)", tara_kg: 3900 },
    "45G1": { nombre: "40' High Cube (HC)", tara_kg: 3900 },
    "42R1": { nombre: "40' Reefer", tara_kg: 4500 },
    "45R1": { nombre: "40' Reefer High Cube", tara_kg: 4800 },
    "42U1": { nombre: "40' Open Top", tara_kg: 4000 },
    "42P1": { nombre: "40' Flat Rack", tara_kg: 4200 },
    L5G1: { nombre: "45' High Cube", tara_kg: 4800 },
  };

  // Datos del Puerto de Chancay - Perú
  const PUERTO_LOCAL = {
    pais: "Perú",
    puerto: "Chancay",
    ciudad: "Chancay",
    departamento: "Lima",
    codigo_puerto: "PECAY",
  };

  const PROPIETARIOS_BIC = {
    MSK: "Maersk",
    MSC: "Mediterranean Shipping Company",
    CMA: "CMA CGM",
    HPL: "Hapag-Lloyd",
    ONE: "Ocean Network Express",
    EVE: "Evergreen",
    HLC: "Hapag-Lloyd",
    YML: "Yang Ming Line",
    CSQ: "COSCO",
    OOC: "OOCL",
    ZIM: "ZIM",
    PIL: "Pacific International Lines",
    HMM: "Hyundai Merchant Marine",
    WHL: "Wan Hai Lines",
    TSL: "T.S. Lines",
    SIT: "Sitc Lines",
    APL: "APL (CMA CGM)",
  };

  // Cache de datos
  let arriboDataCache = {};

  // ====== FUNCIONES DE UTILIDAD ======

  function getElement(id) {
    return document.getElementById(id);
  }

  /**
   * Crea un botón de flecha azul para auto-completar
   */
  function createAutoFillButton(fieldId, tooltip, onClick) {
    console.log(`🔘 createAutoFillButton llamado para: ${fieldId}`);

    const field = getElement(fieldId);
    if (!field) {
      console.log(`❌ Campo no encontrado: ${fieldId}`);
      return null;
    }

    // Buscar el contenedor del campo
    const fieldWrapper = field.closest(".flex-container") || field.parentNode;

    // Verificar si ya existe el botón
    if (fieldWrapper.querySelector(".auto-fill-btn")) {
      console.log(`⚠️ Botón ya existe para: ${fieldId}`);
      return null;
    }

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "auto-fill-btn";
    btn.innerHTML = "➡️";
    btn.title = tooltip;
    btn.style.cssText = `
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      margin-left: 8px;
      background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
      transition: all 0.2s ease;
      vertical-align: middle;
    `;

    btn.addEventListener("mouseenter", function () {
      this.style.transform = "scale(1.1)";
      this.style.boxShadow = "0 4px 8px rgba(59, 130, 246, 0.4)";
    });

    btn.addEventListener("mouseleave", function () {
      this.style.transform = "scale(1)";
      this.style.boxShadow = "0 2px 4px rgba(59, 130, 246, 0.3)";
    });

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      // Animación de click
      this.style.transform = "scale(0.95)";
      setTimeout(() => {
        this.style.transform = "scale(1)";
      }, 100);
      onClick();
    });

    // Insertar después del campo (o del select2 container si existe)
    const select2Container = fieldWrapper.querySelector(".select2-container");
    if (select2Container) {
      select2Container.insertAdjacentElement("afterend", btn);
      console.log(`✅ Botón ➡️ insertado después de select2 para: ${fieldId}`);
    } else {
      field.insertAdjacentElement("afterend", btn);
      console.log(`✅ Botón ➡️ insertado después del campo: ${fieldId}`);
    }

    return btn;
  }

  /**
   * Muestra mensaje de éxito al auto-completar
   */
  function showSuccessMessage(fieldId, message) {
    const field = getElement(fieldId);
    if (!field) return;

    const fieldRow = field.closest(".form-row") || field.parentNode;

    // Remover mensaje anterior
    const existing = fieldRow.querySelector(".auto-fill-success");
    if (existing) existing.remove();

    const msg = document.createElement("div");
    msg.className = "auto-fill-success";
    msg.innerHTML = `✅ ${message}`;
    msg.style.cssText = `
      font-size: 11px;
      color: #059669;
      margin-top: 4px;
      padding: 6px 10px;
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
      border-left: 3px solid #10b981;
      border-radius: 0 6px 6px 0;
      animation: fadeIn 0.3s ease;
    `;

    fieldRow.appendChild(msg);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
      msg.style.opacity = "0";
      msg.style.transition = "opacity 0.3s";
      setTimeout(() => msg.remove(), 300);
    }, 5000);
  }

  /**
   * Marca campo como auto-completado visualmente
   */
  function markAsAutoFilled(fieldId) {
    const field = getElement(fieldId);
    if (!field) return;

    field.style.backgroundColor = "#f0f9ff";
    field.style.borderColor = "#3b82f6";
    field.style.color = "#1e3a5f";

    // Agregar indicador ⚡ si no existe
    const fieldRow = field.closest(".form-row") || field.parentNode;
    if (!fieldRow.querySelector(".auto-filled-indicator")) {
      const indicator = document.createElement("span");
      indicator.className = "auto-filled-indicator";
      indicator.innerHTML = "⚡";
      indicator.title = "Campo auto-completado";
      indicator.style.cssText = `
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        margin-left: 6px;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        border-radius: 50%;
        font-size: 10px;
        vertical-align: middle;
      `;

      const label = fieldRow.querySelector("label");
      if (label) {
        label.appendChild(indicator);
      }
    }
  }

  // ====== 1. CÓDIGO ISO ➡️ BIC PROPIETARIO ======

  function initCodigoIsoAutoFill() {
    const codigoIsoField = getElement("id_codigo_iso");
    const bicField = getElement("id_bic_propietario");

    if (!codigoIsoField || !bicField) return;

    // Hacer BIC visualmente como solo lectura
    bicField.style.backgroundColor = "#f3f4f6";
    bicField.style.color = "#1f2937";

    // Crear botón de auto-completar
    createAutoFillButton(
      "id_codigo_iso",
      "Auto-completar BIC Propietario desde Código ISO",
      function () {
        const codigo = codigoIsoField.value.toUpperCase().trim();
        if (codigo.length >= 3) {
          const bic = codigo.substring(0, 3);
          bicField.value = bic;
          markAsAutoFilled("id_bic_propietario");

          const propietario = PROPIETARIOS_BIC[bic];
          const mensaje = propietario
            ? `BIC: ${bic} (${propietario})`
            : `BIC: ${bic}`;
          showSuccessMessage("id_codigo_iso", mensaje);
        } else {
          alert("Ingrese un Código ISO válido (mínimo 3 caracteres)");
        }
      }
    );
  }

  // ====== 2. ARRIBO ➡️ DIRECCIÓN, CARRIER, ORIGEN/DESTINO ======

  function initArriboAutoFill() {
    const arriboSelect = getElement("id_arribo");
    if (!arriboSelect) return;

    // Crear botón de auto-completar
    const initButton = function () {
      // Esperar a que select2 se inicialice
      const fieldWrapper =
        arriboSelect.closest(".flex-container") || arriboSelect.parentNode;
      const select2Container = fieldWrapper.querySelector(".select2-container");

      if (!select2Container) {
        setTimeout(initButton, 200);
        return;
      }

      createAutoFillButton(
        "id_arribo",
        "Auto-completar Dirección, Carrier y Origen/Destino desde Arribo",
        async function () {
          const arriboId = arriboSelect.value;
          if (!arriboId) {
            alert("Seleccione un Arribo primero");
            return;
          }

          // Obtener datos del arribo
          try {
            let arriboData = arriboDataCache[arriboId];

            if (!arriboData) {
              const response = await fetch(`/api/arribo/${arriboId}/`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
              });

              if (!response.ok) throw new Error("Error al obtener arribo");

              const data = await response.json();
              if (!data.success) throw new Error("Arribo no encontrado");

              arriboData = {
                tipoOperacion: data.arribo.tipo_operacion,
                naviera: data.arribo.naviera,
                buqueNombre: data.arribo.buque_nombre,
                fechaEta: data.arribo.fecha_eta,
                fechaEtd: data.arribo.fecha_etd,
              };
              arriboDataCache[arriboId] = arriboData;
            }

            // Aplicar datos
            let completados = [];

            // Dirección
            const direccionField = getElement("id_direccion");
            if (direccionField && arriboData.tipoOperacion) {
              if (arriboData.tipoOperacion === "DESCARGA") {
                direccionField.value = "IMPORT";
                markAsAutoFilled("id_direccion");
                completados.push("Dirección→Import");
              } else if (arriboData.tipoOperacion === "CARGA") {
                direccionField.value = "EXPORT";
                markAsAutoFilled("id_direccion");
                completados.push("Dirección→Export");
              }

              // Disparar evento change DESPUÉS de asignar valor para activar botones
              console.log(
                "🔔 Disparando evento change en dirección:",
                direccionField.value
              );
              const changeEvent = new Event("change", { bubbles: true });
              direccionField.dispatchEvent(changeEvent);
            }

            // Carrier
            const carrierField = getElement("id_carrier");
            if (carrierField) {
              const naviera = arriboData.naviera || arriboData.buqueNombre;
              if (naviera) {
                carrierField.value = naviera;
                markAsAutoFilled("id_carrier");
                completados.push(`Carrier→${naviera}`);
              }
            }

            // Guardar fechas para validación
            if (arriboData.fechaEta) {
              arriboSelect.dataset.fechaEta = arriboData.fechaEta;
            }
            if (arriboData.fechaEtd) {
              arriboSelect.dataset.fechaEtd = arriboData.fechaEtd;
            }

            showSuccessMessage("id_arribo", completados.join(" | "));
          } catch (error) {
            console.error("Error:", error);
            alert("No se pudo obtener datos del arribo");
          }
        }
      );
    };

    setTimeout(initButton, 500);
  }

  /**
   * Aplica lógica de origen/destino según dirección
   */
  function applyDireccionLogic(direccion) {
    if (direccion === "IMPORT") {
      // Import: Destino es Perú
      setFieldIfEmpty("id_destino_pais", PUERTO_LOCAL.pais);
      setFieldIfEmpty("id_destino_puerto", PUERTO_LOCAL.puerto);
      setFieldIfEmpty("id_destino_ciudad", PUERTO_LOCAL.ciudad);
      markAsAutoFilled("id_destino_pais");

      // Ubicación: A BORDO
      setFieldIfEmpty("id_ubicacion_actual", "A BORDO");
      markAsAutoFilled("id_ubicacion_actual");
    } else if (direccion === "EXPORT") {
      // Export: Origen es Perú
      setFieldIfEmpty("id_origen_pais", PUERTO_LOCAL.pais);
      setFieldIfEmpty("id_origen_puerto", PUERTO_LOCAL.puerto);
      setFieldIfEmpty("id_origen_ciudad", PUERTO_LOCAL.ciudad);
      markAsAutoFilled("id_origen_pais");

      // Ubicación: GATE IN
      setFieldIfEmpty("id_ubicacion_actual", "GATE IN");
      markAsAutoFilled("id_ubicacion_actual");
    }
  }

  function setFieldIfEmpty(fieldId, value) {
    const field = getElement(fieldId);
    if (field && !field.value) {
      field.value = value;
    }
  }

  // ====== 3. TIPO/TAMAÑO ➡️ TARA ======

  function initTipoTamañoAutoFill() {
    const tipoField = getElement("id_tipo_tamaño");
    const taraField = getElement("id_tara_kg");

    if (!tipoField || !taraField) return;

    // Hacer tara visualmente como auto-completado
    taraField.style.backgroundColor = "#f3f4f6";

    createAutoFillButton(
      "id_tipo_tamaño",
      "Auto-completar Tara según tipo de contenedor",
      function () {
        const tipo = tipoField.value;
        const info = TIPOS_CONTENEDOR[tipo];

        if (info && info.tara_kg) {
          taraField.value = info.tara_kg;
          markAsAutoFilled("id_tara_kg");
          showSuccessMessage(
            "id_tipo_tamaño",
            `Tara: ${info.tara_kg} kg (${info.nombre})`
          );
        } else {
          alert("Seleccione un Tipo/Tamaño válido primero");
        }
      }
    );
  }

  // ====== 4. TRANSITARIO ➡️ CONSIGNATARIO ======

  function initTransitarioAutoFill() {
    const transitarioSelect = getElement("id_transitario");
    const consignatarioField = getElement("id_consignatario");

    if (!transitarioSelect || !consignatarioField) return;

    // Hacer consignatario visualmente como auto-completado
    consignatarioField.style.backgroundColor = "#f3f4f6";
    consignatarioField.style.color = "#1f2937";

    const initButton = function () {
      const fieldWrapper =
        transitarioSelect.closest(".flex-container") ||
        transitarioSelect.parentNode;
      const select2Container = fieldWrapper.querySelector(".select2-container");

      if (!select2Container) {
        setTimeout(initButton, 200);
        return;
      }

      createAutoFillButton(
        "id_transitario",
        "Auto-completar Consignatario desde Transitario",
        function () {
          // Obtener nombre del transitario seleccionado
          let transitarioNombre = "";

          // Intentar obtener de select2
          if (typeof jQuery !== "undefined") {
            const $select = jQuery(transitarioSelect);
            const data = $select.select2("data");
            if (data && data[0] && data[0].text) {
              transitarioNombre = data[0].text;
            }
          }

          // Fallback a opción seleccionada
          if (!transitarioNombre && transitarioSelect.selectedIndex >= 0) {
            const option =
              transitarioSelect.options[transitarioSelect.selectedIndex];
            if (option && option.value) {
              transitarioNombre = option.text || option.textContent;
            }
          }

          if (transitarioNombre && transitarioNombre !== "---------") {
            consignatarioField.value = transitarioNombre;
            markAsAutoFilled("id_consignatario");
            showSuccessMessage(
              "id_transitario",
              `Consignatario: ${transitarioNombre}`
            );
          } else {
            alert("Seleccione un Transitario primero");
          }
        }
      );
    };

    setTimeout(initButton, 500);
  }

  // ====== 5. ORIGEN ➡️ AUTO-COMPLETAR CON PERÚ (solo si EXPORT) ======

  // ====== 5. ORIGEN ➡️ AUTO-COMPLETAR CON PUERTO DE CHANCAY ======

  function initOrigenAutoFill() {
    const origenPaisField = getElement("id_origen_pais");

    if (!origenPaisField) {
      console.log("❌ Origen: No se encontró origen_pais");
      return;
    }

    console.log("🌍 Iniciando auto-fill de Origen...");

    // Siempre mostrar botón para auto-completar con Puerto de Chancay
    createAutoFillButton(
      "id_origen_pais",
      "🇵🇪 Auto-completar con Puerto de Chancay",
      function () {
        getElement("id_origen_pais").value = PUERTO_LOCAL.pais;
        getElement("id_origen_puerto").value = PUERTO_LOCAL.puerto;
        getElement("id_origen_ciudad").value = PUERTO_LOCAL.ciudad;
        markAsAutoFilled("id_origen_pais");
        markAsAutoFilled("id_origen_puerto");
        markAsAutoFilled("id_origen_ciudad");
        showSuccessMessage(
          "id_origen_pais",
          `Origen: Puerto de ${PUERTO_LOCAL.puerto}, ${PUERTO_LOCAL.pais}`
        );
      }
    );
  }

  // ====== 6. DESTINO ➡️ AUTO-COMPLETAR CON PUERTO DE CHANCAY ======

  function initDestinoAutoFill() {
    const destinoPaisField = getElement("id_destino_pais");

    if (!destinoPaisField) {
      console.log("❌ Destino: No se encontró destino_pais");
      return;
    }

    console.log("📍 Iniciando auto-fill de Destino...");

    // Siempre mostrar botón para auto-completar con Puerto de Chancay
    createAutoFillButton(
      "id_destino_pais",
      "🇵🇪 Auto-completar con Puerto de Chancay",
      function () {
        getElement("id_destino_pais").value = PUERTO_LOCAL.pais;
        getElement("id_destino_puerto").value = PUERTO_LOCAL.puerto;
        getElement("id_destino_ciudad").value = PUERTO_LOCAL.ciudad;
        markAsAutoFilled("id_destino_pais");
        markAsAutoFilled("id_destino_puerto");
        markAsAutoFilled("id_destino_ciudad");
        showSuccessMessage(
          "id_destino_pais",
          `Destino: Puerto de ${PUERTO_LOCAL.puerto}, ${PUERTO_LOCAL.pais}`
        );
      }
    );
  }

  // ====== 7. UBICACIÓN ➡️ AUTO-COMPLETAR SEGÚN DIRECCIÓN ======

  function initUbicacionAutoFill() {
    const direccionField = getElement("id_direccion");
    const ubicacionField = getElement("id_ubicacion_actual");

    if (!direccionField || !ubicacionField) {
      console.log("❌ Ubicación: No se encontró dirección o ubicacion_actual");
      return;
    }

    console.log("📍 Iniciando auto-fill de Ubicación...");

    const createUbicacionButton = function () {
      // Remover botón anterior si existe
      const existingBtn =
        ubicacionField.parentNode.querySelector(".auto-fill-btn");
      if (existingBtn) existingBtn.remove();

      const direccion = direccionField.value;
      console.log("📍 Ubicación - Dirección actual:", direccion);

      // Mostrar botón si hay dirección seleccionada
      if (direccion === "IMPORT" || direccion === "EXPORT") {
        const valorSugerido = direccion === "IMPORT" ? "A BORDO" : "GATE IN";
        const tooltip =
          direccion === "IMPORT"
            ? "🚢 Sugerir ubicación: A BORDO (Import)"
            : "🚛 Sugerir ubicación: GATE IN (Export)";

        console.log(
          "✅ Ubicación: Creando botón para",
          direccion,
          "->",
          valorSugerido
        );
        createAutoFillButton("id_ubicacion_actual", tooltip, function () {
          ubicacionField.value = valorSugerido;
          markAsAutoFilled("id_ubicacion_actual");
          showSuccessMessage(
            "id_ubicacion_actual",
            `Ubicación: ${valorSugerido}`
          );
        });
      }
    };

    // Escuchar cambios en dirección
    direccionField.addEventListener("change", function () {
      console.log("🔄 Ubicación - Dirección cambió a:", this.value);
      createUbicacionButton();
    });

    // Verificar estado inicial con delay más largo
    setTimeout(createUbicacionButton, 800);
  }

  // ====== 8. REFERENCIA VISUAL DE TARA EN PESO BRUTO ======

  function initTaraReference() {
    const pesoBrutoField = getElement("id_peso_bruto_kg");
    const taraField = getElement("id_tara_kg");

    console.log("📦 Buscando campos para Tara Reference:");
    console.log("  - peso_bruto_kg:", pesoBrutoField);
    console.log("  - tara_kg:", taraField);

    if (!pesoBrutoField || !taraField) {
      console.log("❌ No se encontró peso_bruto o tara");
      return;
    }

    console.log("📦 Iniciando referencia de Tara...");

    // Crear contenedor de referencia
    const taraRefContainer = document.createElement("div");
    taraRefContainer.id = "tara-reference";
    taraRefContainer.style.cssText = `
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      margin: 10px 0;
      background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
      border: 2px solid #3b82f6;
      border-radius: 8px;
      font-size: 13px;
      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    `;

    const updateTaraRef = function () {
      const tara = parseFloat(taraField.value) || 0;
      if (tara > 0) {
        taraRefContainer.innerHTML = `
          <span style="color: #60a5fa; font-weight: 600;">📦 Tara del contenedor:</span>
          <span style="color: #fbbf24; font-weight: 700; font-size: 16px;">${tara.toLocaleString()} kg</span>
          <span style="color: #93c5fd; font-size: 11px;">(El peso bruto debe ser mayor)</span>
        `;
      } else {
        taraRefContainer.innerHTML = `
          <span style="color: #f59e0b; font-weight: 600;">⚠️ Tara no definida</span>
          <span style="color: #9ca3af; font-size: 11px;">→ Seleccione Tipo/Tamaño en "Paso 1" y presione ➡️</span>
        `;
      }
    };

    // Buscar el fieldset de "Contenido y Pesos" o el form-row del peso bruto
    const pesoBrutoRow = pesoBrutoField.closest(".form-row");
    const fieldset = pesoBrutoField.closest("fieldset");

    if (fieldset) {
      // Insertar después del título del fieldset
      const fieldsetContent = fieldset.querySelector(
        ".fieldset-content, .form-row"
      );
      if (fieldsetContent) {
        fieldset.insertBefore(taraRefContainer, fieldsetContent);
        console.log("✅ Referencia de Tara insertada en fieldset");
      } else {
        // Insertar al inicio del fieldset después del h2
        const h2 = fieldset.querySelector("h2");
        if (h2 && h2.nextSibling) {
          fieldset.insertBefore(taraRefContainer, h2.nextSibling);
          console.log("✅ Referencia de Tara insertada después de h2");
        } else {
          fieldset.appendChild(taraRefContainer);
          console.log("✅ Referencia de Tara añadida al fieldset");
        }
      }
    } else if (pesoBrutoRow) {
      pesoBrutoRow.parentNode.insertBefore(taraRefContainer, pesoBrutoRow);
      console.log("✅ Referencia de Tara insertada antes del form-row");
    } else {
      // Fallback: insertar justo antes del campo
      pesoBrutoField.parentNode.insertBefore(taraRefContainer, pesoBrutoField);
      console.log("✅ Referencia de Tara insertada antes del campo");
    }

    // Actualizar cuando cambie la tara
    taraField.addEventListener("input", updateTaraRef);
    taraField.addEventListener("change", updateTaraRef);

    // Estado inicial
    updateTaraRef();

    // Verificar periódicamente por cambios programáticos
    setInterval(updateTaraRef, 1500);
  }

  // ====== VALIDACIONES ======

  function initValidations() {
    // Validación Peso Bruto > Tara
    const pesoBrutoField = getElement("id_peso_bruto_kg");
    const taraField = getElement("id_tara_kg");

    if (pesoBrutoField && taraField) {
      const validatePesos = function () {
        const pesoBruto = parseFloat(pesoBrutoField.value) || 0;
        const tara = parseFloat(taraField.value) || 0;

        // Remover warning anterior
        const existing =
          pesoBrutoField.parentNode.querySelector(".peso-warning");
        if (existing) existing.remove();

        if (pesoBruto > 0 && tara > 0) {
          if (pesoBruto < tara) {
            const warning = document.createElement("div");
            warning.className = "peso-warning";
            warning.style.cssText = `
              font-size: 11px;
              color: #dc2626;
              margin-top: 4px;
              padding: 4px 8px;
              background: #fef2f2;
              border-left: 3px solid #ef4444;
              border-radius: 0 4px 4px 0;
            `;
            warning.textContent =
              "⚠️ El peso bruto no puede ser menor que la tara";
            pesoBrutoField.parentNode.appendChild(warning);
          } else {
            const cargaNeta = pesoBruto - tara;
            showSuccessMessage(
              "id_peso_bruto_kg",
              `Carga neta: ${cargaNeta.toLocaleString()} kg`
            );
          }
        }
      };

      pesoBrutoField.addEventListener("input", validatePesos);
      taraField.addEventListener("input", validatePesos);
    }

    // Validación Fecha Retiro vs ETA/ETD
    const fechaRetiroField = getElement("id_fecha_retiro_transitario_0");
    const direccionField = getElement("id_direccion");
    const arriboSelect = getElement("id_arribo");

    if (fechaRetiroField && direccionField && arriboSelect) {
      fechaRetiroField.addEventListener("change", function () {
        const direccion = direccionField.value;
        const fechaRetiro = this.value;

        if (!fechaRetiro) return;

        const fechaEta = arriboSelect.dataset.fechaEta;
        const fechaEtd = arriboSelect.dataset.fechaEtd;

        // Remover warning anterior
        const existing = this.parentNode.querySelector(".date-warning");
        if (existing) existing.remove();

        let warning = null;

        if (direccion === "IMPORT" && fechaEta) {
          if (new Date(fechaRetiro) < new Date(fechaEta.split("T")[0])) {
            warning = `⚠️ La fecha de retiro no puede ser anterior al arribo (ETA: ${
              fechaEta.split("T")[0]
            })`;
          }
        } else if (direccion === "EXPORT" && fechaEtd) {
          if (new Date(fechaRetiro) > new Date(fechaEtd.split("T")[0])) {
            warning = `⚠️ La fecha de entrega debe ser antes de la salida (ETD: ${
              fechaEtd.split("T")[0]
            })`;
          }
        }

        if (warning) {
          const warningEl = document.createElement("div");
          warningEl.className = "date-warning";
          warningEl.style.cssText = `
            font-size: 11px;
            color: #dc2626;
            margin-top: 4px;
            padding: 4px 8px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            border-radius: 0 4px 4px 0;
          `;
          warningEl.textContent = warning;
          this.parentNode.appendChild(warningEl);
        }
      });
    }
  }

  // ====== ESTILOS GLOBALES ======

  function addGlobalStyles() {
    if (document.getElementById("contenedor-autofill-styles")) return;

    const style = document.createElement("style");
    style.id = "contenedor-autofill-styles";
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .auto-fill-btn:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
      }

      /* ===== SECCIÓN 1: DATOS FUENTE (Azul) ===== */
      fieldset:first-of-type {
        border: 3px solid #2563eb !important;
        background: #1e3a5f !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
      }

      fieldset:first-of-type h2 {
        color: #60a5fa !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
      }

      fieldset:first-of-type .description {
        color: #93c5fd !important;
        font-size: 12px !important;
        background: rgba(59, 130, 246, 0.2) !important;
        padding: 8px 12px !important;
        border-radius: 4px !important;
        margin-bottom: 10px !important;
      }

      fieldset:first-of-type .form-row > div > label {
        color: #bfdbfe !important;
        font-weight: 600 !important;
      }

      fieldset:first-of-type .help {
        color: #93c5fd !important;
      }

      /* ===== SECCIÓN 2: DATOS AUTO-COMPLETADOS (Amarillo/Ámbar) ===== */
      fieldset:nth-of-type(2) {
        border: 3px solid #d97706 !important;
        background: #422006 !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
      }

      fieldset:nth-of-type(2) h2 {
        color: #fbbf24 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
      }

      fieldset:nth-of-type(2) .description {
        color: #fcd34d !important;
        font-size: 12px !important;
        background: rgba(245, 158, 11, 0.2) !important;
        padding: 8px 12px !important;
        border-radius: 4px !important;
        margin-bottom: 10px !important;
      }

      fieldset:nth-of-type(2) .form-row > div > label {
        color: #fde68a !important;
        font-weight: 600 !important;
      }

      fieldset:nth-of-type(2) .help {
        color: #fcd34d !important;
      }

      /* Campos de entrada en secciones destacadas */
      fieldset:first-of-type input,
      fieldset:first-of-type select,
      fieldset:nth-of-type(2) input,
      fieldset:nth-of-type(2) select {
        background-color: #1f2937 !important;
        color: #f9fafb !important;
        border: 1px solid #4b5563 !important;
      }

      fieldset:first-of-type input:focus,
      fieldset:first-of-type select:focus,
      fieldset:nth-of-type(2) input:focus,
      fieldset:nth-of-type(2) select:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.3) !important;
      }

      /* Select2 en secciones destacadas */
      fieldset:first-of-type .select2-container--default .select2-selection--single,
      fieldset:nth-of-type(2) .select2-container--default .select2-selection--single {
        background-color: #1f2937 !important;
        border: 1px solid #4b5563 !important;
      }

      fieldset:first-of-type .select2-container--default .select2-selection--single .select2-selection__rendered,
      fieldset:nth-of-type(2) .select2-container--default .select2-selection--single .select2-selection__rendered {
        color: #f9fafb !important;
      }
    `;
    document.head.appendChild(style);
  }

  // ====== INICIALIZACIÓN ======

  function init() {
    // Verificar que estamos en el formulario de contenedor
    const form = document.querySelector('form[action*="contenedor"]');
    if (!form && !getElement("id_codigo_iso")) return;

    console.log("🚛 Inicializando formulario de Contenedor con botones ➡️...");

    addGlobalStyles();
    initCodigoIsoAutoFill();
    initArriboAutoFill();
    initTipoTamañoAutoFill();
    initTransitarioAutoFill();
    initOrigenAutoFill();
    initDestinoAutoFill();
    initUbicacionAutoFill();
    initTaraReference();
    initValidations();

    console.log("✅ Formulario de Contenedor configurado");
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 300);
  }
})();

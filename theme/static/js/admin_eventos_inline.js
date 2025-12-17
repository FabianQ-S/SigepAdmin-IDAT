/**
 * Admin Eventos Inline - Automatización y validaciones
 *
 * Funcionalidades:
 * 1. Auto-completar ubicación para eventos locales (Puerto de Chancay)
 * 2. Vincular tipo_evento con medio_transporte
 * 3. Visual alerts para eventos especiales (CUSTOMS_HOLD, DAMAGED)
 * 4. Validación cronológica visual
 * 5. Bloqueo/desbloqueo inteligente de campos según tipo de evento
 */
(function () {
  "use strict";

  // === CONFIGURACIÓN ===
  const PUERTO_LOCAL = {
    pais: "Perú",
    puerto: "Chancay",
    ciudad: "Chancay",
  };

  // ====== MATRIZ DE VALIDACIONES POR EVENTO ======
  // Cada evento define qué campos están habilitados y sus valores por defecto
  const EVENTO_CONFIG = {
    // === INICIO: Preparación y carga ===
    GATE_OUT_EMPTY: {
      descripcion: "Retiro de contenedor vacío del depósito",
      medioTransporte: { valor: "TRUCK", bloqueado: true },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Depósito de vacíos, Terminal...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "normal",
    },
    GATE_IN_FULL: {
      descripcion: "Ingreso de contenedor cargado al puerto",
      medioTransporte: { valor: "TRUCK", bloqueado: true },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Terminal de carga, Puerto...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "normal",
    },
    LOADED: {
      descripcion: "Contenedor cargado al buque",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: { placeholder: "Puerto de embarque...", autocompletar: true },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "maritimo",
    },
    // === INTERMEDIO: Tránsito marítimo ===
    DEPARTED: {
      descripcion: "Buque zarpó del puerto",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: false, limpiar: true }, // No aplica - zarpe
      lugar: { placeholder: "Puerto de origen...", autocompletar: true },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "maritimo",
    },
    IN_TRANSIT: {
      descripcion: "En tránsito marítimo",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: false, limpiar: true }, // No hay ciudad en el océano
      lugar: { placeholder: "Océano Pacífico, Mar Caribe, Canal de Panamá..." },
      pais: { habilitado: false, limpiar: true }, // No hay país en aguas internacionales
      esLocal: false,
      estilo: "maritimo",
    },
    TRANSSHIPMENT: {
      descripcion: "Transbordo en puerto intermedio",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: true },
      lugar: { placeholder: "Puerto de transbordo..." },
      pais: { habilitado: true },
      esLocal: false,
      estilo: "maritimo",
    },
    ARRIVED: {
      descripcion: "Buque arribó al puerto destino",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: { placeholder: "Puerto de destino...", autocompletar: true },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "maritimo",
    },
    // === FINAL: Descarga y entrega ===
    DISCHARGED: {
      descripcion: "Contenedor descargado del buque",
      medioTransporte: { valor: "VESSEL", bloqueado: true },
      buque: { habilitado: true, requerido: true },
      referenciaViaje: { habilitado: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: { placeholder: "Terminal de descarga...", autocompletar: true },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "maritimo",
    },
    GATE_OUT_FULL: {
      descripcion: "Salida del contenedor cargado del puerto",
      medioTransporte: { valor: "TRUCK", bloqueado: false },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Terminal, puerta de salida...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "normal",
    },
    DELIVERED: {
      descripcion: "Entregado al cliente final",
      medioTransporte: { valor: "TRUCK", bloqueado: false },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true },
      lugar: { placeholder: "Almacén del cliente, dirección de entrega..." },
      pais: { habilitado: true },
      esLocal: false,
      estilo: "liberacion",
    },
    GATE_IN_EMPTY: {
      descripcion: "Devolución del contenedor vacío",
      medioTransporte: { valor: "TRUCK", bloqueado: true },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Depósito de vacíos, Terminal...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "liberacion",
    },
    // === EXCEPCIONES: Eventos especiales ===
    CUSTOMS_HOLD: {
      descripcion: "Retención aduanera",
      medioTransporte: { valor: null, bloqueado: false },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Zona de inspección, Almacén aduanero...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "alerta",
    },
    CUSTOMS_RELEASED: {
      descripcion: "Liberado por aduana",
      medioTransporte: { valor: null, bloqueado: false },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: {
        placeholder: "Zona de inspección, Almacén aduanero...",
        autocompletar: true,
      },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "liberacion",
    },
    INSPECTION: {
      descripcion: "En inspección",
      medioTransporte: { valor: null, bloqueado: false },
      buque: { habilitado: false, limpiar: true },
      referenciaViaje: { habilitado: false, limpiar: true },
      ciudad: { habilitado: true, autocompletar: true },
      lugar: { placeholder: "Zona de inspección...", autocompletar: true },
      pais: { autocompletar: true },
      esLocal: true,
      estilo: "alerta",
    },
    DAMAGED: {
      descripcion: "Daño reportado",
      medioTransporte: { valor: null, bloqueado: false },
      buque: { habilitado: false },
      referenciaViaje: { habilitado: false },
      ciudad: { habilitado: true },
      lugar: { placeholder: "Ubicación donde se detectó el daño..." },
      pais: { habilitado: true },
      esLocal: false,
      estilo: "alerta",
    },
  };

  // Estilos por categoría
  const ESTILOS = {
    normal: { bg: "", border: "" },
    maritimo: { bg: "#1a3a5c", border: "#2196f3" },
    alerta: { bg: "#5c2626", border: "#f44336" },
    liberacion: { bg: "#1b3d1f", border: "#4caf50" },
  };

  /**
   * Bloquea visualmente un campo sin deshabilitarlo
   * IMPORTANTE: No usamos disabled=true porque impide que el valor se envíe al servidor
   * El servidor auto-asigna los valores correctos según el tipo de evento
   */
  function setFieldState(field, bloqueado, reason = "") {
    if (!field) return;

    // NO deshabilitar - solo aplicar estilos visuales
    // field.disabled = bloqueado; // ← REMOVIDO: causaba que no se enviara el valor

    if (bloqueado) {
      field.style.backgroundColor = "#1a1a1a";
      field.style.opacity = "0.5";
      field.style.cursor = "not-allowed";
      field.style.pointerEvents = "none"; // Bloquea interacción sin deshabilitar
      field.title = reason || "Campo auto-asignado según tipo de evento";
      field.tabIndex = -1; // Evita navegación por teclado
    } else {
      field.style.backgroundColor = "";
      field.style.opacity = "1";
      field.style.cursor = "";
      field.style.pointerEvents = "";
      field.title = "";
      field.tabIndex = 0;
    }
  }

  /**
   * Procesa una fila de evento inline
   */
  function processEventRow(row) {
    const tipoEventoSelect = row.querySelector('select[name$="-tipo_evento"]');
    const ubicacionPuertoInput = row.querySelector(
      'input[name$="-ubicacion_puerto"]'
    );
    const ubicacionCiudadInput = row.querySelector(
      'input[name$="-ubicacion_ciudad"]'
    );
    const ubicacionPaisInput = row.querySelector(
      'input[name$="-ubicacion_pais"]'
    );
    const medioTransporteSelect = row.querySelector(
      'select[name$="-medio_transporte"]'
    );
    const buqueSelect = row.querySelector(
      'select[name$="-buque"], input[name$="-buque"]'
    );
    const referenciaViajeInput = row.querySelector(
      'input[name$="-referencia_viaje"]'
    );

    if (!tipoEventoSelect) return;

    // Función para aplicar configuración según tipo de evento
    function aplicarConfiguracionEvento() {
      const tipoEvento = tipoEventoSelect.value;

      if (!tipoEvento || !EVENTO_CONFIG[tipoEvento]) {
        // Sin evento seleccionado - habilitar todos
        setFieldState(medioTransporteSelect, false);
        setFieldState(buqueSelect, false);
        setFieldState(referenciaViajeInput, false);
        setFieldState(ubicacionCiudadInput, false);
        setFieldState(ubicacionPaisInput, false);
        row.style.backgroundColor = "";
        row.style.borderLeft = "";
        return;
      }

      const config = EVENTO_CONFIG[tipoEvento];

      // ====== 1. MEDIO DE TRANSPORTE ======
      if (medioTransporteSelect) {
        // Filtrar opciones según tipo de evento
        const opcionesMaritimas = ["VESSEL"];
        const opcionesTerrestres = ["TRUCK", "RAIL", "BARGE"];
        
        // Restaurar todas las opciones primero
        const todasLasOpciones = [
          { value: "VESSEL", text: "Buque" },
          { value: "TRUCK", text: "Camión" },
          { value: "RAIL", text: "Ferrocarril" },
          { value: "BARGE", text: "Barcaza" },
        ];
        
        // Determinar opciones permitidas
        let opcionesPermitidas;
        if (config.buque.habilitado) {
          // Evento marítimo - solo Buque
          opcionesPermitidas = opcionesMaritimas;
        } else {
          // Evento terrestre - sin Buque
          opcionesPermitidas = opcionesTerrestres;
        }
        
        // Guardar valor actual
        const valorActual = medioTransporteSelect.value;
        
        // Limpiar y reconstruir opciones
        medioTransporteSelect.innerHTML = "";
        todasLasOpciones.forEach((opt) => {
          if (opcionesPermitidas.includes(opt.value)) {
            const option = document.createElement("option");
            option.value = opt.value;
            option.textContent = opt.text;
            medioTransporteSelect.appendChild(option);
          }
        });
        
        // Restaurar valor si es válido, sino usar el por defecto
        if (opcionesPermitidas.includes(valorActual)) {
          medioTransporteSelect.value = valorActual;
        } else if (config.medioTransporte.valor) {
          medioTransporteSelect.value = config.medioTransporte.valor;
        }
        
        setFieldState(
          medioTransporteSelect,
          config.medioTransporte.bloqueado,
          config.medioTransporte.bloqueado
            ? `Fijado para: ${config.descripcion}`
            : ""
        );
      }

      // ====== 2. BUQUE (Autocomplete Select2) ======
      if (buqueSelect) {
        const buqueCell = buqueSelect.closest("td");
        const buqueWrapper = buqueSelect.closest(".related-widget-wrapper");
        
        if (!config.buque.habilitado) {
          // Limpiar valor del buque
          if (buqueSelect.tagName === "SELECT") {
            buqueSelect.value = "";
            // Disparar evento para actualizar Select2
            buqueSelect.dispatchEvent(new Event("change"));
          } else if (buqueSelect.tagName === "INPUT") {
            buqueSelect.value = "";
          }
          
          // Bloquear toda la celda visualmente
          if (buqueCell) {
            buqueCell.style.opacity = "0.3";
            buqueCell.style.pointerEvents = "none";
            buqueCell.title = "No aplica para eventos terrestres";
          }
          
          // Ocultar botones de Select2 (+, ✏️, 🔍)
          if (buqueWrapper) {
            const actionButtons = buqueWrapper.querySelectorAll("a");
            actionButtons.forEach((btn) => {
              btn.style.display = "none";
            });
          }
        } else {
          // Habilitar campo
          if (buqueCell) {
            buqueCell.style.opacity = "1";
            buqueCell.style.pointerEvents = "";
            buqueCell.title = "";
          }
          
          // Mostrar botones
          if (buqueWrapper) {
            const actionButtons = buqueWrapper.querySelectorAll("a");
            actionButtons.forEach((btn) => {
              btn.style.display = "";
            });
          }
        }
        
        setFieldState(
          buqueSelect,
          !config.buque.habilitado,
          !config.buque.habilitado ? "No aplica para este evento" : ""
        );
      }

      // ====== 3. REFERENCIA DE VIAJE ======
      if (referenciaViajeInput) {
        setFieldState(
          referenciaViajeInput,
          !config.referenciaViaje.habilitado,
          !config.referenciaViaje.habilitado
            ? "Solo aplica para transporte marítimo"
            : ""
        );
        if (config.referenciaViaje.limpiar) {
          referenciaViajeInput.value = "";
        }
      }

      // ====== 4. CIUDAD ======
      if (ubicacionCiudadInput) {
        const ciudadHabilitada = config.ciudad.habilitado !== false;
        setFieldState(
          ubicacionCiudadInput,
          !ciudadHabilitada,
          !ciudadHabilitada ? "No aplica para este tipo de evento" : ""
        );
        if (config.ciudad.limpiar) {
          ubicacionCiudadInput.value = "";
        }
        if (
          config.ciudad.autocompletar &&
          config.esLocal &&
          !ubicacionCiudadInput.value
        ) {
          ubicacionCiudadInput.value = PUERTO_LOCAL.ciudad;
        }
      }

      // ====== 5. PAÍS ======
      if (ubicacionPaisInput) {
        const paisHabilitado = config.pais.habilitado !== false;
        setFieldState(
          ubicacionPaisInput,
          !paisHabilitado,
          !paisHabilitado ? "No aplica para este tipo de evento" : ""
        );
        if (config.pais.limpiar) {
          ubicacionPaisInput.value = "";
        }
        if (
          config.pais.autocompletar &&
          config.esLocal &&
          !ubicacionPaisInput.value
        ) {
          ubicacionPaisInput.value = PUERTO_LOCAL.pais;
        }
      }

      // ====== 6. LUGAR (PUERTO) ======
      if (ubicacionPuertoInput) {
        ubicacionPuertoInput.placeholder = config.lugar.placeholder || "";
        if (
          config.lugar.autocompletar &&
          config.esLocal &&
          !ubicacionPuertoInput.value
        ) {
          ubicacionPuertoInput.value = PUERTO_LOCAL.puerto;
        }
      }

      // ====== 7. APLICAR ESTILO DE FILA ======
      const estilo = ESTILOS[config.estilo] || ESTILOS.normal;
      row.style.backgroundColor = estilo.bg;
      row.style.borderLeft = estilo.border ? `4px solid ${estilo.border}` : "";

      // Aplicar clase para CSS
      row.classList.remove(
        "evento-alerta",
        "evento-liberacion",
        "evento-maritimo"
      );
      if (config.estilo === "alerta") row.classList.add("evento-alerta");
      else if (config.estilo === "liberacion")
        row.classList.add("evento-liberacion");
      else if (config.estilo === "maritimo")
        row.classList.add("evento-maritimo");

      // Aplicar colores de texto para filas con fondo
      if (estilo.bg) {
        const allInputs = row.querySelectorAll("input, select, textarea");
        allInputs.forEach((el) => {
          el.style.color = "#ffffff";
          if (el.tagName === "SELECT" || el.tagName === "INPUT") {
            el.style.backgroundColor = estilo.bg;
          }
        });
      }
    }

    // Escuchar cambios en tipo_evento
    tipoEventoSelect.addEventListener("change", aplicarConfiguracionEvento);

    // Procesar estado inicial si ya tiene valor
    if (tipoEventoSelect.value) {
      aplicarConfiguracionEvento();
    }
  }

  /**
   * Agrega indicadores visuales al inline header
   */
  function addInlineHeader() {
    const inlineGroup = document.querySelector(
      ".inline-group:has([id*='eventocontenedor'])"
    );
    if (!inlineGroup) return;

    // Verificar si el contenedor tiene bloqueo activo
    const bloqueadoField = document.querySelector("#id_bloqueado_por_evento");
    if (bloqueadoField && bloqueadoField.checked) {
      const header = inlineGroup.querySelector("h2");
      if (header && !header.querySelector(".alerta-bloqueo")) {
        const alertSpan = document.createElement("span");
        alertSpan.className = "alerta-bloqueo";
        alertSpan.style.cssText = `
          background-color: #f44336;
          color: white;
          padding: 2px 8px;
          border-radius: 4px;
          margin-left: 10px;
          font-size: 12px;
          font-weight: bold;
        `;
        alertSpan.textContent = "⚠️ CONTENEDOR BLOQUEADO";
        header.appendChild(alertSpan);
      }
    }
  }

  /**
   * Observar cuando se agregan nuevas filas dinámicamente
   */
  function observeNewRows() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (
            node.nodeType === 1 &&
            node.classList.contains("dynamic-eventocontenedor")
          ) {
            processEventRow(node);
          }
          // También buscar en nodos hijos
          if (node.querySelectorAll) {
            node
              .querySelectorAll(".dynamic-eventocontenedor")
              .forEach(processEventRow);
          }
        });
      });
    });

    const inlineGroup = document.querySelector(
      ".inline-group:has([id*='eventocontenedor']), #eventocontenedor_set-group"
    );
    if (inlineGroup) {
      observer.observe(inlineGroup, { childList: true, subtree: true });
    }
  }

  /**
   * Agregar leyenda de colores
   */
  function addColorLegend() {
    const inlineGroup = document.querySelector(
      ".inline-group:has([id*='eventocontenedor']), #eventocontenedor_set-group"
    );
    if (!inlineGroup || inlineGroup.querySelector(".eventos-leyenda")) return;

    const legend = document.createElement("div");
    legend.className = "eventos-leyenda";
    legend.style.cssText = `
      display: flex;
      gap: 20px;
      margin: 10px 0;
      padding: 8px 15px;
      background: #2a2a2a;
      border-radius: 4px;
      font-size: 12px;
      color: #fff;
    `;
    legend.innerHTML = `
      <span style="display: flex; align-items: center; gap: 5px;">
        <span style="width: 12px; height: 12px; background: #1a3a5c; border: 2px solid #2196f3; border-radius: 2px;"></span>
        Marítimo
      </span>
      <span style="display: flex; align-items: center; gap: 5px;">
        <span style="width: 12px; height: 12px; background: #5c2626; border: 2px solid #f44336; border-radius: 2px;"></span>
        Retención/Alerta
      </span>
      <span style="display: flex; align-items: center; gap: 5px;">
        <span style="width: 12px; height: 12px; background: #1b3d1f; border: 2px solid #4caf50; border-radius: 2px;"></span>
        Liberación/Entrega
      </span>
    `;

    const header = inlineGroup.querySelector("h2");
    if (header) {
      header.parentNode.insertBefore(legend, header.nextSibling);
    }
  }

  /**
   * Inicialización principal
   */
  function init() {
    console.log("[EventosInline] Iniciando automatización de eventos");

    // Procesar filas existentes
    const eventRows = document.querySelectorAll(
      ".dynamic-eventocontenedor, tr.form-row:has([name$='-tipo_evento'])"
    );
    eventRows.forEach(processEventRow);

    // Agregar header con indicador de bloqueo
    addInlineHeader();

    // Agregar leyenda de colores
    addColorLegend();

    // Observar nuevas filas
    observeNewRows();

    console.log(
      `[EventosInline] ${eventRows.length} filas de eventos procesadas`
    );
  }

  // Ejecutar al cargar el DOM
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

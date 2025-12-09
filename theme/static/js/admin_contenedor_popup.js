/**
 * Admin Contenedor Popup - Sistema de registro de contenedores vía popup modal
 *
 * Funcionalidad:
 * - Agrega botón "+ Agregar Contenedor" en el inline de Arribos
 * - Abre popup con formulario completo de Contenedor
 * - Pre-selecciona el Arribo actual
 * - Refresca la página al cerrar el popup para mostrar el nuevo contenedor
 */
(function () {
  "use strict";

  // ====== CONFIGURACIÓN ======
  const CONFIG = {
    inlineSelector: ".inline-group",
    addRowSelector: ".add-row",
    popupWidth: 1200,
    popupHeight: 800,
    contenedorAddUrl: "/admin/control/contenedor/add/",
  };

  // ====== UTILIDADES ======
  function getArriboId() {
    // Obtener el ID del arribo desde la URL
    const match = window.location.pathname.match(/\/arribo\/(\d+)\//);
    return match ? match[1] : null;
  }

  function isContenedorInline(element) {
    // Verificar si el inline es de Contenedor
    const heading = element.querySelector("h2");
    if (heading) {
      const text = heading.textContent.toLowerCase();
      return text.includes("contenedor");
    }
    // También verificar por el ID del inline
    const id = element.id || "";
    return id.toLowerCase().includes("contenedor");
  }

  function getContenedorInline() {
    const inlines = document.querySelectorAll(CONFIG.inlineSelector);
    for (const inline of inlines) {
      if (isContenedorInline(inline)) {
        return inline;
      }
    }
    return null;
  }

  function log(message) {
    console.log(`[ContenedorPopup] ${message}`);
  }

  // ====== FUNCIONES PRINCIPALES ======

  /**
   * Muestra mensaje de funcionalidad en construcción para importar CSV/Excel
   */
  function showImportMessage() {
    // Crear overlay del modal
    const overlay = document.createElement("div");
    overlay.id = "import-modal-overlay";
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      animation: fadeIn 0.2s ease;
    `;

    // Crear modal
    overlay.innerHTML = `
      <div style="
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 450px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
      ">
        <div style="font-size: 60px; margin-bottom: 15px;">🚧</div>
        <h3 style="margin: 0 0 15px 0; color: #2c3e50; font-size: 20px;">
          Funcionalidad en Construcción
        </h3>
        <p style="color: #7f8c8d; margin: 0 0 20px 0; line-height: 1.6;">
          La importación masiva de contenedores desde archivos 
          <strong>CSV/Excel</strong> aún no está implementada.
        </p>
        <p style="color: #95a5a6; font-size: 13px; margin: 0 0 25px 0;">
          Esta funcionalidad permitirá cargar múltiples contenedores 
          de forma rápida y eficiente. ¡Próximamente!
        </p>
        <button type="button" id="close-import-modal" style="
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 12px 30px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        ">
          Entendido
        </button>
      </div>
    `;

    // Agregar estilos de animación
    const style = document.createElement("style");
    style.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(overlay);

    // Cerrar modal al hacer clic en el botón
    const closeBtn = document.getElementById("close-import-modal");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        overlay.remove();
        style.remove();
      });

      // Hover effect
      closeBtn.addEventListener("mouseenter", () => {
        closeBtn.style.transform = "translateY(-2px)";
        closeBtn.style.boxShadow = "0 4px 12px rgba(102, 126, 234, 0.4)";
      });
      closeBtn.addEventListener("mouseleave", () => {
        closeBtn.style.transform = "translateY(0)";
        closeBtn.style.boxShadow = "none";
      });
    }

    // Cerrar modal al hacer clic fuera
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.remove();
        style.remove();
      }
    });

    // Cerrar con tecla Escape
    const handleEscape = (e) => {
      if (e.key === "Escape") {
        overlay.remove();
        style.remove();
        document.removeEventListener("keydown", handleEscape);
      }
    };
    document.addEventListener("keydown", handleEscape);

    log("Modal de importación mostrado");
  }

  /**
   * Abre el popup para agregar un nuevo contenedor
   */
  function openContenedorPopup() {
    const arriboId = getArriboId();
    if (!arriboId) {
      alert(
        "Error: No se pudo determinar el Arribo actual. Guarde el Arribo primero."
      );
      return;
    }

    // Construir URL con parámetros
    // _popup=1 muestra solo el formulario sin el panel de admin completo
    const url = `${CONFIG.contenedorAddUrl}?_popup=1&arribo=${arriboId}`;

    // Calcular posición centrada
    const left = (screen.width - CONFIG.popupWidth) / 2;
    const top = (screen.height - CONFIG.popupHeight) / 2;

    // Abrir popup
    const popup = window.open(
      url,
      "addContenedor",
      `width=${CONFIG.popupWidth},height=${CONFIG.popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes`
    );

    if (popup) {
      // Monitorear cuando se cierra el popup
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          log("Popup cerrado, refrescando página...");
          // Refrescar la página para mostrar el nuevo contenedor
          window.location.reload();
        }
      }, 500);

      // También refrescar si el popup navega a otra página (después de guardar)
      // Django redirige a la lista o al change después de guardar
      popup.addEventListener("beforeunload", () => {
        // Pequeño delay para permitir que la navegación se complete
        setTimeout(() => {
          if (!popup.closed) {
            // El popup navegó a otra página, probablemente se guardó
            log("Popup navegó, posiblemente se guardó el contenedor");
          }
        }, 100);
      });
    } else {
      alert(
        "No se pudo abrir el popup. Verifique que los popups no estén bloqueados."
      );
    }
  }

  /**
   * Oculta el botón original de agregar fila del inline
   */
  function hideOriginalAddButton() {
    const inlineGroup = getContenedorInline();
    if (!inlineGroup) {
      log("No se encontró el grupo inline de contenedores");
      return false;
    }

    const addRow = inlineGroup.querySelector(CONFIG.addRowSelector);
    if (addRow) {
      addRow.style.display = "none";
      log("Botón original de agregar ocultado");
    }
    return true;
  }

  /**
   * Oculta los campos editables del inline y los hace solo lectura visual
   */
  function makeInlineReadonly() {
    const inlineGroup = getContenedorInline();
    if (!inlineGroup) return;

    // Hacer todos los campos del inline solo lectura
    const inputs = inlineGroup.querySelectorAll(
      'input:not([type="checkbox"]), select, textarea'
    );
    inputs.forEach((input) => {
      // Para los inputs de texto, mostrar como texto plano
      if (input.tagName === "INPUT" || input.tagName === "TEXTAREA") {
        input.readOnly = true;
        input.style.backgroundColor = "transparent";
        input.style.border = "none";
        input.style.pointerEvents = "none";
      }
      // Para los selects, deshabilitar pero mantener visible
      if (input.tagName === "SELECT") {
        input.disabled = true;
        input.style.pointerEvents = "none";
        input.style.backgroundColor = "transparent";
        input.style.border = "none";
        input.style.appearance = "none";
        input.style.WebkitAppearance = "none";
        input.style.cursor = "default";
      }
    });

    // Ocultar checkboxes de eliminación del inline (usarán la vista de detalle para eliminar)
    const deleteCheckboxes = inlineGroup.querySelectorAll(
      '.delete input[type="checkbox"]'
    );
    deleteCheckboxes.forEach((cb) => {
      const parent = cb.closest(".delete") || cb.closest("td");
      if (parent) {
        parent.style.display = "none";
      }
    });

    log("Inline convertido a solo lectura");
  }

  /**
   * Crea y agrega el botón personalizado de agregar contenedor
   */
  function addCustomButton() {
    const inlineGroup = getContenedorInline();
    if (!inlineGroup) return;

    // Verificar si ya existe el botón
    if (document.getElementById("add-contenedor-popup-btn")) {
      log("Botón ya existe");
      return;
    }

    // Verificar si es un arribo nuevo (sin ID)
    const arriboId = getArriboId();
    const isNewArribo = !arriboId;

    // Crear contenedor del botón
    const buttonContainer = document.createElement("div");
    buttonContainer.style.cssText = `
            margin: 15px 0;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;

    if (isNewArribo) {
      // Mensaje para arribos nuevos
      buttonContainer.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px;">📦</span>
                    <div>
                        <strong style="color: white; font-size: 14px;">Agregar Contenedores</strong>
                        <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin: 4px 0 0 0;">
                            Guarde el Arribo primero para poder agregar contenedores
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button type="button" id="import-csv-btn" title="🚧 Funcionalidad en construcción - Aún no implementada" style="
                        background: rgba(255,255,255,0.2);
                        color: rgba(255,255,255,0.7);
                        border: 1px dashed rgba(255,255,255,0.5);
                        padding: 10px 16px;
                        border-radius: 6px;
                        font-size: 13px;
                        cursor: help;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        <span style="font-size: 16px;">📥</span>
                        Importar CSV/Excel
                        <span style="font-size: 10px; background: #f39c12; color: white; padding: 2px 6px; border-radius: 10px;">Recomendado</span>
                    </button>
                    <button type="button" disabled style="
                        background: rgba(255,255,255,0.3);
                        color: rgba(255,255,255,0.6);
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-size: 14px;
                        cursor: not-allowed;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <span style="font-size: 18px;">➕</span>
                        Agregar Contenedor
                    </button>
                </div>
            `;
    } else {
      // Botón funcional para arribos existentes
      buttonContainer.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px;">📦</span>
                    <div>
                        <strong style="color: white; font-size: 14px;">Gestión de Contenedores</strong>
                        <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin: 4px 0 0 0;">
                            Haga clic en "Ver detalles" para editar/eliminar • Use los botones para agregar nuevos
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button type="button" id="import-csv-btn" title="🚧 Funcionalidad en construcción - Aún no implementada" style="
                        background: rgba(255,255,255,0.15);
                        color: white;
                        border: 1px dashed rgba(255,255,255,0.5);
                        padding: 10px 16px;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: 500;
                        cursor: help;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        transition: all 0.2s ease;
                    ">
                        <span style="font-size: 16px;">📥</span>
                        Importar CSV/Excel
                        <span style="font-size: 10px; background: #f39c12; color: white; padding: 2px 6px; border-radius: 10px;">Recomendado</span>
                    </button>
                    <button type="button" id="add-contenedor-popup-btn" style="
                        background: white;
                        color: #667eea;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 600;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        transition: all 0.2s ease;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <span style="font-size: 18px;">➕</span>
                        Agregar Contenedor
                    </button>
                </div>
            `;
    }

    // Insertar antes de la tabla del inline
    const inlineTable = inlineGroup.querySelector("table, fieldset");
    if (inlineTable) {
      inlineTable.parentNode.insertBefore(buttonContainer, inlineTable);
    } else {
      inlineGroup.appendChild(buttonContainer);
    }

    // Agregar evento al botón de agregar contenedor
    const btn = document.getElementById("add-contenedor-popup-btn");
    if (btn) {
      btn.addEventListener("click", openContenedorPopup);

      // Efectos hover
      btn.addEventListener("mouseenter", () => {
        btn.style.transform = "translateY(-2px)";
        btn.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
      });
      btn.addEventListener("mouseleave", () => {
        btn.style.transform = "translateY(0)";
        btn.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
      });
    }

    // Agregar evento al botón de importar CSV/Excel
    const importBtn = document.getElementById("import-csv-btn");
    if (importBtn) {
      importBtn.addEventListener("click", showImportMessage);

      // Efectos hover
      importBtn.addEventListener("mouseenter", () => {
        importBtn.style.background = "rgba(255,255,255,0.25)";
        importBtn.style.borderColor = "rgba(255,255,255,0.8)";
      });
      importBtn.addEventListener("mouseleave", () => {
        importBtn.style.background = "rgba(255,255,255,0.15)";
        importBtn.style.borderColor = "rgba(255,255,255,0.5)";
      });
    }

    log("Botones personalizados agregados");
  }

  /**
   * Mejora visual de la tabla del inline
   */
  function enhanceInlineTable() {
    const inlineGroup = getContenedorInline();
    if (!inlineGroup) return;

    // Mejorar encabezado
    const header = inlineGroup.querySelector("h2");
    if (header) {
      header.style.cssText = `
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            `;
      if (!header.innerHTML.includes("📦")) {
        header.innerHTML = "📦 " + header.innerHTML;
      }
    }

    const table = inlineGroup.querySelector("table");
    if (!table) return;

    // Agregar columna "Acciones" al encabezado si no existe
    const thead = table.querySelector("thead tr");
    if (thead && !thead.querySelector("th.actions-header")) {
      const actionsHeader = document.createElement("th");
      actionsHeader.className = "actions-header";
      actionsHeader.textContent = "Acciones";
      actionsHeader.style.cssText = "text-align: center; width: 80px;";
      thead.appendChild(actionsHeader);
    }

    // Procesar cada fila de datos
    const tableRows = table.querySelectorAll(
      "tbody tr.form-row:not(.empty-form)"
    );

    tableRows.forEach((row) => {
      // Evitar procesar si ya fue procesado
      if (row.dataset.enhanced) return;
      row.dataset.enhanced = "true";

      // Obtener el ID del contenedor desde el input hidden o desde el ID de la fila
      // Django genera inputs hidden con name como "contenedor_set-0-id"
      let contenedorId = null;

      // Método 1: Buscar input hidden con el ID
      const idInput = row.querySelector('input[name$="-id"]');
      if (idInput && idInput.value) {
        contenedorId = idInput.value;
      }

      // Método 2: Buscar en el atributo id de la fila (formato: contenedor_set-0)
      if (!contenedorId) {
        const rowId = row.id || "";
        // Algunos temas de admin usan data attributes
        contenedorId = row.dataset.inlineId || row.dataset.objectId;
      }

      // Método 3: Buscar cualquier enlace que contenga /contenedor/ y /change/
      if (!contenedorId) {
        const anyLink = row.querySelector(
          'a[href*="/contenedor/"][href*="/change/"]'
        );
        if (anyLink) {
          const match = anyLink.href.match(/\/contenedor\/([^/]+)\/change\//);
          if (match) {
            contenedorId = match[1];
          }
        }
      }

      // Obtener el código ISO de la celda correspondiente
      const isoCell = row.querySelector("td.field-codigo_iso");
      let isoCode = null;

      if (isoCell) {
        // Obtener el texto del código ISO (puede estar en un span, div o directamente)
        const textContent = isoCell.textContent.trim();
        // Buscar patrón de código ISO: 4 letras + 7 dígitos
        const match = textContent.match(/[A-Z]{4}\d{7}/i);
        if (match) {
          isoCode = match[0].toUpperCase();
        }
      }

      // Si no hay ID, no podemos crear el botón de editar
      if (!contenedorId) {
        log(`No se encontró ID para la fila: ${row.id}`);
        // Aún así, agregar celda vacía para mantener la estructura
        if (!row.querySelector("td.actions-cell")) {
          const emptyCell = document.createElement("td");
          emptyCell.className = "actions-cell";
          row.appendChild(emptyCell);
        }
        return;
      }

      // Construir URL de cambio
      const changeUrl = `/admin/control/contenedor/${contenedorId}/change/`;

      // Crear nueva celda de acciones al final
      if (!row.querySelector("td.actions-cell")) {
        const actionsCell = document.createElement("td");
        actionsCell.className = "actions-cell";
        actionsCell.style.cssText =
          "text-align: center; vertical-align: middle;";

        // Botón de editar
        const editBtn = document.createElement("a");
        editBtn.href = changeUrl;
        editBtn.innerHTML = "✏️";
        editBtn.title = "Ver/Editar contenedor";
        editBtn.style.cssText = `
          display: inline-flex;
          align-items: center;
          justify-content: center;
          background: #3498db;
          color: white !important;
          width: 28px;
          height: 28px;
          border-radius: 6px;
          text-decoration: none;
          font-size: 14px;
          transition: all 0.2s ease;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        editBtn.addEventListener("mouseenter", () => {
          editBtn.style.background = "#2980b9";
          editBtn.style.transform = "scale(1.1)";
        });
        editBtn.addEventListener("mouseleave", () => {
          editBtn.style.background = "#3498db";
          editBtn.style.transform = "scale(1)";
        });

        actionsCell.appendChild(editBtn);
        row.appendChild(actionsCell);
      }
    });

    // OCULTAR la fila/encabezado extra que Django genera con "(IMP) - qweweq Modificar"
    // Django genera elementos h3 dentro de .inline-related que muestran la representación del objeto
    // También puede estar en divs o spans con enlaces de modificar

    // 1. Ocultar todos los h3 dentro del inline (contienen la representación del objeto)
    const inlineHeaders = inlineGroup.querySelectorAll(
      ".inline-related h3, .djn-inline-form h3"
    );
    inlineHeaders.forEach((h3) => {
      h3.style.display = "none";
    });

    // 2. Ocultar elementos con clase "inline_label" o similar
    const inlineLabels = inlineGroup.querySelectorAll(
      ".inline_label, .djn-drag-handler"
    );
    inlineLabels.forEach((el) => {
      el.style.display = "none";
    });

    // 3. Buscar y ocultar cualquier elemento que contenga el patrón "(IMP)" o "Modificar"
    const allElements = inlineGroup.querySelectorAll("*");
    allElements.forEach((el) => {
      // Solo procesar elementos de texto directo (no contenedores grandes)
      if (
        el.children.length === 0 ||
        el.tagName === "A" ||
        el.tagName === "SPAN"
      ) {
        const text = el.textContent || "";
        if (
          (text.includes("(IMP)") || text.includes("Modificar")) &&
          !el.closest("table") &&
          !el.classList.contains("actions-cell")
        ) {
          // Ocultar el elemento padre si es pequeño
          const parent = el.closest("h3, .inline-related > div, span");
          if (parent) {
            parent.style.display = "none";
          } else {
            el.style.display = "none";
          }
        }
      }
    });

    // 4. Específicamente buscar la estructura de Django inline stacked
    const stackedItems = inlineGroup.querySelectorAll(".inline-related");
    stackedItems.forEach((item) => {
      const h3 = item.querySelector("h3");
      if (h3) {
        h3.style.display = "none";
      }
    });

    // Mensaje si no hay contenedores
    const tbody = inlineGroup.querySelector("tbody");
    const contentRows = tbody
      ? tbody.querySelectorAll("tr.form-row:not(.empty-form)")
      : [];

    if (contentRows.length === 0) {
      // Verificar si ya existe el mensaje
      if (!document.getElementById("no-contenedores-msg")) {
        const noDataMsg = document.createElement("div");
        noDataMsg.id = "no-contenedores-msg";
        noDataMsg.style.cssText = `
                    text-align: center;
                    padding: 30px;
                    color: #7f8c8d;
                    font-style: italic;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin: 10px 0;
                `;
        noDataMsg.innerHTML = `
                    <span style="font-size: 40px; display: block; margin-bottom: 10px;">📭</span>
                    <p style="margin: 0; font-size: 14px;">No hay contenedores registrados para este arribo</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px;">Use el botón "+ Agregar Contenedor" para registrar uno</p>
                `;

        const table = inlineGroup.querySelector("table");
        if (table) {
          table.parentNode.insertBefore(noDataMsg, table.nextSibling);
          table.style.display = "none";
        }
      }
    }

    log("Tabla inline mejorada visualmente");
  }

  /**
   * Función principal de inicialización
   */
  function init() {
    log("Inicializando...");

    // Verificar si estamos en la página de edición/creación de Arribo
    if (!window.location.pathname.includes("/arribo/")) {
      log("No estamos en la página de Arribo, saliendo");
      return;
    }

    // Solo aplicar en cambio (edit), no en add
    // En add no hay inline todavía
    const isAddPage = window.location.pathname.endsWith("/add/");

    // Esperar a que el DOM esté completamente cargado
    setTimeout(() => {
      // Ocultar el botón original de agregar
      hideOriginalAddButton();

      // Agregar botón personalizado
      addCustomButton();

      // Hacer el inline solo lectura (solo mostrar datos)
      makeInlineReadonly();

      // Mejorar visualmente la tabla
      enhanceInlineTable();

      log("Inicialización completada");
    }, 100);
  }

  // ====== EVENT LISTENERS ======

  // Esperar al DOM
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Callbacks para Django admin popup (cuando se guarda el contenedor en el popup)
  // Django usa diferentes funciones dependiendo de la versión y contexto

  // Función principal para cerrar popup y refrescar
  function handlePopupClose(win, objId, objRepr) {
    log(`Contenedor creado: ID=${objId}, Repr=${objRepr}`);
    try {
      win.close();
    } catch (e) {
      log("No se pudo cerrar la ventana: " + e.message);
    }
    // Refrescar para ver el nuevo contenedor
    window.location.reload();
  }

  // Django 3+ usa dismissAddRelatedObjectPopup
  window.dismissAddRelatedObjectPopup = handlePopupClose;

  // Django también puede usar dismissAddAnotherPopup
  window.dismissAddAnotherPopup = handlePopupClose;

  // Función legacy para versiones anteriores
  window.dismissAddPopup = handlePopupClose;

  // También interceptar el cierre del popup desde el propio popup
  // cuando Django hace window.close() después de guardar
  window.addEventListener("message", function (event) {
    if (event.data && event.data.action === "popup_saved") {
      log("Mensaje recibido del popup: contenedor guardado");
      window.location.reload();
    }
  });
})();

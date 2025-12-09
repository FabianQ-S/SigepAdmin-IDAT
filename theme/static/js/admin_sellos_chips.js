/**
 * Sistema de Chips/Tags para Sellos de Contenedor
 * Transforma el campo de texto en una interfaz visual de etiquetas
 *
 * Formato interno: TIPO:CODIGO*|TIPO:CODIGO
 * El * indica sello principal
 */

(function () {
  "use strict";

  const TIPOS_SELLO = {
    NAVIERA: { label: "Naviera", color: "#1e40af", bgColor: "#dbeafe" },
    ADUANAS: { label: "Aduanas", color: "#166534", bgColor: "#dcfce7" },
    SENASA: { label: "SENASA", color: "#9a3412", bgColor: "#ffedd5" },
    EXPORTADOR: { label: "Exportador", color: "#7c2d12", bgColor: "#fef3c7" },
    OTRO: { label: "Otro", color: "#374151", bgColor: "#f3f4f6" },
  };

  // Sanitiza el código de sello
  function sanitizeCodigo(codigo) {
    if (!codigo) return "";
    return codigo.trim().replace(/\s+/g, "").toUpperCase();
  }

  // Parsea el valor del campo a array de objetos
  function parseSellos(value) {
    if (!value || !value.trim()) return [];

    const sellos = [];
    const partes = value.split("|");

    for (const parte of partes) {
      const trimmed = parte.trim();
      if (!trimmed || !trimmed.includes(":")) continue;

      const [tipo, codigoRaw] = trimmed.split(":", 2);
      const esPrincipal = codigoRaw.endsWith("*");
      const codigo = codigoRaw.replace("*", "").trim().toUpperCase();

      if (codigo) {
        sellos.push({
          tipo: tipo.trim().toUpperCase(),
          codigo: codigo,
          esPrincipal: esPrincipal,
        });
      }
    }
    return sellos;
  }

  // Convierte array de objetos a string para el campo
  function serializeSellos(sellos) {
    return sellos
      .map((s) => {
        const principal = s.esPrincipal ? "*" : "";
        return `${s.tipo}:${s.codigo}${principal}`;
      })
      .join("|");
  }

  // Crea el HTML de un chip
  function createChipElement(sello, index, onRemove, onSetPrincipal) {
    const tipoInfo = TIPOS_SELLO[sello.tipo] || TIPOS_SELLO["OTRO"];

    const chip = document.createElement("div");
    chip.className = "sello-chip";
    chip.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 10px;
            margin: 4px;
            border-radius: 20px;
            background: ${tipoInfo.bgColor};
            border: 2px solid ${sello.esPrincipal ? "#f59e0b" : tipoInfo.color};
            color: ${tipoInfo.color};
            font-size: 13px;
            font-weight: 500;
            box-shadow: ${sello.esPrincipal ? "0 0 0 2px #fbbf24" : "none"};
            transition: all 0.2s;
        `;

    // Tipo badge
    const tipoBadge = document.createElement("span");
    tipoBadge.style.cssText = `
            font-size: 10px;
            text-transform: uppercase;
            opacity: 0.8;
            font-weight: 600;
        `;
    tipoBadge.textContent = tipoInfo.label;

    // Código
    const codigoSpan = document.createElement("span");
    codigoSpan.style.cssText = "font-weight: 700; letter-spacing: 0.5px;";
    codigoSpan.textContent = sello.codigo;

    // Botón estrella (marcar como principal)
    const starBtn = document.createElement("button");
    starBtn.type = "button";
    starBtn.innerHTML = sello.esPrincipal ? "⭐" : "☆";
    starBtn.title = sello.esPrincipal
      ? "Sello Principal"
      : "Marcar como principal";
    starBtn.style.cssText = `
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 0 2px;
            opacity: ${sello.esPrincipal ? "1" : "0.5"};
            transition: opacity 0.2s;
        `;
    starBtn.addEventListener("click", () => onSetPrincipal(index));
    starBtn.addEventListener("mouseenter", () => (starBtn.style.opacity = "1"));
    starBtn.addEventListener("mouseleave", () => {
      if (!sello.esPrincipal) starBtn.style.opacity = "0.5";
    });

    // Botón eliminar
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.innerHTML = "✕";
    removeBtn.title = "Eliminar sello";
    removeBtn.style.cssText = `
            background: none;
            border: none;
            cursor: pointer;
            font-size: 12px;
            color: ${tipoInfo.color};
            opacity: 0.6;
            padding: 0 2px;
            margin-left: 2px;
            transition: opacity 0.2s;
        `;
    removeBtn.addEventListener("click", () => onRemove(index));
    removeBtn.addEventListener("mouseenter", () => {
      removeBtn.style.opacity = "1";
      removeBtn.style.color = "#dc2626";
    });
    removeBtn.addEventListener("mouseleave", () => {
      removeBtn.style.opacity = "0.6";
      removeBtn.style.color = tipoInfo.color;
    });

    chip.appendChild(tipoBadge);
    chip.appendChild(codigoSpan);
    chip.appendChild(starBtn);
    chip.appendChild(removeBtn);

    return chip;
  }

  // Crea el formulario para agregar nuevo sello
  function createAddForm(onAdd) {
    const form = document.createElement("div");
    form.className = "sello-add-form";
    form.style.cssText = `
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            padding: 12px;
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
        `;

    // Select de tipo
    const tipoSelect = document.createElement("select");
    tipoSelect.style.cssText = `
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 13px;
            background: white;
            color: #1f2937;
            cursor: pointer;
        `;
    for (const [key, info] of Object.entries(TIPOS_SELLO)) {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = info.label;
      tipoSelect.appendChild(option);
    }

    // Input de código
    const codigoInput = document.createElement("input");
    codigoInput.type = "text";
    codigoInput.placeholder = "Código del sello (ej: HL123456)";
    codigoInput.style.cssText = `
            flex: 1;
            min-width: 180px;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 13px;
            text-transform: uppercase;
            color: #1f2937;
            background-color: white;
        `;

    // Auto-sanitizar mientras escribe
    codigoInput.addEventListener("input", (e) => {
      const pos = e.target.selectionStart;
      e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9\-]/g, "");
      e.target.setSelectionRange(pos, pos);
    });

    // Agregar con Enter
    codigoInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        addBtn.click();
      }
    });

    // Botón agregar
    const addBtn = document.createElement("button");
    addBtn.type = "button";
    addBtn.innerHTML = "+ Agregar Sello";
    addBtn.style.cssText = `
            padding: 8px 16px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        `;
    addBtn.addEventListener(
      "mouseenter",
      () => (addBtn.style.background = "#1d4ed8")
    );
    addBtn.addEventListener(
      "mouseleave",
      () => (addBtn.style.background = "#2563eb")
    );
    addBtn.addEventListener("click", () => {
      const tipo = tipoSelect.value;
      const codigo = sanitizeCodigo(codigoInput.value);

      if (!codigo) {
        codigoInput.style.borderColor = "#dc2626";
        codigoInput.focus();
        return;
      }

      if (codigo.length < 4) {
        alert("El código de sello debe tener al menos 4 caracteres.");
        codigoInput.focus();
        return;
      }

      codigoInput.style.borderColor = "#d1d5db";
      onAdd(tipo, codigo);
      codigoInput.value = "";
      codigoInput.focus();
    });

    // Labels
    const tipoLabel = document.createElement("label");
    tipoLabel.textContent = "Tipo:";
    tipoLabel.style.cssText =
      "font-size: 12px; color: #6b7280; font-weight: 500;";

    form.appendChild(tipoLabel);
    form.appendChild(tipoSelect);
    form.appendChild(codigoInput);
    form.appendChild(addBtn);

    return form;
  }

  // Inicializa el widget de chips para un campo
  function initSellosWidget(inputField) {
    // Ocultar el input original
    inputField.style.display = "none";

    // Crear contenedor principal
    const container = document.createElement("div");
    container.className = "sellos-widget";
    container.style.cssText = `
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 12px;
            background: white;
            min-height: 60px;
        `;

    // Contenedor de chips
    const chipsContainer = document.createElement("div");
    chipsContainer.className = "sellos-chips-container";
    chipsContainer.style.cssText = "display: flex; flex-wrap: wrap; gap: 4px;";

    // Mensaje cuando no hay sellos
    const emptyMessage = document.createElement("div");
    emptyMessage.className = "sellos-empty";
    emptyMessage.innerHTML =
      "📦 No hay sellos registrados. Agregue al menos el <strong>sello de la Naviera</strong>.";
    emptyMessage.style.cssText = `
            color: #6b7280;
            font-size: 13px;
            padding: 8px;
            text-align: center;
        `;

    // Estado
    let sellos = parseSellos(inputField.value);

    // Actualiza el campo oculto y la UI
    function updateUI() {
      // Actualizar campo oculto
      inputField.value = serializeSellos(sellos);

      // Limpiar chips
      chipsContainer.innerHTML = "";

      if (sellos.length === 0) {
        chipsContainer.appendChild(emptyMessage);
        return;
      }

      // Crear chips
      sellos.forEach((sello, index) => {
        const chip = createChipElement(
          sello,
          index,
          removeByIndex,
          setPrincipal
        );
        chipsContainer.appendChild(chip);
      });
    }

    // Agregar sello
    function addSello(tipo, codigo) {
      // Verificar duplicado
      const exists = sellos.some((s) => s.codigo === codigo);
      if (exists) {
        alert(`⚠️ El sello "${codigo}" ya está agregado.`);
        return;
      }

      // Si es el primero o es tipo NAVIERA y no hay principal, marcarlo como principal
      const esPrincipal =
        sellos.length === 0 ||
        (tipo === "NAVIERA" && !sellos.some((s) => s.esPrincipal));

      // Si va a ser principal, quitar marca de otros
      if (esPrincipal) {
        sellos.forEach((s) => (s.esPrincipal = false));
      }

      sellos.push({ tipo, codigo, esPrincipal });
      updateUI();
    }

    // Eliminar por índice
    function removeByIndex(index) {
      const wasMain = sellos[index].esPrincipal;
      sellos.splice(index, 1);

      // Si se eliminó el principal y quedan sellos, marcar el primero como principal
      if (wasMain && sellos.length > 0) {
        // Priorizar NAVIERA
        const navieraIdx = sellos.findIndex((s) => s.tipo === "NAVIERA");
        if (navieraIdx >= 0) {
          sellos[navieraIdx].esPrincipal = true;
        } else {
          sellos[0].esPrincipal = true;
        }
      }

      updateUI();
    }

    // Establecer principal
    function setPrincipal(index) {
      sellos.forEach((s, i) => (s.esPrincipal = i === index));
      updateUI();
    }

    // Formulario de agregar
    const addForm = createAddForm(addSello);

    // Ensamblar
    container.appendChild(chipsContainer);
    container.appendChild(addForm);

    // Insertar después del campo original
    inputField.parentNode.insertBefore(container, inputField.nextSibling);

    // Render inicial
    updateUI();

    // Agregar leyenda de tipos
    const legend = document.createElement("div");
    legend.style.cssText = `
            margin-top: 10px;
            padding: 8px 12px;
            background: #fefce8;
            border: 1px solid #fef08a;
            border-radius: 6px;
            font-size: 11px;
            color: #713f12;
        `;
    legend.innerHTML = `
            <strong>ℹ️ Información:</strong> El sello marcado con ⭐ es el <strong>principal</strong> (generalmente el de la Naviera). 
            Este es el que se reporta en el manifiesto de aduanas.
        `;
    container.appendChild(legend);
  }

  // Buscar e inicializar campos de sello
  function init() {
    // Buscar el campo numero_sello
    const selloField = document.getElementById("id_numero_sello");
    if (selloField && !selloField.dataset.sellosWidgetInit) {
      selloField.dataset.sellosWidgetInit = "true";
      initSellosWidget(selloField);
    }

    // También buscar en inlines (para cuando se agrega contenedor desde Arribo)
    document
      .querySelectorAll('input[name$="-numero_sello"]')
      .forEach((field) => {
        if (!field.dataset.sellosWidgetInit) {
          field.dataset.sellosWidgetInit = "true";
          initSellosWidget(field);
        }
      });
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Observar cambios para inlines dinámicos
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.addedNodes.length) {
        setTimeout(init, 100);
      }
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();

const DB_URL = "./public/data/guia.sqlite.gz";
const DB_CACHE_KEY = "guia-sqlite-v3";
const GRID_LIMIT = 400;
const PAGE_SIZE = 50;
const DEFAULT_VISIBLE_COLS = 3;

const datasets = {
  graduacao: {
    prefix: "grad",
    label: "Graduação",
    table: "graduacao",
    orderBy: "nome_curso, nome_ies, municipio",
    columns: [
      
      { id: "nome_ies", name: "Instituição" },
      { id: "nome_curso", name: "Curso" },
      { id: "municipio", name: "Município" },
      { id: "uf", name: "UF" },
      { id: "grau", name: "Grau" },
      { id: "modalidade", name: "Modalidade" },
      { id: "area_conhecimento", name: "Área" },
      { id: "vagas_autorizadas", name: "Vagas autorizadas" },
    ],
    filters: [
      { type: "multi", id: "grad-curso", column: "nome_curso", operator: "like", label: "Nome do curso", placeholder: "Filtrar curso" },
      { type: "multi", id: "grad-area", column: "area_conhecimento", label: "Área de conhecimento", placeholder: "Filtrar área" },
      { type: "multi", id: "grad-ies", column: "nome_ies", label: "Instituição", placeholder: "Filtrar instituição" },
      { type: "multi", id: "grad-uf", column: "uf", label: "UF", placeholder: "Filtrar estado" },
      { type: "multi", id: "grad-municipio", column: "municipio", label: "Município", placeholder: "Filtrar município" },
      { type: "multi", id: "grad-grau", column: "grau", label: "Grau", placeholder: "Filtrar grau" },
      { type: "multi", id: "grad-modalidade", column: "modalidade", label: "Modalidade", placeholder: "Filtrar modalidade" },
    ],
    defaults: {
      "grad-grau": ["Bacharelado", "Licenciatura","Tecnológico"],
      "grad-modalidade": ["Educação Presencial"],
    },
  },
  especializacao: {
    prefix: "esp",
    label: "Especialização",
    table: "especializacao",
    orderBy: "nome_especializacao, nome_ies, municipio",
    columns: [
      
      { id: "nome_ies", name: "Instituição" },
      { id: "nome_especializacao", name: "Curso" },
      { id: "municipio", name: "Município" },
      { id: "uf", name: "UF" },
      { id: "modalidade", name: "Modalidade" },
      { id: "carga_horaria", name: "Carga horária" },
      { id: "duracao_meses", name: "Duração (meses)" },
      { id: "area_conhecimento", name: "Área" },
    ],
    filters: [
      
      { type: "multi", id: "esp-curso", column: "nome_especializacao", label: "Nome do curso", placeholder: "Ex.: Engenharia de Software" },
      { type: "multi", id: "esp-area", column: "area_conhecimento", label: "Área de conhecimento", placeholder: "Filtrar área" },
      
      { type: "multi", id: "esp-ies", column: "nome_ies", label: "Instituição", placeholder: "Filtrar instituição" },
      { type: "multi", id: "esp-modalidade", column: "modalidade", label: "Modalidade", placeholder: "Filtrar modalidade" },

      { type: "multi", id: "esp-uf", column: "uf", label: "UF", placeholder: "Filtrar estado" },
      { type: "multi", id: "esp-municipio", column: "municipio", label: "Município", placeholder: "Filtrar município" },
      {
        type: "range",
        minId: "esp-carga-min",
        maxId: "esp-carga-max",
        column: "carga_horaria",
        labelMin: "Carga horária mínima",
        labelMax: "Carga horária máxima",
        placeholderMin: "180",
        placeholderMax: "1440",
      },
      {
        type: "range",
        minId: "esp-duracao-min",
        maxId: "esp-duracao-max",
        column: "duracao_meses",
        labelMin: "Duração mínima (meses)",
        labelMax: "Duração máxima (meses)",
        placeholderMin: "3",
        placeholderMax: "48",
      },
    ],
  },
  pos: {
    prefix: "pos",
    label: "Mestrado/Doutorado",
    table: "pos",
    orderBy: "nome_programa, sigla_ies, municipio",
    columns: [
      { id: "sigla_ies", name: "Sigla Instituição" },
      { id: "nome_programa", name: "Programa" },
      { id: "municipio", name: "Município" },
      { id: "uf", name: "UF" },
      { id: "area_conhecimento", name: "Área de conhecimento" },
      { id: "nota_conceito", name: "Nota" },
      { id: "nome_ies", name: "Instituição" },
      { id: "nivel_programa", name: "Nível" },
      { id: "modalidade", name: "Modalidade" },
      { id: "link", name: "Mais informações" },
    ],
    filters: [
      { type: "multi", id: "pos-nome", column: "nome_programa", operator: "like", label: "Programa", placeholder: "Filtrar pelo nome do programa" },
      { type: "multi", id: "pos-nivel", column: "nivel_programa", operator: "like", label: "Nível", placeholder: "Filtrar nível" },
      { type: "multi", id: "pos-area", column: "area_conhecimento", label: "Área de conhecimento", placeholder: "Filtrar área" },
      { type: "multi", id: "pos-nota", column: "nota_conceito", label: "Nota CAPES", placeholder: "Filtrar nota" },
      { type: "multi", id: "pos-modalidade", column: "modalidade", label: "Modalidade", placeholder: "Filtrar modalidade" },
      { type: "multi", id: "pos-uf", column: "uf", label: "UF", placeholder: "Filtrar estado" },
      { type: "multi", id: "pos-municipio", column: "municipio", label: "Município", placeholder: "Filtrar município" },
      { type: "multi", id: "pos-sigla", column: "sigla_ies", label: "Sigla da Instituição", placeholder: "Filtrar sigla" },
      { type: "multi", id: "pos-ies", column: "nome_ies", label: "Nome da Instituição", placeholder: "Filtrar instituição" },
    ],
    defaults: {
      "pos-nivel": ["MESTRADO", "DOUTORADO"],
    },
  },
};

let db;
const gridInstances = {};
const lastData = {};
const loadedTabs = new Set();
const selectedColumns = {};

function buildPanels() {
  const root = document.getElementById("tabPanels");
  const tpl = document.getElementById("panel-template");
  if (!root || !tpl) return;

  Object.entries(datasets).forEach(([key, cfg], idx) => {
    const fragment = tpl.content.cloneNode(true);
    const section = fragment.querySelector(".tab-panel");
    section.dataset.panel = key;
    if (idx === 0) section.classList.remove("d-none");

    const details = section.querySelector("details");
    details.dataset.filters = key;
    const summary = details.querySelector("summary");
    summary.innerHTML = `
      <span class="summary-icon" aria-hidden="true">🔍</span>
      <span class="summary-label">Filtros de ${cfg.label}</span>
      <span class="summary-hint">Clique para abrir e ajustar</span>
    `;
    const fields = section.querySelector("[data-filter-fields]");
    cfg.filters.forEach((filter) => {
      const node = renderFilterField(filter);
      if (node) fields.appendChild(node);
    });

    const btnFilter = section.querySelector('[data-role="filtrar"]');
    const btnClear = section.querySelector('[data-role="limpar"]');
    const btnDownload = section.querySelector('[data-role="download"]');
    btnFilter.id = `${cfg.prefix}-filtrar`;
    btnClear.id = `${cfg.prefix}-limpar`;
    btnDownload.id = `${cfg.prefix}-download`;

    const gridTitle = section.querySelector("[data-grid-title]");
    const gridBody = section.querySelector("[data-grid-body]");
    gridTitle.textContent = `Lista de cursos – ${cfg.label}`;
    gridBody.id = `grid-ag-${key}`;
    section.querySelector(".grid-card").dataset.gridCard = key;
    const colPicker = section.querySelector("[data-column-options]");
    if (colPicker) {
      colPicker.dataset.gridKey = key;
      buildColumnPicker(key, cfg.columns, colPicker);
    }

    root.appendChild(section);
  });
}

function getSelectedColumns(key) {
  if (!selectedColumns[key] || !selectedColumns[key].length) {
    selectedColumns[key] = datasets[key].columns.slice(0, DEFAULT_VISIBLE_COLS).map((c) => c.id);
  }
  return selectedColumns[key];
}

function buildColumnPicker(key, columns, container) {
  const selectedSet = new Set(getSelectedColumns(key));
  container.innerHTML = "";
  columns.forEach((col, idx) => {
    const label = document.createElement("label");
    label.className = "column-pill";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = col.id;
    input.checked = selectedSet.has(col.id) || (!selectedSet.size && idx < DEFAULT_VISIBLE_COLS);
    if (input.checked) label.classList.add("column-pill--active");

    input.addEventListener("change", (ev) => handleColumnPickerChange(ev, key, container));

    const text = document.createElement("span");
    text.textContent = col.name;

    label.appendChild(input);
    label.appendChild(text);
    container.appendChild(label);
  });
}

function handleColumnPickerChange(ev, key, container) {
  const checked = Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((el) => el.value);
  container.querySelectorAll(".column-pill").forEach((pill) => {
    const cb = pill.querySelector('input[type="checkbox"]');
    pill.classList.toggle("column-pill--active", cb?.checked);
  });
  if (!checked.length) {
    ev.target.checked = true;
    ev.target.closest(".column-pill")?.classList.add("column-pill--active");
    return;
  }
  selectedColumns[key] = checked;
  refreshGridColumns(key);
}

function refreshGridColumns(key) {
  const grid = gridInstances[key];
  const cfg = datasets[key];
  if (!grid || !cfg) return;
  const colDefs = buildAgColumns(cfg.columns, new Set(getSelectedColumns(key)));
  grid.api.setColumnDefs(colDefs);
  grid.api.sizeColumnsToFit();
}

function renderFilterField(filter) {
  if (filter.type === "multi") {
    const wrap = document.createElement("div");
    wrap.className = "col-md-3";
    wrap.appendChild(buildLabel(filter.label ?? filter.id, filter.id));
    wrap.appendChild(buildMultiBox(filter.id, filter.placeholder ?? "Filtrar"));
    return wrap;
  }
  if (filter.type === "text") {
    const wrap = document.createElement("div");
    wrap.className = "col-md-3";
    wrap.appendChild(buildLabel(filter.label ?? filter.id, filter.id));
    const input = document.createElement("input");
    input.id = filter.id;
    input.type = "text";
    input.className = "form-control";
    input.placeholder = filter.placeholder ?? "";
    wrap.appendChild(input);
    return wrap;
  }
  if (filter.type === "range") {
    const frag = document.createDocumentFragment();
    frag.appendChild(buildNumberField(filter.minId, filter.labelMin ?? "Mínimo", filter.placeholderMin));
    frag.appendChild(buildNumberField(filter.maxId, filter.labelMax ?? "Máximo", filter.placeholderMax));
    return frag;
  }
  return null;
}

function buildLabel(text, forId) {
  const label = document.createElement("label");
  label.className = "form-label";
  label.htmlFor = forId;
  label.textContent = text;
  return label;
}

function buildMultiBox(id, placeholder) {
  const box = document.createElement("div");
  box.className = "multi-box";
  box.dataset.multibox = "true";
  box.id = id;

  const search = document.createElement("input");
  search.type = "search";
  search.className = "form-control form-control-sm multi-search";
  search.placeholder = placeholder ?? "Filtrar";

  const status = document.createElement("div");
  status.className = "multi-status small text-muted";

  const options = document.createElement("div");
  options.className = "multi-options";

  box.appendChild(search);
  box.appendChild(status);
  box.appendChild(options);
  return box;
}

function buildNumberField(id, labelText, placeholder) {
  const wrap = document.createElement("div");
  wrap.className = "col-md-3";
  wrap.appendChild(buildLabel(labelText, id));
  const input = document.createElement("input");
  input.type = "number";
  input.min = "0";
  input.id = id;
  input.className = "form-control";
  if (placeholder) input.placeholder = placeholder;
  wrap.appendChild(input);
  return wrap;
}

document.addEventListener("DOMContentLoaded", () => {
  init().catch((err) => {
    console.error(err);
    setStatus(`Erro ao iniciar: ${err.message}`);
  });
});

async function init() {
  setStatus("Baixando base SQLite (cache em IndexedDB)...");
  db = await loadDatabase();
  setStatus("Base carregada. Monte seus filtros e consulte.");

  buildPanels();
  await hydrateFilters();
  wireNavigation();
  wireButtons();
  wireResize();
  await runQuery("graduacao");
  loadedTabs.add("graduacao");
}

async function loadDatabase() {
  const SQL = await initSqlJs({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/sql.js@1.11.0/dist/${file}`,
  });

  const cached = await localforage.getItem(DB_CACHE_KEY);
  let bytes;
  if (cached) {
    bytes = new Uint8Array(cached);
  } else {
    const resp = await fetch(DB_URL);
    const compressed = new Uint8Array(await resp.arrayBuffer());
    try {
      bytes = pako.ungzip(compressed);
    } catch (err) {
      console.error("Erro ao descompactar, usando arquivo original", err);
      bytes = compressed;
    }
    await localforage.setItem(DB_CACHE_KEY, bytes);
  }

  return new SQL.Database(bytes);
}

async function hydrateFilters() {
  await Promise.all(
    Object.entries(datasets).map(async ([key, cfg]) => {
      for (const filter of cfg.filters) {
        if (filter.type !== "multi") continue;
        const values = await distinctValues(cfg.table, filter.column);
        fillSelect(filter.id, values, cfg.defaults?.[filter.id]);
      }
    })
  );

  const rangeStmt = db.prepare(
    "SELECT MIN(carga_horaria) AS min_ch, MAX(carga_horaria) AS max_ch, MIN(duracao_meses) AS min_dm, MAX(duracao_meses) AS max_dm FROM especializacao"
  );
  rangeStmt.step();
  const range = rangeStmt.getAsObject();
  rangeStmt.free();
  const chMin = document.getElementById("esp-carga-min");
  const chMax = document.getElementById("esp-carga-max");
  const duMin = document.getElementById("esp-duracao-min");
  const duMax = document.getElementById("esp-duracao-max");
  if (range.min_ch !== null) chMin.placeholder = range.min_ch;
  if (range.max_ch !== null) chMax.placeholder = range.max_ch;
  if (range.min_dm !== null) duMin.placeholder = range.min_dm;
  if (range.max_dm !== null) duMax.placeholder = range.max_dm;
}

function distinctValues(table, column) {
  const stmt = db.prepare(`SELECT DISTINCT ${column} AS value FROM ${table} WHERE ${column} IS NOT NULL ORDER BY ${column}`);
  const values = [];
  while (stmt.step()) {
    const { value } = stmt.getAsObject();
    if (value !== null && value !== "") values.push(value);
  }
  stmt.free();
  return values;
}

function fillSelect(id, values, defaults = []) {
  const target = document.getElementById(id);
  if (!target) return;
  if (isMultiBox(target)) {
    fillMultiBox(target, values, defaults);
    return;
  }

  target.innerHTML = "";
  values.forEach((val) => {
    const opt = document.createElement("option");
    opt.value = val;
    opt.textContent = val;
    if (defaults?.includes(val)) {
      opt.selected = true;
    }
    target.appendChild(opt);
  });
}

function isMultiBox(el) {
  return el?.dataset?.multibox === "true";
}

function fillMultiBox(container, values, defaults = []) {
  const optionsWrapper = container.querySelector(".multi-options");
  if (!optionsWrapper) return;
  const search = container.querySelector(".multi-search");
  const defaultsSet = new Set(defaults ?? []);

  optionsWrapper.innerHTML = "";
  values.forEach((val, idx) => {
    const label = document.createElement("label");
    label.className = "form-check d-flex align-items-center gap-2 py-1";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "form-check-input";
    checkbox.value = val;
    checkbox.id = `${container.id}-${idx}`;
    checkbox.checked = defaultsSet.has(val);

    const span = document.createElement("span");
    span.className = "form-check-label ms-2 flex-grow-1";
    span.textContent = val;

    label.setAttribute("for", checkbox.id);
    label.appendChild(checkbox);
    label.appendChild(span);
    optionsWrapper.appendChild(label);
  });

  if (search && !search.dataset.boundSearch) {
    search.addEventListener("input", () => filterMultiBox(container, search.value));
    search.dataset.boundSearch = "true";
  }

  if (!optionsWrapper.dataset.boundChange) {
    optionsWrapper.addEventListener("change", (ev) => {
      if (ev.target && ev.target.matches('input[type="checkbox"]')) {
        updateMultiStatus(container);
      }
    });
    optionsWrapper.dataset.boundChange = "true";
  }

  updateMultiStatus(container);
}

function filterMultiBox(container, term) {
  const normalized = term.trim().toLowerCase();
  let visible = 0;
  container.querySelectorAll(".form-check").forEach((row) => {
    const text = row.textContent.toLowerCase();
    const show = !normalized || text.includes(normalized);
    row.style.display = show ? "" : "none";
    if (show) visible++;
  });
  updateMultiStatus(container, visible);
}

function updateMultiStatus(container, visibleCount) {
  const statusEl = container.querySelector(".multi-status");
  if (!statusEl) return;
  const rows = Array.from(container.querySelectorAll(".form-check"));
  const total = rows.length;
  const selected = container.querySelectorAll('input[type="checkbox"]:checked').length;
  const visible =
    visibleCount ??
    rows.filter((row) => {
      const style = row.style.display;
      return style !== "none";
    }).length;
  const term = container.querySelector(".multi-search")?.value.trim();
  if (!total) {
    statusEl.textContent = "Nenhum resultado";
    return;
  }
  const termText = term ? ` para "${term}"` : "";
  statusEl.textContent = `Mostrando ${visible}/${total}${termText} • Selecionados ${selected}`;
}

function wireNavigation() {
  document.querySelectorAll("#tabNav [data-tab]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      document.querySelectorAll("#tabNav [data-tab]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const tab = btn.dataset.tab;
      document.querySelectorAll(".tab-panel").forEach((panel) => {
        panel.classList.toggle("d-none", panel.dataset.panel !== tab);
      });
      if (!loadedTabs.has(tab)) {
        await runQuery(tab);
        loadedTabs.add(tab);
      }
    });
  });
}

function wireButtons() {
  Object.entries(datasets).forEach(([key, cfg]) => {
    document.getElementById(`${cfg.prefix}-filtrar`).addEventListener("click", async () => {
      await runQuery(key);
      collapseFilters(key);
      focusGrid(key);
    });
    document.getElementById(`${cfg.prefix}-limpar`).addEventListener("click", () => {
      clearFilters(key);
      runQuery(key);
    });
    document.getElementById(`${cfg.prefix}-download`).addEventListener("click", () => downloadCsv(key));
  });
}

function clearFilters(key) {
  const cfg = datasets[key];
  cfg.filters.forEach((filter) => {
    if (filter.type === "multi") {
      resetMulti(filter.id, cfg.defaults?.[filter.id]);
    } else if (filter.type === "text") {
      document.getElementById(filter.id).value = "";
    } else if (filter.type === "range") {
      document.getElementById(filter.minId).value = "";
      document.getElementById(filter.maxId).value = "";
    }
  });
}

function resetMulti(id, defaults = []) {
  const el = document.getElementById(id);
  if (!el) return;
  const defaultSet = new Set(defaults ?? []);

  if (isMultiBox(el)) {
    el.querySelectorAll('input[type="checkbox"]').forEach((cb) => {
      cb.checked = defaultSet.has(cb.value);
    });
    const search = el.querySelector(".multi-search");
    if (search) {
      search.value = "";
      filterMultiBox(el, "");
    } else {
      updateMultiStatus(el);
    }
    return;
  }

  if (el.tagName === "SELECT") {
    Array.from(el.options).forEach((opt) => (opt.selected = defaultSet.has(opt.value)));
  }
}

async function runQuery(key) {
  const cfg = datasets[key];
  const selectedIds = cfg.columns.map((c) => c.id);
  const { where, params } = buildWhere(cfg);
  const sql = `SELECT ${selectedIds.join(", ")} FROM ${cfg.table} ${where} ORDER BY ${cfg.orderBy} LIMIT ${GRID_LIMIT}`;
  const stmt = db.prepare(sql);
  stmt.bind(params);
  const rows = [];
  while (stmt.step()) {
    rows.push(stmt.getAsObject());
  }
  stmt.free();
  lastData[key] = rows;
  renderAgGrid(key, cfg, rows);
  setStatus(`Resultados ${cfg.label}: ${rows.length}.`);
}

function buildWhere(cfg) {
  const clauses = [];
  const params = [];
  cfg.filters.forEach((filter) => {
    if (filter.type === "multi") {
      const values = getMultiValues(filter.id);
      if (values.length) {
        if (filter.operator === "like") {
          clauses.push(`(${values.map(() => `${filter.column} LIKE ?`).join(" OR ")})`);
          params.push(...values.map((v) => `%${v}%`));
        } else {
          clauses.push(`${filter.column} IN (${values.map(() => "?").join(", ")})`);
          params.push(...values);
        }
      }
    } else if (filter.type === "text") {
      const text = document.getElementById(filter.id).value.trim();
      if (text) {
        clauses.push(`${filter.column} LIKE ?`);
        params.push(`%${text}%`);
      }
    } else if (filter.type === "range") {
      const minVal = document.getElementById(filter.minId).value;
      const maxVal = document.getElementById(filter.maxId).value;
      if (minVal) {
        clauses.push(`${filter.column} >= ?`);
        params.push(Number(minVal));
      }
      if (maxVal) {
        clauses.push(`${filter.column} <= ?`);
        params.push(Number(maxVal));
      }
    }
  });
  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  return { where, params };
}

function getMultiValues(id) {
  const el = document.getElementById(id);
  if (!el) return [];
  if (isMultiBox(el)) {
    return Array.from(el.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value);
  }
  if (el.tagName === "SELECT") {
    return Array.from(el.selectedOptions).map((opt) => opt.value);
  }
  return [];
}

function renderAgGrid(key, cfg, rows) {
  const container = document.getElementById(`grid-ag-${key}`);
  if (!container || typeof agGrid === "undefined") return;
  const colDefs = buildAgColumns(cfg.columns, new Set(getSelectedColumns(key)));
  if (gridInstances[key]) {
    gridInstances[key].api.setColumnDefs(colDefs);
    gridInstances[key].api.setRowData(rows);
    gridInstances[key].api.sizeColumnsToFit();
    return;
  }
  const gridOptions = {
    columnDefs: colDefs,
    rowData: rows,
    defaultColDef: {
      sortable: true,
      filter: true,
      resizable: true,
      minWidth: 140,
      flex: 1,
      wrapText: true,
      autoHeight: true,
    },
    pagination: true,
    paginationPageSize: PAGE_SIZE,
    animateRows: true,
    domLayout: "autoHeight",
    onFirstDataRendered: (params) => params.api.sizeColumnsToFit(),
    onGridSizeChanged: (params) => params.api.sizeColumnsToFit(),
  };
  new agGrid.Grid(container, gridOptions);
  gridInstances[key] = gridOptions;
}

function buildAgColumns(columns, selectedSet) {
  const safeSet = selectedSet && selectedSet.size ? selectedSet : new Set(columns.slice(0, DEFAULT_VISIBLE_COLS).map((c) => c.id));
  return columns.map((col) => {
    if (col.id === "link") {
      return {
        headerName: col.name,
        field: col.id,
        hide: !safeSet.has(col.id),
        cellRenderer: (params) => {
          if (!params.value) return "";
          const link = document.createElement("a");
          link.href = params.value;
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = "Abrir";
          return link;
        },
      };
    }
    return {
      headerName: col.name,
      field: col.id,
      hide: !safeSet.has(col.id),
    };
  });
}

function downloadCsv(key) {
  const rows = lastData[key] ?? [];
  if (!rows.length) {
    alert("Nenhum dado para exportar. Rode uma consulta antes.");
    return;
  }
  const header = datasets[key].columns.map((c) => c.id);
  const csv = [header.join(",")].concat(
    rows.map((row) =>
      header
        .map((h) => {
          const value = row[h] ?? "";
          if (typeof value === "string" && /[,\n"]/.test(value)) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        })
        .join(",")
    )
  );
  const blob = new Blob([csv.join("\n")], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${key}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function setStatus(text) {
  const el = document.getElementById("status");
  if (el) el.textContent = text;
}

function collapseFilters(key) {
  const details = document.querySelector(`[data-filters="${key}"]`);
  if (details) details.open = false;
}

function focusGrid(key) {
  const cards = document.querySelectorAll(".grid-card");
  cards.forEach((card) => card.classList.remove("grid-card--focus"));
  const target = document.querySelector(`[data-grid-card="${key}"]`);
  if (target) {
    target.classList.add("grid-card--focus");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function wireResize() {
  window.addEventListener("resize", () => {
    Object.values(gridInstances).forEach((grid) => {
      if (grid?.api) grid.api.sizeColumnsToFit();
    });
  });
}

const DB_URL = "./public/data/guia.sqlite.gz";
const DB_CACHE_KEY = "guia-sqlite-v2";
const GRID_LIMIT = 400;

const datasets = {
  graduacao: {
    prefix: "grad",
    label: "Graduação",
    table: "graduacao",
    orderBy: "nome_curso, nome_ies, uf",
    columns: [
      { id: "nome_curso", name: "Curso" },
      { id: "nome_ies", name: "Instituição" },
      { id: "grau", name: "Grau" },
      { id: "modalidade", name: "Modalidade" },
      { id: "area_conhecimento", name: "Área" },
      { id: "municipio", name: "Município" },
      { id: "uf", name: "UF" },
      { id: "vagas_autorizadas", name: "Vagas autorizadas" },
    ],
    filters: [
      { type: "multi", id: "grad-grau", column: "grau" },
      { type: "multi", id: "grad-modalidade", column: "modalidade" },
      { type: "multi", id: "grad-uf", column: "uf" },
      { type: "multi", id: "grad-municipio", column: "municipio" },
      { type: "multi", id: "grad-area", column: "area_conhecimento" },
      { type: "multi", id: "grad-ies", column: "nome_ies" },
      { type: "text", id: "grad-curso", column: "nome_curso" },
    ],
    defaults: {
      "grad-grau": ["Bacharelado", "Licenciatura"],
      "grad-modalidade": ["Educação Presencial"],
    },
  },
  especializacao: {
    prefix: "esp",
    label: "Especialização",
    table: "especializacao",
    orderBy: "nome_especializacao, nome_ies, uf",
    columns: [
      { id: "nome_especializacao", name: "Curso" },
      { id: "nome_ies", name: "Instituição" },
      { id: "modalidade", name: "Modalidade" },
      { id: "carga_horaria", name: "Carga horária" },
      { id: "duracao_meses", name: "Duração (meses)" },
      { id: "municipio", name: "Município" },
      { id: "uf", name: "UF" },
      { id: "area_conhecimento", name: "Área" },
    ],
    filters: [
      { type: "multi", id: "esp-area", column: "area_conhecimento" },
      { type: "multi", id: "esp-modalidade", column: "modalidade" },
      { type: "multi", id: "esp-uf", column: "uf" },
      { type: "multi", id: "esp-municipio", column: "municipio" },
      { type: "multi", id: "esp-ies", column: "nome_ies" },
      { type: "text", id: "esp-curso", column: "nome_especializacao" },
      { type: "range", minId: "esp-carga-min", maxId: "esp-carga-max", column: "carga_horaria" },
      { type: "range", minId: "esp-duracao-min", maxId: "esp-duracao-max", column: "duracao_meses" },
    ],
  },
  pos: {
    prefix: "pos",
    label: "Mestrado/Doutorado",
    table: "pos",
    orderBy: "nome_programa, sigla_ies, uf",
    columns: [
      { id: "nome_programa", name: "Programa" },
      { id: "sigla_ies", name: "Sigla IES" },
      { id: "nome_ies", name: "Instituição" },
      { id: "uf", name: "UF" },
      { id: "municipio", name: "Município" },
      { id: "area_conhecimento", name: "Área de conhecimento" },
      { id: "nota_conceito", name: "Nota" },
      { id: "nivel_programa", name: "Nível" },
      { id: "modalidade", name: "Modalidade" },
      { id: "link", name: "Mais informações" },
    ],
    filters: [
      { type: "multi", id: "pos-nivel", column: "nivel_programa", operator: "like" },
      { type: "multi", id: "pos-area", column: "area_conhecimento" },
      { type: "multi", id: "pos-nota", column: "nota_conceito" },
      { type: "multi", id: "pos-modalidade", column: "modalidade" },
      { type: "multi", id: "pos-uf", column: "uf" },
      { type: "multi", id: "pos-municipio", column: "municipio" },
      { type: "multi", id: "pos-sigla", column: "sigla_ies" },
      { type: "multi", id: "pos-ies", column: "nome_ies" },
    ],
    defaults: {
      "pos-nivel": ["MESTRADO", "DOUTORADO"],
    },
  },
};

let db;
const grids = {};
const lastData = {};
const loadedTabs = new Set();
const selectedColumns = {};

document.addEventListener("DOMContentLoaded", () => {
  init().catch((err) => {
    console.error(err);
    setStatus(`Erro ao iniciar: ${err.message}`);
  });
});

async function init() {
  setStatus("Baixando base SQLite (cache em IndexedDB para os próximos acessos)...");
  db = await loadDatabase();
  setStatus("Base carregada. Monte seus filtros e consulte.");

  initGrids();
  await hydrateFilters();
  wireNavigation();
  wireButtons();
  initColumnToggles();

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

function initGrids() {
  Object.entries(datasets).forEach(([key, cfg]) => {
    const container = document.getElementById(`grid-${key}`);
    const cols = getSelectedColumns(key);
    grids[key] = new gridjs.Grid({
      columns: buildGridColumns(cfg, cols),
      data: [],
      pagination: { limit: 20 },
      sort: true,
      style: {
        table: { width: "100%" },
      },
      language: {
        search: { placeholder: "Filtrar..." },
        pagination: {
          previous: "Anterior",
          next: "Próximo",
          showing: "Mostrando",
          of: "de",
          to: "até",
          results: "registros",
        },
      },
    }).render(container);
  });
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

  // Ajusta placeholders de faixas numéricas da especialização com os valores reais
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

function getSelectedColumns(key) {
  if (!selectedColumns[key] || !selectedColumns[key].length) {
    selectedColumns[key] = datasets[key].columns.slice(0, 4).map((c) => c.id);
  }
  return selectedColumns[key];
}

function buildGridColumns(cfg, colIds) {
  const map = new Map(cfg.columns.map((c) => [c.id, c]));
  return colIds.map((id) => {
    const col = map.get(id);
    if (!col) return { id, name: id, sort: true };
    if (col.id === "link") {
      return {
        name: col.name,
        formatter: (cell) => (cell ? gridjs.html(`<a href="${cell}" target="_blank" rel="noopener">Abrir</a>`) : ""),
      };
    }
    return { id: col.id, name: col.name, sort: true };
  });
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

function initColumnToggles() {
  Object.entries(datasets).forEach(([key, cfg]) => {
    const wrapper = document.querySelector(`[data-col-toggle="${key}"]`);
    if (!wrapper) return;
    const options = wrapper.querySelector(".toggle-options");
    if (!options) return;
    const selectedSet = new Set(getSelectedColumns(key));
    options.innerHTML = "";

    cfg.columns.forEach((col, idx) => {
      const label = document.createElement("label");
      label.className = "form-check column-check";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.className = "form-check-input";
      checkbox.value = col.id;
      checkbox.id = `${key}-col-${idx}`;
      checkbox.checked = selectedSet.has(col.id);

      const span = document.createElement("span");
      span.className = "form-check-label";
      span.textContent = col.name;

      label.setAttribute("for", checkbox.id);
      label.appendChild(checkbox);
      label.appendChild(span);
      options.appendChild(label);

      checkbox.addEventListener("change", (ev) => handleColumnToggleChange(ev, key));
    });
  });
}

function handleColumnToggleChange(ev, key) {
  const container = ev.target.closest(".toggle-options");
  if (!container) return;
  const checked = Array.from(container.querySelectorAll('input[type="checkbox"]:checked')).map((cb) => cb.value);
  if (!checked.length) {
    ev.target.checked = true;
    return;
  }
  const ordered = datasets[key].columns.filter((col) => checked.includes(col.id)).map((col) => col.id);
  selectedColumns[key] = ordered;
  runQuery(key);
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
    document.getElementById(`${cfg.prefix}-filtrar`).addEventListener("click", () => runQuery(key));
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
  const visibleColumns = getSelectedColumns(key);
  const columnDefs = cfg.columns.filter((c) => visibleColumns.includes(c.id));
  const selectedIds = columnDefs.length ? columnDefs.map((c) => c.id) : [cfg.columns[0].id];
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
  grids[key]
    .updateConfig({
      columns: buildGridColumns(cfg, selectedIds),
      data: rows,
    })
    .forceRender();
  setStatus(`Resultado (${datasets[key].label}): ${rows.length} registros exibidos (máx. ${GRID_LIMIT}).`);
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

function downloadCsv(key) {
  const rows = lastData[key] ?? [];
  if (!rows.length) {
    alert("Nenhum dado para exportar. Rode uma consulta antes.");
    return;
  }
  const header = getSelectedColumns(key);
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
  document.getElementById("status").textContent = text;
}

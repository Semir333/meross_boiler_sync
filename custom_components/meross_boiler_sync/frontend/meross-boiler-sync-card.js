/*!
 * Meross Boiler Sync – Lovelace kártya / Lovelace card
 * Verzió / version: 2.6.0
 *
 * Felvétel: Irányítópult szerkesztése → Kártya hozzáadása → "Meross Boiler Sync".
 * Add: Edit dashboard → Add card → "Meross Boiler Sync".
 * YAML: type: custom:meross-boiler-sync-card
 */
(() => {
  "use strict";
  const TAG = "meross-boiler-sync-card";
  const EDITOR_TAG = "meross-boiler-sync-card-editor";
  if (customElements.get(TAG)) return;

  /* ===================================================================
   *  Fordítások (hu / en)
   * =================================================================== */
  const STR = {
    en: {
      st_idle: "Not calling", st_demand: "Calling for heat", st_boost: "Valve forced open",
      st_waiting: "Waiting", st_rest: "Resting", st_stale: "Stale sensor",
      st_window: "Window open", st_windowpend: "Window opening…", st_off: "Valve off",
      target: "Target", boiler: "Boiler", on: "On", off: "Off", calling: "Calling",
      rooms_word: "rooms", outdoor: "Outdoor", avg24: "24 h avg", summer: "Summer mode",
      active: "Active", inactive: "Inactive", valve_control: "Automatic valve control",
      link: "Boiler demand tied to valve", dry: "Dry run", no_data: "No data",
      no_rooms: "No rooms found. Add rooms in the Meross Boiler Sync integration (Configure).",
      description: "Rooms, heat demand and summer mode of the Meross Boiler Sync integration.",
      // szerkesztő
      sec_general: "General", sec_show: "What to show", sec_values: "Values and look", sec_colors: "Colors",
      design: "Design", d_glass: "Glass – ring gauge", d_minimal: "Minimal – compact rows",
      d_gradient: "Gradient tiles", d_list: "List – table with bar",
      title: "Title (optional)", rooms: "Rooms to show",
      h_rooms: "Leave empty to show all rooms. The order is the order you pick them in.",
      columns: "Columns", h_columns: "0 = automatic (fits the card width)",
      show_header: "Show header", show_boiler: "Boiler state", show_demand: "Number of rooms calling for heat",
      show_summer: "Summer mode and outdoor temperature", show_current: "Current temperature",
      show_target: "Target temperature", show_humidity: "Humidity", show_deviation: "Deviation from target",
      show_status: "Status chip", show_flags: "Flags (valve control, link, dry run)",
      gauge_min: "Gauge minimum (°C)", gauge_max: "Gauge maximum (°C)", decimals: "Decimals",
      radius: "Corner radius (px)", opacity: "Background opacity (%)", blur: "Background blur (px)",
      h_gauge: "The ring / bar scale", reset_colors: "Reset colors",
      color_idle: "Color: not calling", color_demand: "Color: calling for heat", color_boost: "Color: valve forced open",
      color_waiting: "Color: waiting", color_rest: "Color: resting", color_stale: "Color: stale sensor",
      color_window: "Color: window open", color_off: "Color: valve off", color_summer: "Color: summer mode",
      editor_no_rooms: "No Meross Boiler Sync rooms found yet – the room list will fill in once they exist.",
      // v2.6
      increase: "Raise target temperature", decrease: "Lower target temperature", preset_word: "Profile",
      size: "Tile size (%)", h_size: "Scales the whole card content (100 = default).",
      tap_action: "Action on tap", ta_valve: "Open the valve thermostat", ta_sensor: "Open the heat demand sensor", ta_none: "Nothing",
      sec_controls: "Controls on the card", show_controls: "− / + buttons (glass design)",
      step: "Step (°C)", h_step: "0 = automatic (the valve's own step)",
      show_presets: "Profile (preset) selector (glass design)",
      sec_effects: "Effects", glow: "Glow around the card", glow_level: "Glow strength (1–5)",
      glow_states: "Glow in these states", h_glow_states: "Pick the states where the glow is shown.",
      animation: "Animated glass design", h_animation: "Glass design only. Turns itself off when the system asks for reduced motion.",
      p_auto: "Auto", p_sleep: "Sleep", p_comfort: "Comfort", p_eco: "Eco", p_away: "Away", p_home: "Home",
      p_manual: "Manual", p_boost: "Boost", p_none: "None",
    },
    hu: {
      st_idle: "Nem kér hőt", st_demand: "Hőt kér", st_boost: "Szelep kinyitva",
      st_waiting: "Vár", st_rest: "Pihenő", st_stale: "Elavult szenzor",
      st_window: "Ablak nyitva", st_windowpend: "Ablak nyílik…", st_off: "Szelep ki",
      target: "Cél", boiler: "Kazán", on: "Be", off: "Ki", calling: "Hőt kér",
      rooms_word: "szoba", outdoor: "Kint", avg24: "24 órás átlag", summer: "Nyári mód",
      active: "Aktív", inactive: "Nem aktív", valve_control: "Automata szelepvezérlés",
      link: "Kazán hőigény a szelephez kötve", dry: "Próbaüzem", no_data: "Nincs adat",
      no_rooms: "Nem találok szobát. Adj hozzá szobákat a Meross Boiler Sync integrációban (Konfigurálás).",
      description: "A Meross Boiler Sync integráció szobái, hőigénye és nyári módja.",
      sec_general: "Általános", sec_show: "Mit mutasson", sec_values: "Értékek és megjelenés", sec_colors: "Színek",
      design: "Dizájn", d_glass: "Üveg – gyűrűs mérő", d_minimal: "Minimál – kompakt sorok",
      d_gradient: "Színátmenetes csempék", d_list: "Lista – táblázat sávval",
      title: "Cím (opcionális)", rooms: "Megjelenítendő szobák",
      h_rooms: "Üresen hagyva az összes szoba megjelenik. A sorrend a kiválasztás sorrendje.",
      columns: "Oszlopok száma", h_columns: "0 = automatikus (a kártya szélességéhez igazodik)",
      show_header: "Fejléc megjelenítése", show_boiler: "Kazán állapota", show_demand: "Hőt kérő szobák száma",
      show_summer: "Nyári mód és kinti hőmérséklet", show_current: "Aktuális hőmérséklet",
      show_target: "Célhőmérséklet", show_humidity: "Páratartalom", show_deviation: "Eltérés a céltól",
      show_status: "Állapotcímke", show_flags: "Jelzők (szelepvezérlés, kötés, próbaüzem)",
      gauge_min: "Mérő alsó értéke (°C)", gauge_max: "Mérő felső értéke (°C)", decimals: "Tizedesjegyek",
      radius: "Sarkok lekerekítése (px)", opacity: "Háttér átlátszatlansága (%)", blur: "Háttér elmosása (px)",
      h_gauge: "A gyűrű / sáv skálája", reset_colors: "Színek visszaállítása",
      color_idle: "Szín: nem kér hőt", color_demand: "Szín: hőt kér", color_boost: "Szín: szelep kinyitva",
      color_waiting: "Szín: vár", color_rest: "Szín: pihenő", color_stale: "Szín: elavult szenzor",
      color_window: "Szín: ablak nyitva", color_off: "Szín: szelep ki", color_summer: "Szín: nyári mód",
      editor_no_rooms: "Még nincs Meross Boiler Sync szoba – a szobalista akkor töltődik fel, ha lesznek.",
      // v2.6
      increase: "Célhőmérséklet növelése", decrease: "Célhőmérséklet csökkentése", preset_word: "Profil",
      size: "Csempe mérete (%)", h_size: "Az egész kártya tartalmát skálázza (100 = alap).",
      tap_action: "Koppintás művelete", ta_valve: "A szelep termosztátjának megnyitása", ta_sensor: "A hőigény szenzor megnyitása", ta_none: "Semmi",
      sec_controls: "Vezérlés a kártyán", show_controls: "− / + gombok (üveg dizájn)",
      step: "Lépésköz (°C)", h_step: "0 = automatikus (a szelep saját lépésköze)",
      show_presets: "Profil (preset) választó (üveg dizájn)",
      sec_effects: "Hatások", glow: "Ragyogás a kártya körül", glow_level: "Ragyogás erőssége (1–5)",
      glow_states: "Mely állapotoknál ragyogjon", h_glow_states: "Jelöld ki azokat az állapotokat, ahol a ragyogás látszik.",
      animation: "Animált üveg dizájn", h_animation: "Csak az üveg dizájnnál. Magától kikapcsol, ha a rendszer csökkentett mozgást kér.",
      p_auto: "Auto", p_sleep: "Alvás", p_comfort: "Komfort", p_eco: "Takarékos", p_away: "Távol", p_home: "Itthon",
      p_manual: "Kézi", p_boost: "Boost", p_none: "Nincs",
    },
  };
  const langOf = (hass) => {
    const l = ((hass && (hass.locale && hass.locale.language || hass.language)) || navigator.language || "en").toLowerCase();
    return l;
  };
  const T = (hass, key) => {
    const l = langOf(hass).startsWith("hu") ? "hu" : "en";
    return (STR[l] && STR[l][key]) || STR.en[key] || key;
  };

  /* ===================================================================
   *  Alapértékek, dizájn előbeállítások, színek
   * =================================================================== */
  const DESIGNS = ["glass", "minimal", "gradient", "list"];
  const DEFAULTS = {
    design: "glass", title: "", rooms: [], columns: 0, size: 100, tap_action: "valve",
    show_controls: true, step: 0, show_presets: true,
    glow: true, glow_level: 3, animation: false,
    show_header: true, show_boiler: true, show_demand: true, show_summer: true,
    show_current: true, show_target: true, show_humidity: true, show_deviation: true,
    show_status: true, show_flags: true,
    gauge_min: 15, gauge_max: 28, decimals: 1,
  };
  const PRESET = {
    glass: { radius: 22, opacity: 55, blur: 14 },
    minimal: { radius: 16, opacity: 40, blur: 0 },
    gradient: { radius: 24, opacity: 100, blur: 0 },
    list: { radius: 14, opacity: 45, blur: 8 },
  };
  const COLOR_KEYS = ["idle", "demand", "boost", "waiting", "rest", "stale", "window", "off", "summer"];
  const DEFAULT_COLORS = {
    idle: [102, 187, 106], demand: [255, 152, 0], boost: [255, 87, 34], waiting: [255, 202, 40],
    rest: [100, 181, 246], stale: [239, 83, 80], window: [79, 195, 247], off: [130, 140, 150],
    summer: [255, 213, 79],
  };
  const GLOW_STATES = ["idle", "demand", "boost", "waiting", "rest", "stale", "window", "off"];
  const GLOW_DEFAULT = GLOW_STATES.filter((k) => k !== "off");
  const FX = {
    demand: '<div class="fx flame"><i></i><i></i><i></i></div>',
    boost: '<div class="fx flame hot"><i></i><i></i><i></i></div>',
    stale: '<div class="fx alarm"></div>',
    window: '<div class="fx wind"><i></i><i></i><i></i><i></i></div>',
    windowpend: '<div class="fx soft"></div>',
    waiting: '<div class="fx"></div>', rest: '<div class="fx"></div>', idle: '<div class="fx soft"></div>',
  };
  const STATUS_COLOR = {
    idle: "idle", demand: "demand", boost: "boost", waiting: "waiting", rest: "rest",
    stale: "stale", window: "window", windowpend: "window", off: "off",
  };

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /** Szín CSS-ként. Tömb [r,g,b] / "#rrggbb" / bármilyen CSS szín (alpha: color-mix). */
  function cssColor(value, alpha) {
    const a = alpha == null ? 1 : alpha;
    let rgb = null;
    if (Array.isArray(value) && value.length >= 3) rgb = value.slice(0, 3).map((n) => clamp(Math.round(Number(n) || 0), 0, 255));
    else if (typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value.trim())) {
      const h = value.trim().slice(1);
      rgb = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
    }
    if (rgb) return a >= 1 ? `rgb(${rgb[0]},${rgb[1]},${rgb[2]})` : `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`;
    if (typeof value === "string" && value) return a >= 1 ? value : `color-mix(in srgb, ${value} ${Math.round(a * 100)}%, transparent)`;
    return "transparent";
  }

  /* ===================================================================
   *  Ikonok (saját, vonalas SVG – nem függ a HA ikonkészletétől)
   * =================================================================== */
  const ICONS = {
    radiator: '<rect x="4" y="5" width="3" height="14" rx="1.5"/><rect x="10.5" y="5" width="3" height="14" rx="1.5"/><rect x="17" y="5" width="3" height="14" rx="1.5"/>',
    drop: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    flame: '<path d="M12 3c.5 3-3 4.5-3 8.5a4 4 0 0 0 8 0c0-2-1-3-2-4.5-.5 1.5-1.5 2-2.5 1.5C13 6.5 12.5 5 12 3z"/>',
    window: '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M12 3v18M5 12h14"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9L7 7M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    valve: '<circle cx="12" cy="12" r="9"/><path d="M12 16V8M8.5 11.5L12 8l3.5 3.5"/>',
    link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    alert: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.1"/>',
    power: '<path d="M12 3v9"/><path d="M6.3 6.8a8 8 0 1 0 11.4 0"/>',
    thermo: '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/>',
    flask: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3"/>',
    pause: '<path d="M9 5v14M15 5v14"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    minus: '<path d="M6 12h12"/>',
    plus: '<path d="M12 6v12M6 12h12"/>',
    chev: '<path d="M6 9l6 6 6-6"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    sofa: '<path d="M5 11V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v3M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v5H3z"/>',
    leaf: '<path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14M5 19l7-7"/>',
    auto: '<circle cx="12" cy="12" r="9"/><path d="M8.5 16l3.5-8 3.5 8M9.8 13.5h4.4"/>',
    tune: '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    home: '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-6h4v6"/>',
    away: '<path d="M5 20V4h8v16M13 12h6M16 9l3 3-3 3"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  };
  const PRESET_ICON = { auto: "auto", sleep: "moon", comfort: "sofa", eco: "leaf", away: "away", home: "home", manual: "tune", boost: "flame" };
  const ic = (name, cls) => `<svg class="ic ${cls || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
  const STATUS_ICON = {
    idle: "thermo", demand: "flame", boost: "valve", waiting: "clock", rest: "pause",
    stale: "alert", window: "window", windowpend: "window", off: "power",
  };

  /* ===================================================================
   *  Adatgyűjtés a HA állapotokból
   * =================================================================== */
  const isRoom = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes &&
    "room_below_target" in s.attributes && "valves" in s.attributes);
  const isSummer = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes &&
    "in_summer_period" in s.attributes);

  function statusOf(a, on) {
    if (a.temperature_sensor_stale) return "stale";
    if (a.window_open) return "window";
    if (a.window_open_pending) return "windowpend";
    if (a.valve_boosted) return "boost";
    if (a.valve_boost_resting) return "rest";
    if (a.valve_boost_waiting) return "waiting";
    if (on) return "demand";
    if (a.valve_active === false) return "off";
    return "idle";
  }

  function collect(hass, cfg) {
    const states = (hass && hass.states) || {};
    let list;
    if (cfg.rooms && cfg.rooms.length) list = cfg.rooms.map((id) => states[id]).filter(isRoom);
    else {
      const lang = langOf(hass);
      list = Object.values(states).filter(isRoom).sort((x, y) =>
        String(x.attributes.room_name || x.attributes.friendly_name).localeCompare(String(y.attributes.room_name || y.attributes.friendly_name), lang));
    }
    const summer = Object.values(states).find(isSummer) || null;
    const boilerId = (summer && summer.attributes.boiler_entity) || cfg.boiler || null;
    const num = (v) => (v == null || v === "" || isNaN(Number(v)) ? null : Number(v));
    const rooms = list.map((s) => {
      const a = s.attributes;
      const on = s.state === "on";
      // a szoba "vezérlő" szelepe: az első elérhető (különben az első létező) climate entitás
      const vs = (Array.isArray(a.valves) ? a.valves : []).map((id) => states[id]).filter(Boolean);
      const v = vs.find((x) => x.state !== "unavailable" && x.state !== "unknown") || vs[0] || null;
      const valve = v ? {
        id: v.entity_id, state: v.state,
        preset: v.attributes.preset_mode == null ? null : String(v.attributes.preset_mode),
        presets: Array.isArray(v.attributes.preset_modes) ? v.attributes.preset_modes.map(String) : [],
        min: num(v.attributes.min_temp), max: num(v.attributes.max_temp), step: num(v.attributes.target_temp_step),
        ok: v.state !== "unavailable" && v.state !== "unknown" && v.state !== "off",
      } : null;
      return {
        id: s.entity_id, on, a, valve,
        valveIds: vs.map((x) => x.entity_id),
        name: a.room_name || a.friendly_name || s.entity_id,
        status: statusOf(a, on),
        cur: a.current_temperature == null ? null : Number(a.current_temperature),
        target: a.target_temperature == null ? null : Number(a.target_temperature),
        hum: a.humidity == null ? null : Number(a.humidity),
        dev: a.deviation == null ? null : Number(a.deviation),
      };
    });
    return { rooms, summer, boiler: boilerId ? states[boilerId] || null : null, boilerId };
  }

  /* ===================================================================
   *  Megjelenítés
   * =================================================================== */
  function arcPath(cx, cy, r, f) {
    const a0 = (135 * Math.PI) / 180;
    const sweep = 270 * clamp(f, 0, 1);
    const a1 = ((135 + sweep) * Math.PI) / 180;
    const x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0);
    const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
    return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${sweep > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
  }
  function pointOn(cx, cy, r, f) {
    const ang = ((135 + 270 * clamp(f, 0, 1)) * Math.PI) / 180;
    return [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
  }

  const CSS = `
    :host { display:block; }
    * { box-sizing:border-box; }
    .root {
      --r: var(--mbs-radius, 22px);
      --op: var(--mbs-opacity, 55%);
      --blur: var(--mbs-blur, 14px);
      --surface: color-mix(in srgb, var(--card-background-color, #1c1c1e) var(--op), transparent);
      --border: color-mix(in srgb, var(--primary-text-color, #fff) 12%, transparent);
      --muted: var(--secondary-text-color, #9aa0a6);
      --text: var(--primary-text-color, #f2f2f2);
      --track: color-mix(in srgb, var(--primary-text-color, #fff) 14%, transparent);
      color: var(--text);
      font-family: var(--ha-font-family-body, var(--paper-font-body1_-_font-family, inherit));
    }
    .ic { width:1.1em; height:1.1em; flex:none; }
    .hd { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 12px; }
    .ttl { font-size:1.15rem; font-weight:600; margin-right:auto; padding-left:4px; }
    .pill { display:inline-flex; align-items:center; gap:7px; padding:7px 13px; border-radius:999px; font-size:.82rem;
      background:var(--surface); border:1px solid var(--border); backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); }
    .pill .ic { color:var(--c, var(--muted)); }
    .pill b { font-weight:600; }
    .pill small { color:var(--muted); font-size:.95em; }
    .pill[data-entity], .t[data-entity] { cursor:pointer; }
    .grid { display:grid; gap:12px; grid-template-columns:repeat(var(--cols), minmax(0,1fr)); }
    .t { position:relative; border-radius:var(--r); background:var(--surface); border:1px solid var(--border);
      backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); overflow:hidden; }
    .t::before { content:""; position:absolute; left:0; right:0; top:0; height:3px; background:var(--c); opacity:.9; }
    .chip { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:999px; font-size:.72rem; font-weight:600;
      color:var(--c); background:color-mix(in srgb, var(--c) 16%, transparent); border:1px solid color-mix(in srgb, var(--c) 35%, transparent); white-space:nowrap; }
    .chip .ic { width:.95em; height:.95em; }
    .fl { display:flex; gap:7px; color:var(--muted); }
    .fl .ic { width:.95em; height:.95em; }
    .dev { font-weight:600; color:var(--c); }
    .msg { padding:18px; border-radius:var(--r); border:1px dashed var(--border); color:var(--muted); text-align:center; }
    ${COLOR_KEYS.map((k) => `[data-st="${k}"] { --c: var(--c-${k}); }`).join("\n")}
    [data-st="windowpend"] { --c: var(--c-window); }

    /* ---------- méretezés (zoom: az egész tartalmat arányosan skálázza) ---------- */
    .zm { zoom:var(--sz, 1); }

    /* ---------- ragyogás (glow) 1-5: az aktuális állapot színével ---------- */
    .gl1 { box-shadow:0 0 .6em 0 color-mix(in srgb, var(--c) 24%, transparent); }
    .gl2 { box-shadow:0 0 1em .05em color-mix(in srgb, var(--c) 34%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 22%, transparent); }
    .gl3 { box-shadow:0 0 1.6em .15em color-mix(in srgb, var(--c) 46%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 34%, transparent); }
    .gl4 { box-shadow:0 0 2.2em .3em color-mix(in srgb, var(--c) 58%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 46%, transparent); }
    .gl5 { box-shadow:0 0 3em .5em color-mix(in srgb, var(--c) 72%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 60%, transparent), inset 0 0 1.6em color-mix(in srgb, var(--c) 14%, transparent); }

    /* ---------- glass ---------- */
    .glass { font-size:16px; text-align:center; }
    .glass .in { position:relative; z-index:2; padding:1em .9em .9em; display:flex; flex-direction:column; align-items:center; gap:.5em; }
    .glass::before { z-index:3; }
    .glass .nm { font-size:1.06em; font-weight:500; letter-spacing:.01em; max-width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .ring { position:relative; width:12.3em; height:12.3em; margin-bottom:.85em; flex:none; }
    .ring svg { width:100%; height:100%; display:block; }
    .ring .mid { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; padding-bottom:1.2em; }
    .big { font-size:3.2em; font-weight:400; line-height:1; display:flex; align-items:flex-start; }
    .big .dc { font-size:.42em; margin-top:.55em; color:var(--muted); }
    .big .un { font-size:.27em; margin:.65em 0 0 .25em; color:var(--muted); }
    .ctl { position:absolute; left:0; right:0; bottom:-.95em; display:flex; align-items:center; justify-content:space-between; padding:0 .45em; }
    .tg { font-size:.82em; color:var(--muted); text-align:center; line-height:1.25; min-width:4em; }
    .tg b { display:block; color:var(--text); font-size:1.15em; font-weight:500; font-variant-numeric:tabular-nums; }
    .pm { width:2.55em; height:2.55em; border-radius:50%; border:1px solid var(--border); padding:0; margin:0; cursor:pointer; font:inherit;
      background:color-mix(in srgb, var(--text) 7%, transparent); color:var(--text); display:grid; place-items:center;
      -webkit-tap-highlight-color:transparent; transition:background .15s, transform .1s; }
    .pm .ic { width:1.15em; height:1.15em; }
    .pm:hover:not(:disabled) { background:color-mix(in srgb, var(--text) 14%, transparent); }
    .pm:active:not(:disabled) { transform:scale(.93); }
    .pm:disabled { opacity:.35; cursor:default; }
    .glass .info { display:flex; gap:1em; align-items:center; justify-content:center; font-size:.88em; min-height:1.4em; }
    .hum { color:var(--c-rest-text, #64b5f6); display:inline-flex; gap:.3em; align-items:center; }
    .glass .foot { position:relative; display:flex; gap:.5em; align-items:center; justify-content:center; flex-wrap:wrap; margin-top:.1em; }
    .glass .chip { font-size:.74em; padding:.28em .75em; }
    .pre { display:inline-flex; align-items:center; gap:.4em; padding:.3em .65em; border-radius:99px; font:inherit; font-size:.76em; font-weight:500;
      color:var(--text); background:color-mix(in srgb, var(--text) 7%, transparent); border:1px solid var(--border); cursor:pointer; white-space:nowrap;
      -webkit-tap-highlight-color:transparent; }
    .pre:hover { background:color-mix(in srgb, var(--text) 14%, transparent); }
    .pre .ic { width:1em; height:1em; }
    .pre .chev { width:.8em; height:.8em; opacity:.7; }
    .menu { position:absolute; right:-.2em; bottom:calc(100% + .5em); min-width:9.5em; max-height:15em; overflow:auto; padding:.35em; border-radius:1em; z-index:6;
      background:color-mix(in srgb, var(--card-background-color, #1c1c1e) 97%, transparent); border:1px solid var(--border);
      box-shadow:0 10px 30px rgba(0,0,0,.45); text-align:left; }
    .mi { display:flex; align-items:center; gap:.6em; width:100%; padding:.5em .65em; border-radius:.7em; font:inherit; font-size:.82em; border:0;
      background:transparent; color:var(--text); cursor:pointer; text-align:left; }
    .mi:hover { background:color-mix(in srgb, var(--text) 9%, transparent); }
    .mi.on { background:color-mix(in srgb, var(--c) 18%, transparent); color:var(--c); font-weight:600; }
    .mi .ic { width:1.15em; height:1.15em; }
    .mi .ck { margin-left:auto; }

    /* ---------- animált réteg (csak az üvegen, kikapcsolható) ---------- */
    .fx { position:absolute; inset:0; z-index:1; pointer-events:none; overflow:hidden; border-radius:inherit; }
    .fx::before { content:""; position:absolute; left:-20%; right:-20%; bottom:-25%; height:60%;
      background:radial-gradient(ellipse 55% 55% at 50% 60%, color-mix(in srgb, var(--c) 62%, transparent), transparent 100%);
      opacity:.35; animation:mbs-breathe 4s ease-in-out infinite; }
    @keyframes mbs-breathe { 0%,100% { opacity:.25; transform:scale(1); } 50% { opacity:.75; transform:scale(1.08); } }
    .fx.soft::before { opacity:.2; animation-name:mbs-breathe-soft; }
    @keyframes mbs-breathe-soft { 0%,100% { opacity:.1; transform:scale(1); } 50% { opacity:.42; transform:scale(1.05); } }
    .fx.flame i { position:absolute; bottom:-18%; width:34%; height:46%; border-radius:50% 50% 45% 45% / 72% 72% 28% 28%;
      background:radial-gradient(ellipse at 50% 100%, color-mix(in srgb, var(--c) 82%, transparent) 0%, color-mix(in srgb, var(--c) 38%, transparent) 46%, transparent 74%);
      filter:blur(8px); transform-origin:50% 100%; opacity:.7; animation:mbs-lick 2s ease-in-out infinite; }
    .fx.flame i:nth-child(1) { left:-4%; animation-duration:2s; animation-delay:-.4s; }
    .fx.flame i:nth-child(2) { left:33%; height:56%; animation-duration:1s; animation-delay:-.2s; }
    .fx.flame i:nth-child(3) { left:70%; animation-duration:2s; animation-delay:-1.1s; }
    @keyframes mbs-lick { 0%,100% { transform:scale(.9,.8) skewX(0); } 25% { transform:scale(1.05,1.1) skewX(-4deg); }
      50% { transform:scale(.95,.95) skewX(3deg); } 75% { transform:scale(1.08,1.2) skewX(-2deg); } }
    .fx.flame.hot i { height:62%; opacity:.95; }
    .fx.flame.hot i:nth-child(2) { height:74%; animation-duration:.5s; }
    .fx.flame.hot i:nth-child(1), .fx.flame.hot i:nth-child(3) { animation-duration:1s; }
    .fx.alarm::before { animation:mbs-alarm 2s ease-in-out infinite; }
    .fx.alarm::after { content:""; position:absolute; left:8%; right:8%; bottom:0; height:2px; border-radius:2px; background:var(--c);
      box-shadow:0 0 14px 2px var(--c); animation:mbs-alarm 2s ease-in-out infinite; }
    @keyframes mbs-alarm { 0%,100% { opacity:.12; } 50% { opacity:.9; } }
    .fx.wind i { position:absolute; left:0; width:60%; height:2px; border-radius:2px; opacity:0;
      background:linear-gradient(90deg, transparent, color-mix(in srgb, var(--c) 75%, transparent), transparent);
      filter:blur(.6px); animation:mbs-gust 4s linear infinite; }
    .fx.wind i:nth-child(1) { top:54%; animation-duration:4s; animation-delay:-.5s; }
    .fx.wind i:nth-child(2) { top:63%; width:45%; animation-duration:2s; animation-delay:-1.2s; }
    .fx.wind i:nth-child(3) { top:72%; width:72%; animation-duration:4s; animation-delay:-2.6s; }
    .fx.wind i:nth-child(4) { top:80%; width:40%; animation-duration:2s; animation-delay:-.3s; }
    @keyframes mbs-gust { 0% { transform:translateX(-70%); opacity:0; } 15% { opacity:.6; } 80% { opacity:.5; } 100% { transform:translateX(240%); opacity:0; } }
    @media (prefers-reduced-motion: reduce) { .fx, .fx::before, .fx::after, .fx * { animation:none !important; } }

    /* ---------- minimal ---------- */
    .minimal { display:flex; align-items:center; gap:12px; padding:11px 14px; }
    .minimal .ib { width:42px; height:42px; border-radius:50%; display:grid; place-items:center; flex:none;
      color:var(--c); background:color-mix(in srgb, var(--c) 18%, transparent); }
    .minimal .ib .ic { width:22px; height:22px; }
    .minimal .tx { min-width:0; flex:1; }
    .minimal .nm { font-weight:600; font-size:.95rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .minimal .sb { font-size:.8rem; color:var(--muted); margin-top:2px; display:flex; flex-wrap:wrap; align-items:center; gap:2px 10px; }
    .minimal .sb > * { white-space:nowrap; }
    .minimal .sb b { color:var(--text); font-weight:600; }

    /* ---------- gradient ---------- */
    .gradient { padding:14px 16px 16px; display:flex; flex-direction:column; gap:6px; border:0;
      background:linear-gradient(155deg, color-mix(in srgb, var(--c) 42%, var(--card-background-color, #1c1c1e)) 0%,
        color-mix(in srgb, var(--c) 10%, var(--card-background-color, #1c1c1e)) 100%); }
    .gradient::before { display:none; }
    .gradient .top { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:6px 8px; }
    .gradient .nm { font-weight:600; font-size:1rem; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .gradient .chip { background:color-mix(in srgb, #000 22%, transparent); color:var(--text); border-color:transparent; }
    .gradient .bg { font-size:2.6rem; font-weight:300; line-height:1.05; }
    .gradient .bg small { font-size:1rem; color:color-mix(in srgb, var(--text) 70%, transparent); margin-left:4px; }
    .gradient .sb { font-size:.82rem; color:color-mix(in srgb, var(--text) 78%, transparent); display:flex; gap:12px; flex-wrap:wrap; }
    .bar { position:relative; height:6px; border-radius:99px; background:color-mix(in srgb, var(--text) 16%, transparent); margin-top:6px; }
    .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:99px; background:var(--c); }
    .bar b { position:absolute; top:-3px; width:3px; height:12px; border-radius:2px; background:var(--text); transform:translateX(-50%); }

    /* ---------- list ---------- */
    .tbl { border-radius:var(--r); background:var(--surface); border:1px solid var(--border); overflow:hidden;
      backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); }
    .rw { display:grid; grid-template-columns:minmax(110px,1.1fr) 84px 92px minmax(90px,2fr) 118px 215px; gap:12px; align-items:center;
      padding:10px 16px; border-top:1px solid var(--border); position:relative; }
    .rw:first-child { border-top:0; }
    .rw::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--c); }
    .rw .nm { font-weight:600; font-size:.93rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .rw .v { font-size:1.05rem; font-variant-numeric:tabular-nums; text-align:right; white-space:nowrap; }
    .rw .v small { color:var(--muted); font-size:.75em; }
    .rw .bar { margin:0; }
    .rw[data-entity] { cursor:pointer; }
    @media (max-width:560px) { .rw { grid-template-columns:1fr auto auto; } .rw .bar, .rw .hum, .rw .fl { display:none; } }
  `;

  class MerossBoilerSyncCard extends HTMLElement {
    static getConfigElement() { return document.createElement(EDITOR_TAG); }
    static getStubConfig() { return { design: "glass" }; }

    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._sig = null;
      this._open = null;          // melyik szoba profil-listája van nyitva
      this._pending = {};         // szoba -> {value, timer, sent, expire}: a + / − gombok még nem érvényesült értéke
      this._pendingPreset = {};   // szoba -> {value, expire}
      this._onDoc = (ev) => {
        if (this._open == null) return;
        if (ev.type === "keydown" && ev.key !== "Escape") return;
        if (ev.type === "click") {
          const path = typeof ev.composedPath === "function" ? ev.composedPath() : [];
          if (path.some((n) => n && n.classList && (n.classList.contains("menu") || n.classList.contains("pre")))) return;
        }
        this._open = null;
        this._sig = null;
        this._render();
      };
    }

    connectedCallback() {
      document.addEventListener("click", this._onDoc, true);
      document.addEventListener("keydown", this._onDoc, true);
    }

    disconnectedCallback() {
      document.removeEventListener("click", this._onDoc, true);
      document.removeEventListener("keydown", this._onDoc, true);
      Object.values(this._pending).forEach((p) => { clearTimeout(p.timer); clearTimeout(p.expire); });
      Object.values(this._pendingPreset).forEach((p) => clearTimeout(p.expire));
      this._pending = {};
      this._pendingPreset = {};
    }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...DEFAULTS, ...config };
      if (!DESIGNS.includes(c.design)) c.design = "glass";
      // régi (2.5) beállítás: tap_more_info: false  ->  tap_action: none
      if (config.tap_action === undefined && config.tap_more_info === false) c.tap_action = "none";
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      this._config = c;
      this._sig = null;
      this._render();
    }

    set hass(hass) {
      this._hass = hass;
      this._render();
    }

    getCardSize() {
      const n = this._data ? this._data.rooms.length : 4;
      const z = clamp(Number(this._config && this._config.size) || 100, 70, 160) / 100;
      if (this._config && this._config.design === "list") return Math.max(2, Math.ceil(n * 0.6) + 1);
      if (this._config && this._config.design === "glass") return Math.max(4, Math.ceil(Math.ceil(n / 3) * 7 * z));
      return Math.max(3, Math.ceil(n / 3) * 3);
    }

    getGridOptions() { return { columns: 12, min_columns: 3 }; }

    _vars(cfg) {
      const p = PRESET[cfg.design];
      const num = (v, d) => (v == null || v === "" || isNaN(Number(v)) ? d : Number(v));
      const colors = COLOR_KEYS.map((k) => `--c-${k}:${cssColor(cfg["color_" + k] != null ? cfg["color_" + k] : DEFAULT_COLORS[k])}`).join(";");
      const cols = Math.round(num(cfg.columns, 0));
      const grid = cols > 0 ? `--cols:${cols}` : `--cols:auto-fill`;
      return `--mbs-radius:${num(cfg.radius, p.radius)}px;--mbs-opacity:${num(cfg.opacity, p.opacity)}%;--mbs-blur:${num(cfg.blur, p.blur)}px;${colors};${grid}`;
    }

    _unit() {
      const u = this._hass && this._hass.config && this._hass.config.unit_system && this._hass.config.unit_system.temperature;
      return u || "°C";
    }

    _num(v, d) {
      if (v == null || isNaN(v)) return "–";
      const lang = langOf(this._hass);
      return Number(v).toLocaleString(lang, { minimumFractionDigits: d, maximumFractionDigits: d });
    }

    _chip(r) {
      if (!this._config.show_status) return "";
      const key = r.status === "windowpend" ? "st_windowpend" : "st_" + r.status;
      return `<span class="chip">${ic(STATUS_ICON[r.status])}${esc(T(this._hass, key))}</span>`;
    }

    _flags(r) {
      if (!this._config.show_flags) return "";
      const a = r.a, h = this._hass, out = [];
      if (a.valve_control) out.push(`<span title="${esc(T(h, "valve_control"))}">${ic("valve")}</span>`);
      if (a.valve_demand_link) out.push(`<span title="${esc(T(h, "link"))}">${ic("link")}</span>`);
      if (a.valve_dry_run && a.valve_control) out.push(`<span title="${esc(T(h, "dry"))}">${ic("flask")}</span>`);
      return out.length ? `<span class="fl">${out.join("")}</span>` : "";
    }

    _dev(r) {
      if (!this._config.show_deviation || r.dev == null) return "";
      if (r.dev > 0.05) return `<span class="dev">−${this._num(r.dev, 1)}°</span>`;
      return `<span class="dev">✓</span>`;
    }

    _hum(r) {
      if (!this._config.show_humidity || r.hum == null) return "";
      return `<span class="hum">${ic("drop")}${this._num(r.hum, 0)}%</span>`;
    }

    /* ---------- koppintás / ragyogás / vezérlés segédek ---------- */
    _tapAction() { return this._config.tap_action; }
    _tapOn() { return this._tapAction() !== "none"; }
    _tapEntity(r) {
      const a = this._tapAction();
      if (a === "none") return null;
      if (a === "valve" && r.valve) return r.valve.id;
      return r.id;
    }
    _tapAttr(r) {
      const e = this._tapEntity(r);
      return e ? `data-entity="${esc(e)}"` : "";
    }

    _glowCls(r) {
      const c = this._config;
      if (!c.glow) return "";
      const lvl = clamp(Math.round(Number(c.glow_level) || 3), 1, 5);
      const list = Array.isArray(c.glow_states) ? c.glow_states : GLOW_DEFAULT;
      const key = r.status === "windowpend" ? "window" : r.status;
      return list.includes(key) ? `gl${lvl}` : "";
    }

    _bounds(r) {
      const v = r.valve, c = this._config;
      const lo = v && v.min != null ? v.min : 5, hi = v && v.max != null ? v.max : 35;
      const step = Number(c.step) > 0 ? Number(c.step) : (v && v.step > 0 ? v.step : 0.5);
      return { lo, hi, step };
    }

    _presetLabel(r, p) {
      const h = this._hass;
      try {
        if (h && typeof h.formatEntityAttributeValue === "function" && h.states[r.valve.id]) {
          const t = h.formatEntityAttributeValue(h.states[r.valve.id], "preset_mode", p);
          if (t && String(t) !== String(p)) return String(t);
        }
      } catch (e) { /* tartalék lent */ }
      const k = "p_" + String(p).toLowerCase();
      if (STR.en[k]) return T(h, k);
      const txt = String(p).replace(/[_-]+/g, " ");
      return txt.charAt(0).toUpperCase() + txt.slice(1);
    }

    _callService(domain, service, data) {
      const h = this._hass;
      if (!h || typeof h.callService !== "function") return Promise.resolve();
      try { return Promise.resolve(h.callService(domain, service, data)); } catch (e) { return Promise.reject(e); }
    }

    _redraw() { this._sig = null; this._render(); }

    _room(id) { return this._data && this._data.rooms.find((x) => x.id === id); }

    /** + / −: a kijelzett érték azonnal változik, a hívás a gyors koppintások után egyszer megy el. */
    _adjust(id, dir) {
      const r = this._room(id);
      if (!r || !r.valve || !r.valve.ok) return;
      const { lo, hi, step } = this._bounds(r);
      const pend = this._pending[id];
      const base = pend ? pend.value : r.target;
      if (base == null) return;
      let v = dir > 0 ? Math.floor(base / step + 1e-9) * step + step : Math.ceil(base / step - 1e-9) * step - step;
      v = Math.round(clamp(v, lo, hi) * 100) / 100;
      if (pend) { clearTimeout(pend.timer); clearTimeout(pend.expire); }
      this._pending[id] = { value: v, sent: false, timer: setTimeout(() => this._commit(id), 700), expire: null };
      this._redraw();
    }

    _commit(id) {
      const p = this._pending[id], r = this._room(id);
      if (!p) return;
      if (!r || !r.valveIds.length) { delete this._pending[id]; this._redraw(); return; }
      p.sent = true;
      p.expire = setTimeout(() => { if (this._pending[id] === p) { delete this._pending[id]; this._redraw(); } }, 8000);
      this._callService("climate", "set_temperature", { entity_id: r.valveIds, temperature: p.value })
        .catch(() => { if (this._pending[id] === p) { clearTimeout(p.expire); delete this._pending[id]; this._redraw(); } });
    }

    _setPreset(id, preset) {
      const r = this._room(id);
      this._open = null;
      if (!r || !r.valveIds.length) { this._redraw(); return; }
      const old = this._pendingPreset[id];
      if (old) clearTimeout(old.expire);
      const p = { value: preset, expire: null };
      p.expire = setTimeout(() => { if (this._pendingPreset[id] === p) { delete this._pendingPreset[id]; this._redraw(); } }, 8000);
      this._pendingPreset[id] = p;
      this._redraw();
      this._callService("climate", "set_preset_mode", { entity_id: r.valveIds, preset_mode: preset })
        .catch(() => { if (this._pendingPreset[id] === p) { clearTimeout(p.expire); delete this._pendingPreset[id]; this._redraw(); } });
    }

    _act(ds) {
      if (ds.act === "inc") this._adjust(ds.room, 1);
      else if (ds.act === "dec") this._adjust(ds.room, -1);
      else if (ds.act === "menu") { this._open = this._open === ds.room ? null : ds.room; this._redraw(); }
      else if (ds.act === "preset") this._setPreset(ds.room, ds.preset);
    }

    /** A hass-ból érkező értékek utolérték a várakozó (optimista) értékeket: eldobjuk őket. */
    _settle(rooms) {
      rooms.forEach((r) => {
        const p = this._pending[r.id];
        if (p && p.sent && r.target != null && Math.abs(r.target - p.value) < 0.05) {
          clearTimeout(p.expire);
          delete this._pending[r.id];
        }
        const q = this._pendingPreset[r.id];
        if (q && r.valve && r.valve.preset === q.value) {
          clearTimeout(q.expire);
          delete this._pendingPreset[r.id];
        }
      });
    }

    _tileGlass(r) {
      const c = this._config, d = Number(c.decimals) || 0, h = this._hass;
      const min = Number(c.gauge_min), max = Number(c.gauge_max), span = Math.max(1, max - min);
      const v = r.valve;
      const pend = this._pending[r.id], pendP = this._pendingPreset[r.id];
      const target = pend ? pend.value : r.target;
      const showCtl = !!(c.show_controls && v && r.target != null);
      const f = r.cur == null ? 0 : (r.cur - min) / span;
      const ft = target == null ? null : (target - min) / span;
      let marker = "";
      if (ft != null && (c.show_target || showCtl)) {
        const [mx, my] = pointOn(60, 60, 50, ft);
        marker = `<circle cx="${mx.toFixed(2)}" cy="${my.toFixed(2)}" r="4.5" fill="var(--text)" stroke="var(--surface)" stroke-width="2"/>`;
      }
      let big = "";
      if (c.show_current) {
        const s = this._num(r.cur, d), sep = s.search(/[.,]/);
        const ip = sep < 0 ? s : s.slice(0, sep), dp = sep < 0 ? "" : s.slice(sep);
        big = `<div class="big">${esc(ip)}${dp ? `<span class="dc">${esc(dp)}</span>` : ""}<span class="un">${esc(this._unit())}</span></div>`;
      }

      // célhőmérséklet + − / + gombok
      const { lo, hi } = this._bounds(r);
      const canChange = showCtl && v.ok;
      const btn = (dir) => {
        if (!showCtl) return "<span></span>";
        const off = !canChange || (dir < 0 ? target <= lo + 1e-9 : target >= hi - 1e-9);
        return `<button type="button" class="pm" data-act="${dir < 0 ? "dec" : "inc"}" data-room="${esc(r.id)}" aria-label="${esc(T(h, dir < 0 ? "decrease" : "increase"))}"${off ? " disabled" : ""}>${ic(dir < 0 ? "minus" : "plus")}</button>`;
      };
      const tg = (c.show_target || showCtl) && target != null
        ? `<div class="tg">${esc(T(h, "target"))}<b>${this._num(target, d)}°</b></div>` : "<span></span>";

      // profil (preset) választó
      const showPre = !!(c.show_presets && v && v.presets.length);
      let pre = "", menu = "";
      if (showPre) {
        const cur = pendP ? pendP.value : v.preset;
        const open = this._open === r.id;
        const label = cur != null ? this._presetLabel(r, cur) : T(h, "preset_word");
        pre = `<button type="button" class="pre" data-act="menu" data-room="${esc(r.id)}" aria-haspopup="listbox" aria-expanded="${open}"${v.state === "unavailable" ? " disabled" : ""}>${ic(PRESET_ICON[cur] || "tune")}<span>${esc(label)}</span>${ic("chev", "chev")}</button>`;
        if (open) {
          menu = `<div class="menu" role="listbox" data-act="none">${v.presets.map((p) =>
            `<button type="button" class="mi${p === cur ? " on" : ""}" role="option" aria-selected="${p === cur}" data-act="preset" data-room="${esc(r.id)}" data-preset="${esc(p)}">${ic(PRESET_ICON[p] || "tune")}<span>${esc(this._presetLabel(r, p))}</span>${p === cur ? `<span class="ck">${ic("check")}</span>` : ""}</button>`).join("")}</div>`;
        }
      }

      const info = [this._hum(r), this._dev(r), this._flags(r)].filter(Boolean).join("");
      const chip = this._chip(r);
      const fx = c.animation ? FX[r.status] || "" : "";
      return `<div class="t glass ${this._glowCls(r)}" data-st="${r.status}" ${this._tapAttr(r)}>
        ${fx}
        <div class="in">
          <div class="nm">${esc(r.name)}</div>
          <div class="ring">
            <svg viewBox="0 0 120 120"><path d="${arcPath(60, 60, 50, 1)}" fill="none" stroke="var(--track)" stroke-width="9" stroke-linecap="round"/>
              ${r.cur != null ? `<path d="${arcPath(60, 60, 50, Math.max(f, 0.001))}" fill="none" stroke="var(--c)" stroke-width="9" stroke-linecap="round"/>` : ""}${marker}</svg>
            <div class="mid">${big}</div>
            <div class="ctl">${btn(-1)}${tg}${btn(1)}</div>
          </div>
          <div class="info">${info}</div>
          ${chip || pre ? `<div class="foot">${chip}${pre}${menu}</div>` : ""}
        </div>
      </div>`;
    }

    _tileMinimal(r) {
      const c = this._config, d = Number(c.decimals) || 0, bits = [];
      if (c.show_current) bits.push(`<b>${this._num(r.cur, d)} ${esc(this._unit())}</b>`);
      if (c.show_target && r.target != null) bits.push(`<span>${esc(T(this._hass, "target"))} ${this._num(r.target, d)}°</span>`);
      if (c.show_humidity && r.hum != null) bits.push(this._hum(r));
      if (c.show_deviation && r.dev != null) bits.push(this._dev(r));
      return `<div class="t minimal ${this._glowCls(r)}" data-st="${r.status}" ${this._tapAttr(r)}>
        <div class="ib">${ic(STATUS_ICON[r.status])}</div>
        <div class="tx"><div class="nm">${esc(r.name)}</div><div class="sb">${bits.join("")}${this._flags(r)}</div></div>
        ${this._chip(r)}
      </div>`;
    }

    _bar(r) {
      const c = this._config, min = Number(c.gauge_min), span = Math.max(1, Number(c.gauge_max) - min);
      const f = r.cur == null ? 0 : clamp((r.cur - min) / span, 0, 1) * 100;
      const ft = r.target == null || !c.show_target ? null : clamp((r.target - min) / span, 0, 1) * 100;
      return `<div class="bar"><i style="width:${f.toFixed(1)}%"></i>${ft != null ? `<b style="left:${ft.toFixed(1)}%"></b>` : ""}</div>`;
    }

    _tileGradient(r) {
      const c = this._config, d = Number(c.decimals) || 0, sb = [];
      if (c.show_target && r.target != null) sb.push(`<span>${esc(T(this._hass, "target"))} ${this._num(r.target, d)}°</span>`);
      if (c.show_humidity && r.hum != null) sb.push(this._hum(r));
      if (c.show_deviation && r.dev != null) sb.push(this._dev(r));
      const flags = this._flags(r);
      return `<div class="t gradient ${this._glowCls(r)}" data-st="${r.status}" ${this._tapAttr(r)}>
        <div class="top"><span class="nm">${esc(r.name)}</span>${this._chip(r)}</div>
        ${c.show_current ? `<div class="bg">${this._num(r.cur, d)}<small>${esc(this._unit())}</small></div>` : ""}
        <div class="sb">${sb.join("")}${flags}</div>
        ${this._bar(r)}
      </div>`;
    }

    _rowList(r) {
      const c = this._config, d = Number(c.decimals) || 0;
      return `<div class="rw" data-st="${r.status}" ${this._tapAttr(r)}>
        <span class="nm">${esc(r.name)}</span>
        <span class="v">${c.show_current ? `${this._num(r.cur, d)}<small> ${esc(this._unit())}</small>` : ""}</span>
        <span class="v">${c.show_target && r.target != null ? `<small>${esc(T(this._hass, "target"))}</small> ${this._num(r.target, d)}°` : ""}</span>
        ${this._bar(r)}
        <span>${this._hum(r)} ${this._dev(r)}</span>
        <span style="display:flex;gap:8px;align-items:center;justify-content:flex-end">${this._flags(r)}${this._chip(r)}</span>
      </div>`;
    }

    _header(data) {
      const c = this._config, h = this._hass, pills = [];
      if (c.show_boiler && data.boiler) {
        const on = data.boiler.state !== "off" && data.boiler.state !== "unavailable" && data.boiler.state !== "unknown";
        pills.push(`<span class="pill" style="--c:${on ? "var(--c-demand)" : "var(--c-off)"}" ${this._tapOn() ? `data-entity="${esc(data.boilerId)}"` : ""}>${ic("flame")}<span>${esc(T(h, "boiler"))}:</span> <b>${esc(T(h, on ? "on" : "off"))}</b></span>`);
      }
      if (c.show_demand) {
        const n = data.rooms.filter((r) => r.on).length;
        pills.push(`<span class="pill" style="--c:${n ? "var(--c-demand)" : "var(--c-idle)"}">${ic("radiator")}<span>${esc(T(h, "calling"))}:</span> <b>${n}/${data.rooms.length}</b> <small>${esc(T(h, "rooms_word"))}</small></span>`);
      }
      if (c.show_summer && data.summer) {
        const s = data.summer, a = s.attributes, on = s.state === "on", u = this._unit();
        const out = a.outdoor_temperature != null ? `${esc(T(h, "outdoor"))} ${this._num(a.outdoor_temperature, 1)}${esc(u)}` : "";
        const avg = a.outdoor_average_24h != null ? `${esc(T(h, "avg24"))} ${this._num(a.outdoor_average_24h, 1)}${esc(u)}` : "";
        pills.push(`<span class="pill" style="--c:${on ? "var(--c-summer)" : "var(--c-off)"}" ${this._tapOn() ? `data-entity="${esc(s.entity_id)}"` : ""}>${ic("sun")}<span>${esc(T(h, "summer"))}:</span> <b>${esc(T(h, on ? "active" : "inactive"))}</b>${out || avg ? ` <small>${[out, avg].filter(Boolean).join(" · ")}</small>` : ""}</span>`);
      }
      const title = c.title ? `<div class="ttl">${esc(c.title)}</div>` : "";
      if (!pills.length && !title) return "";
      return `<div class="hd">${title}${c.show_header ? pills.join("") : ""}</div>`;
    }

    _render() {
      if (!this._config || !this._hass) return;
      const cfg = this._config;
      const data = collect(this._hass, cfg);
      this._data = data;
      this._settle(data.rooms);
      const ui = [this._open, Object.keys(this._pending).map((k) => [k, this._pending[k].value]),
        Object.keys(this._pendingPreset).map((k) => [k, this._pendingPreset[k].value])];
      const sig = JSON.stringify([cfg, data.rooms.map((r) => [r.id, r.on, r.a, r.valve, r.valveIds]), data.summer && [data.summer.state, data.summer.attributes],
        data.boiler && data.boiler.state, langOf(this._hass), ui]);
      if (sig === this._sig) return;
      this._sig = sig;

      let body;
      if (!data.rooms.length) body = `<div class="msg">${esc(T(this._hass, "no_rooms"))}</div>`;
      else if (cfg.design === "list") body = `<div class="tbl">${data.rooms.map((r) => this._rowList(r)).join("")}</div>`;
      else {
        const tile = { glass: "_tileGlass", minimal: "_tileMinimal", gradient: "_tileGradient" }[cfg.design];
        const minw = { glass: 250, minimal: 300, gradient: 235 }[cfg.design];
        body = `<div class="grid" style="${Number(cfg.columns) > 0 ? "" : `grid-template-columns:repeat(auto-fill,minmax(min(100%,${minw}px),1fr))`}">${data.rooms.map((r) => this[tile](r)).join("")}</div>`;
      }
      if (data.rooms.length) body = `<div class="zm">${body}</div>`;
      const sz = clamp(Number(cfg.size) || 100, 70, 160) / 100;
      this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="root" style="${this._vars(cfg)};--sz:${sz}">${data.rooms.length || cfg.title ? this._header(data) : ""}${body}</div>`;
      const root = this.shadowRoot;
      root.querySelectorAll("[data-entity]").forEach((el) => {
        el.addEventListener("click", (ev) => {
          if (ev.target && ev.target.closest && ev.target.closest("[data-act]")) return;
          this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId: el.getAttribute("data-entity") } }));
        });
      });
      root.querySelectorAll("[data-act]").forEach((el) => {
        el.addEventListener("click", (ev) => {
          ev.stopPropagation();
          this._act(el.dataset);
        });
      });
    }
  }

  /* ===================================================================
   *  Vizuális szerkesztő (ha-form alapú)
   * =================================================================== */
  class MerossBoilerSyncCardEditor extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._config = { ...DEFAULTS };
      this._built = false;
    }

    setConfig(config) {
      this._config = { ...config };
      this._update();
    }

    set hass(hass) {
      this._hass = hass;
      this._update();
    }

    connectedCallback() { this._update(); }

    _label(name) { return T(this._hass, name); }

    _roomOptions() {
      const states = (this._hass && this._hass.states) || {};
      return Object.values(states).filter(isRoom)
        .map((s) => ({ value: s.entity_id, label: s.attributes.room_name || s.attributes.friendly_name || s.entity_id }))
        .sort((a, b) => a.label.localeCompare(b.label, langOf(this._hass)));
    }

    _sections() {
      const B = (name) => ({ name, selector: { boolean: {} } });
      const col = (k) => ({ name: "color_" + k, selector: { color_rgb: {} } });
      return [
        { id: "sec_general", open: true, schema: [
          { name: "design", selector: { select: { mode: "dropdown", options: DESIGNS.map((d) => ({ value: d, label: this._label("d_" + d) })) } } },
          { name: "title", selector: { text: {} } },
          { name: "rooms", selector: { select: { multiple: true, mode: "list", options: this._roomOptions() } } },
          { name: "columns", selector: { number: { min: 0, max: 8, step: 1, mode: "box" } } },
          { name: "size", selector: { number: { min: 70, max: 160, step: 5, mode: "slider", unit_of_measurement: "%" } } },
          { name: "tap_action", selector: { select: { mode: "dropdown", options: ["valve", "sensor", "none"].map((v) => ({ value: v, label: this._label("ta_" + v) })) } } },
        ] },
        { id: "sec_controls", schema: [
          B("show_controls"),
          { name: "step", selector: { number: { min: 0, max: 2, step: 0.1, mode: "box", unit_of_measurement: "°C" } } },
          B("show_presets"),
        ] },
        { id: "sec_effects", schema: [
          B("glow"),
          { name: "glow_level", selector: { number: { min: 1, max: 5, step: 1, mode: "slider" } } },
          { name: "glow_states", selector: { select: { multiple: true, mode: "list", options: GLOW_STATES.map((k) => ({ value: k, label: this._label("st_" + k) })) } } },
          B("animation"),
        ] },
        { id: "sec_show", schema: ["show_header", "show_boiler", "show_demand", "show_summer", "show_current", "show_target",
          "show_humidity", "show_deviation", "show_status", "show_flags"].map(B) },
        { id: "sec_values", schema: [
          { name: "gauge_min", selector: { number: { min: -20, max: 40, step: 0.5, mode: "box", unit_of_measurement: "°C" } } },
          { name: "gauge_max", selector: { number: { min: -10, max: 60, step: 0.5, mode: "box", unit_of_measurement: "°C" } } },
          { name: "decimals", selector: { select: { mode: "dropdown", options: [{ value: "0", label: "0" }, { value: "1", label: "1" }, { value: "2", label: "2" }] } } },
          { name: "radius", selector: { number: { min: 0, max: 40, step: 1, mode: "slider", unit_of_measurement: "px" } } },
          { name: "opacity", selector: { number: { min: 0, max: 100, step: 1, mode: "slider", unit_of_measurement: "%" } } },
          { name: "blur", selector: { number: { min: 0, max: 30, step: 1, mode: "slider", unit_of_measurement: "px" } } },
        ] },
        { id: "sec_colors", schema: COLOR_KEYS.map(col), reset: true },
      ];
    }

    /** A szerkesztő mezőiben a kijelzett érték: alapértékek + dizájn előbeállítás + a felhasználó beállításai. */
    _display() {
      const c = { ...DEFAULTS, ...this._config };
      if (!DESIGNS.includes(c.design)) c.design = "glass";
      const p = PRESET[c.design];
      ["radius", "opacity", "blur"].forEach((k) => { if (c[k] == null) c[k] = p[k]; });
      c.decimals = String(c.decimals);
      if (!Array.isArray(c.rooms)) c.rooms = [];
      if (this._config.tap_action === undefined && this._config.tap_more_info === false) c.tap_action = "none";
      delete c.tap_more_info;
      if (!Array.isArray(c.glow_states)) c.glow_states = GLOW_DEFAULT.slice();
      return c;
    }

    _emit(value) {
      const v = { ...value };
      v.decimals = Number(v.decimals);
      // ami az előző vagy az új dizájn alapértéke, az nem egyéni beállítás (dizájnváltáskor ne ragadjon be)
      const pNew = PRESET[DESIGNS.includes(v.design) ? v.design : "glass"];
      const pOld = PRESET[DESIGNS.includes(this._config.design) ? this._config.design : "glass"];
      ["radius", "opacity", "blur"].forEach((k) => { if (Number(v[k]) === pNew[k] || Number(v[k]) === pOld[k]) delete v[k]; });
      Object.keys(v).forEach((k) => { if (v[k] === undefined || v[k] === null || v[k] === "") delete v[k]; });
      if (Array.isArray(v.rooms) && !v.rooms.length) delete v.rooms;
      delete v.tap_more_info;
      // az alapértelmezett állapotlista nem egyéni beállítás
      if (Array.isArray(v.glow_states) && v.glow_states.length === GLOW_DEFAULT.length && GLOW_DEFAULT.every((k) => v.glow_states.includes(k))) delete v.glow_states;
      this._config = v;
      this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: v }, bubbles: true, composed: true }));
    }

    _build() {
      this._built = true;
      const style = document.createElement("style");
      style.textContent = `
        :host { display:block; }
        details { border:1px solid var(--divider-color, #444); border-radius:12px; margin:0 0 10px; overflow:hidden; }
        summary { cursor:pointer; padding:12px 14px; font-weight:600; background:color-mix(in srgb, var(--primary-text-color, #fff) 5%, transparent); }
        .body { padding:12px 14px 4px; }
        .hint { color:var(--secondary-text-color); font-size:.85rem; margin:0 0 10px; }
        button { margin:4px 0 12px; padding:8px 14px; border-radius:8px; border:1px solid var(--divider-color, #555);
          background:transparent; color:var(--primary-text-color); cursor:pointer; font:inherit; }
      `;
      this.shadowRoot.appendChild(style);
      this._wrap = document.createElement("div");
      this.shadowRoot.appendChild(this._wrap);
      this._forms = [];
    }

    _update() {
      if (!this._hass && !this.isConnected) return;
      if (!this._built) this._build();
      const sections = this._sections();
      const data = this._display();
      if (!this._wrap.children.length) {
        sections.forEach((sec) => {
          const det = document.createElement("details");
          if (sec.open) det.open = true;
          const sum = document.createElement("summary");
          sum.dataset.key = sec.id;
          det.appendChild(sum);
          const body = document.createElement("div");
          body.className = "body";
          det.appendChild(body);
          const form = document.createElement("ha-form");
          form.addEventListener("value-changed", (ev) => { ev.stopPropagation(); this._emit(ev.detail.value); });
          body.appendChild(form);
          if (sec.reset) {
            const btn = document.createElement("button");
            btn.dataset.key = "reset_colors";
            btn.addEventListener("click", () => {
              const v = { ...this._config };
              COLOR_KEYS.forEach((k) => delete v["color_" + k]);
              this._config = v;
              this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: v }, bubbles: true, composed: true }));
              this._update();
            });
            body.appendChild(btn);
          }
          this._wrap.appendChild(det);
          this._forms.push({ form, sec });
        });
      }
      const helpers = { rooms: "h_rooms", columns: "h_columns", gauge_min: "h_gauge", gauge_max: "h_gauge", size: "h_size",
        step: "h_step", glow_states: "h_glow_states", animation: "h_animation" };
      this._wrap.querySelectorAll("summary").forEach((s) => { s.textContent = this._label(s.dataset.key); });
      this._wrap.querySelectorAll("button").forEach((b) => { b.textContent = this._label(b.dataset.key); });
      this._forms.forEach(({ form, sec }, i) => {
        const fresh = this._sections()[i];
        form.hass = this._hass;
        form.data = data;
        form.schema = fresh.schema;
        form.computeLabel = (s) => this._label(s.name);
        form.computeHelper = (s) => (helpers[s.name] ? this._label(helpers[s.name]) : "");
      });
      const noRooms = !this._roomOptions().length;
      let hint = this._wrap.querySelector(".hint");
      if (noRooms && !hint) {
        hint = document.createElement("p");
        hint.className = "hint";
        this._wrap.insertBefore(hint, this._wrap.firstChild);
      }
      if (hint) { if (noRooms) hint.textContent = this._label("editor_no_rooms"); else hint.remove(); }
    }
  }

  customElements.define(TAG, MerossBoilerSyncCard);
  customElements.define(EDITOR_TAG, MerossBoilerSyncCardEditor);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: TAG,
    name: "Meross Boiler Sync",
    description: (navigator.language || "").toLowerCase().startsWith("hu") ? STR.hu.description : STR.en.description,
    preview: true,
  });
})();

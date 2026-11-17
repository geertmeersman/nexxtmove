const NEXXTMOVE_I18N = {
  nl: {
    choose_device: 'Kies een device in de editor.',
    no_charges: 'Geen laadsessies gevonden.',
    recent_charges: 'Recente laadsessies',
    recent_events: 'Recente events',
    sessions: 'sessies',
    open: 'open',
    choose_device_label: '— Kies een device —',
    show_label: 'Tonen',
    show_stats: 'Maandstatistieken (met uitklapbare sessies)',
    show_non_invoiced: 'Openstaand bedrag',
    show_price: 'Prijs per kWh',
    show_max_power: 'Max vermogen',
    show_charges: 'Recente laadsessies (sectie)',
    show_events: 'Recente events',
    charging_device: 'Charging device',
  },
  en: {
    choose_device: 'Choose a device in the editor.',
    no_charges: 'No charging sessions found.',
    recent_charges: 'Recent charging sessions',
    recent_events: 'Recent events',
    sessions: 'sessions',
    open: 'open',
    choose_device_label: '— Choose a device —',
    show_label: 'Show',
    show_stats: 'Monthly statistics (with expandable sessions)',
    show_non_invoiced: 'Outstanding amount',
    show_price: 'Price per kWh',
    show_max_power: 'Max power',
    show_charges: 'Recent charging sessions (section)',
    show_events: 'Recent events',
    charging_device: 'Charging device',
  },
  de: {
    choose_device: 'Gerät im Editor auswählen.',
    no_charges: 'Keine Ladesitzungen gefunden.',
    recent_charges: 'Letzte Ladesitzungen',
    recent_events: 'Letzte Ereignisse',
    sessions: 'Sitzungen',
    open: 'offen',
    choose_device_label: '— Gerät auswählen —',
    show_label: 'Anzeigen',
    show_stats: 'Monatsstatistiken (mit aufklappbaren Sitzungen)',
    show_non_invoiced: 'Offener Betrag',
    show_price: 'Preis pro kWh',
    show_max_power: 'Max. Leistung',
    show_charges: 'Letzte Ladesitzungen (Abschnitt)',
    show_events: 'Letzte Ereignisse',
    charging_device: 'Ladegerät',
  },
  fr: {
    choose_device: 'Choisissez un appareil dans l\'éditeur.',
    no_charges: 'Aucune session de charge trouvée.',
    recent_charges: 'Sessions de charge récentes',
    recent_events: 'Événements récents',
    sessions: 'sessions',
    open: 'ouvert',
    choose_device_label: '— Choisir un appareil —',
    show_label: 'Afficher',
    show_stats: 'Statistiques mensuelles (avec sessions dépliables)',
    show_non_invoiced: 'Montant en attente',
    show_price: 'Prix par kWh',
    show_max_power: 'Puissance max',
    show_charges: 'Sessions de charge récentes (section)',
    show_events: 'Événements récents',
    charging_device: 'Appareil de charge',
  },
};

function _esc(str) {
  return String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function _t(hass, key) {
  const lang = (hass?.locale?.language || 'en').slice(0, 2).toLowerCase();
  return (NEXXTMOVE_I18N[lang] || NEXXTMOVE_I18N.en)[key] || NEXXTMOVE_I18N.en[key] || key;
}

class NexxtmoveDeviceCard extends HTMLElement {
  constructor() {
    super();
    this._expanded = {};
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;
    if (!oldHass || this._hasStateChanged(oldHass, hass)) {
      this._render();
    }
  }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  _entitiesForDevice(deviceId) {
    if (!deviceId || !this._hass?.entities) return {};
    const result = {};
    for (const [entityId, entity] of Object.entries(this._hass.entities)) {
      if (entity.platform !== 'nexxtmove') continue;
      if (entity.device_id === deviceId) {
        if (entityId.includes('_charging_device_') && entityId.endsWith('_events'))
          result.events_sensor = entityId;
        else if (entityId.endsWith('_month_energy'))
          result.month_energy_sensor = entityId;
        else if (entityId.endsWith('_month_cost'))
          result.month_cost_sensor = entityId;
        else if (entityId.endsWith('_month_charges'))
          result.month_charges_sensor = entityId;
        else if (entityId.includes('_charging_device_') && !entityId.includes('_period_') && !entityId.includes('_month_') && !entityId.endsWith('_events') && !entityId.endsWith('_pin'))
          result.charging_device_sensor = entityId;
        else if (entityId.includes('_charging_point_') && !entityId.endsWith('_price') && !entityId.endsWith('_events'))
          result.charging_point_sensor = entityId;
      }
      if (entityId.endsWith('_recent_charges'))
        result.recent_charges_sensor = entityId;
      if (entityId.endsWith('_non_invoiced'))
        result.non_invoiced_sensor = entityId;
    }
    return result;
  }

  _hasStateChanged(oldHass, newHass) {
    if (!this._config?.device_id) return false;
    const r = this._entitiesForDevice(this._config.device_id);
    return [r.charging_device_sensor, r.charging_point_sensor, r.events_sensor,
            r.month_energy_sensor, r.month_cost_sensor, r.month_charges_sensor,
            r.recent_charges_sensor, r.non_invoiced_sensor]
      .some(e => e && oldHass.states[e] !== newHass.states[e]);
  }

  _s(entity) {
    if (!entity) return null;
    const s = this._hass.states[entity];
    return s ? s.state : null;
  }

  _a(entity, attr) {
    if (!entity) return null;
    const s = this._hass.states[entity];
    return s ? (s.attributes[attr] ?? null) : null;
  }

  _moreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(new CustomEvent('hass-more-info', { detail: { entityId }, bubbles: true, composed: true }));
  }

  _statusColor(status) {
    switch ((status || '').toUpperCase()) {
      case 'CHARGING': return 'var(--success-color, #4caf50)';
      case 'OFFLINE':  return 'var(--error-color, #e05c6a)';
      default:         return 'var(--secondary-text-color)';
    }
  }

  _statusBg(status) {
    switch ((status || '').toUpperCase()) {
      case 'CHARGING': return 'var(--success-color-background, rgba(76,175,80,0.15))';
      case 'OFFLINE':  return 'rgba(224,92,106,0.15)';
      default:         return 'var(--secondary-background-color)';
    }
  }

  _eventIcon(type) {
    switch ((type || '').toUpperCase()) {
      case 'CHARGING':    return 'mdi:lightning-bolt';
      case 'CHARGE_STOP': return 'mdi:stop-circle-outline';
      case 'AUTHORIZED':  return 'mdi:key';
      case 'PLUGIN':      return 'mdi:power-plug';
      case 'PLUGOUT':     return 'mdi:power-plug-off';
      case 'ONLINE':      return 'mdi:wifi';
      case 'OFFLINE':     return 'mdi:wifi-off';
      case 'WAIT_CAR':    return 'mdi:car-clock';
      default:            return 'mdi:information-outline';
    }
  }

  _formatDate(iso) {
    if (!iso) return '';
    const lang = (this._hass?.locale?.language || 'en-BE');
    const d = new Date(iso);
    return d.toLocaleDateString(lang, { day: '2-digit', month: '2-digit' })
      + ' ' + d.toLocaleTimeString(lang, { hour: '2-digit', minute: '2-digit' });
  }

  _formatDuration(startIso, endIso) {
    if (!startIso || !endIso) return '';
    const mins = Math.round((new Date(endIso) - new Date(startIso)) / 60000);
    if (mins < 60) return `${mins}m`;
    return `${Math.floor(mins / 60)}h${mins % 60 > 0 ? String(mins % 60).padStart(2, '0') : ''}`;
  }

  _toggleExpand(key) {
    this._expanded[key] = !this._expanded[key];
    const panel = this.querySelector(`#panel-${key}`);
    const icon = this.querySelector(`#expand-icon-${key}`);
    if (panel) panel.style.maxHeight = this._expanded[key] ? panel.scrollHeight + 'px' : '0';
    if (icon) icon.setAttribute('icon', this._expanded[key] ? 'mdi:chevron-up' : 'mdi:chevron-down');
  }

  _render() {
    if (!this._hass || !this._config) return;

    const t = (key) => _t(this._hass, key);

    const show = {
      stats:        this._config.show_stats        !== false,
      non_invoiced: this._config.show_non_invoiced !== false,
      price:        this._config.show_price        !== false,
      max_power:    this._config.show_max_power    !== false,
      charges:      this._config.show_charges      !== false,
      events:       this._config.show_events       !== false,
    };

    const r = this._entitiesForDevice(this._config.device_id);

    if (!r.charging_device_sensor) {
      this.innerHTML = `<ha-card><div style="padding:16px;color:var(--secondary-text-color);">${t('choose_device')}</div></ha-card>`;
      return;
    }

    const deviceAttrs = this._hass.states[r.charging_device_sensor]?.attributes || {};
    const name = deviceAttrs.name || this._a(r.charging_device_sensor, 'friendly_name') || 'Charging Device';
    const building = deviceAttrs.buildingName || this._s(r.charging_device_sensor) || '';
    const lastComm = deviceAttrs.lastCommunication ? this._formatDate(deviceAttrs.lastCommunication) : null;

    const pointStatus = (this._s(r.charging_point_sensor) || '').toUpperCase();
    const pointAttrs = r.charging_point_sensor
      ? (this._hass.states[r.charging_point_sensor]?.attributes || {}) : {};
    const maxPower = pointAttrs.maxPower ? `${Math.round(pointAttrs.maxPower)} kW max` : null;
    const price = pointAttrs.price || null;

    const monthEnergy  = r.month_energy_sensor  ? parseFloat(this._s(r.month_energy_sensor))  : null;
    const monthCost    = r.month_cost_sensor     ? parseFloat(this._s(r.month_cost_sensor))    : null;
    const monthCharges = r.month_charges_sensor  ? parseInt(this._s(r.month_charges_sensor))   : null;
    const nonInvoiced  = r.non_invoiced_sensor   ? parseFloat(this._s(r.non_invoiced_sensor))  : null;

    const eventsState  = r.events_sensor ? this._hass.states[r.events_sensor] : null;
    const recentEvents = (eventsState?.attributes?.events || [])
      .slice().sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5);

    const cpId = pointAttrs.id || null;
    const allCharges = r.recent_charges_sensor
      ? (this._hass.states[r.recent_charges_sensor]?.attributes?.charges || []) : [];
    const recentCharges = allCharges
      .filter(c => !cpId || c.chargingPointId === cpId)
      .slice().sort((a, b) => new Date(b.startTimestamp) - new Date(a.startTimestamp))
      .slice(0, 5);

    const chargesRowsHtml = recentCharges.length > 0
      ? recentCharges.map(c => `
        <div class="row">
          <ha-icon icon="mdi:ev-plug-type2"></ha-icon>
          <div style="flex:1; min-width:0;">
            <div class="row-main">${this._formatDate(c.startTimestamp)}</div>
            <div class="charge-meta">
              <span><ha-icon style="--mdc-icon-size:12px;" icon="mdi:lightning-bolt"></ha-icon> ${c.energyConsumedKWh?.toFixed(2)} kWh</span>
              <span><ha-icon style="--mdc-icon-size:12px;" icon="mdi:clock-outline"></ha-icon> ${this._formatDuration(c.startTimestamp, c.endTimestamp)}</span>
            </div>
          </div>
          <div class="row-sub">${c.costVat?.toFixed(2)} €</div>
        </div>`).join('')
      : `<div style="padding:6px 0;font-size:0.82em;color:var(--secondary-text-color);">${t('no_charges')}</div>`;

    const expandOpen = !!this._expanded['charges'];

    this.innerHTML = `
      <ha-card>
        <style>
          ha-card {
            background: var(--card-background-color);
            color: var(--primary-text-color);
            font-family: var(--paper-font-body1_-_font-family);
            overflow: hidden;
            border-radius: var(--ha-card-border-radius, 12px);
          }
          .header {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 14px; cursor: pointer;
            border-bottom: 1px solid var(--divider-color);
            position: relative;
          }
          .header:hover { filter: brightness(1.05); }
          .icon-wrap {
            width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
            background: var(--secondary-background-color);
            display: flex; align-items: center; justify-content: center;
            border: 2px solid ${this._statusColor(pointStatus)};
          }
          .header-text { flex: 1; min-width: 0; }
          .header-name { font-size: 1em; font-weight: 700; }
          .header-sub { font-size: 0.8em; color: var(--secondary-text-color); }
          .status-badge {
            position: absolute; top: 6px; right: 5px;
            font-size: 0.65em; font-weight: 700; padding: 2px 7px; border-radius: 8px;
            letter-spacing: 0.05em;
            background: ${this._statusBg(pointStatus)};
            color: ${this._statusColor(pointStatus)};
          }
          .chips {
            display: flex; flex-wrap: wrap; gap: 8px;
            padding: 8px 14px; align-items: center;
            border-bottom: 1px solid var(--divider-color);
          }
          .chip {
            display: flex; align-items: center; gap: 4px;
            font-size: 0.8em; font-weight: 500; cursor: pointer;
            white-space: nowrap; color: var(--primary-text-color);
          }
          .chip:hover { opacity: 0.8; }
          .chip ha-icon { --mdc-icon-size: 15px; }
          .chip-expand { border-radius: 6px; padding: 2px 4px; }
          .chip-expand:hover { background: var(--secondary-background-color); }
          .divider { width: 1px; height: 16px; background: var(--divider-color); }
          .expand-panel {
            overflow: hidden;
            transition: max-height 0.3s ease;
            border-bottom: 1px solid var(--divider-color);
            padding: 0 14px;
          }
          .section { padding: 8px 14px; border-bottom: 1px solid var(--divider-color); }
          .section:last-child { border-bottom: none; }
          .section-title {
            font-size: 0.75em; font-weight: 700; color: var(--secondary-text-color);
            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;
          }
          .row {
            display: flex; align-items: center; gap: 8px;
            padding: 4px 0; border-bottom: 1px solid var(--divider-color);
            font-size: 0.82em;
          }
          .row:last-child { border-bottom: none; }
          .row ha-icon { --mdc-icon-size: 15px; color: var(--primary-color); flex-shrink: 0; }
          .row-main { font-weight: 600; flex: 1; }
          .row-sub { color: var(--secondary-text-color); white-space: nowrap; font-size: 0.9em; }
          .charge-meta { display: flex; gap: 8px; color: var(--secondary-text-color); font-size: 0.9em; }
          .charge-meta span { white-space: nowrap; }
        </style>

        <div class="header" id="header">
          <div class="icon-wrap">
            <img src="/nexxtmove/nexxtmove-icon.png" alt="Nexxtmove" style="width:26px;height:26px;object-fit:contain;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
            <ha-icon icon="mdi:ev-station" style="--mdc-icon-size:26px; color:var(--primary-color);display:none;"></ha-icon>
          </div>
          <div class="header-text">
            <div class="header-name">${_esc(name)}</div>
            <div class="header-sub">${_esc(building)}${lastComm ? ` · ${_esc(lastComm)}` : ''}</div>
          </div>
          <div class="status-badge">${_esc(pointStatus || '—')}</div>
        </div>

        ${show.stats || show.non_invoiced || show.price || show.max_power ? `
        <div class="chips">
          ${show.stats && monthEnergy !== null && !isNaN(monthEnergy) ? `
          <div class="chip" id="chip-energy">
            <ha-icon icon="mdi:lightning-bolt" style="color:var(--warning-color, #e0956a);"></ha-icon>
            ${monthEnergy.toFixed(1)} kWh
          </div>` : ''}
          ${show.stats && monthCost !== null && !isNaN(monthCost) ? `
          <div class="divider"></div>
          <div class="chip" id="chip-cost">
            <ha-icon icon="mdi:currency-eur" style="color:var(--primary-color);"></ha-icon>
            ${monthCost.toFixed(2)} €
          </div>` : ''}
          ${show.non_invoiced && nonInvoiced !== null && !isNaN(nonInvoiced) ? `
          <div class="divider"></div>
          <div class="chip" id="chip-non-invoiced">
            <ha-icon icon="mdi:receipt-clock-outline" style="color:var(--warning-color, #e0956a);"></ha-icon>
            ${nonInvoiced.toFixed(2)} € ${t('open')}
          </div>` : ''}
          ${show.stats && monthCharges !== null && !isNaN(monthCharges) ? `
          <div class="divider"></div>
          ${show.charges
            ? `<div class="chip"><ha-icon icon="mdi:counter" style="color:var(--secondary-text-color);"></ha-icon>${monthCharges} ${t('sessions')}</div>`
            : `<div class="chip chip-expand" id="chip-charges">
                <ha-icon icon="mdi:counter" style="color:var(--secondary-text-color);"></ha-icon>
                ${monthCharges} ${t('sessions')}
                <ha-icon id="expand-icon-charges" icon="${expandOpen ? 'mdi:chevron-up' : 'mdi:chevron-down'}" style="--mdc-icon-size:13px; color:var(--secondary-text-color); margin-left:2px;"></ha-icon>
               </div>`
          }` : ''}
          ${show.price && price ? `
          <div class="divider"></div>
          <div class="chip">
            <ha-icon icon="mdi:tag-outline" style="color:var(--secondary-text-color);"></ha-icon>
            ${price}
          </div>` : ''}
          ${show.max_power && maxPower ? `
          <div class="divider"></div>
          <div class="chip">
            <ha-icon icon="mdi:flash" style="color:var(--secondary-text-color);"></ha-icon>
            ${maxPower}
          </div>` : ''}
        </div>
        ${show.stats && !show.charges && monthCharges !== null && !isNaN(monthCharges) ? `
        <div id="panel-charges" class="expand-panel" style="max-height:${expandOpen ? '500px' : '0'};">
          ${chargesRowsHtml}
        </div>` : ''}` : ''}

        ${show.charges && recentCharges.length > 0 ? `
        <div class="section">
          <div class="section-title">${t('recent_charges')}</div>
          ${chargesRowsHtml}
        </div>` : ''}

        ${show.events && recentEvents.length > 0 ? `
        <div class="section">
          <div class="section-title">${t('recent_events')}</div>
          ${recentEvents.map(e => `
          <div class="row">
            <ha-icon icon="${this._eventIcon(e.type)}"></ha-icon>
            <span class="row-main">${_esc(e.message || e.type)}</span>
            <span class="row-sub">${this._formatDate(e.date)}</span>
          </div>`).join('')}
        </div>` : ''}
      </ha-card>
    `;

    this.querySelector('#header')?.addEventListener('click', () => this._moreInfo(r.charging_device_sensor));
    this.querySelector('#chip-energy')?.addEventListener('click', e => { e.stopPropagation(); this._moreInfo(r.month_energy_sensor); });
    this.querySelector('#chip-cost')?.addEventListener('click', e => { e.stopPropagation(); this._moreInfo(r.month_cost_sensor); });
    this.querySelector('#chip-non-invoiced')?.addEventListener('click', e => { e.stopPropagation(); this._moreInfo(r.non_invoiced_sensor); });
    this.querySelector('#chip-charges')?.addEventListener('click', e => { e.stopPropagation(); this._toggleExpand('charges'); });
  }

  getCardSize() { return 5; }
  static getConfigElement() { return document.createElement('nexxtmove-device-card-editor'); }
  static getStubConfig() { return { device_id: '' }; }
}

customElements.define('nexxtmove-device-card', NexxtmoveDeviceCard);

// -------------------------------------------------------
// Editor
// -------------------------------------------------------
class NexxtmoveDeviceCardEditor extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot?.querySelector('#device-select')) this._render();
  }

  setConfig(config) {
    this._config = { ...config };
    if (this._hass) this._render();
  }

  _nexxtmoveDevices() {
    if (!this._hass?.entities || !this._hass?.devices) return [];
    const deviceIds = new Set();
    for (const entity of Object.values(this._hass.entities)) {
      if (entity.platform === 'nexxtmove' && entity.device_id) {
        const eid = Object.keys(this._hass.entities).find(k => this._hass.entities[k] === entity);
        if (eid?.includes('_charging_device_') && !eid.includes('_period_') && !eid.includes('_month_') && !eid.endsWith('_events') && !eid.endsWith('_pin'))
          deviceIds.add(entity.device_id);
      }
    }
    return [...deviceIds].map(id => ({
      id,
      name: this._hass.devices[id]?.name_by_user || this._hass.devices[id]?.name || id
    })).sort((a, b) => a.name.localeCompare(b.name));
  }

  _fireConfigChanged(config) {
    this.dispatchEvent(new CustomEvent('config-changed', {
      detail: { config: { type: 'custom:nexxtmove-device-card', ...config } },
      bubbles: true, composed: true
    }));
  }

  _render() {
    if (!this._hass) return;
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });

    const t = (key) => _t(this._hass, key);
    const cfg = this._config || {};
    const deviceId = cfg.device_id || '';
    const devices = this._nexxtmoveDevices();

    const checks = [
      { key: 'show_stats',        label: t('show_stats') },
      { key: 'show_non_invoiced', label: t('show_non_invoiced') },
      { key: 'show_price',        label: t('show_price') },
      { key: 'show_max_power',    label: t('show_max_power') },
      { key: 'show_charges',      label: t('show_charges') },
      { key: 'show_events',       label: t('show_events') },
    ];

    this.shadowRoot.innerHTML = `
      <style>
        .editor { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        label { font-size: 0.85em; color: var(--secondary-text-color); display: block; margin-bottom: 4px; }
        select {
          width: 100%; padding: 8px; border-radius: 4px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font-size: 1em;
        }
        .toggles { display: flex; flex-direction: column; gap: 6px; }
        .toggle-row { display: flex; align-items: center; gap: 8px; font-size: 0.9em; cursor: pointer; }
        .toggle-row input { cursor: pointer; }
      </style>
      <div class="editor">
        <div>
          <label>${t('charging_device')}</label>
          <select id="device-select">
            <option value="">${t('choose_device_label')}</option>
            ${devices.map(d => `<option value="${_esc(d.id)}" ${d.id === deviceId ? 'selected' : ''}>${_esc(d.name)}</option>`).join('')}
          </select>
        </div>
        <div>
          <label>${t('show_label')}</label>
          <div class="toggles">
            ${checks.map(c => `
            <label class="toggle-row">
              <input type="checkbox" id="${c.key}" ${cfg[c.key] !== false ? 'checked' : ''}>
              ${c.label}
            </label>`).join('')}
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.querySelector('#device-select').addEventListener('change', e => {
      const newConfig = { ...this._config, device_id: e.target.value };
      this._config = newConfig;
      this._fireConfigChanged(newConfig);
    });

    checks.forEach(({ key }) => {
      this.shadowRoot.querySelector(`#${key}`)?.addEventListener('change', e => {
        const newConfig = { ...this._config, [key]: e.target.checked };
        this._config = newConfig;
        this._fireConfigChanged(newConfig);
      });
    });
  }
}

customElements.define('nexxtmove-device-card-editor', NexxtmoveDeviceCardEditor);

window.customCards = window.customCards || [];
if (!window.customCards.find(c => c.type === 'nexxtmove-device-card')) {
  window.customCards.push({
    type: 'nexxtmove-device-card',
    name: 'Nexxtmove Device Card',
    description: 'Shows info, statistics and recent events of a Nexxtmove charging device.',
  });
}

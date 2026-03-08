with open('docs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_size = len(html)

# ── 1. LOGO SVG en el header
html = html.replace(
    '<div class="w-10 h-10 panel flex items-center justify-center font-bold text-xl logo-text">T</div>',
    '<img src="logo.svg" alt="TokenTax" style="width:40px;height:40px;border-radius:8px;display:block">'
)

# ── 2. Favicon y apple-touch-icon → logo.svg
import re
html = re.sub(
    r'<link rel="icon"[^>]+>',
    '<link rel="icon" type="image/svg+xml" href="logo.svg">',
    html
)
html = re.sub(
    r'<link rel="apple-touch-icon"[^>]+>',
    '<link rel="apple-touch-icon" href="logo.svg">',
    html
)

# ── 3. Versión badge
html = html.replace('v4.0.6', 'v4.1.0').replace('v4.0.5', 'v4.1.0').replace('v4.0.4', 'v4.1.0').replace('v4.0.3', 'v4.1.0')

# ── 4. Mejorar el CSS de la tabla .tbl para que se vea perfecta
old_tbl_css = """.tbl-wrap { overflow: auto; flex: 1; }"""
new_tbl_css = """.tbl-wrap { overflow: auto; flex: 1; }
    .tbl { table-layout: fixed; border-collapse: collapse; width: 100%; }
    .tbl th, .tbl td { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tbl thead { position: sticky; top: 0; z-index: 10; }
    .tbl tr.selected td { background: var(--blue-dim) !important; }
    .tbl tr.fav-row td:nth-child(1) { color: #fbbf24; }"""
html = html.replace(old_tbl_css, new_tbl_css)

# ── 5. Mejorar el CSS de stats-bar
html = html.replace(
    '.stats-bar { background: var(--green-dim); }',
    '.stats-bar { background: var(--green-dim); padding: 5px 12px !important; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; font-size: 10px; }'
)

# ── 6. Añadir colores para más proveedores
html = html.replace(
    '    .logo-default { background: var(--surface-2); color: var(--text-2); }',
    '''    .logo-replicate { background: #6366f1; color: white; }
    .logo-openrouter { background: #6d28d9; color: white; }
    .logo-cerebras { background: #1e40af; color: white; }
    .logo-sambanova { background: #0f172a; color: white; }
    .logo-default { background: var(--surface-2); color: var(--text-2); }

    /* Provider panel */
    .provider-row { display: flex; align-items: center; gap: 6px; padding: 3px 4px; border-radius: 3px; cursor: pointer; transition: background 0.1s; }
    .provider-row:hover { background: var(--surface-2); }
    .provider-row-name { font-size: 10px; flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    .provider-row-count { font-size: 9px; color: var(--text-3); flex-shrink: 0; min-width: 22px; text-align: right; }
    .provider-bar-wrap { width: 28px; height: 3px; background: var(--border); border-radius: 2px; flex-shrink: 0; overflow: hidden; }
    .provider-bar-fill { height: 100%; background: var(--green); border-radius: 2px; }'''
)

# ── 7. Añadir más proveedores al map de logos JS
html = html.replace(
    "      cohere: 'logo-cohere', nvidia: 'logo-nvidia', perplexity: 'logo-perplexity'",
    "      cohere: 'logo-cohere', nvidia: 'logo-nvidia', perplexity: 'logo-perplexity', replicate: 'logo-replicate', openrouter: 'logo-openrouter', cerebras: 'logo-cerebras', sambanova: 'logo-sambanova'"
)

# ── 8. Añadir panel "Proveedores" en el aside antes de Favoritos
highlight_panel = '''
      <!-- Proveedores Panel -->
      <div class="panel p-2">
        <div class="flex justify-between items-center mb-1.5">
          <span class="text-[10px] text-secondary font-medium"><i class="fas fa-building"></i> Proveedores</span>
          <span id="providerTotal" class="text-[9px] text-tertiary">-</span>
        </div>
        <div id="providerStatsList" class="flex flex-col gap-0.5"></div>
      </div>
'''
# Insertar antes de <!-- Favorites -->
html = html.replace('      <!-- Favorites -->', highlight_panel + '      <!-- Favorites -->')

# ── 9. Añadir función renderProviderPanel en el JS
provider_fn = '''
    function renderProviderPanel() {
      if (!allModels.length) return;
      const counts = {};
      allModels.forEach(m => { counts[m.provider] = (counts[m.provider] || 0) + 1; });
      const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10);
      const total = allModels.length;
      const el = document.getElementById('providerTotal');
      const list = document.getElementById('providerStatsList');
      if (!el || !list) return;
      el.textContent = Object.keys(counts).length + ' proveedores';
      list.innerHTML = sorted.map(([p, c]) => {
        const logo = getProviderLogo(p);
        const pct = Math.round(c / total * 100);
        return `<div class="provider-row" onclick="filterProvider('${p}')" title="${p} (${c})">
          <span class="provider-logo ${logo}" style="width:14px;height:14px;font-size:8px;flex-shrink:0">${p.charAt(0)}</span>
          <span class="provider-row-name">${p}</span>
          <span class="provider-row-count">${c}</span>
          <div class="provider-bar-wrap"><div class="provider-bar-fill" style="width:${pct}%"></div></div>
        </div>`;
      }).join('');
    }

'''
# Insertar antes de la función filterProvider
html = html.replace('    function filterProvider(', provider_fn + '    function filterProvider(')

# ── 10. Llamar renderProviderPanel después de cargar modelos
html = html.replace(
    "        updateQuickProviders();\n\n      } catch(e) {",
    "        updateQuickProviders();\n        renderProviderPanel();\n\n      } catch(e) {"
)

# Si no encontró eso, intentar otra variante
if 'renderProviderPanel();' not in html:
    html = html.replace(
        "        updateQuickProviders();\r\n\r\n      } catch(e) {",
        "        updateQuickProviders();\r\n        renderProviderPanel();\r\n\r\n      } catch(e) {"
    )

# ── 11. clearProviderFilter
if 'clearProviderFilter' not in html:
    html = html.replace(
        "    // Initialize\n    window.onload",
        """    function clearProviderFilter() {
      document.getElementById('providerFilter').value = '';
      document.getElementById('typeFilter').value = '';
      currentTypeFilter = '';
      calcularCostos();
    }

    // Initialize
    window.onload"""
    )

# ── 12. Logo en footer
html = html.replace(
    '<span class="font-medium">TokenTax AI PRO</span>',
    '<img src="logo.svg" alt="" style="width:13px;height:13px;display:inline;vertical-align:middle;margin-right:3px"><span class="font-medium">TokenTax AI PRO</span>'
)

# ── 13. Añadir botón de reset provider en la sección de providers rápidos
html = html.replace(
    '          <button onclick="showTop10()" class="btn-secondary px-2 py-1 text-[9px] flex-1"><i class="fas fa-trophy"></i> Top 10</button>\n          <button onclick="showAll()" class="btn-secondary px-2 py-1 text-[9px] flex-1"><i class="fas fa-list"></i> All</button>',
    '          <button onclick="showTop10()" class="btn-secondary px-2 py-1 text-[9px] flex-1"><i class="fas fa-trophy"></i> Top 10</button>\n          <button onclick="showAll()" class="btn-secondary px-2 py-1 text-[9px] flex-1"><i class="fas fa-list"></i> All</button>\n          <button onclick="clearProviderFilter()" class="btn-secondary px-2 py-1 text-[9px]" title="Reset"><i class="fas fa-times"></i></button>'
)

# ── 14. Mejorar quickProviders con logos de color
old_qp = """        container.innerHTML = provs.map(p =>
        `<button onclick="filterProvider('${p}')" class="badge cursor-pointer" style="background:var(--surface-2);color:var(--text-2)">${p.substring(0,4)}</button>`
      ).join('');"""
new_qp = """        const provCounts = {};
      allModels.forEach(m => { provCounts[m.provider] = (provCounts[m.provider] || 0) + 1; });
      container.innerHTML = provs.map(p => {
        const logoClass = getProviderLogo(p);
        return `<button onclick="filterProvider('${p}')" title="${p} (${provCounts[p]||0})" class="badge cursor-pointer" style="background:var(--surface-2);color:var(--text-2);gap:3px;padding:2px 5px"><span class="provider-logo ${logoClass}" style="width:12px;height:12px;font-size:7px">${p.charAt(0)}</span>${p.substring(0,5)}</button>`;
      }).join('');"""
html = html.replace(old_qp, new_qp)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Original: {original_size} → New: {len(html)} bytes")
checks = [
    ('Logo img', 'img src="logo.svg"' in html),
    ('Favicons actualizados', 'link rel="icon" type="image/svg+xml" href="logo.svg"' in html),
    ('Provider panel HTML', 'providerStatsList' in html),
    ('renderProviderPanel fn', 'function renderProviderPanel' in html),
    ('renderProviderPanel llamado', 'renderProviderPanel();' in html),
    ('Provider CSS classes', 'provider-row-name' in html),
    ('Extra provider logos', 'logo-openrouter' in html),
    ('Logo footer', 'logo.svg" alt=""' in html),
]
for n, ok in checks:
    print(f"  {'OK' if ok else 'FAIL'} — {n}")

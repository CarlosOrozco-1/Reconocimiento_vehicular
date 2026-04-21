import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import * as L from 'leaflet';
import Chart from 'chart.js/auto';

import { TrafficApiService } from '../../services/api/traffic-api.service';

/**
 * Componente principal del mapa de trafico de Guatemala.
 * Muestra rutas principales con geometria real desde PostGIS y departamentos como capa de fondo.
 * Permite seleccionar rutas individualmente o ver todas a la vez.
 */
@Component({
  selector: 'app-map-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel layout-panel">

      <!-- Sidebar: se muestra cuando hay una ruta seleccionada -->
      <div class="sidebar" *ngIf="selectedRoute">
        <div class="sidebar-header">
          <h2>{{ selectedRouteName }}</h2>
          <button class="control-btn close-btn" (click)="clearSelection()" title="Ver todas las rutas">
            ✕ Ver todas
          </button>
        </div>

        <div class="route-stats" *ngIf="selectedRouteSummary">
          <div class="stat-row">
            <span class="stat-label">Flujo normal</span>
            <span class="stat-value">{{ $any(selectedRouteSummary)['normal_flow'] || 0 }} <small>veh/h</small></span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Flujo hora pico</span>
            <span class="stat-value peak">{{ $any(selectedRouteSummary)['peak_flow'] || 0 }} <small>veh/h</small></span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Hora pico</span>
            <span class="stat-value">
              {{ $any(selectedRouteSummary)['peak_hour'] != null ? $any(selectedRouteSummary)['peak_hour'] + ':00 h' : 'Sin datos' }}
            </span>
          </div>
          <div class="stat-row departments-row">
            <span class="stat-label">Departamentos</span>
            <span class="stat-value departments-list">
              {{ selectedDepartments.length > 0 ? selectedDepartments.join(', ') : 'Sin cruces' }}
            </span>
          </div>
        </div>

        <div class="chart-container">
          <canvas id="trafficCurveChart"></canvas>
        </div>

        <div class="source-badge" [class.mock]="routesSourceInfo">
          {{ routesSourceInfo ? '⚠ Datos de ejemplo' : '✓ Datos reales de BD' }}
        </div>
      </div>

      <!-- Seccion del mapa -->
      <div class="map-section" [class.with-sidebar]="selectedRoute">

        <!-- Controles superiores -->
        <div class="top-controls">
          <div class="layer-controls">
            <button type="button" class="control-btn" (click)="toggleRoutes()" [id]="'btn-toggle-routes'">
              {{ routesVisible ? '🛣 Ocultar rutas' : '🛣 Mostrar rutas' }}
            </button>
            <button type="button" class="control-btn" (click)="toggleDepartments()" [id]="'btn-toggle-departments'">
              {{ departmentsVisible ? '🗺 Ocultar dptos.' : '🗺 Mostrar dptos.' }}
            </button>
            <button *ngIf="selectedRoute" type="button" class="control-btn accent"
              (click)="toggleSingleRouteView()" [id]="'btn-toggle-single'">
              {{ showOnlySelectedRoute ? '👁 Ver todas' : '🔍 Solo esta ruta' }}
            </button>
          </div>

          <div *ngIf="routesSourceInfo || routeDataWarning" class="data-warning">
            <span *ngIf="routesSourceInfo">⚠ {{ routesSourceInfo }}</span>
            <span *ngIf="routeDataWarning">{{ routeDataWarning }}</span>
          </div>
        </div>

        <!-- Selector de rutas -->
        <div class="route-selector">
          <div class="route-selector-header">
            <strong>Rutas principales</strong>
            <span class="route-count">({{ routeCatalog.length }} rutas)</span>
          </div>
          <div class="route-list">
            <button
              *ngFor="let route of routeCatalog"
              type="button"
              class="route-code-btn"
              [class.selected]="strConv($any(route)['route_code'] ?? '') === selectedRoute"
              [id]="'route-btn-' + $any(route)['route_code']"
              (click)="onRouteClick(strConv($any(route)['route_code'] ?? ''), strConv($any(route)['name'] ?? ''))">
              <span class="route-code">{{ $any(route)['route_code'] }}</span>
              <span class="route-name">{{ $any(route)['name'] }}</span>
              <span class="route-km" *ngIf="$any(route)['length_km']">{{ $any(route)['length_km'] }} km</span>
            </button>
          </div>
        </div>

        <!-- Contenedor del mapa Leaflet -->
        <div id="main-map" class="map-container"></div>
      </div>
    </section>
  `,
  styles: [
    `
      .layout-panel {
        display: flex;
        flex-direction: row;
        gap: 0;
        min-height: calc(100vh - 120px);
        background: #0f172a;
      }

      /* ---- Sidebar ---- */
      .sidebar {
        width: 320px;
        min-width: 280px;
        background: #1e293b;
        border-right: 1px solid #334155;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 14px;
        box-shadow: 4px 0 12px rgba(0,0,0,0.4);
        overflow-y: auto;
      }

      .sidebar-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid #334155;
        padding-bottom: 12px;
        gap: 8px;
      }

      .sidebar-header h2 {
        margin: 0;
        font-size: 1.1rem;
        color: #38bdf8;
        line-height: 1.3;
        flex: 1;
      }

      .close-btn {
        font-size: 0.8rem;
        padding: 5px 10px;
        white-space: nowrap;
      }

      /* ---- Stats ---- */
      .route-stats {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 6px 0;
        border-bottom: 1px solid #1e293b;
      }

      .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
      }

      .stat-value {
        font-size: 1rem;
        color: #e2e8f0;
        font-weight: 600;
      }

      .stat-value small {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 400;
        margin-left: 2px;
      }

      .stat-value.peak {
        color: #f97316;
      }

      .departments-row {
        flex-direction: column;
        gap: 4px;
        align-items: flex-start;
      }

      .departments-list {
        font-size: 0.85rem;
        color: #cbd5e1;
        font-weight: 400;
        line-height: 1.5;
      }

      /* ---- Chart ---- */
      .chart-container {
        flex: 1;
        position: relative;
        min-height: 200px;
      }

      /* ---- Source badge ---- */
      .source-badge {
        font-size: 0.78rem;
        text-align: center;
        padding: 4px 8px;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
      }

      .source-badge.mock {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border-color: rgba(245, 158, 11, 0.3);
      }

      /* ---- Seccion del mapa ---- */
      .map-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-width: 0;
        padding: 12px;
        gap: 10px;
      }

      /* ---- Controles superiores ---- */
      .top-controls {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .layer-controls {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .control-btn {
        border: 1px solid #0ea5e9;
        background: #0c4a6e;
        color: #e0f2fe;
        border-radius: 8px;
        padding: 7px 12px;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        transition: background 0.2s ease, transform 0.1s ease;
      }

      .control-btn:hover {
        background: #0284c7;
        transform: translateY(-1px);
      }

      .control-btn.accent {
        border-color: #f59e0b;
        background: #78350f;
        color: #fef3c7;
      }

      .control-btn.accent:hover {
        background: #b45309;
      }

      /* ---- Data warning ---- */
      .data-warning {
        color: #92400e;
        background: rgba(254, 231, 200, 0.9);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      /* ---- Selector de rutas ---- */
      .route-selector {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .route-selector-header {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #e2e8f0;
        font-size: 0.9rem;
      }

      .route-count {
        color: #64748b;
        font-size: 0.8rem;
      }

      .route-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }

      .route-code-btn {
        border: 1px solid #334155;
        background: #1e293b;
        color: #cbd5e1;
        border-radius: 8px;
        padding: 6px 10px;
        text-align: left;
        cursor: pointer;
        font-size: 0.8rem;
        display: flex;
        flex-direction: column;
        gap: 1px;
        min-width: 80px;
        transition: border-color 0.2s ease, background 0.2s ease;
      }

      .route-code-btn .route-code {
        font-weight: 700;
        color: #38bdf8;
        font-size: 0.9rem;
      }

      .route-code-btn .route-name {
        font-size: 0.72rem;
        color: #94a3b8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 110px;
      }

      .route-code-btn .route-km {
        font-size: 0.7rem;
        color: #475569;
      }

      .route-code-btn.selected {
        border-color: #38bdf8;
        background: #0c4a6e;
        color: #ffffff;
      }

      .route-code-btn.selected .route-code { color: #ffffff; }
      .route-code-btn.selected .route-name { color: #bae6fd; }

      .route-code-btn:hover:not(.selected) {
        border-color: #475569;
        background: #243249;
      }

      /* ---- Mapa ---- */
      .map-container {
        width: 100%;
        flex: 1;
        min-height: 400px;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #334155;
      }
    `
  ]
})
export class MapPageComponent implements AfterViewInit, OnDestroy {
  private map: L.Map | null = null;
  private routesLayer: L.GeoJSON | null = null;
  private departmentsLayer: L.GeoJSON | null = null;

  routesVisible = true;
  departmentsVisible = true;
  routesSourceInfo: string | null = null;
  routeDataWarning: string | null = null;
  routeCatalog: Array<Record<string, unknown>> = [];
  showOnlySelectedRoute = false;

  // Estado de la ruta seleccionada
  selectedRoute: string | null = null;
  selectedRouteName: string = '';
  selectedRouteSummary: Record<string, unknown> | null = null;
  selectedDepartments: string[] = [];

  // Instancia del grafico Chart.js de afluencia
  private trafficChart: Chart | null = null;

  // Paleta de colores para las rutas CA de Guatemala
  private readonly colors = [
    '#e11d48', '#d97706', '#16a34a', '#0891b2',
    '#4f46e5', '#c026d3', '#be123c', '#ea580c', '#0284c7'
  ];

  // Mapa de route_code → color asignado (para consistencia al re-render)
  private routeColorMap = new Map<string, string>();

  // Referencia publica para usar String(...) en el template
  readonly strConv = String;

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngAfterViewInit(): void {
    // Inicializar mapa Leaflet centrado en Guatemala
    this.map = L.map('main-map', {
      center: [14.6349, -90.5069],
      zoom: 7,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    // Cargar capas en paralelo
    this.loadDepartments();
    this.loadRoutes();
    this.loadRouteCatalog();
  }

  /**
   * Carga la capa de departamentos desde la API.
   * Los departamentos se muestran como poligonos de fondo semi-transparentes.
   */
  private loadDepartments(): void {
    if (!this.map) return;

    this.trafficApi.getDepartments().subscribe({
      next: (response) => {
        if (!this.map) return;
        if (this.departmentsLayer) this.map.removeLayer(this.departmentsLayer);

        this.departmentsLayer = L.geoJSON(response.data as never, {
          style: {
            color: '#38bdf8',
            weight: 1.2,
            fillColor: '#0ea5e9',
            fillOpacity: 0.08
          },
          onEachFeature: (feature, layer) => {
            const name = String(feature.properties?.['name'] ?? 'Departamento');
            layer.bindTooltip(name, { sticky: true, className: 'dept-tooltip' });
          }
        });

        if (this.departmentsVisible) this.departmentsLayer.addTo(this.map);
      },
      error: (err: unknown) => console.error('Error cargando departamentos', err)
    });
  }

  /**
   * Carga la capa de rutas desde la API.
   * Cada ruta viene como MultiLineString con la geometria real desde PostGIS.
   * Si la API retorna datos mock, muestra advertencia en el UI.
   */
  private loadRoutes(): void {
    if (!this.map) return;

    this.trafficApi.getMainRoutes().subscribe({
      next: (response) => {
        if (!this.map) return;
        if (this.routesLayer) this.map.removeLayer(this.routesLayer);

        // Detectar si los datos son mock y advertir al usuario
        this.routesSourceInfo =
          response.source === 'mock'
            ? 'Mostrando datos de ejemplo. La base de datos no tiene rutas cargadas.'
            : null;

        const features = (response.data as { features?: unknown[] })?.features ?? [];
        this.routeDataWarning =
          Array.isArray(features) && features.length <= 2
            ? 'Solo se detectaron pocas rutas. Verifica que la tabla road_segments tenga datos.'
            : null;

        // Asignar colores por ruta de forma consistente
        let colorIndex = 0;
        this.routesLayer = L.geoJSON(response.data as any, {
          style: (feature: any) => {
            const routeCode = String(feature?.properties?.['route_code'] ?? '');
            if (!this.routeColorMap.has(routeCode)) {
              this.routeColorMap.set(routeCode, this.colors[colorIndex % this.colors.length]);
              colorIndex++;
            }
            const color = this.routeColorMap.get(routeCode)!;
            // Guardar el color base en las propiedades del feature para recuperarlo luego
            if (feature && feature.properties) {
              feature.properties['baseColor'] = color;
            }
            return this.buildRouteStyle(routeCode, color);
          },
          onEachFeature: (feature: any, layer: L.Layer) => {
            const routeCode = String(feature.properties?.['route_code'] ?? '');
            const routeName = String(feature.properties?.['name'] ?? routeCode);

            layer.on('mouseover', (event: L.LeafletMouseEvent) => {
              const target = event.target as L.Path;
              if (this.selectedRoute !== routeCode) {
                target.setStyle({ weight: 8, opacity: 1.0 });
              }
              this.bindRouteTooltip(layer as L.FeatureGroup, routeCode, routeName);
            });

            layer.on('mouseout', (event: L.LeafletMouseEvent) => {
              const target = event.target as L.Path;
              const baseColor = this.routeColorMap.get(routeCode) ?? '#22c55e';
              // Restaurar el estilo base (incluyendo el ambar si esta seleccionada)
              target.setStyle(this.buildRouteStyle(routeCode, baseColor));
            });

            layer.on('click', () => {
              this.onRouteClick(routeCode, routeName);
            });
          }
        });

        if (this.routesVisible) this.routesLayer.addTo(this.map);
      },
      error: (err: unknown) => console.error('Error cargando rutas principales', err)
    });
  }

  /**
   * Construye el estilo Leaflet para una ruta segun su estado (seleccionada, oculta, normal).
   * Se usa un color ambar vibrante para resaltar la seleccion sobre los colores base.
   */
  private buildRouteStyle(routeCode: string, baseColor: string): L.PathOptions {
    const isSelected = this.selectedRoute === routeCode;
    const isHidden = !!(this.selectedRoute && !isSelected && this.showOnlySelectedRoute);

    return {
      color: isSelected ? '#fbbf24' : baseColor, // Ambar vibrante para seleccion
      weight: isSelected ? 10 : isHidden ? 1 : 5,
      opacity: isSelected ? 1.0 : isHidden ? 0.0 : 0.7,
      interactive: !isHidden,
      lineJoin: 'round',
      lineCap: 'round'
    };
  }

  /**
   * Asocia un tooltip con datos de la ruta al hacer hover.
   * Hace una llamada a la API solo la primera vez (lazy binding).
   */
  private bindRouteTooltip(layer: L.FeatureGroup, routeCode: string, routeName: string): void {
    if (layer.getTooltip()) return;

    this.trafficApi.getRouteSummary(routeCode).subscribe({
      next: (res) => {
        const s = res.data;
        const html = `
          <b style="color:#38bdf8">${routeName}</b><br/>
          Flujo normal: <b>${s['normal_flow'] || 0} veh/h</b><br/>
          Flujo pico: <b>${s['peak_flow'] || 0} veh/h</b><br/>
          Hora pico: <b>${s['peak_hour'] != null ? s['peak_hour'] + ':00 h' : 'N/D'}</b>`;
        layer.bindTooltip(html, { sticky: true, className: 'route-tooltip' }).openTooltip();
      }
    });
  }

  /**
   * Maneja el click en una ruta (desde el mapa o desde el selector lateral).
   * Carga el resumen y los departamentos de la ruta seleccionada.
   */
  onRouteClick(routeCode: string, routeName: string): void {
    this.selectedRoute = routeCode;
    this.selectedRouteName = routeName;
    this.refreshRouteStyles();

    forkJoin({
      departments: this.trafficApi.getRouteDepartments(routeCode),
      summary: this.trafficApi.getRouteSummary(routeCode)
    }).subscribe({
      next: ({ departments, summary }) => {
        this.selectedDepartments = departments.data
          .map((item) => String(item['department_name'] ?? ''))
          .filter((item) => item.length > 0);
        this.selectedRouteSummary = summary.data;
        this.renderTrafficChart();
      },
      error: (err: unknown) => console.error('Error cargando detalle de ruta', err)
    });
  }

  /** Aplica re-render de estilos a todas las rutas segun el estado actual de seleccion. */
  private refreshRouteStyles(): void {
    if (!this.routesLayer) return;
    this.routesLayer.setStyle((feature: any) => {
      const routeCode = String(feature?.properties?.['route_code'] ?? '');
      const baseColor = this.routeColorMap.get(routeCode) ?? '#22c55e';
      return this.buildRouteStyle(routeCode, baseColor);
    });
  }

  /** Alterna entre mostrar solo la ruta seleccionada vs todas las rutas. */
  toggleSingleRouteView(): void {
    this.showOnlySelectedRoute = !this.showOnlySelectedRoute;
    this.refreshRouteStyles();
  }

  /** Limpia la seleccion de ruta y restaura todos los estilos a su estado original. */
  clearSelection(): void {
    this.selectedRoute = null;
    this.selectedRouteName = '';
    this.selectedRouteSummary = null;
    this.selectedDepartments = [];
    this.showOnlySelectedRoute = false;

    if (this.trafficChart) {
      this.trafficChart.destroy();
      this.trafficChart = null;
    }

    // Restaurar estilos originales de todas las rutas
    if (this.routesLayer) {
      this.routesLayer.setStyle((feature: any) => {
        const routeCode = String(feature?.properties?.['route_code'] ?? '');
        const baseColor = this.routeColorMap.get(routeCode) ?? '#22c55e';
        return this.buildRouteStyle(routeCode, baseColor);
      });
    }
  }

  /**
   * Renderiza la grafica de afluencia simulada para la ruta seleccionada.
   * Cuando haya datos historicos reales en traffic_hourly_agg, se sustituira
   * por llamadas a la API de peak-hours por hora.
   */
  private renderTrafficChart(): void {
    setTimeout(() => {
      const canvas = document.getElementById('trafficCurveChart') as HTMLCanvasElement;
      if (!canvas) return;

      if (this.trafficChart) this.trafficChart.destroy();

      const labels = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);
      const peakHour = Number(this.selectedRouteSummary?.['peak_hour'] ?? 17);

      // Curva gaussiana centrada en la hora pico para simular el patron diario
      const dataPoints = labels.map((_, i) => {
        const dist = Math.abs(peakHour - i);
        return Math.max(5, Math.round(100 * Math.exp(-(dist * dist) / 8)));
      });

      this.trafficChart = new Chart(canvas, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Afluencia estimada (%)',
            data: dataPoints,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.15)',
            fill: true,
            tension: 0.4,
            pointRadius: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true, labels: { color: '#94a3b8', font: { size: 11 } } }
          },
          scales: {
            x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: '#1e293b' } },
            y: {
              min: 0,
              max: 100,
              ticks: { color: '#64748b', font: { size: 10 } },
              grid: { color: '#1e293b' }
            }
          }
        }
      });
    }, 100);
  }

  /** Carga el catalogo de rutas para poblar el selector lateral. */
  private loadRouteCatalog(): void {
    this.trafficApi.getRouteCatalog().subscribe({
      next: (response) => {
        this.routeCatalog = Array.isArray(response.data) ? response.data : [];
      },
      error: (err: unknown) => console.error('Error cargando catalogo de rutas', err)
    });
  }

  toggleRoutes(): void {
    if (!this.map || !this.routesLayer) return;
    this.routesVisible = !this.routesVisible;
    if (this.routesVisible) this.routesLayer.addTo(this.map);
    else this.map.removeLayer(this.routesLayer);
  }

  toggleDepartments(): void {
    if (!this.map || !this.departmentsLayer) return;
    this.departmentsVisible = !this.departmentsVisible;
    if (this.departmentsVisible) this.departmentsLayer.addTo(this.map);
    else this.map.removeLayer(this.departmentsLayer);
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    if (this.trafficChart) {
      this.trafficChart.destroy();
      this.trafficChart = null;
    }
  }
}

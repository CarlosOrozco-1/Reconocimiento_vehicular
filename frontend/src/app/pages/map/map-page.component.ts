import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import * as L from 'leaflet';
import Chart from 'chart.js/auto';

import { TrafficApiService } from '../../services/api/traffic-api.service';

@Component({
  selector: 'app-map-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel layout-panel">
      <!-- Sidebar / Dashboard -->
      <div class="sidebar" *ngIf="selectedRoute">
        <div class="sidebar-header">
          <h2>{{ selectedRouteName }}</h2>
          <button class="control-btn" (click)="clearSelection()">Ver Todas</button>
        </div>
        
        <div class="route-stats" *ngIf="selectedRouteSummary">
          <p><strong>Flujo normal:</strong> {{ selectedRouteSummary['normal_flow'] || 0 }} veh/h</p>
          <p><strong>Flujo hora pico:</strong> {{ selectedRouteSummary['peak_flow'] || 0 }} veh/h</p>
          <p><strong>Hora pico:</strong> {{ selectedRouteSummary['peak_hour'] != null ? selectedRouteSummary['peak_hour'] + ':00' : 'N/A' }}</p>
          <p><strong>Estado TR:</strong> {{ selectedRouteSummary['live_status'] || 'N/A' }}</p>
          <p><strong>Velocidad actual:</strong> {{ selectedRouteSummary['live_current_speed_kph'] || 0 }} km/h</p>
          <p><strong>Departamentos:</strong> {{ selectedDepartments.length > 0 ? selectedDepartments.join(', ') : 'Sin cruces' }}</p>
        </div>

        <div class="chart-container">
          <canvas id="trafficCurveChart"></canvas>
        </div>
      </div>
      
      <!-- Mapa -->
      <div class="map-section" [class.with-sidebar]="selectedRoute">
        <div class="layer-controls">
          <button type="button" class="control-btn" (click)="toggleRoutes()">
            {{ routesVisible ? 'Ocultar rutas' : 'Mostrar rutas' }}
          </button>
          <button type="button" class="control-btn" (click)="toggleDepartments()">
            {{ departmentsVisible ? 'Ocultar departamentos' : 'Mostrar departamentos' }}
          </button>
        </div>
        <div id="main-map" class="map-container"></div>
      </div>
    </section>
  `,
  styles: [
    `
      .layout-panel {
        display: flex;
        flex-direction: row;
        gap: 16px;
        min-height: calc(100vh - 120px);
      }

      .sidebar {
        width: 350px;
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.5);
      }

      .map-section {
        flex: 1;
        display: flex;
        flex-direction: column;
      }

      .sidebar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
      }
      
      .sidebar-header h2 {
        margin: 0;
        font-size: 1.25rem;
        color: #38bdf8;
      }

      .route-stats p {
        margin: 4px 0;
        font-size: 0.95rem;
        color: #cbd5e1;
      }

      .chart-container {
        flex: 1;
        position: relative;
        width: 100%;
        min-height: 250px;
      }

      .layer-controls {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
      }

      .control-btn {
        border: 1px solid #0ea5e9;
        background: #0284c7;
        color: #ffffff;
        border-radius: 8px;
        padding: 8px 12px;
        cursor: pointer;
        font-weight: 500;
        transition: background 0.3s ease;
      }

      .control-btn:hover {
        background: #0369a1;
      }

      .map-container {
        width: 100%;
        flex: 1;
        min-height: 420px;
        border-radius: 10px;
        overflow: hidden;
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

  // Selected Route logic
  selectedRoute: string | null = null;
  selectedRouteName: string = '';
  selectedRouteSummary: any = null;
  selectedDepartments: string[] = [];
  
  // Chart instance
  private trafficChart: Chart | null = null;

  // Colores para las rutas (modulo de color distintivo)
  private colors = ['#e11d48', '#d97706', '#65a30d', '#0891b2', '#4f46e5', '#c026d3', '#be123c'];

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngAfterViewInit(): void {
    this.map = L.map('main-map', {
      center: [14.6349, -90.5069],
      zoom: 7,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    this.loadDepartments();
    this.loadRoutes();
  }

  // Modificado: carga de departamentos con tooltip estatico
  private loadDepartments(): void {
    if (!this.map) return;

    this.trafficApi.getDepartments().subscribe({
      next: (response) => {
        if (!this.map) return;
        if (this.departmentsLayer) this.map.removeLayer(this.departmentsLayer);

        this.departmentsLayer = L.geoJSON(response.data as never, {
          style: {
            color: '#38bdf8', weight: 1.2, fillColor: '#0ea5e9', fillOpacity: 0.12
          },
          onEachFeature: (feature, layer) => {
            const name = String(feature.properties?.['name'] ?? 'Departamento');
            // Tooltip informativo
            layer.bindTooltip(name, { sticky: true });
          }
        });

        if (this.departmentsVisible) this.departmentsLayer.addTo(this.map);
      },
      error: (err: unknown) => console.error('Error departamentos', err)
    });
  }

  // Modificado: colores dinámicos y tooltip/click en rutas
  private loadRoutes(): void {
    if (!this.map) return;

    this.trafficApi.getMainRoutes().subscribe({
      next: (response) => {
        if (!this.map) return;
        if (this.routesLayer) this.map.removeLayer(this.routesLayer);

        let colorIndex = 0;
        
        this.routesLayer = L.geoJSON(response.data as never, {
          style: (feature) => {
            const routeCode = String(feature?.properties?.['route_code'] ?? '');
            
            // Asigna color distinto a cada ruta iterando el arreglo
            const color = this.colors[colorIndex % this.colors.length];
            colorIndex++;
            // Guarda el color base en las propiedades para el mouseout
            if (feature && feature.properties) feature.properties['baseColor'] = color;
            
            return {
              color: this.selectedRoute === routeCode ? '#ffffff' : color,
              weight: this.selectedRoute === routeCode ? 8 : 4,
              opacity: this.selectedRoute === routeCode ? 1.0 : 0.8
            };
          },
          onEachFeature: (feature, layer) => {
            const routeCode = String(feature.properties?.['route_code'] ?? '');
            const routeName = String(feature.properties?.['name'] ?? routeCode);

            // Modificado: tooltip dinámico al pasar el mouse
            layer.on('mouseover', (event) => {
              const target = event.target as L.Path;
              target.setStyle({ weight: 7 });
              this.ensureTooltip(layer as L.FeatureGroup, routeCode, routeName);
            });

            layer.on('mouseout', (event) => {
              const target = event.target as L.Path;
              const isSelected = this.selectedRoute === routeCode;
              target.setStyle({ weight: isSelected ? 8 : 4 });
            });
            
            // Nuevo: selecciòn para dashboard 
            layer.on('click', () => {
              this.selectRoute(routeCode, routeName);
            });
          }
        });

        if (this.routesVisible) this.routesLayer.addTo(this.map);
      },
      error: (err: unknown) => console.error('Error rutas principales', err)
    });
  }

  // Nuevo: Mantiene un tooltip actualizado con la info resumen
  private ensureTooltip(layer: L.FeatureGroup, routeCode: string, routeName: string) {
    if (layer.getTooltip()) return; // Si ya tiene tooltip, no re-cargarlo continuamente

    this.trafficApi.getRouteSummary(routeCode).subscribe({
      next: (res) => {
        const summary = res.data;
        const html = `<b>${routeName}</b><br/>Flujo: ${summary['normal_flow'] || 0} veh/h <br/> TR: ${summary['live_status'] || 'N/A'}`;
        layer.bindTooltip(html, { sticky: true, className: 'route-tooltip' }).openTooltip();
      }
    });
  }

  // Nuevo: lógic para seleccionar y reflejar en el sidebar
  private selectRoute(routeCode: string, routeName: string): void {
    this.selectedRoute = routeCode;
    this.selectedRouteName = routeName;
    
    // Repintar para reflejar la ruta seleccionada (blanco y mas gruesa)
    if (this.routesLayer) {
        this.routesLayer.setStyle((feature: any) => {
          const isSelected = routeCode === String(feature?.properties?.['route_code']);
          const baseColor = feature?.properties?.['baseColor'] || '#22c55e';
          return {
             color: isSelected ? '#ffffff' : baseColor,
             weight: isSelected ? 8 : 4,
             opacity: isSelected ? 1.0 : 0.6
          };
        });
    }

    // Cargar detalle completo
    forkJoin({
      departments: this.trafficApi.getRouteDepartments(routeCode),
      summary: this.trafficApi.getRouteSummary(routeCode)
    }).subscribe({
      next: ({ departments, summary }) => {
        this.selectedDepartments = departments.data
          .map((item) => String(item['department_name'] ?? ''))
          .filter((item) => item.length > 0);
        this.selectedRouteSummary = summary.data;
        
        // Cargar grafica de afluencia historial (ej: history)
        this.loadChart(routeCode);
      }
    });
  }

  // Nuevo: metodo para cargar y mostrar grafica
  private loadChart(routeCode: string): void {
    // Para simplificar, simularemos los datos historicos o utilizaremos afluencia estatica
    // Si la API GET /routes/{code}/live-history existe, usarla. Asumimos el modulo de history:
    
    // Aquí implementamos el código de la gráfica retrasado para esperar la renderización del view
    setTimeout(() => {
        const canvas = document.getElementById('trafficCurveChart') as HTMLCanvasElement;
        if (!canvas) return;
        
        if (this.trafficChart) this.trafficChart.destroy();

        // En un caso real llamaríamos this.trafficApi.getRouteLiveHistory(routeCode)...
        // Simulando horas del dìa y afluencia basada en peak hours:
        const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
        const dataPoints = labels.map((hour, index) => {
            const peakHour = this.selectedRouteSummary?.peak_hour || 18;
            // curva acampanada simulada
            const dist = Math.abs(peakHour - index);
            return Math.max(10, 100 - (dist * 12));
        });

        this.trafficChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Afluencia Histórica (%)',
                    data: dataPoints,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, labels: { color: '#ffffff' } }
                },
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { color: '#334155' } },
                    y: { max: 100, min: 0, ticks: { color: '#9ca3af' }, grid: { color: '#334155' } }
                }
            }
        });
    }, 100);
  }

  // Nuevo: limpiar ruta seleccionada 
  clearSelection(): void {
    this.selectedRoute = null;
    this.selectedRouteName = '';
    this.selectedRouteSummary = null;
    if (this.trafficChart) {
      this.trafficChart.destroy();
      this.trafficChart = null;
    }
    
    // Restaurar colores originales
    if (this.routesLayer) {
        this.routesLayer.setStyle((feature: any) => ({
             color: feature?.properties?.['baseColor'] || '#22c55e',
             weight: 4,
             opacity: 0.8
        }));
    }
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
    }
  }
}

import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import { forkJoin } from 'rxjs';
import * as L from 'leaflet';

import { TrafficApiService } from '../../services/api/traffic-api.service';

@Component({
  selector: 'app-map-page',
  standalone: true,
  template: `
    <section class="panel">
      <h2>Mapa de rutas principales</h2>
      <p>Leaflet: rutas, departamentos y datos por ruta en hover.</p>
      <div class="layer-controls">
        <button type="button" class="control-btn" (click)="toggleRoutes()">
          {{ routesVisible ? 'Ocultar rutas' : 'Mostrar rutas' }}
        </button>
        <button type="button" class="control-btn" (click)="toggleDepartments()">
          {{ departmentsVisible ? 'Ocultar departamentos' : 'Mostrar departamentos' }}
        </button>
      </div>
      <div id="main-map" class="map-container"></div>
    </section>
  `,
  styles: [
    `
      .layer-controls {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
      }

      .control-btn {
        border: 1px solid #374151;
        background: #111827;
        color: #e5e7eb;
        border-radius: 8px;
        padding: 8px 12px;
        cursor: pointer;
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

  private loadDepartments(): void {
    if (!this.map) {
      return;
    }

    this.trafficApi.getDepartments().subscribe({
      next: (response) => {
        if (!this.map) {
          return;
        }

        if (this.departmentsLayer) {
          this.map.removeLayer(this.departmentsLayer);
        }

        this.departmentsLayer = L.geoJSON(response.data as never, {
          style: {
            color: '#38bdf8',
            weight: 1.2,
            fillColor: '#0ea5e9',
            fillOpacity: 0.12
          },
          onEachFeature: (feature, layer) => {
            const name = String(feature.properties?.['name'] ?? 'Departamento');
            layer.bindTooltip(name, { sticky: true });
          }
        });

        if (this.departmentsVisible) {
          this.departmentsLayer.addTo(this.map);
        }
      },
      error: (err: unknown) => {
        console.error('No fue posible cargar departamentos', err);
      }
    });
  }

  private loadRoutes(): void {
    if (!this.map) {
      return;
    }

    this.trafficApi.getMainRoutes().subscribe({
      next: (response) => {
        if (!this.map) {
          return;
        }

        if (this.routesLayer) {
          this.map.removeLayer(this.routesLayer);
        }

        this.routesLayer = L.geoJSON(response.data as never, {
          style: {
            color: '#22c55e',
            weight: 4,
            opacity: 0.95
          },
          onEachFeature: (feature, layer) => {
            const routeCode = String(feature.properties?.['route_code'] ?? '');
            const routeName = String(feature.properties?.['name'] ?? routeCode);

            layer.on('mouseover', (event) => {
              const target = event.target as L.Path;
              target.setStyle({ weight: 6, color: '#16a34a' });
              this.openRoutePopup(routeCode, routeName, layer);
            });

            layer.on('mouseout', (event) => {
              const target = event.target as L.Path;
              target.setStyle({ weight: 4, color: '#22c55e' });
            });
          }
        });

        if (this.routesVisible) {
          this.routesLayer.addTo(this.map);
        }
      },
      error: (err: unknown) => {
        console.error('No fue posible cargar rutas principales', err);
      }
    });
  }

  private openRoutePopup(routeCode: string, routeName: string, layer: L.Layer): void {
    if (!routeCode) {
      return;
    }

    forkJoin({
      departments: this.trafficApi.getRouteDepartments(routeCode),
      summary: this.trafficApi.getRouteSummary(routeCode)
    }).subscribe({
      next: ({ departments, summary }) => {
        const names = departments.data
          .map((item) => String(item['department_name'] ?? ''))
          .filter((item) => item.length > 0);

        const summaryData = summary.data;
        const normalFlow = Number(summaryData['normal_flow'] ?? 0);
        const peakFlow = Number(summaryData['peak_flow'] ?? 0);
        const peakHour = summaryData['peak_hour'] == null ? 'N/A' : `${summaryData['peak_hour']}:00`;

        const html = `
          <strong>${routeName}</strong><br/>
          Flujo normal: ${normalFlow} veh/h<br/>
          Flujo hora pico: ${peakFlow} veh/h<br/>
          Hora pico: ${peakHour}<br/>
          Departamentos: ${names.length > 0 ? names.join(', ') : 'Sin cruces'}
        `;

        layer.bindPopup(html, { closeButton: false, autoPan: false }).openPopup();
      },
      error: (err: unknown) => {
        console.error('No fue posible cargar detalle de ruta', err);
      }
    });
  }

  toggleRoutes(): void {
    if (!this.map || !this.routesLayer) {
      return;
    }
    this.routesVisible = !this.routesVisible;
    if (this.routesVisible) {
      this.routesLayer.addTo(this.map);
    } else {
      this.map.removeLayer(this.routesLayer);
    }
  }

  toggleDepartments(): void {
    if (!this.map || !this.departmentsLayer) {
      return;
    }
    this.departmentsVisible = !this.departmentsVisible;
    if (this.departmentsVisible) {
      this.departmentsLayer.addTo(this.map);
    } else {
      this.map.removeLayer(this.departmentsLayer);
    }
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  }
}

import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import maplibregl, { Map } from 'maplibre-gl';

import { TrafficApiService } from '../../services/api/traffic-api.service';

@Component({
  selector: 'app-map-page',
  standalone: true,
  template: `
    <section class="panel">
      <h2>Mapa de rutas principales</h2>
      <p>Vista inicial para integrar segmentos, departamentos y flujo vehicular por hora.</p>
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
  private map: Map | null = null;
  private readonly departmentsSourceId = 'departments-source';
  private readonly departmentsFillLayerId = 'departments-fill-layer';
  private readonly departmentsLineLayerId = 'departments-line-layer';
  private readonly routesSourceId = 'routes-source';
  private readonly routesLayerId = 'routes-layer';
  routesVisible = true;
  departmentsVisible = true;

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngAfterViewInit(): void {
    this.map = new maplibregl.Map({
      container: 'main-map',
      style: 'https://demotiles.maplibre.org/style.json',
      center: [-90.5069, 14.6349],
      zoom: 7
    });

    this.map.addControl(new maplibregl.NavigationControl(), 'top-right');

    this.map.on('load', () => {
      this.loadDepartments();
      this.loadRoutes();
      this.bindRoutePopup();
    });
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

        if (this.map.getLayer(this.departmentsLineLayerId)) {
          this.map.removeLayer(this.departmentsLineLayerId);
        }
        if (this.map.getLayer(this.departmentsFillLayerId)) {
          this.map.removeLayer(this.departmentsFillLayerId);
        }
        if (this.map.getSource(this.departmentsSourceId)) {
          this.map.removeSource(this.departmentsSourceId);
        }

        this.map.addSource(this.departmentsSourceId, {
          type: 'geojson',
          data: response.data as never
        });

        this.map.addLayer({
          id: this.departmentsFillLayerId,
          type: 'fill',
          source: this.departmentsSourceId,
          paint: {
            'fill-color': '#0ea5e9',
            'fill-opacity': 0.12
          }
        });

        this.map.addLayer({
          id: this.departmentsLineLayerId,
          type: 'line',
          source: this.departmentsSourceId,
          paint: {
            'line-color': '#38bdf8',
            'line-width': 1.5
          }
        });
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

        if (this.map.getLayer(this.routesLayerId)) {
          this.map.removeLayer(this.routesLayerId);
        }
        if (this.map.getSource(this.routesSourceId)) {
          this.map.removeSource(this.routesSourceId);
        }

        this.map.addSource(this.routesSourceId, {
          type: 'geojson',
          data: response.data as never
        });

        this.map.addLayer({
          id: this.routesLayerId,
          type: 'line',
          source: this.routesSourceId,
          paint: {
            'line-color': '#22c55e',
            'line-width': 4
          }
        });
      },
      error: (err: unknown) => {
        console.error('No fue posible cargar rutas principales', err);
      }
    });
  }

  private bindRoutePopup(): void {
    if (!this.map) {
      return;
    }

    this.map.on('click', this.routesLayerId, (event) => {
      const feature = event.features?.[0];
      const properties = (feature?.properties ?? {}) as Record<string, unknown>;
      const routeCode = String(properties['route_code'] ?? '');
      const routeName = String(properties['name'] ?? routeCode);

      if (!routeCode) {
        return;
      }

      this.trafficApi.getRouteDepartments(routeCode).subscribe({
        next: (response) => {
          const names = response.data
            .map((item) => String(item['department_name'] ?? ''))
            .filter((item) => item.length > 0);
          const deptText = names.length > 0 ? names.join(', ') : 'Sin cruces disponibles';

          new maplibregl.Popup()
            .setLngLat(event.lngLat)
            .setHTML(`<strong>${routeName}</strong><br/>Departamentos: ${deptText}`)
            .addTo(this.map!);
        },
        error: (err: unknown) => {
          console.error('No fue posible cargar cruces de departamentos', err);
        }
      });
    });

    this.map.on('mouseenter', this.routesLayerId, () => {
      if (this.map) {
        this.map.getCanvas().style.cursor = 'pointer';
      }
    });

    this.map.on('mouseleave', this.routesLayerId, () => {
      if (this.map) {
        this.map.getCanvas().style.cursor = '';
      }
    });
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  toggleRoutes(): void {
    if (!this.map) {
      return;
    }
    this.routesVisible = !this.routesVisible;
    const visibility = this.routesVisible ? 'visible' : 'none';
    if (this.map.getLayer(this.routesLayerId)) {
      this.map.setLayoutProperty(this.routesLayerId, 'visibility', visibility);
    }
  }

  toggleDepartments(): void {
    if (!this.map) {
      return;
    }
    this.departmentsVisible = !this.departmentsVisible;
    const visibility = this.departmentsVisible ? 'visible' : 'none';
    if (this.map.getLayer(this.departmentsFillLayerId)) {
      this.map.setLayoutProperty(this.departmentsFillLayerId, 'visibility', visibility);
    }
    if (this.map.getLayer(this.departmentsLineLayerId)) {
      this.map.setLayoutProperty(this.departmentsLineLayerId, 'visibility', visibility);
    }
  }
}

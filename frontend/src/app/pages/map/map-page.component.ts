import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import * as L from 'leaflet';
import Chart from 'chart.js/auto';

import { TrafficApiService } from '../../services/api/traffic-api.service';

/**
 * Componente principal del mapa de tráfico de Guatemala.
 * Separado en archivos (.ts, .html, .css) para mejor estructura y mantenimiento.
 */
@Component({
  selector: 'app-map-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './map-page.component.html',
  styleUrls: ['./map-page.component.css']
})
export class MapPageComponent implements AfterViewInit, OnDestroy {
  private map!: L.Map;
  private routesLayer!: L.GeoJSON;
  private departmentsLayer!: L.GeoJSON;
  private trafficChart: Chart | null = null;

  routeCatalog: Array<Record<string, any>> = [];
  selectedRoute: string | null = null;
  selectedRouteName: string | null = null;
  selectedRouteSummary: Record<string, any> | null = null;
  selectedDepartments: string[] = [];

  routesVisible = true;
  departmentsVisible = true;
  showOnlySelectedRoute = false;
  routesSourceInfo = '';
  routeDataWarning = '';

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngAfterViewInit(): void {
    this.initMap();
    this.loadInitialData();
  }

  ngOnDestroy(): void {
    if (this.trafficChart) this.trafficChart.destroy();
    if (this.map) this.map.remove();
  }

  private initMap(): void {
    this.map = L.map('main-map', {
      center: [15.7835, -90.2308],
      zoom: 7,
      zoomControl: true
    });

    // Fondo estándar de OpenStreetMap para evitar errores de conexión (ERR_NAME_NOT_RESOLVED)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);
  }

  private loadInitialData(): void {
    console.log('Iniciando carga de datos del mapa...');
    forkJoin({
      catalog: this.trafficApi.getRouteCatalog(),
      routes: this.trafficApi.getMainRoutes(),
      departments: this.trafficApi.getDepartments()
    }).subscribe({
      next: (res) => {
        console.log('Datos recibidos con éxito:', res);
        this.routeCatalog = Array.isArray(res.catalog.data) ? res.catalog.data : [];
        this.renderRoutes(res.routes.data);
        this.renderDepartments(res.departments.data);
        this.routesSourceInfo = res.routes.source === 'mock' ? 'Datos de ejemplo' : 'Datos reales (PostGIS)';
      },
      error: (err) => {
        console.error('ERROR CRÍTICO CARGANDO DATOS:', err);
        this.routeDataWarning = 'Error de conexión con el servidor de datos.';
      }
    });
  }

  private renderRoutes(geoJson: any): void {
    if (this.routesLayer) this.map.removeLayer(this.routesLayer);

    this.routesLayer = L.geoJSON(geoJson, {
      style: (feature) => this.buildRouteStyle(feature?.properties?.route_code),
      onEachFeature: (feature, layer) => {
        const props = feature.properties;
        
        // Al hacer clic, seleccionar la ruta, mostrar el side-panel y centrar el mapa
        layer.on('click', (e) => {
          this.onRouteClick(props.route_code, props.name);
          // Centrar el mapa en la ruta seleccionada con un poco de padding para el side-panel
          if (layer instanceof L.Polyline || layer instanceof L.Polygon) {
            this.map.fitBounds(layer.getBounds(), { paddingBottomRight: [400, 0] });
          }
        });
      }
    }).addTo(this.map);
  }

  private renderDepartments(geoJson: any): void {
    if (this.departmentsLayer) this.map.removeLayer(this.departmentsLayer);
    
    this.departmentsLayer = L.geoJSON(geoJson, {
      style: {
        color: '#64748b',
        weight: 1,
        fillColor: 'transparent', // <--- QUITAMOS EL GRIS PESADO
        fillOpacity: 0
      },
      interactive: false // Para que no interfiera con el clic en las rutas
    }).addTo(this.map);
  }

  onRouteClick(routeCode: string, routeName: string): void {
    this.selectedRoute = routeCode;
    this.selectedRouteName = routeName;
    this.updateLayersVisibility();
    this.loadRouteDetails(routeCode);
  }

  private loadRouteDetails(routeCode: string): void {
    forkJoin({
      summary: this.trafficApi.getRouteSummary(routeCode),
      depts: this.trafficApi.getRouteDepartments(routeCode)
    }).subscribe({
      next: (res) => {
        this.selectedRouteSummary = res.summary.data;
        this.selectedDepartments = Array.isArray(res.depts.data) 
          ? res.depts.data.map((d: any) => d.dept_name) 
          : [];
        this.renderTrafficChart();
      }
    });
  }

  private renderTrafficChart(): void {
    const ctx = document.getElementById('trafficCurveChart') as HTMLCanvasElement;
    if (!ctx) return;

    if (this.trafficChart) this.trafficChart.destroy();

    // Simulación de curva basada en el flujo pico
    const peakHour = this.selectedRouteSummary?.['peak_hour'] || 18;
    const peakFlow = this.selectedRouteSummary?.['peak_flow'] || 1000;
    
    const data = Array.from({ length: 24 }, (_, i) => {
      const dist = Math.abs(peakHour - i);
      const factor = Math.exp(-(dist * dist) / 15);
      return Math.round(peakFlow * (0.2 + 0.8 * factor));
    });

    this.trafficChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: Array.from({ length: 24 }, (_, i) => `${i}h`),
        datasets: [{
          label: 'Flujo Estimado',
          data: data,
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { 
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#64748b', font: { size: 10 } }
          }
        }
      }
    });
  }

  private buildRouteStyle(routeCode: string): L.PathOptions {
    const isSelected = routeCode === this.selectedRoute;
    const isHidden = this.showOnlySelectedRoute && this.selectedRoute && !isSelected;

    return {
      color: isSelected ? '#f59e0b' : '#3b82f6', // Amber for selected, vibrant Blue for default
      weight: isSelected ? 8 : (isHidden ? 0 : 5),
      opacity: isSelected ? 1 : (isHidden ? 0 : 0.8),
      lineJoin: 'round'
    };
  }

  private updateLayersVisibility(): void {
    if (this.routesLayer) {
      this.routesLayer.setStyle((feature: any) => 
        this.buildRouteStyle(feature?.properties?.route_code)
      );
    }
  }

  clearSelection(): void {
    this.selectedRoute = null;
    this.selectedRouteName = null;
    this.selectedRouteSummary = null;
    this.showOnlySelectedRoute = false;
    this.updateLayersVisibility();
  }

  toggleRoutes(): void {
    this.routesVisible = !this.routesVisible;
    if (this.routesVisible) this.routesLayer.addTo(this.map);
    else this.map.removeLayer(this.routesLayer);
  }

  toggleDepartments(): void {
    this.departmentsVisible = !this.departmentsVisible;
    if (this.departmentsVisible) this.departmentsLayer.addTo(this.map);
    else this.map.removeLayer(this.departmentsLayer);
  }

  toggleSingleRouteView(): void {
    this.showOnlySelectedRoute = !this.showOnlySelectedRoute;
    this.updateLayersVisibility();
  }

  strConv(val: any): string {
    return String(val ?? '');
  }
}

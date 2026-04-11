import { AfterViewInit, Component, OnDestroy } from '@angular/core';
import maplibregl, { Map } from 'maplibre-gl';

import { TrafficApiService } from '../../services/api/traffic-api.service';

@Component({
  selector: 'app-map-page',
  standalone: true,
  template: `
    <section class="panel">
      <h2>Mapa de rutas principales</h2>
      <p>Vista inicial para integrar segmentos y flujo vehicular por hora.</p>
      <div id="main-map" class="map-container"></div>
    </section>
  `
})
export class MapPageComponent implements AfterViewInit, OnDestroy {
  private map: Map | null = null;

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
      this.trafficApi.getMainRoutes().subscribe({
        next: (response) => {
          if (!this.map) {
            return;
          }

          const sourceId = 'routes-source';
          const layerId = 'routes-layer';

          if (this.map.getLayer(layerId)) {
            this.map.removeLayer(layerId);
          }
          if (this.map.getSource(sourceId)) {
            this.map.removeSource(sourceId);
          }

          this.map.addSource(sourceId, {
            type: 'geojson',
            data: response.data as never
          });

          this.map.addLayer({
            id: layerId,
            type: 'line',
            source: sourceId,
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
    });
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }
}

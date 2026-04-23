import { Component, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import * as L from 'leaflet';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-tomtom-sandbox',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tomtom-sandbox.component.html',
  styleUrls: ['./tomtom-sandbox.component.css']
})
export class TomtomSandboxComponent implements AfterViewInit, OnDestroy {
  private map!: L.Map;
  private tomtomLayer: L.TileLayer | null = null;
  
  isTrafficLayerActive = false;
  apiResponse: any = null;
  isLoading = false;
  errorMsg = '';

  constructor(private http: HttpClient) {}

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    // Centrar en Ciudad de Guatemala
    this.map = L.map('sandbox-map', {
      center: [14.6349, -90.5069],
      zoom: 13,
      zoomControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    // Al hacer clic en el mapa, obtener la velocidad en vivo de ese punto
    this.map.on('click', (e: L.LeafletMouseEvent) => {
      this.fetchTomTomData(e.latlng.lat, e.latlng.lng);
    });
  }

  toggleTrafficLayer(): void {
    this.isTrafficLayerActive = !this.isTrafficLayerActive;
    
    if (this.isTrafficLayerActive) {
      // Usar un API Key de prueba temporal o requerir que el usuario lo ponga en environment
      // Nota: Idealmente TomTom Traffic Tiles se consume directamente si se tiene la llave expuesta
      // o se pasa a traves de un proxy. Aqui asumimos que el usuario lo configurara si quiere la visualizacion directa.
      const apiKey = 'YUtYmvSNZ6LsVTYEc17rSljCiYbB1i55'; // Llave real para la capa visual
      this.tomtomLayer = L.tileLayer(`https://api.tomtom.com/traffic/map/4/tile/flow/relative/{z}/{x}/{y}.png?key=${apiKey}`, {
        opacity: 0.7,
        maxZoom: 22,
        attribution: '&copy; TomTom'
      }).addTo(this.map);
    } else {
      if (this.tomtomLayer) {
        this.map.removeLayer(this.tomtomLayer);
        this.tomtomLayer = null;
      }
    }
  }

  private activeSegment: L.Polyline | null = null;

  fetchTomTomData(lat: number = 14.6349, lon: number = -90.5069): void {
    this.isLoading = true;
    this.errorMsg = '';
    this.apiResponse = null;
    
    if (this.activeSegment) {
      this.map.removeLayer(this.activeSegment);
      this.activeSegment = null;
    }

    const url = `${environment.apiBaseUrl}/sandbox/tomtom-flow?lat=${lat}&lon=${lon}`;
    
    this.http.get(url).subscribe({
      next: (data: any) => {
        this.apiResponse = data;
        this.isLoading = false;
        
        // Dibujar el segmento en el mapa si TomTom devuelve coordenadas
        if (data && data.flowSegmentData && data.flowSegmentData.coordinates) {
          const coords = data.flowSegmentData.coordinates.coordinate.map((c: any) => [c.latitude, c.longitude]);
          
          // Determinar el color basado en la velocidad
          const current = data.flowSegmentData.currentSpeed;
          const free = data.flowSegmentData.freeFlowSpeed;
          const ratio = current / free;
          let color = '#10b981'; // Verde (Fluido)
          if (ratio < 0.5) color = '#ef4444'; // Rojo (Congestionado)
          else if (ratio < 0.8) color = '#f59e0b'; // Naranja (Moderado)

          this.activeSegment = L.polyline(coords, {
            color: color,
            weight: 8,
            opacity: 0.9,
            lineCap: 'round'
          }).addTo(this.map);
          
          // Ajustar la vista del mapa para que el segmento se vea completo
          this.map.fitBounds(this.activeSegment.getBounds(), { padding: [50, 50] });
        }
      },
      error: (err) => {
        this.errorMsg = err.message || 'Error al conectar con el backend de Sandbox';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  jumpToMexicoCity(): void {
    const mxLat = 19.4326;
    const mxLon = -99.1332;
    this.fetchTomTomData(mxLat, mxLon);
  }

  jumpToCA2(): void {
    // Coordenada CA-2 (Ayutla, Frontera con MX)
    const ca2Lat = 14.676580;
    const ca2Lon = -92.147855;
    this.fetchTomTomData(ca2Lat, ca2Lon);
  }
}

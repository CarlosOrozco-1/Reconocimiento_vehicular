import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';

import { TrafficApiService } from '../../services/api/traffic-api.service';

/**
 * Componente de dashboard de trafico.
 * Muestra el catalogo de rutas con su longitud, y las horas pico por ruta
 * obtenidas desde la tabla traffic_hourly_agg de la base de datos.
 * Este componente reemplaza el dashboard del worker que fue archivado.
 */
@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel">
      <div class="dashboard-header">
        <h2>Dashboard de Tráfico — Guatemala</h2>
        <p class="subtitle">Resumen de rutas principales y horas pico registradas en la base de datos.</p>
      </div>

      <!-- Indicadores globales -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🛣️</div>
          <div class="stat-content">
            <span class="stat-number">{{ routeCatalog.length }}</span>
            <span class="stat-label">Rutas principales</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📏</div>
          <div class="stat-content">
            <span class="stat-number">{{ totalKm }}</span>
            <span class="stat-label">Kilómetros totales</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏰</div>
          <div class="stat-content">
            <span class="stat-number">{{ peakHours.length }}</span>
            <span class="stat-label">Rutas con datos de pico</span>
          </div>
        </div>
        <div class="stat-card" [class.connected]="dbConnected === true" [class.error]="dbConnected === false">
          <div class="stat-icon">{{ dbConnected === true ? '✅' : dbConnected === false ? '❌' : '⏳' }}</div>
          <div class="stat-content">
            <span class="stat-number">{{ dbConnected === true ? 'Online' : dbConnected === false ? 'Error' : '...' }}</span>
            <span class="stat-label">Base de datos</span>
          </div>
        </div>
      </div>

      <!-- Catalogo de rutas -->
      <div class="section-block">
        <h3>Catálogo de rutas</h3>
        <div *ngIf="routeCatalog.length === 0" class="empty-state">
          <span>Sin rutas cargadas en la base de datos.</span>
        </div>
        <div class="route-cards" *ngIf="routeCatalog.length > 0">
          <div class="route-card" *ngFor="let route of routeCatalog"
               [id]="'dash-route-' + route['route_code']">
            <div class="route-card-header">
              <span class="route-badge">{{ route['route_code'] }}</span>
              <span class="route-km">{{ route['length_km'] }} km</span>
            </div>
            <div class="route-card-name">{{ route['name'] }}</div>
            <div class="route-card-meta">{{ route['segment_count'] }} segmentos</div>
          </div>
        </div>
      </div>

      <!-- Horas pico por ruta -->
      <div class="section-block">
        <h3>Horas pico por ruta</h3>
        <p class="section-note" *ngIf="peakHours.length === 0">
          Sin datos de horas pico. Se poblarán cuando haya registros en <code>traffic_hourly_agg</code>.
        </p>
        <table *ngIf="peakHours.length > 0">
          <thead>
            <tr>
              <th>Ruta</th>
              <th>Nombre</th>
              <th>Hora pico</th>
              <th>Flujo promedio</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let row of peakHours" [id]="'peak-row-' + row['route_code']">
              <td><span class="route-badge small">{{ row['route_code'] }}</span></td>
              <td>{{ row['route_name'] }}</td>
              <td class="peak-hour">{{ row['peak_hour'] }}:00 h</td>
              <td>{{ row['avg_flow'] }} veh/h</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  `,
  styles: [
    `
      .panel {
        padding: 24px;
        color: #e2e8f0;
      }

      .dashboard-header {
        margin-bottom: 24px;
      }

      .dashboard-header h2 {
        margin: 0 0 4px 0;
        font-size: 1.6rem;
        color: #f1f5f9;
      }

      .subtitle {
        margin: 0;
        color: #64748b;
        font-size: 0.95rem;
      }

      /* ---- Stats grid ---- */
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 32px;
      }

      .stat-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: border-color 0.2s ease;
      }

      .stat-card.connected { border-color: #10b981; }
      .stat-card.error     { border-color: #ef4444; }

      .stat-icon { font-size: 2rem; }

      .stat-content {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .stat-number {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
        line-height: 1;
      }

      .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      /* ---- Section blocks ---- */
      .section-block {
        margin-bottom: 32px;
      }

      .section-block h3 {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 0 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e293b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .section-note {
        color: #64748b;
        font-size: 0.9rem;
        font-style: italic;
        margin: 0;
      }

      code {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.85rem;
        color: #38bdf8;
      }

      /* ---- Route cards ---- */
      .route-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
      }

      .route-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        transition: border-color 0.2s;
      }

      .route-card:hover { border-color: #38bdf8; }

      .route-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .route-badge {
        background: #0c4a6e;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
      }

      .route-badge.small { font-size: 0.78rem; padding: 2px 6px; }

      .route-km {
        color: #94a3b8;
        font-size: 0.82rem;
      }

      .route-card-name {
        color: #cbd5e1;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .route-card-meta {
        color: #475569;
        font-size: 0.78rem;
      }

      /* ---- Table ---- */
      table {
        width: 100%;
        border-collapse: collapse;
      }

      th, td {
        text-align: left;
        padding: 10px 12px;
        border-bottom: 1px solid #1e293b;
        font-size: 0.9rem;
      }

      th {
        color: #64748b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .peak-hour {
        color: #f97316;
        font-weight: 600;
      }

      .empty-state {
        color: #64748b;
        font-size: 0.9rem;
        text-align: center;
        padding: 24px;
        border: 1px dashed #334155;
        border-radius: 10px;
      }
    `
  ]
})
export class DashboardPageComponent implements OnInit {
  routeCatalog: Array<Record<string, unknown>> = [];
  peakHours: Array<Record<string, unknown>> = [];
  totalKm = 0;
  dbConnected: boolean | null = null;

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngOnInit(): void {
    this.loadCatalog();
    this.loadPeakHours();
  }

  private loadCatalog(): void {
    this.trafficApi.getRouteCatalog().subscribe({
      next: (res) => {
        this.routeCatalog = Array.isArray(res.data) ? res.data : [];
        // Calcular km totales sumando los km de cada ruta
        this.totalKm = this.routeCatalog.reduce((acc, r) => acc + Number(r['length_km'] ?? 0), 0);
        // Si el catalogo carga, la DB esta disponible
        this.dbConnected = res.source === 'db';
      },
      error: () => {
        this.dbConnected = false;
      }
    });
  }

  private loadPeakHours(): void {
    this.trafficApi.getPeakHours().subscribe({
      next: (res) => {
        this.peakHours = Array.isArray(res.data) ? res.data : [];
      },
      error: (err: unknown) => console.error('Error cargando horas pico', err)
    });
  }
}

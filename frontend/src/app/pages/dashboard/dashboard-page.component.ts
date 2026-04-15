import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { TrafficApiService } from '../../services/api/traffic-api.service';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="panel">
      <h2>Dashboard de monitoreo</h2>
      <p>Estado real del worker, rutas monitoreadas y últimas solicitudes.</p>

      <div class="actions">
        <button type="button" class="control-btn" (click)="startWorker()">Iniciar worker</button>
        <button type="button" class="control-btn" (click)="stopWorker()">Detener worker</button>
        <button type="button" class="control-btn" (click)="refreshAll()">Actualizar</button>
      </div>

      <div class="status-grid" *ngIf="workerStatus">
        <div class="status-card">
          <strong>Estado</strong>
          <span>{{ workerStatus['status'] }}</span>
        </div>
        <div class="status-card">
          <strong>Runtime</strong>
          <span>{{ workerStatus['runtime_running'] ? 'running' : 'stopped' }}</span>
        </div>
        <div class="status-card">
          <strong>Última corrida</strong>
          <span>{{ workerStatus['last_run_at'] || 'N/A' }}</span>
        </div>
        <div class="status-card">
          <strong>Último éxito</strong>
          <span>{{ workerStatus['last_success_at'] || 'N/A' }}</span>
        </div>
        <div class="status-card">
          <strong>Requests OK</strong>
          <span>{{ workerStatus['requests_ok'] || 0 }}</span>
        </div>
        <div class="status-card">
          <strong>Requests Error</strong>
          <span>{{ workerStatus['requests_error'] || 0 }}</span>
        </div>
      </div>

      <h3>Rutas monitoreadas</h3>
      <div class="route-actions">
        <input [(ngModel)]="newRouteCode" placeholder="Ej: CA-2" />
        <button type="button" class="control-btn" (click)="addRoute()">Agregar ruta</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Ruta</th>
            <th>Enabled</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let route of monitoredRoutes">
            <td>{{ route['route_code'] }}</td>
            <td>{{ route['enabled'] }}</td>
            <td>
              <button type="button" class="danger-btn" (click)="removeRoute(route['route_code'])">
                Quitar
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <h3>Curva de afluencia (tiempo real)</h3>
      <div class="route-actions">
        <label>Ruta:</label>
        <select [(ngModel)]="selectedRouteCode" (change)="refreshHistory()">
          <option *ngFor="let route of monitoredRoutes" [value]="route['route_code']">
            {{ route['route_code'] }}
          </option>
        </select>
        <button type="button" class="control-btn" (click)="refreshHistory()">Actualizar curva</button>
      </div>

      <div class="chart-box" *ngIf="historyChartPoints.length > 0; else noHistoryTpl">
        <svg viewBox="0 0 600 180" class="history-chart">
          <polyline points="0,170 600,170" class="axis-line"></polyline>
          <polyline [attr.points]="historyChartPolyline" class="curve-line"></polyline>
        </svg>
        <div class="chart-meta">
          <span>Último valor afluencia: {{ latestAfluenciaPct }}%</span>
          <span>Lecturas: {{ historyChartPoints.length }}</span>
        </div>
      </div>
      <ng-template #noHistoryTpl>
        <p class="muted">Sin datos de historial para esta ruta. Inicia el worker y espera algunas lecturas.</p>
      </ng-template>

      <h3>Últimas solicitudes del worker</h3>
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Ruta</th>
            <th>Resultado</th>
            <th>Duración ms</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let req of workerRequests">
            <td>{{ req['created_at'] }}</td>
            <td>{{ req['route_code'] }}</td>
            <td>{{ req['result'] }}</td>
            <td>{{ req['duration_ms'] }}</td>
            <td>{{ req['error_message'] || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  `,
  styles: [
    `
      .actions,
      .route-actions {
        display: flex;
        gap: 8px;
        margin-bottom: 12px;
        align-items: center;
      }

      .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px;
        margin-bottom: 16px;
      }

      .status-card {
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 10px;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .control-btn,
      .danger-btn {
        border: 1px solid #374151;
        background: #111827;
        color: #e5e7eb;
        border-radius: 8px;
        padding: 8px 10px;
        cursor: pointer;
      }

      .danger-btn {
        border-color: #7f1d1d;
      }

      table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 18px;
      }

      th,
      td {
        text-align: left;
        border-bottom: 1px solid #1f2937;
        padding: 8px;
        font-size: 13px;
      }

      th {
        color: #9ca3af;
      }

      input {
        border: 1px solid #374151;
        background: #0f172a;
        color: #e5e7eb;
        border-radius: 8px;
        padding: 8px;
      }

      select {
        border: 1px solid #374151;
        background: #0f172a;
        color: #e5e7eb;
        border-radius: 8px;
        padding: 8px;
      }

      .chart-box {
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 16px;
      }

      .history-chart {
        width: 100%;
        height: 200px;
        background: #020617;
        border-radius: 6px;
      }

      .axis-line {
        fill: none;
        stroke: #334155;
        stroke-width: 1;
      }

      .curve-line {
        fill: none;
        stroke: #22c55e;
        stroke-width: 3;
      }

      .chart-meta {
        display: flex;
        gap: 16px;
        margin-top: 8px;
        color: #9ca3af;
        font-size: 12px;
      }

      .muted {
        color: #9ca3af;
      }
    `
  ]
})
export class DashboardPageComponent implements OnInit, OnDestroy {
  workerStatus: Record<string, unknown> | null = null;
  workerRequests: Array<Record<string, unknown>> = [];
  monitoredRoutes: Array<Record<string, unknown>> = [];
  historyChartPoints: Array<Record<string, unknown>> = [];
  historyChartPolyline = '';
  latestAfluenciaPct = 0;
  selectedRouteCode = '';
  newRouteCode = '';

  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngOnInit(): void {
    this.refreshAll();
    this.refreshTimer = setInterval(() => this.refreshAll(), 10000);
  }

  ngOnDestroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  refreshAll(): void {
    this.trafficApi.getWorkerStatus().subscribe({
      next: (res) => {
        this.workerStatus = res.data;
      }
    });

    this.trafficApi.getWorkerRequests(60, 80).subscribe({
      next: (res) => {
        this.workerRequests = res.data;
      }
    });

    this.trafficApi.getMonitoredRoutes(false).subscribe({
      next: (res) => {
        this.monitoredRoutes = res.data;
        if (!this.selectedRouteCode && this.monitoredRoutes.length > 0) {
          this.selectedRouteCode = String(this.monitoredRoutes[0]['route_code'] ?? '');
        }
        if (this.selectedRouteCode) {
          this.refreshHistory();
        }
      }
    });
  }

  refreshHistory(): void {
    const routeCode = this.selectedRouteCode.trim().toUpperCase();
    if (!routeCode) {
      this.historyChartPoints = [];
      this.historyChartPolyline = '';
      this.latestAfluenciaPct = 0;
      return;
    }

    this.trafficApi.getRouteLiveHistory(routeCode, 24, 300).subscribe({
      next: (res) => {
        this.historyChartPoints = res.data;
        this.updateHistoryPolyline();
      },
      error: () => {
        this.historyChartPoints = [];
        this.historyChartPolyline = '';
        this.latestAfluenciaPct = 0;
      }
    });
  }

  private updateHistoryPolyline(): void {
    const rows = this.historyChartPoints;
    if (rows.length === 0) {
      this.historyChartPolyline = '';
      this.latestAfluenciaPct = 0;
      return;
    }

    const values = rows
      .map((row) => Number(row['afluencia_pct'] ?? 0))
      .filter((value) => Number.isFinite(value));

    if (values.length === 0) {
      this.historyChartPolyline = '';
      this.latestAfluenciaPct = 0;
      return;
    }

    const maxY = Math.max(100, ...values);
    const width = 600;
    const height = 170;
    const steps = Math.max(1, values.length - 1);

    const points = values.map((value, index) => {
      const x = (index / steps) * width;
      const y = height - (value / maxY) * height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    });

    this.historyChartPolyline = points.join(' ');
    this.latestAfluenciaPct = Number(values[values.length - 1].toFixed(2));
  }

  startWorker(): void {
    this.trafficApi.startWorker().subscribe({
      next: () => this.refreshAll()
    });
  }

  stopWorker(): void {
    this.trafficApi.stopWorker().subscribe({
      next: () => this.refreshAll()
    });
  }

  addRoute(): void {
    const routeCode = this.newRouteCode.trim().toUpperCase();
    if (!routeCode) {
      return;
    }

    this.trafficApi.addMonitoredRoute(routeCode).subscribe({
      next: () => {
        this.newRouteCode = '';
        this.selectedRouteCode = routeCode;
        this.refreshAll();
      }
    });
  }

  removeRoute(routeCodeRaw: unknown): void {
    const routeCode = String(routeCodeRaw || '').trim().toUpperCase();
    if (!routeCode) {
      return;
    }

    this.trafficApi.removeMonitoredRoute(routeCode).subscribe({
      next: () => {
        if (this.selectedRouteCode === routeCode) {
          this.selectedRouteCode = '';
        }
        this.refreshAll();
      }
    });
  }
}

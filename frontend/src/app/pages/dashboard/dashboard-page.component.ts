import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';

import { TrafficApiService } from '../../services/api/traffic-api.service';

/**
 * Dashboard de Análisis Avanzado de Tráfico.
 * Separado en archivos (.ts, .html, .css) para mejor estructura.
 */
@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './dashboard-page.component.html',
  styleUrls: ['./dashboard-page.component.css']
})
export class DashboardPageComponent implements OnInit {
  routeCatalog: Array<Record<string, any>> = [];
  peakHours: Array<Record<string, any>> = [];
  vehicleMix: Array<Record<string, any>> = [];
  filteredVehicleMix: Array<Record<string, any>> = [];
  
  currentStep = 0;
  totalKm = 0;
  dbConnected: boolean | null = null;

  // Configuración para el gráfico de Parque Vehicular (Dona)
  public doughnutChartType: ChartType = 'doughnut';
  public doughnutChartData: ChartData<'doughnut'> = {
    labels: ['Automóviles', 'Motocicletas', 'Transporte Pesado'],
    datasets: [{
      data: [6500, 4200, 4720],
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };
  public doughnutChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#94a3b8' } }
    }
  };

  // Configuración para el gráfico de Barras (Flujo por ruta)
  public barChartType: ChartType = 'bar';
  public barChartData: ChartData<'bar'> = {
    labels: ['CA-1', 'CA-2', 'CA-9', 'CA-13'],
    datasets: [
      { data: [4500, 3200, 5100, 1500], label: 'Volumen Actual', backgroundColor: '#3b82f6', borderRadius: 4 },
      { data: [6000, 4000, 6500, 2000], label: 'Capacidad Máx', backgroundColor: 'rgba(59, 130, 246, 0.2)', borderRadius: 4 }
    ]
  };
  public barChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
      x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
    },
    plugins: {
      legend: { position: 'top', labels: { color: '#94a3b8' } }
    }
  };

  constructor(private readonly trafficApi: TrafficApiService) {}

  ngOnInit(): void {
    this.loadCatalog();
    this.loadPeakHours();
    this.loadVehicleMix();
  }

  private loadCatalog(): void {
    this.trafficApi.getRouteCatalog().subscribe({
      next: (res) => {
        this.routeCatalog = Array.isArray(res.data) ? res.data : [];
        this.totalKm = this.routeCatalog.reduce((acc, r) => acc + Number(r['length_km'] ?? 0), 0);
        this.dbConnected = res.source === 'db';
      },
      error: () => this.dbConnected = false
    });
  }

  private loadPeakHours(): void {
    this.trafficApi.getPeakHours().subscribe({
      next: (res) => this.peakHours = Array.isArray(res.data) ? res.data : [],
      error: (err: unknown) => console.error('Error cargando horas pico', err)
    });
  }

  private loadVehicleMix(): void {
    this.trafficApi.getVehicleMix().subscribe({
      next: (res) => {
        this.vehicleMix = Array.isArray(res.data) ? res.data : [];
        this.filteredVehicleMix = [...this.vehicleMix];
      },
      error: (err: unknown) => console.error('Error cargando mix vehicular', err)
    });
  }

  setStep(step: number): void {
    this.currentStep = step;
  }

  onFilterChange(event: any): void {
    const value = event.target.value;
    if (!value) {
      this.filteredVehicleMix = [...this.vehicleMix];
    } else {
      this.filteredVehicleMix = this.vehicleMix.filter(v => v['vehicle_type'] === value);
    }
  }
}

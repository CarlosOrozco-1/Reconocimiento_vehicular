import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';

import { TrafficApiService } from '../../services/api/traffic-api.service';

/**
 * Dashboard de Análisis Avanzado de Tráfico.
 * Separado en archivos (.ts, .html, .css) para mejor estructura.
 */
@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
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

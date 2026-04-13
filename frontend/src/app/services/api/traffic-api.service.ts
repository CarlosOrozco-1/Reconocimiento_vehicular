import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class TrafficApiService {
  readonly baseUrl = environment.apiBaseUrl;

  constructor(private readonly http: HttpClient) {}

  getMainRoutes(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/routes/main`
    );
  }

  getDepartments(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/departments`
    );
  }

  getRouteDepartments(
    routeCode: string
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/${routeCode}/departments`
    );
  }

  getRouteSummary(routeCode: string): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/routes/${routeCode}/summary`
    );
  }

  getPeakHours(): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/peak-hours`
    );
  }

  routesMainUrl(): string {
    return `${this.baseUrl}/routes/main`;
  }

  peakHoursUrl(): string {
    return `${this.baseUrl}/peak-hours`;
  }

  departmentsUrl(): string {
    return `${this.baseUrl}/departments`;
  }
}

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

  getRouteCatalog(): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/catalog`
    );
  }

  getRouteDepartments(
    routeCode: string
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/${routeCode}/departments`
    );
  }

  getRouteSummary(
    routeCode: string,
    includeLive: boolean = true
  ): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/routes/${routeCode}/summary?include_live=${includeLive}`
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

  getWorkerStatus(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/monitor/worker/status`
    );
  }

  getWorkerRequests(
    minutes: number = 60,
    limit: number = 100
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/monitor/worker/requests?minutes=${minutes}&limit=${limit}`
    );
  }

  startWorker(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.post<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/monitor/worker/start`,
      {}
    );
  }

  stopWorker(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.post<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/monitor/worker/stop`,
      {}
    );
  }

  getMonitoredRoutes(
    onlyEnabled: boolean = false
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/monitor/routes?only_enabled=${onlyEnabled}`
    );
  }

  addMonitoredRoute(routeCode: string): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.post<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/monitor/routes/${encodeURIComponent(routeCode)}`,
      {}
    );
  }

  removeMonitoredRoute(
    routeCode: string
  ): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.delete<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/monitor/routes/${encodeURIComponent(routeCode)}`
    );
  }

  getRouteLiveHistory(
    routeCode: string,
    hours: number = 24,
    limit: number = 300
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/${encodeURIComponent(routeCode)}/live-history?hours=${hours}&limit=${limit}`
    );
  }
}

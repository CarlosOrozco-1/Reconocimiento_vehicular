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
}

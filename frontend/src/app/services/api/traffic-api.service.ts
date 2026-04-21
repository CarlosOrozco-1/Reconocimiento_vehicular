import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

/**
 * Servicio que encapsula todas las llamadas HTTP a la API de trafico de Guatemala.
 * La URL base se configura por entorno en environment.ts / environment.prod.ts.
 */
@Injectable({ providedIn: 'root' })
export class TrafficApiService {
  readonly baseUrl = environment.apiBaseUrl;

  constructor(private readonly http: HttpClient) {}

  /** GeoJSON con la geometria real de las rutas principales (MultiLineString por ruta). */
  getMainRoutes(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/routes/main`
    );
  }

  /** GeoJSON de los departamentos de Guatemala (capa de fondo del mapa). */
  getDepartments(): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/departments`
    );
  }

  /** Catalogo de rutas: codigo, nombre, segmentos y longitud en km. */
  getRouteCatalog(): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/catalog`
    );
  }

  /** Departamentos que atraviesa una ruta (union espacial en PostGIS). */
  getRouteDepartments(
    routeCode: string
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(
      `${this.baseUrl}/routes/${encodeURIComponent(routeCode)}/departments`
    );
  }

  /** Resumen de trafico de una ruta: flujo normal, flujo pico y hora pico. */
  getRouteSummary(
    routeCode: string
  ): Observable<{ source: string; data: Record<string, unknown> }> {
    return this.http.get<{ source: string; data: Record<string, unknown> }>(
      `${this.baseUrl}/routes/${encodeURIComponent(routeCode)}/summary`
    );
  }

  /** Horas pico por ruta con filtro opcional de fechas. */
  getPeakHours(
    fromDate?: string,
    toDate?: string
  ): Observable<{ source: string; data: Array<Record<string, unknown>> }> {
    let url = `${this.baseUrl}/peak-hours`;
    const params: string[] = [];
    if (fromDate) params.push(`from_date=${fromDate}`);
    if (toDate) params.push(`to_date=${toDate}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<{ source: string; data: Array<Record<string, unknown>> }>(url);
  }
}

import { Routes } from '@angular/router';

import { DashboardPageComponent } from './pages/dashboard/dashboard-page.component';
import { MapPageComponent } from './pages/map/map-page.component';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'map' },
  { path: 'map', component: MapPageComponent },
  { path: 'dashboard', component: DashboardPageComponent },
  { path: 'sandbox', loadComponent: () => import('./pages/sandbox/tomtom-sandbox.component').then(m => m.TomtomSandboxComponent) },
  { path: '**', redirectTo: 'map' }
];

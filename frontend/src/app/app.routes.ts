import { Routes } from '@angular/router';

import { DashboardPageComponent } from './pages/dashboard/dashboard-page.component';
import { MapPageComponent } from './pages/map/map-page.component';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'map' },
  { path: 'map', component: MapPageComponent },
  { path: 'dashboard', component: DashboardPageComponent },
  { path: '**', redirectTo: 'map' }
];

import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">Traffic Map Guatemala</div>
        <a class="nav-link" routerLink="/map" routerLinkActive="active">Mapa</a>
        <a class="nav-link" routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
      </header>
      <main class="page">
        <router-outlet />
      </main>
    </div>
  `
})
export class AppComponent {}

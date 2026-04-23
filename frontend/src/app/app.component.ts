import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">
          <span style="font-size: 2rem;" title="Traffic GT">🛣️</span>
        </div>
        <nav class="nav-links">
          <a class="nav-link" routerLink="/map" routerLinkActive="active">Mapa</a>
          <a class="nav-link" routerLink="/dashboard" routerLinkActive="active">Datos</a>
          <a class="nav-link" routerLink="/sandbox" routerLinkActive="active">Sandbox</a>
        </nav>
      </header>
      <main class="page">
        <router-outlet />
      </main>
    </div>
  `
})
export class AppComponent {}

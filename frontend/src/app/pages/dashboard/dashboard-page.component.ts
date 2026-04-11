import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel">
      <h2>Dashboard de trafico</h2>
      <p>Aqui se mostraran horas pico, volumen por ruta y ranking por segmento.</p>

      <table>
        <thead>
          <tr>
            <th>Ruta</th>
            <th>Hora pico</th>
            <th>Vehiculos/h</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let item of mockRows">
            <td>{{ item.route }}</td>
            <td>{{ item.peakHour }}</td>
            <td>{{ item.flow }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  `,
  styles: [
    `
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th,
      td {
        text-align: left;
        border-bottom: 1px solid #1f2937;
        padding: 10px;
      }
      th {
        color: #9ca3af;
      }
    `
  ]
})
export class DashboardPageComponent {
  readonly mockRows = [
    { route: 'CA-1 Occidente', peakHour: '07:00-08:00', flow: 0 },
    { route: 'CA-9 Sur', peakHour: '17:00-18:00', flow: 0 },
    { route: 'CA-2', peakHour: '12:00-13:00', flow: 0 }
  ];
}

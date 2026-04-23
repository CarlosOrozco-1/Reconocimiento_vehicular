# Reglas de Desarrollo para Agentes AI

Este documento contiene las reglas obligatorias para el desarrollo en este repositorio. Cualquier agente que trabaje aquí debe seguir estas directrices.

## 1. Arquitectura Angular
- **Separación de Responsabilidades**: Todo componente de Angular debe estar separado en sus tres archivos fundamentales:
  - `[nombre].component.ts`: Lógica del componente.
  - `[nombre].component.html`: Estructura HTML.
  - `[nombre].component.css`: Estilos específicos.
- **Standalone Components**: Se prefiere el uso de componentes `standalone: true` para mantener la modularidad.

## 2. Estética y Diseño
- **Premium UI**: Se debe mantener una estética oscura (Dark Mode), con efectos de *glassmorphism* (cristal), tipografía moderna (Outfit/Inter) y acentos vibrantes (Sky Blue/Amber).
- **Consistencia**: Las tarjetas, botones y tablas deben seguir el diseño definido en `styles.css`.

## 3. Manejo de Datos
- **Tipado**: Evitar el uso de `any` siempre que sea posible. Usar interfaces o tipos de TypeScript.
- **Backend First**: Priorizar el uso de datos reales desde la base de datos PostgreSQL/PostGIS.

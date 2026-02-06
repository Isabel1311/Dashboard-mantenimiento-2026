# 🏗️ BBVA Conservación NE — Centro de Análisis

Plataforma de análisis de órdenes de mantenimiento para la Región Noreste de BBVA Conservación.

## Características

- **Dashboard General**: KPIs ejecutivos, distribución por estatus, tipo de orden, zonas, especialidades e importes
- **Análisis por Proveedor**: Rendimiento individual, comparativa general, evolución mensual y supervisores asociados
- **Análisis por Supervisor**: Carga de trabajo, zonas asignadas, sucursales, heatmap supervisor×zona
- **Filtros dinámicos**: Por tipo de orden, estatus, supervisor, zona, proveedor, fecha y tipo de banca
- **Vinculación automática**: Enlace Centro de Coste → CR → Supervisor (Sheet2 del archivo BP)
- **Exportación CSV** de datos filtrados

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Selecciona `app.py` como archivo principal
5. Deploy

## Estructura del archivo BP esperado

| Hoja | Contenido |
|------|-----------|
| Sheet1 | Órdenes de mantenimiento (SAP) con 31 columnas |
| Sheet2 | Catálogo de sucursales con CR, Sucursal, Tipo de Banca, DZ y Supervisor |

La vinculación se realiza extrayendo el número del **Centro de Coste** (`MX11XXXXXX` → `XXXXXX`) y empatando con el campo **CR** de la Sheet2.

---

Desarrollado para la Dirección de Administración y Operaciones · BBVA Conservación Región Noreste

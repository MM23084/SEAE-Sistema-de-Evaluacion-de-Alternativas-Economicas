# ⟨SEAE⟩ — Sistema de Evaluación de Alternativas Económicas

> Herramienta de escritorio desarrollada en Python para evaluar y comparar alternativas económicas mediante los métodos **VPN**, **CAE** y **TIR**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Tkinter](https://img.shields.io/badge/Interfaz-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/Licencia-Académica-lightgrey?style=flat-square)
![UES](https://img.shields.io/badge/UES-Ciclo%20I%2F2026-red?style=flat-square)

---

##  Descripción

**SEAE** es un sistema de escritorio desarrollado como proyecto del Ciclo I/2026 para la materia de **Ingeniería de Negocios** de la Universidad de El Salvador. Permite evaluar proyectos de inversión a través de tres métodos financieros clásicos, comparar alternativas y exportar reportes.

---

##  Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| **VPN** | Calcula el Valor Presente Neto con flujos variables y valor de salvamento |
| **CAE** | Convierte el VPN en un flujo anual uniforme para comparar proyectos de distinta vida |
| **TIR** | Encuentra la Tasa Interna de Retorno mediante bisección numérica |
| **Comparar** | Compara dos alternativas guardadas y emite un veredicto automático |
| **Reporte** | Exporta los resultados en formato **TXT** o **CSV** con portada del equipo |

---

## Requisitos

- Python **3.8 o superior**
- No requiere instalar librerías externas — usa únicamente módulos incluidos con Python:
  - `tkinter`
  - `math`
  - `datetime`

---

## Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/SEAE-Evaluacion-Economica.git
cd SEAE-Evaluacion-Economica
```

### 2. Verificar que Python esté instalado
```bash
python --version
```
Debe mostrar `Python 3.8.x` o superior.

### 3. Ejecutar el sistema
```bash
python SEAE.py
```

> También puedes abrir el archivo en **Visual Studio Code** y presionar `F5` o el botón ▶ para ejecutarlo directamente.

---

##  Cómo usar el sistema

1. **Selecciona un método** desde el menú lateral (VPN, CAE o TIR)
2. **Ingresa los datos** del proyecto — usa números limpios sin símbolos (`50000` en lugar de `$50,000`)
3. **Presiona Calcular** para obtener el resultado y la decisión automática
4. **Guarda como Alternativa 1 o 2** para habilitar la comparación
5. Ve a **Comparar Alternativas** para ver el veredicto entre ambas opciones
6. Ve a **Generar Reporte** para exportar los resultados a TXT o CSV

---

## Métodos implementados

**Valor Presente Neto (VPN)**
```
VPN = -P + F1/(1+i)^1 + F2/(1+i)^2 + ... + Fn/(1+i)^n
```
Aceptar si VPN > 0

**Costo Anual Equivalente (CAE)**
```
CAE = VPN × [ i(1+i)^n / ((1+i)^n - 1) ]
```
Aceptar si CAE > 0

**Tasa Interna de Retorno (TIR)**
```
0 = -P + F1/(1+TIR)^1 + F2/(1+TIR)^2 + ... + Fn/(1+TIR)^n
```
Calculada mediante bisección numérica con precisión de 1×10⁻⁷

Aceptar si TIR ≥ TMAR

---

## Equipo

| Nombre | Carnet |
|--------|--------|
| Ricardo Antonio Mora Morales   | MM23084 |
| Diana Vanessa Zepeda Posadas   | 000000 |
| Jennifer Lisbeth Reyes Pleitez | 000000 |
| Ana Esmeralda Trejo Zepeda     | 000000 |
| Kevin Gerardo Martínez Guillén | 000000 |
| Ronald Osvaldo Manzano Deleón  | 000000 |


---

## Información académica

| Campo | Detalle |
|-------|---------|
| Universidad | Universidad de El Salvador |
| Facultad | Multidisciplinaria de Occidente |
| Departamento | Ingeniería y Arquitectura |
| Carrera | Ingeniería en Desarrollo de Software |
| Materia | Ingeniería de Negocios |
| Ciclo | I / 2026 |
| Docente | Ing. Clara Rojas |

---

<p align="center">
  Desarrollado con 🐍 Python · UES Ciclo I/2026
</p>

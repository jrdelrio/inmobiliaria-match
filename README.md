# 🏢 Inmobiliaria Matching – Comparador de Promesas y Certificados

Este proyecto automatiza la verificación de documentos relacionados a la compraventa de propiedades. A partir de dos carpetas —una con **promesas de compraventa** y otra con **certificados de crédito hipotecario**— el sistema:

1. Extrae información clave desde los archivos PDF.
2. Compara los datos de ambos documentos.
3. Genera un informe en Excel resaltando inconsistencias.

---

## 📂 Estructura del Proyecto

```
inmobiliaria-match/
├── main.py
├── requirements.txt
├── .env
├── src/
│   ├── gui.py              # Interfaz gráfica con Tkinter
│   ├── extractor.py        # Procesa texto con OpenAI
│   ├── matcher.py          # Compara datos de promesas y certificados
│   ├── reporter.py         # Genera Excel con resultados
│   ├── utils.py            # OCR, normalización de texto
├── reports/                # Carpeta de salida para los reportes generados
```

---

## 🖥️ Requisitos del sistema

* Python 3.12+ (con soporte para `tkinter`)
* Dependencias definidas en `requirements.txt`
* API Key de OpenAI (almacenada en `.env`)

---

## 🔌 Instalación

```bash
# Clona el repositorio y entra al proyecto
cd inmobiliaria-match

# Crea entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instala dependencias
pip install -r requirements.txt
```

---

## 🔐 Configuración del entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## ▶️ Uso

```bash
python main.py
```

Se abrirá una interfaz gráfica donde podrás seleccionar:

* Carpeta de certificados
* Carpeta de promesas
* Botón "Ejecutar Comparación"

El sistema analizará y generará un reporte Excel dentro de `reports/`.

---

## 📊 Estructura del reporte Excel

Cada fila representa un match entre promesa y certificado.

Colores:

* 🟩 **Verde**: todos los datos coinciden.
* 🟧 **Naranja**: hay diferencias entre campos (ej. RUT o monto).
* 🔵 **Rojo**: falta certificado correspondiente.

---

## 🧠 Uso de OpenAI API

Este proyecto utiliza la API de OpenAI para analizar documentos PDF complejos de múltiples bancos. Se utiliza el modelo `gpt-4o` para convertir texto en JSON estructurado.

### 📌 ¿Por qué usar la API?

Dado que cada certificado tiene su propia plantilla (según el banco), el análisis tradicional con expresiones regulares es poco confiable. Por eso, cada archivo PDF es convertido a texto y enviado a un LLM para extracción precisa de:

* Nombre
* RUT
* Departamento
* Monto del crédito
* Fecha de emisión

---

## 💵 Costos asociados al uso de la API

OpenAI cobra por token procesado. Los precios para `gpt-4o` son los siguientes:

| Modelo | Input (prompt)         | Output (respuesta)     |
| ------ | ---------------------- | ---------------------- |
| gpt-4o | \$0.005 / 1,000 tokens | \$0.015 / 1,000 tokens |

### 📄 ¿Cuántos tokens usa un PDF?

* Un PDF de 1 página puede tener entre **800 y 2,000 tokens**.
* Archivos escaneados con OCR tienden a ser más ruidosos y largos.

### 📊 Ejemplo de costos

* 1 documento de 1.500 tokens input + 300 output ≈ 1.800 tokens.
* Costo ≈ \$0.005 × 1.5 + \$0.015 × 0.3 ≈ **\$0.009**

| PDFs procesados por día | Tokens promedio  | Costo diario estimado |
| ----------------------- | ---------------- | --------------------- |
| 10 PDFs                 | 1,800 tokens c/u | \$0.09                |
| 100 PDFs                | 1,800 tokens c/u | \$0.90                |
| 500 PDFs                | 1,800 tokens c/u | \$4.50                |

> **Nota**: los costos reales dependen del contenido y tamaño del documento.

---

## 🚀 Futuras mejoras

* [ ] Cachear respuestas de la API para evitar costos duplicados.
* [ ] Barra de progreso en la GUI.
* [ ] Validación visual antes de ejecutar.
* [ ] Exportación también en CSV.
* [ ] Versión web con Streamlit o FastAPI.

---

## 🧑‍💻 Desarrollado por

[🌶️chilisites](https://chilisites.com)

> Proyecto: `inmobiliaria-matching`
> Lenguaje: Python + Tkinter + OpenAI API
> IA utilizada: GPT-4o

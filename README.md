# Convertidor de Imagen a PDF - Azure Function

Este proyecto proporciona un endpoint HTTP serverless, construido como una Azure Function, para convertir uno o más archivos de imagen en un único documento PDF. Incluye autenticación con token "bearer" para un acceso seguro.

## Características

- Convierte múltiples imágenes (JPG, PNG, etc.) en un solo PDF.
- Endpoint seguro con autenticación de token "bearer".
- Acepta `multipart/form-data` para una carga de archivos sencilla.
- Maneja errores de conversión comunes de forma elegante (ej. PDF demasiado grande, imágenes con canal alfa).
- Genera un nombre de archivo significativo para el PDF de salida.

## Prerrequisitos

- Python 3.9+
- Azure Functions Core Tools
- Una cuenta de Azure (para el despliegue)

## Configuración

Esta función requiere una variable de entorno para la autenticación.

- **`EXPECTED_BEARER_TOKEN`**: El token "bearer" secreto que los clientes deben proporcionar para usar la API. Elija una cadena fuerte y difícil de adivinar.

## Desarrollo y Ejecución Local

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd img2pdf
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .\.venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tus variables de entorno locales:**
    Crea un archivo llamado `local.settings.json` en la raíz del proyecto con el siguiente contenido:

    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "EXPECTED_BEARER_TOKEN": "TU_TOKEN_SUPER_SECRETO_AQUI"
      }
    }
    ```
    Reemplaza `TU_TOKEN_SUPER_SECRETO_AQUI` con el token que desees usar para las pruebas locales.

5.  **Inicia la función:**
    ```bash
    func start
    ```
    La función estará disponible en `http://localhost:7071/api/img2pdf`.

## Despliegue

Esta función está lista para ser desplegada en una Azure Function App. Después del despliegue, asegúrate de configurar el `EXPECTED_BEARER_TOKEN` en la sección de **Configuración > Configuración de la aplicación** de tu Function App en el portal de Azure.

## Uso / API

- **Endpoint:** `POST /api/img2pdf`
- **Autenticación:** Se requiere un encabezado `Authorization`.
  - `Authorization: Bearer TU_TOKEN_SUPER_SECRETO_AQUI`
- **Cuerpo de la Petición:** `multipart/form-data`
  - Adjunta uno o más archivos de imagen. El nombre del campo no importa (ej. `file1`, `image_a`, etc.).

### Ejemplo con `curl`

```bash
curl -X POST "http://localhost:7071/api/img2pdf" \
-H "Authorization: Bearer TU_TOKEN_SUPER_SECRETO_AQUI" \
-F "image1=@/ruta/a/tu/primera_imagen.jpg" \
-F "image2=@/ruta/a/tu/segunda_imagen.png" \
--output resultado.pdf
```

Este comando enviará dos imágenes a la función y guardará el PDF resultante como `resultado.pdf`.

## Dependencias Principales

- `azure-functions`: Para el modelo de programación de Azure Functions.
- `img2pdf`: La biblioteca principal para la conversión de imágenes a PDF.
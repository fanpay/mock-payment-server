# mock-payment-server

Servidor mock HTTP local para endpoints de Payment Gateway Experience API.

## Requisitos

- Python 3.10+

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar servidor (puerto 4010)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4010
```

## Despliegue en Netlify

El proyecto incluye una función Python en `netlify/functions/mock_payment_server.py` y un redirect en `netlify.toml` para que Netlify envíe todas las rutas a esa función.

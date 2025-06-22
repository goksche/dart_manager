# Dart Manager

This project is a simple API for managing dart tournaments using FastAPI.

## Updating Dependencies

The `requirements.txt` file pins versions for the core packages used by the
application. When new releases become available you can update them with the
following steps:

1. Check which versions are published:

   ```bash
   pip index versions fastapi | head -n 2
   pip index versions uvicorn | head -n 2
   pip index versions sqlmodel | head -n 2
   ```

2. Pick compatible versions (typically the latest) and edit `requirements.txt`
   to replace the existing version numbers.
3. Reinstall dependencies and ensure the application still runs as expected:

   ```bash
   pip install -r requirements.txt
   ```

Committing the updated `requirements.txt` keeps everyone on the same package
versions.

## License

This project is licensed under the terms of the [MIT License](LICENSE).

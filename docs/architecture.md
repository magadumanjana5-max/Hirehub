# HireHub Architecture

The application follows a Flask application factory pattern with blueprints for web and API routes. The flow is:

Routes -> Services -> Repositories -> Storage

Web routes handle HTTP requests and page rendering, while API blueprints expose JSON endpoints. Services contain domain-specific logic, repositories encapsulate storage access, and the in-memory datastore supports lightweight local development.

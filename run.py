from app import create_app
from app.config import config
from app.utils.watchdog_service import init_watchdog

if __name__ == "__main__":
    init_watchdog()
    app = create_app()
    app.run(debug=config.DEBUG, use_reloader=False, port=config.PORT)
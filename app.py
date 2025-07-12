
import os
import sys
from flask_migrate import Migrate

from config import config_dict
from __init__ import create_app, db

# Get configuration mode from environment or default to Production
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    print('Error: Invalid <config_mode>. Expected values [Debug, Production]')
    sys.exit(1)

app = create_app(app_config)
Migrate(app, db)

if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

# For Render deployment
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
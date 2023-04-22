from handlers import client
# Сначала более специфичные хэндлеры
from handlers.buttons_handlers import report_handlers
from handlers.buttons_handlers import settings_handlers
from handlers.buttons_handlers import income_spend_handlers
# Потом менее
from handlers import text_handlers
from handlers.models import income_spend_model

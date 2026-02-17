
"""
Sistema de Gestión de Conversaciones para TARS (modularizado)
"""

# Import modularized components
from conversation_manager.manager import *
from conversation_manager.db import *
from conversation_manager.search import *
from conversation_manager.summaries import *
from conversation_manager.graph import *
from conversation_manager.utils import *

# This file now delegates all logic to submodules.
# See conversation_manager/manager.py, db.py, search.py, summaries.py, graph.py, utils.py for implementation.

"""
Nodos del StateGraph - Cada nodo maneja una parte del flujo conversacional
"""

# Importar todos los nodos (se agregarán conforme los creemos)
from nodes.receive_message import receive_message_node
from nodes.extract_filters import extract_filters_node
from nodes.check_completion import check_completion_node,route_after_check_completion
from nodes.ask_missing_filter import ask_missing_filter_node
from nodes.ask_additional import ask_additional_filters_node
from nodes.collect_optional import collect_optional_filters_node,route_after_collect_optional
from nodes.generate_sql import generate_sql_node
from nodes.validate_sql import validate_sql_node,route_after_validate_sql
from nodes.execute_sql import execute_sql_node
from nodes.format_results import format_results_node

__all__ = [
    'receive_message_node',
    'extract_filters_node',
    'check_completion_node',
    'route_after_check_completion',
    'ask_missing_filter_node',
    'ask_additional_filters_node',
    'collect_optional_filters_node',
    'route_after_collect_optional',
    'generate_sql_node',
    'validate_sql_node',
    'route_after_validate_sql',
    'execute_sql_node',
    'format_results_node',
]
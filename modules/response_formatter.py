"""
Response formatting utilities for Genie API responses
"""
from typing import Dict


class ResponseFormatter:
    """Formats Genie API responses into user-friendly output"""
    
    @staticmethod
    def process_query_results(answer_json: Dict) -> str:
        """Process and format the query results from Genie"""
        from .config import Config
        
        response = ""
        
        if "columns" in answer_json and "data" in answer_json:
            columns = answer_json["columns"]
            data = answer_json["data"]
            
            if isinstance(columns, dict) and "columns" in columns:
                # Create table header
                header = "| " + " | ".join(col["name"] for col in columns["columns"]) + " |"
                separator = "|" + "|".join(["-----" for _ in columns["columns"]]) + "|"
                response += header + "\n" + separator + "\n"
                
                # Add data rows
                row_count = 0
                max_rows = Config.MAX_DISPLAY_ROWS  # Use config value
                
                for row in data["data_array"]:
                    if row_count >= max_rows:
                        break
                        
                    formatted_row = []
                    for value, col in zip(row, columns["columns"]):
                        if value is None:
                            formatted_value = "NULL"
                        elif col["type_name"] in ["DECIMAL", "DOUBLE", "FLOAT"]:
                            formatted_value = f"{float(value):,.2f}"
                        elif col["type_name"] in ["INT", "BIGINT", "LONG"]:
                            formatted_value = f"{int(value):,}"
                        else:
                            formatted_value = str(value)
                        formatted_row.append(formatted_value)
                    
                    response += "| " + " | ".join(formatted_row) + " |\n"
                    row_count += 1
                
                # Only show truncation message if there are more rows
                total_rows = len(data["data_array"])
                if total_rows > max_rows:
                    response += f"\n*Mostrando {max_rows} de {total_rows} linhas*\n"
                    
            else:
                response += f"Formato de coluna inesperado: {columns}\n\n"
                
        elif "message" in answer_json:
            response += f"{answer_json['message']}"
        elif "error" in answer_json:
            response += f"❌ **Erro:** {answer_json['error']}"
        else:
            response += "⚠️ Nenhum dado disponível."
        
        return response

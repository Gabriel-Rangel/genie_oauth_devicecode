"""
Databricks Genie API client and utilities
"""
import os
import json
import asyncio
import logging
from typing import Optional, Dict, Tuple
import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

logger = logging.getLogger(__name__)


class GenieClient:
    """Handles Databricks Genie API interactions"""
    
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.workspace_client = None
        self.genie_api = None
        self.space_id = os.getenv("GENIE_SPACE_ID")
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize workspace and Genie clients"""
        try:
            self.workspace_client = WorkspaceClient(
                host=os.getenv("DATABRICKS_HOST"),
                token=self.oauth_token
            )
            
            # Store workspace client in session state for async functions
            st.session_state.workspace_client = self.workspace_client
            
            self.genie_api = GenieAPI(self.workspace_client.api_client)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Genie client: {str(e)}")
            st.error(f"Failed to initialize Genie client: {str(e)}")
            return False
    
    async def ask_genie_async(self, question: str, conversation_id: Optional[str] = None) -> Tuple[str, str]:
        """Async function to ask Genie and get structured response"""
        try:
            loop = asyncio.get_running_loop()
            
            if not self.workspace_client or not self.genie_api:
                return json.dumps({"error": "Workspace client not initialized"}), conversation_id
            
            if conversation_id is None:
                initial_message = await loop.run_in_executor(
                    None, self.genie_api.start_conversation_and_wait, self.space_id, question
                )
                conversation_id = initial_message.conversation_id
            else:
                initial_message = await loop.run_in_executor(
                    None, self.genie_api.create_message_and_wait, self.space_id, conversation_id, question
                )

            query_result = None
            if initial_message.query_result is not None:
                query_result = await loop.run_in_executor(
                    None, self.genie_api.get_message_query_result,
                    self.space_id, initial_message.conversation_id, initial_message.id
                )

            message_content = await loop.run_in_executor(
                None, self.genie_api.get_message,
                self.space_id, initial_message.conversation_id, initial_message.id
            )

            if query_result and query_result.statement_response:
                results = await loop.run_in_executor(
                    None, self.workspace_client.statement_execution.get_statement,
                    query_result.statement_response.statement_id
                )
                
                query_description = ""
                for attachment in message_content.attachments:
                    if attachment.query and attachment.query.description:
                        query_description = attachment.query.description
                        break

                return json.dumps({
                    "columns": results.manifest.schema.as_dict(),
                    "data": results.result.as_dict(),
                    "query_description": query_description
                }), conversation_id

            if message_content.attachments:
                for attachment in message_content.attachments:
                    if attachment.text and attachment.text.content:
                        return json.dumps({"message": attachment.text.content}), conversation_id

            return json.dumps({"message": message_content.content}), conversation_id
        except Exception as e:
            logger.error(f"Error in ask_genie: {str(e)}")
            return json.dumps({"error": "An error occurred while processing your request."}), conversation_id
    
    def ask_genie(self, question: str, max_wait_time: int = 60) -> Dict:
        """Synchronous wrapper for the async ask_genie function"""
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("🧞 Iniciando conversa com Genie...")
            progress_bar.progress(0.1)
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                status_text.text("🤖 Processando consulta...")
                progress_bar.progress(0.5)
                
                answer_json_str, conversation_id = loop.run_until_complete(
                    self.ask_genie_async(question)
                )
                
                progress_bar.progress(0.9)
                status_text.text("✅ Formatando resposta...")
                
                # Parse the JSON response
                answer_json = json.loads(answer_json_str)
                
                progress_bar.progress(1.0)
                status_text.text("✅ Concluído!")
                
                progress_bar.empty()
                status_text.empty()
                
                return {
                    "success": True,
                    "response": answer_json,
                    "conversation_id": conversation_id,
                    "raw_data": answer_json
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
                
            logger.error(f"Error in ask_genie wrapper: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao processar solicitação: {str(e)}"
            }

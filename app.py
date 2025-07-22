"""
Genie AI Chatbot - Main Application
A modular Streamlit chatbot for interacting with Databricks Genie API
"""
import streamlit as st
import logging
from dotenv import load_dotenv

# Import custom modules
from modules.auth_handler import AzureAuthHandler
from modules.genie_client import GenieClient
from modules.response_formatter import ResponseFormatter
from modules.ui_components import UIComponents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GenieChatbot:
    """Main chatbot application class"""
    
    def __init__(self):
        self.auth_handler = AzureAuthHandler()
        self.ui = UIComponents()
        self.formatter = ResponseFormatter()
        self.genie_client = None
        
        # Initialize page configuration
        st.set_page_config(
            page_title="🤖 Genie AI Chatbot",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "👋 Olá! Pergunte para AI/BI Databricks Genie! Pergunte para sua base de dados."
                }
            ]
    
    def initialize_genie_client(self):
        """Initialize the Genie client if authenticated"""
        if st.session_state.authenticated and "genie_client" not in st.session_state:
            self.genie_client = GenieClient(st.session_state.oauth_token)
            st.session_state.genie_client = self.genie_client
        elif "genie_client" in st.session_state:
            self.genie_client = st.session_state.genie_client
    
    def display_chat_messages(self):
        """Display all chat messages"""
        for message in st.session_state.messages:
            if message["role"] == "user":
                self.ui.render_user_message(message["content"])
            else:
                self.ui.render_bot_message(message["content"])
    
    def handle_user_input(self, user_input: str):
        """Process user input and generate response"""
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        self.ui.render_user_message(user_input)
        
        # Check if Genie client is available
        if not self.genie_client or not hasattr(self.genie_client, 'genie_api'):
            error_msg = "❌ Genie client not available. Please check your configuration."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            self.ui.render_error_message(error_msg)
            return
        
        # Get response from Genie
        response = self.genie_client.ask_genie(user_input)
        
        if response.get("success"):
            # Format the response using the formatter
            formatted_response = self.formatter.process_query_results(response["response"])
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})
            self.ui.render_bot_message(formatted_response)
        else:
            error_msg = f"❌ **Erro:** {response.get('error', 'Erro desconhecido')}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            self.ui.render_error_message(error_msg)
    
    def run_chat_interface(self):
        """Run the main chat interface"""
        # Apply styling
        self.ui.apply_dark_theme()
        
        # Render header
        self.ui.render_header()
        
        # Show welcome message on first load
        if "welcome_shown" not in st.session_state:
            st.success("✅ Authorization was successful! Welcome to Genie AI Chatbot.")
            st.session_state.welcome_shown = True
        
        # Render sidebar
        self.ui.render_sidebar()
        
        # Initialize Genie client
        self.initialize_genie_client()
        
        # Display chat messages
        self.display_chat_messages()
        
        # Chat input
        user_input = st.chat_input("Ask me about your data...")
        
        # Handle input from sidebar buttons
        if "user_input" in st.session_state:
            user_input = st.session_state.user_input
            del st.session_state.user_input
        
        # Process user input
        if user_input:
            self.handle_user_input(user_input)
            st.rerun()
        
        # Render footer
        self.ui.render_footer()
    
    def run(self):
        """Main application entry point"""
        # Initialize session state
        self.initialize_session_state()
        
        # Show authentication page if not authenticated
        if not st.session_state.authenticated:
            self.ui.apply_dark_theme()
            self.auth_handler.handle_oauth_flow()
            return
        
        # Run main chat interface
        self.run_chat_interface()


def main():
    """Application entry point"""
    app = GenieChatbot()
    app.run()


if __name__ == "__main__":
    main()

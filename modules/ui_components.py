"""
UI components and styling for the Genie chatbot
"""
import streamlit as st


class UIComponents:
    """Handles UI components and styling"""
    
    @staticmethod
    def apply_dark_theme():
        """Apply dark theme CSS styling"""
        st.markdown("""
        <style>
            /* Dark theme styles */
            .stApp {
                background-color: #0e1117;
                color: #ffffff;
            }
            
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #00d4ff;
                text-align: center;
                margin-bottom: 2rem;
                text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
            }
            
            .chat-message {
                padding: 1rem;
                border-radius: 0.8rem;
                margin: 1rem 0;
                display: flex;
                align-items: flex-start;
                gap: 0.5rem;
                color: #ffffff;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            }
            
            .user-message {
                background: linear-gradient(135deg, #1a365d 0%, #2a4a6b 100%);
                border-left: 4px solid #00d4ff;
                color: #ffffff;
            }
            
            .bot-message {
                background: linear-gradient(135deg, #2d1b4e 0%, #3d2a5c 100%);
                border-left: 4px solid #9c27b0;
                color: #ffffff;
            }
            
            .error-message {
                background: linear-gradient(135deg, #4a1a1a 0%, #5a2a2a 100%);
                border-left: 4px solid #ff4444;
                color: #ffffff;
            }
            
            .success-message {
                background: linear-gradient(135deg, #1a4a1a 0%, #2a5a2a 100%);
                border-left: 4px solid #4caf50;
                color: #ffffff;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background-color: #1a1a1a;
            }
            
            /* Text color fixes for dark theme */
            .stMarkdown, .stText, p, div, span {
                color: #ffffff !important;
            }
            
            /* Button styling */
            .stButton > button {
                background-color: #2a4a6b;
                color: #ffffff;
                border: 1px solid #00d4ff;
                border-radius: 0.5rem;
            }
            
            .stButton > button:hover {
                background-color: #3a5a7b;
                border-color: #20e4ff;
            }
            
            /* Chat input styling */
            .stChatInput > div > div > input {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
            }
            
            /* Info box styling */
            .stInfo {
                background-color: rgba(0, 212, 255, 0.1);
                border: 1px solid #00d4ff;
                color: #ffffff;
            }
            
            /* Login page styling */
            .login-container {
                max-width: 600px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(135deg, #1a2332 0%, #2a3442 100%);
                border-radius: 1rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            }
            
            .login-header {
                text-align: center;
                color: #00d4ff;
                font-size: 2rem;
                margin-bottom: 1.5rem;
                text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
            }
            
            .step-indicator {
                background: linear-gradient(135deg, #2d1b4e 0%, #3d2a5c 100%);
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                border-left: 4px solid #9c27b0;
            }
            
            .auth-code {
                background-color: #2a2a2a;
                padding: 1.5rem;
                border-radius: 0.5rem;
                font-family: monospace;
                font-size: 1.8rem;
                text-align: center;
                color: #00d4ff;
                border: 2px solid #00d4ff;
                margin: 1rem 0;
                letter-spacing: 4px;
                font-weight: bold;
            }
            
            .success-container {
                background: linear-gradient(135deg, #1a4a1a 0%, #2a5a2a 100%);
                padding: 2rem;
                border-radius: 1rem;
                border-left: 4px solid #4caf50;
                text-align: center;
                margin: 2rem 0;
            }
            
            .user-info {
                background-color: #2a2a2a;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
                border-left: 4px solid #00d4ff;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Render the main header with logout button"""
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<div class="main-header">🤖 Genie AI Chatbot</div>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 Logout", key="logout_btn"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    @staticmethod
    def render_sidebar():
        """Render the sidebar with sample questions"""
        from .config import Config
        
        with st.sidebar:
            st.header("💡 Perguntas de Exemplo")
            for question in Config.SAMPLE_QUESTIONS:
                if st.button(question, key=f"sample_{question}", use_container_width=True):
                    st.session_state.user_input = question
                    st.rerun()
    
    @staticmethod
    def render_user_message(content: str):
        """Render a user message"""
        st.markdown(f'''
            <div class="chat-message user-message">
                <strong>🧑‍💻 You:</strong> {content}
            </div>
        ''', unsafe_allow_html=True)
    
    @staticmethod
    def render_bot_message(content: str):
        """Render a bot message with proper markdown support"""
        with st.container():
            st.markdown("**🤖 Genie:**")
            st.markdown(content)
    
    @staticmethod
    def render_error_message(content: str):
        """Render an error message"""
        with st.container():
            st.markdown("**🤖 Genie:**")
            st.error(content)
    
    @staticmethod
    def render_footer():
        """Render the footer"""
        st.markdown("---")
        st.markdown("*Powered by Databricks Genie API and Streamlit*")

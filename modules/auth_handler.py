"""
Authentication handler for Azure OAuth2 device code flow
"""
import os
import time
import requests
import streamlit as st
from typing import Dict, Optional


class AzureAuthHandler:
    """Handles Azure OAuth2 device code flow authentication"""
    
    def __init__(self):
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.scope = os.getenv("SCOPE", "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default https://graph.microsoft.com/User.Read")
    
    def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Microsoft Graph API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'name': user_data.get('displayName', 'User'),
                    'email': user_data.get('mail') or user_data.get('userPrincipalName', 'user@example.com'),
                    'success': True
                }
            else:
                # If Graph API fails, return default user info
                return {
                    'name': 'Authenticated User',
                    'email': 'user@authenticated.com',
                    'success': True
                }
        except Exception as e:
            # If Graph API fails, return default user info
            return {
                'name': 'Authenticated User', 
                'email': 'user@authenticated.com',
                'success': True
            }
    
    def start_device_code_flow(self) -> Optional[Dict]:
        """Start the device code flow and get the device code"""
        try:
            device_code_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/devicecode"
            device_code_data = {
                'client_id': self.client_id,
                'scope': self.scope
            }
            
            response = requests.post(device_code_url, data=device_code_data)
            device_code_response = response.json()
            
            if 'error' in device_code_response:
                st.error(f"❌ Error: {device_code_response.get('error_description', 'Unknown error')}")
                return None
            
            return device_code_response
        except Exception as e:
            st.error(f"❌ Error starting authentication: {str(e)}")
            return None
    
    def check_device_code_status(self, device_code: str) -> Optional[Dict]:
        """Check the status of device code authentication"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            token_data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'client_id': self.client_id,
                'device_code': device_code
            }
            
            response = requests.post(token_url, data=token_data)
            return response.json()
        except Exception as e:
            st.error(f"❌ Error checking authentication: {str(e)}")
            return None
    
    def handle_oauth_flow(self) -> bool:
        """Handle the complete OAuth authentication flow in the UI"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">🔐 Sign in to Genie AI</div>', unsafe_allow_html=True)
        
        # Step 1: Start Authentication
        if "auth_step" not in st.session_state:
            st.markdown("""
            <div class="step-indicator">
                <strong>Step 1:</strong> Clique para iniciar a autenticação
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Iniciar Autenticação", use_container_width=True, type="primary", key="start_auth"):
                device_code_response = self.start_device_code_flow()
                if device_code_response:
                    # Store device code info in session state
                    st.session_state.device_code = device_code_response['device_code']
                    st.session_state.user_code = device_code_response['user_code']
                    st.session_state.verification_uri = device_code_response['verification_uri']
                    st.session_state.expires_in = device_code_response['expires_in']
                    st.session_state.interval = device_code_response['interval']
                    st.session_state.auth_step = "show_code"
                    st.rerun()
        
        # Step 2: Show Code and Redirect
        elif st.session_state.auth_step == "show_code":
            st.markdown("""
            <div class="step-indicator">
                <strong>Step 2:</strong> Copie o código e faça login
            </div>
            """, unsafe_allow_html=True)
            
            # Display the user code prominently
            st.markdown(f'''
            <div class="auth-code">
                {st.session_state.user_code}
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("**Instruções:** Copie o código acima, então clique no botão vermelho para fazer login.")

            col1, col2 = st.columns(2)
            
            with col1:
                # Use link_button to properly open the Microsoft login page
                st.link_button("🌐 Go to Microsoft Login", "https://microsoft.com/devicelogin", use_container_width=True, type="primary")
                
                # Simplified: After opening link, show completion button immediately
                if st.button("✅ I've Completed Authentication", use_container_width=True, key="check_auth", type="primary"):
                    st.session_state.checking_auth = True
                    st.rerun()
            
            with col2:
                if st.button("🔄 Start Over", use_container_width=True, key="restart_auth"):
                    # Clear all auth session state
                    for key in ['auth_step', 'device_code', 'user_code', 'verification_uri', 'checking_auth']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            # Check authentication status
            if st.session_state.get("checking_auth"):
                with st.spinner("🔍 Verifying authentication..."):
                    token_response = self.check_device_code_status(st.session_state.device_code)
                    
                    if token_response and 'access_token' in token_response:
                        # Get user information (with fallback)
                        user_info = self.get_user_info(token_response['access_token'])
                        
                        # Always proceed since we have fallback user info
                        st.session_state.oauth_token = token_response['access_token']
                        st.session_state.user_name = user_info['name']
                        st.session_state.user_email = user_info['email']
                        st.session_state.authenticated = True
                        st.session_state.checking_auth = False
                        
                        # Clear temporary auth state
                        for key in ['auth_step', 'device_code', 'user_code', 'verification_uri']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        # Show brief success message
                        st.success("✅ Autorização bem-sucedida! Redirecionando para o chatbot...")
                        time.sleep(1)
                        st.rerun()
                        
                    elif token_response and token_response.get('error') == 'authorization_pending':
                        st.warning("⏳ Autenticação ainda está pendente. Por favor, complete o processo de login e tente novamente.")
                        st.session_state.checking_auth = False
                        
                    elif token_response and token_response.get('error') == 'authorization_declined':
                        st.error("❌ Autenticação foi recusada. Por favor, comece novamente.")
                        # Clear auth session state
                        for key in ['auth_step', 'device_code', 'user_code', 'verification_uri', 'checking_auth']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                    elif token_response and token_response.get('error') == 'expired_token':
                        st.error("⏰ Authentication code expired. Please start over.")
                        # Clear auth session state
                        for key in ['auth_step', 'device_code', 'user_code', 'verification_uri', 'checking_auth']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                    else:
                        error_desc = token_response.get('error_description', 'Unknown error') if token_response else 'Connection error'
                        st.error(f"❌ Authentication error: {error_desc}")
                        st.session_state.checking_auth = False
        
        st.markdown('</div>', unsafe_allow_html=True)
        return False

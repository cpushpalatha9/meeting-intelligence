import os
from dataclasses import dataclass

@dataclass
class IntegrationStatus:
    provider: str
    configured: bool
    message: str


def status(provider):
    if provider.lower() == 'zoom':
        configured = bool(os.getenv('ZOOM_ACCOUNT_ID') and os.getenv('ZOOM_CLIENT_ID') and os.getenv('ZOOM_CLIENT_SECRET'))
    else:
        configured = bool(os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'))
    return IntegrationStatus(provider, configured, 'Credentials configured; live retrieval can be enabled.' if configured else 'Connector is ready, but provider credentials are not configured.')


def retrieve_recordings(provider):
    s=status(provider)
    if not s.configured:
        return False, s.message + ' Upload a downloaded recording through Process Intelligence for immediate processing.'
    return False, f'{provider} connector credentials are present. Complete the provider-specific OAuth/recording permission flow before automatic retrieval.'

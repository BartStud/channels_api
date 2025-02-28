from keycloak.keycloak_admin import KeycloakAdmin
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("keycloak")
logger.setLevel(logging.DEBUG)

keycloak_admin = KeycloakAdmin(
    server_url="http://keycloak:8080/",
    client_id="admin-cli",
    client_secret_key="wSVxDu1FL5SIbdDlqEpr9wohnB8bxYO7",
    realm_name="paw_connect",
    verify=False,
)
# ustawiwnia admin-cli
#   - Client authentication - on
#   - Authorization Enabled - on
#   - Direct Access Grants - on
#   - Service Accounts Roles Enabled - on
# client_secret_key -> Clients -> admin-cli -> Credentials -> Client Secret
# dodanie ról:
#   Clients -> admin-cli -> Service Account Roles -> view-users
#   Clients -> admin-cli -> Service Account Roles -> manage-users

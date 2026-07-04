import logging

logger = logging.getLogger(__name__)


def get_claims(event):
    """
    Restituisce i claims del JWT validato da API Gateway.
    """

    return (
        event.get("requestContext", {})
             .get("authorizer", {})
             .get("claims", {})
    )


def get_current_user(event):
    """
    Restituisce il Cognito User ID (sub).
    """

    return get_claims(event).get("sub")


def get_current_email(event):
    """
    Restituisce l'email dell'utente autenticato.
    """

    return get_claims(event).get("email")
from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.compliance import ConsentCreateIn, get_user_consents, record_user_consent
from app.models import AuditLog, ConsentRecord, User
from app.schemas.user import UserRegister


def test_dpdp_consent_and_audit_logging_flow(db):
    # 1. Register User
    reg = register_user(
        user_in=UserRegister(
            email="privacy.artisan@craftlens.org",
            password="SecurePass#123",
            full_name="Craft Artisan Privacy Test",
        ),
        db=db,
    )
    user = db.query(User).filter(User.email == "privacy.artisan@craftlens.org").first()

    # Mock Request
    request = MagicMock()
    request.client.host = "192.168.1.100"

    # 2. Record explicit DPDP consent
    consent_in = ConsentCreateIn(consent_type="DPDP_PRIVACY_POLICY", granted=True)
    res = record_user_consent(consent_in=consent_in, request=request, db=db, current_user=user)
    assert res.success is True
    assert res.data.consent_type == "DPDP_PRIVACY_POLICY"
    assert res.data.granted is True

    # 3. Verify audit log entry was automatically created
    audit = db.query(AuditLog).filter(AuditLog.user_id == user.id).first()
    assert audit is not None
    assert audit.action == "RECORD_CONSENT"
    assert audit.resource == "ConsentRecord"
    assert audit.ip_address == "192.168.1.100"

    # 4. Retrieve user consents
    list_res = get_user_consents(db=db, current_user=user)
    assert len(list_res.data) == 1
    assert list_res.data[0].consent_type == "DPDP_PRIVACY_POLICY"

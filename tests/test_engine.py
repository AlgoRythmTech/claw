from secretary.config import Settings
from secretary.engine import SecretaryEngine
from secretary.memory import MemoryStore
from secretary.models import IncomingMessage


def test_master_can_schedule(tmp_path):
    settings = Settings(master_number="+15550001", database_path=str(tmp_path / "m.db"), master_name="Avery")
    store = MemoryStore(settings.database_path)
    store.upsert_contact(settings.master_number, "master", "Avery")
    engine = SecretaryEngine(settings, store)

    reply = engine.handle(IncomingMessage(sender=settings.master_number, body="schedule board review at 2026-03-04 10:00"))

    assert "Scheduled" in reply.text
    assert store.upcoming_commitments()[0][0] == "Board Review"


def test_external_gets_secretary_style_reply(tmp_path):
    settings = Settings(master_number="+15550001", database_path=str(tmp_path / "m.db"), master_name="Avery")
    store = MemoryStore(settings.database_path)
    store.upsert_contact(settings.master_number, "master", "Avery")
    engine = SecretaryEngine(settings, store)

    reply = engine.handle(IncomingMessage(sender="+18889990000", body="Is he available tomorrow?"))

    assert "manage Avery's calendar" in reply.text

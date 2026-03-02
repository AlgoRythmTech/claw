from secretary.config import Settings
from secretary.memory import MemoryStore
from secretary.models import ContactTier, IncomingMessage, SecretaryReply


class SecretaryEngine:
    def __init__(self, settings: Settings, store: MemoryStore) -> None:
        self.settings = settings
        self.store = store

    def _tier_for(self, phone: str) -> ContactTier:
        if phone == self.settings.master_number:
            return ContactTier.master
        contact = self.store.get_contact(phone)
        if contact:
            return ContactTier(contact[1])
        return ContactTier.unknown

    def _tone_prefix(self, tier: ContactTier) -> str:
        return {
            ContactTier.master: "Understood.",
            ContactTier.high_priority: "Thank you for reaching out.",
            ContactTier.close: "Of course.",
            ContactTier.professional: "Noted.",
            ContactTier.unknown: "Hello.",
        }[tier]

    def handle(self, msg: IncomingMessage) -> SecretaryReply:
        tier = self._tier_for(msg.sender)
        self.store.remember_message(msg.sender, "incoming", msg.body)

        lower = msg.body.lower()
        if tier == ContactTier.master:
            if lower.startswith("tag "):
                _, phone, new_tier = msg.body.split(maxsplit=2)
                self.store.upsert_contact(phone.strip(), new_tier.strip())
                reply = SecretaryReply(f"Contact {phone} is now tagged as {new_tier}.", "updated_contact_tier")
            elif "schedule" in lower and " at " in lower:
                _, payload = msg.body.split("schedule", 1)
                title, starts_at = payload.split(" at ", 1)
                self.store.add_commitment(title.strip().title(), starts_at.strip(), priority=1)
                reply = SecretaryReply(f"Scheduled: {title.strip().title()} at {starts_at.strip()}.", "scheduled_commitment")
            else:
                upcoming = self.store.upcoming_commitments()[:3]
                bullets = "; ".join([f"{title} ({ts})" for title, ts, _ in upcoming]) or "No upcoming commitments yet"
                reply = SecretaryReply(f"{self._tone_prefix(tier)} Current priorities: {bullets}.")
        else:
            if any(k in lower for k in ["available", "meeting", "tomorrow"]):
                reply = SecretaryReply(
                    f"{self._tone_prefix(tier)} I manage {self.settings.master_name}'s calendar. "
                    "Please share your preferred time window and agenda, and I'll revert with confirmation."
                )
            elif "urgent" in lower:
                reply = SecretaryReply(
                    f"{self._tone_prefix(tier)} I understand the urgency. I've flagged this for immediate review and will get back shortly."
                )
            else:
                reply = SecretaryReply(
                    f"{self._tone_prefix(tier)} Please share the objective and deadline so I can prioritize this appropriately."
                )

        self.store.remember_message(msg.sender, "outgoing", reply.text)
        return reply

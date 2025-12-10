"""Utilities for composing SMTP messages."""

import os
from typing import Mapping

from envelope import Envelope


class Mailer:
    """Compose and send emails using the :mod:`envelope` API.

    Environment variables inspected during initialization (roughly in the
    order they are applied):

    * ``SMTP_SERVER`` (default: ``smtp.gmail.com``)
    * ``SMTP_PORT`` (default: ``587``)
    * ``SMTP_USERNAME`` or ``GMAIL_EMAIL_FROM``
    * ``SMTP_PASSWORD`` or ``GMAIL_APP_PW``
    * ``EMAIL_FROM`` or ``GMAIL_EMAIL_FROM``
    * ``EMAIL_TO`` or ``GMAIL_EMAIL_TO`` (used as the default recipient)

    If required values are missing, a clear :class:`EnvironmentError` is
    raised immediately.
    """

    DEFAULT_SMTP_SERVER = "smtp.gmail.com"
    DEFAULT_SMTP_PORT = 587

    def __init__(self, env: Mapping[str, str] | None = None) -> None:
        self._env = env or os.environ

        self.smtp_server = self._env.get("SMTP_SERVER", self.DEFAULT_SMTP_SERVER)
        self.smtp_port = int(self._env.get("SMTP_PORT", str(self.DEFAULT_SMTP_PORT)))

        self.username = self._env.get("SMTP_USERNAME") or self._env.get(
            "GMAIL_EMAIL_FROM"
        )
        raw_password = self._env.get("SMTP_PASSWORD") or self._env.get(
            "GMAIL_APP_PW"
        )
        self.password = raw_password.strip() if raw_password else None

        self.address_from = self._env.get("EMAIL_FROM") or self._env.get(
            "GMAIL_EMAIL_FROM"
        )
        self.default_to = self._env.get("EMAIL_TO") or self._env.get("GMAIL_EMAIL_TO")

        self._ensure_required()

    def _ensure_required(self) -> None:
        missing: list[str] = []

        if not self.address_from:
            missing.append("EMAIL_FROM or GMAIL_EMAIL_FROM")
        if not self.password:
            missing.append("SMTP_PASSWORD or GMAIL_APP_PW")
        if not self.default_to:
            missing.append("EMAIL_TO or GMAIL_EMAIL_TO")

        if missing:
            formatted = ", ".join(missing)
            raise EnvironmentError(f"Missing required environment variables: {formatted}")

        if not self.username:
            # Fall back to the from-address when no username override is supplied.
            self.username = self.address_from

    def compose(self, *, subject: str, message: str, to: str | None = None) -> Envelope:
        """Build an :class:`~envelope.Envelope` with the configured SMTP settings."""

        recipient = to or self.default_to
        if not recipient:
            raise ValueError("Recipient email address not provided")

        envelope = (
            Envelope()
            .from_(self.address_from)
            .to(recipient)
            .subject(subject)
            .message(message)
        )
        envelope.smtp(self.smtp_server, self.smtp_port, self.username, self.password)
        return envelope

    def send(self, *, subject: str, message: str, to: str | None = None) -> None:
        """Compose and immediately send a message."""

        self.compose(subject=subject, message=message, to=to).send()


def main() -> None:
    print("Mailer is ready; configure environment variables before sending.")


if __name__ == "__main__":
    main()

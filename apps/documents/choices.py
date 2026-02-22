"""
Centralised choices for the documents app.
"""

from django.db import models


class DocumentType(models.TextChoices):
    PASSPORT = "PASSPORT", "Passport"
    PHOTO = "PHOTO", "Passport-size Photo"
    BANK_STATEMENT = "BANK_STATEMENT", "Bank Statement"
    INVITATION_LETTER = "INVITATION_LETTER", "Invitation Letter"
    TRAVEL_ITINERARY = "TRAVEL_ITINERARY", "Travel Itinerary"
    ACCOMMODATION_PROOF = "ACCOMMODATION_PROOF", "Accommodation Proof"
    OTHER = "OTHER", "Other"

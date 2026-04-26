START TRANSACTION;

UPDATE visas_visatype
SET code = 'TOURIST',
    name = 'Tourist Visa',
    description = 'Tourist visa for leisure travel. Apply at least 7 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT, TRAVEL_ITINERARY.',
    fee_amount = 50.00,
    max_stay_days = 30,
    is_active = TRUE
WHERE code = 'TOURIST_30';

UPDATE visas_visatype
SET code = 'BUSINESS',
    name = 'Business Visa',
    description = 'Visa for business engagements. Apply at least 14 days before entry. Required documents: PASSPORT, PHOTO, INVITATION_LETTER, BANK_STATEMENT.',
    fee_amount = 120.00,
    max_stay_days = 90,
    is_active = TRUE
WHERE code = 'BUSINESS_90';

UPDATE visas_visatype
SET code = 'STUDENT',
    name = 'Student Visa',
    description = 'Visa for educational programs. Apply at least 30 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT, INVITATION_LETTER, ACCOMMODATION_PROOF.',
    fee_amount = 250.00,
    max_stay_days = 365,
    is_active = TRUE
WHERE code = 'STUDENT_365';

UPDATE visas_visatype
SET code = 'NONIMMIGRANT',
    name = 'Nonimmigrant Visa',
    description = 'General nonimmigrant visa. Apply at least 7 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT.',
    fee_amount = 80.00,
    max_stay_days = 90,
    is_active = TRUE
WHERE code IN ('Nonimmigrant', 'NONIMMIGRANT');

INSERT INTO visas_visatype (
    code,
    name,
    description,
    fee_amount,
    max_stay_days,
    is_active
)
VALUES
    (
        'TOURIST',
        'Tourist Visa',
        'Tourist visa for leisure travel. Apply at least 7 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT, TRAVEL_ITINERARY.',
        50.00,
        30,
        TRUE
    ),
    (
        'BUSINESS',
        'Business Visa',
        'Visa for business engagements. Apply at least 14 days before entry. Required documents: PASSPORT, PHOTO, INVITATION_LETTER, BANK_STATEMENT.',
        120.00,
        90,
        TRUE
    ),
    (
        'STUDENT',
        'Student Visa',
        'Visa for educational programs. Apply at least 30 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT, INVITATION_LETTER, ACCOMMODATION_PROOF.',
        250.00,
        365,
        TRUE
    ),
    (
        'NONIMMIGRANT',
        'Nonimmigrant Visa',
        'General nonimmigrant visa. Apply at least 7 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT.',
        80.00,
        90,
        TRUE
    ),
    (
        'TRANSIT',
        'Transit Visa',
        'Short transit visa for connecting travel. Apply at least 3 days before entry. Required documents: PASSPORT, PHOTO, TRAVEL_ITINERARY.',
        30.00,
        7,
        TRUE
    ),
    (
        'MEDICAL',
        'Medical Visa',
        'Visa for medical treatment visits. Apply at least 10 days before entry. Required documents: PASSPORT, PHOTO, BANK_STATEMENT, INVITATION_LETTER, ACCOMMODATION_PROOF.',
        140.00,
        60,
        TRUE
    ),
    (
        'CONFERENCE',
        'Conference Visa',
        'Visa for conferences and seminars. Apply at least 10 days before entry. Required documents: PASSPORT, PHOTO, INVITATION_LETTER, TRAVEL_ITINERARY, BANK_STATEMENT.',
        110.00,
        30,
        TRUE
    ),
    (
        'FAMILY_VISIT',
        'Family Visit Visa',
        'Visa for visiting family members. Apply at least 7 days before entry. Required documents: PASSPORT, PHOTO, INVITATION_LETTER, ACCOMMODATION_PROOF, BANK_STATEMENT.',
        95.00,
        60,
        TRUE
    ),
    (
        'WORK',
        'Work Visa',
        'Visa for employment-related stays. Apply at least 21 days before entry. Required documents: PASSPORT, PHOTO, INVITATION_LETTER, BANK_STATEMENT, ACCOMMODATION_PROOF.',
        180.00,
        180,
        TRUE
    )
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    description = VALUES(description),
    fee_amount = VALUES(fee_amount),
    max_stay_days = VALUES(max_stay_days),
    is_active = VALUES(is_active);

COMMIT;

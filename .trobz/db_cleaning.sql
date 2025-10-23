UPDATE ir_cron SET active = FALSE;
DELETE FROM ir_mail_server;
DELETE FROM fetchmail_server;
DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';
DELETE FROM queue_job where state in ('pending', 'started');

-- ##### comment these lines for migrated
-- UPDATE res_users SET password = 'songonight' WHERE login = 'admin';
-- UPDATE res_users SET password = 1 WHERE id > 2;

UPDATE ir_module_module SET state = 'uninstalled'
WHERE name = 'hw_cashlogy';

CREATE OR REPLACE FUNCTION _foodcoop_clean_partner()
  RETURNS void
  LANGUAGE PLPGSQL
AS $$
DECLARE
  PARTNER_NAME text := 'Dupont';
  PARTNER_CITY text := 'Paris';
  PARTNER_STREET text := '112 rue du Sacré Coeur';
  PARTNER_ZIP text := '75000';
  PARTNER_TZ text := 'Europe/Paris';

  v_partner_ref text;
  v_partner_phone text;
  v_partner_mobile text;
  v_partner_email text;
  v_title_id int;
  v_partner_birth date;
  v_partner_country int;

  v_record record;

BEGIN
  SELECT id INTO v_title_id
  FROM res_partner_title
  WHERE shortcut ilike 'Mr.%' LIMIT 1;

  FOR v_record IN (SELECT * FROM res_partner) LOOP

    -- 4320
    v_partner_ref := floor(random() * (9999 - 1000 + 1) + 1000);
    -- 0660254327
    v_partner_phone := '0' || floor(random() * (999999999 - 100000000 + 1) + 100000000)::text;
    -- dupont[random_number]@gmail.com
    v_partner_email := 'dupont' || v_record.id || '@gmail.com';
    v_partner_birth := ((now() - interval '30 years') + random() * ((now() - interval '19 years') - (now() - interval '30 years')))::date;

    UPDATE res_partner
    SET
      name = PARTNER_NAME,
      display_name = PARTNER_NAME,
      city = PARTNER_CITY,
      street = PARTNER_STREET,
      street2 = PARTNER_STREET,
      zip = PARTNER_ZIP,
      ref = v_partner_ref,
      phone = v_partner_phone,
      mobile = v_partner_phone,
      email = v_partner_email,
      state_id = NULL,
      title = v_title_id,
      tz = PARTNER_TZ,
      -- adult_number_home = 3,
      birthdate = v_partner_birth,
      comment = NULL,
      contact_us_message = NULL,
      date_of_death = NULL,
      email_validation_string = NULL,
      -- Job Function
      function = NULL,
      sex = 'm',
      website = NULL
    WHERE id = v_record.id;

    DELETE FROM ir_attachment
    WHERE res_name = 'res.partner' AND res_id = v_record.id;

  END LOOP;

  -- Reset users' signature
  UPDATE res_users
  SET signature = NULL
  WHERE id <> 1;

  -- Keep login info for internal users
  UPDATE res_users
  SET login = 'dupont' || res_users.id || '@gmail.com'
  WHERE id <> 1 AND share <> 'f';

  UPDATE res_partner_bank
  SET
    sanitized_acc_number = 'FR' || res_partner_bank.id,
    acc_number = res_partner_bank.id;

  SELECT id INTO v_partner_country
  FROM res_country
  WHERE code = 'FR' LIMIT 1;

  FOR v_record IN (SELECT * FROM res_bank) LOOP

    RAISE NOTICE '[INFO] Processing bank %', v_record.name;

    v_partner_phone := '0' || floor(random() * (999999999 - 100000000 + 1) + 100000000)::text;
    v_partner_email := 'dupont' || v_record.id || '@gmail.com';

    UPDATE res_bank
    SET
      name = PARTNER_NAME,
      zip = PARTNER_ZIP,
      city = PARTNER_CITY,
      country = v_partner_country,
      street2 = PARTNER_STREET,
      street = PARTNER_STREET,
      bic = NULL,
      state = NULL,
      phone = v_partner_phone,
      email = v_partner_email
    WHERE id = v_record.id;

  END LOOP;

  UPDATE mail_mass_mailing_contact
  SET name = PARTNER_NAME,
    email = 'dupont' || mail_mass_mailing_contact.id || '@gmail.com';

END;
$$;

CREATE OR REPLACE FUNCTION _foodcoop_clean_mail_message()
  RETURNS void
  LANGUAGE PLPGSQL
AS $$
BEGIN
  UPDATE mail_tracking_value
  SET
    old_value_datetime = NULL,
    old_value_monetary = NULL,
    new_value_monetary = NULL,
    old_value_char = NULL,
    old_value_float = NULL,
    new_value_text = NULL,
    new_value_float = NULL,
    old_value_text = NULL,
    new_value_char = NULL,
    new_value_datetime = NULL,
    new_value_integer = NULL,
    old_value_integer = NULL;

  UPDATE mail_message
  SET
    -- dupont[random_number]@gmail.com
    email_from = 'dupont' || mail_message.id || '@gmail.com',
    reply_to = 'dupont' || mail_message.id || '@gmail.com',
    body = NULL,
    subject = NULL;

  UPDATE mail_mail
  SET body_html = NULL, email_cc = NULL, email_to = NULL;

  DELETE FROM ir_attachment
  WHERE res_model = 'mail.message';

  UPDATE mail_mass_mailing
  SET
    body_html = NULL,
    reply_to = 'dupont' || mail_mass_mailing.id || '@gmail.com',
    email_from = 'dupont' || mail_mass_mailing.id || '@gmail.com';

END;
$$;

CREATE OR REPLACE FUNCTION _foodcoop_clean_project()
  RETURNS void
  LANGUAGE PLPGSQL
AS $$
BEGIN
  UPDATE project_task
  SET description = NULL;
END;
$$;

-- ##### comment these lines for migrated
-- SELECT _foodcoop_clean_partner();
-- SELECT _foodcoop_clean_mail_message();
-- SELECT _foodcoop_clean_project();

DROP FUNCTION IF EXISTS _foodcoop_clean_partner();
DROP FUNCTION IF EXISTS _foodcoop_clean_mail_message();
DROP FUNCTION IF EXISTS _foodcoop_clean_project();

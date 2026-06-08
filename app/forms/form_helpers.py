def required_fields_present(form, field_names):
    return all(form.get(field_name, "").strip() for field_name in field_names)
